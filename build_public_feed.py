#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""تحويل ملفات Steam/Epic الداخلية إلى feed صغير وآمن للواجهة."""

import datetime
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from update_timestamp import utc_now_iso, validate_source

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


ROOT = Path(__file__).resolve().parent
ALLOWED_STORE_HOSTS = {
    "steam": {"store.steampowered.com"},
    "epic": {"store.epicgames.com"},
}


def valid_https_url(value: Any, allowed_hosts: set[str] | None = None) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    parsed = urlparse(value.strip())
    if parsed.scheme != "https" or not parsed.hostname:
        return None
    if allowed_hosts is not None and parsed.hostname.lower() not in allowed_hosts:
        return None
    return value.strip()


def canonical_store_url(value: Any, store: str) -> str | None:
    safe_url = valid_https_url(value, ALLOWED_STORE_HOSTS[store])
    if safe_url is None:
        return None
    parsed = urlparse(safe_url)
    # Steam يغيّر معاملات snr باستمرار؛ ليست جزءًا من هوية العرض.
    return parsed._replace(query="", fragment="").geturl()


def normalize_utc_timestamp(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    try:
        parsed = datetime.datetime.fromisoformat(text.replace("Z", "+00:00").replace(" ", "T"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        # تواريخ انتهاء العروض القديمة جُمعت على GitHub runner بتوقيت UTC.
        parsed = parsed.replace(tzinfo=datetime.timezone.utc)
    return parsed.astimezone(datetime.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def normalize_game(raw: Any, store: str) -> dict[str, Any] | None:
    if not isinstance(raw, list) or len(raw) < 7:
        return None

    title = str(raw[0] or "").strip()
    store_url = canonical_store_url(raw[1], store)
    discount_label = str(raw[6] or "").strip()
    if not title or not store_url or "100%" not in discount_label:
        return None
    if "Coming Soon" in discount_label or "مجاني دائماً" in discount_label:
        return None

    image = valid_https_url(raw[2])
    fallback_image = valid_https_url(raw[3]) if store == "steam" and len(raw) > 3 else None
    end_at = normalize_utc_timestamp(raw[7]) if len(raw) > 7 and raw[7] else None
    if end_at:
        end_datetime = datetime.datetime.fromisoformat(end_at.replace("Z", "+00:00"))
        if end_datetime <= datetime.datetime.now(datetime.timezone.utc):
            return None

    identifier = hashlib.sha256(f"{store}:{store_url}".encode("utf-8")).hexdigest()[:16]
    return {
        "id": f"{store}-{identifier}",
        "store": store,
        "title": title,
        "url": store_url,
        "image": image,
        "fallback_image": fallback_image,
        "original_price": str(raw[4] or "").strip(),
        "current_price": str(raw[5] or "").strip(),
        "discount_label": discount_label,
        "discount_percent": 100,
        "end_at": end_at,
    }


def load_deals() -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    configs = {
        "steam": ("free_goods_detail.json", ["discounted_games"]),
        "epic": ("epic_goods_detail.json", ["free_games", "discounted_games"]),
    }
    deals: list[dict[str, Any]] = []
    sources: dict[str, dict[str, Any]] = {}
    seen: set[str] = set()

    for store, (filename, list_names) in configs.items():
        filepath = ROOT / filename
        validation = validate_source(store, str(filepath))
        with filepath.open("r", encoding="utf-8") as source_file:
            data = json.load(source_file)

        sources[store] = {
            "last_success": validation["updated_at"].isoformat(timespec="seconds").replace("+00:00", "Z"),
            "source_total": validation["total_count"],
            "status": "ok",
        }

        for list_name in list_names:
            for raw_game in data.get(list_name, []):
                game = normalize_game(raw_game, store)
                if game and game["id"] not in seen:
                    seen.add(game["id"])
                    deals.append(game)

    deals.sort(key=lambda game: (game["end_at"] or "9999", game["title"].casefold(), game["id"]))
    return deals, sources


def atomic_write(filepath: Path, data: dict[str, Any]) -> None:
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=filepath.parent, delete=False) as output_file:
            json.dump(data, output_file, ensure_ascii=False, separators=(",", ":"))
            output_file.write("\n")
            output_file.flush()
            os.fsync(output_file.fileno())
            temp_path = Path(output_file.name)
        os.replace(temp_path, filepath)
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()


def load_existing_feed(filepath: Path) -> dict[str, Any] | None:
    try:
        with filepath.open("r", encoding="utf-8") as feed_file:
            feed = json.load(feed_file)
        if isinstance(feed, dict) and isinstance(feed.get("deals"), list):
            return feed
    except (OSError, json.JSONDecodeError):
        pass
    return None


def catalog_changed(existing: dict[str, Any] | None, deals: list[dict[str, Any]]) -> bool:
    """قارن المحتوى الذي يراه الزائر وتجاهل أوقات الفحص المتغيرة."""
    if existing is None or existing.get("schema_version") != 1:
        return True
    return existing.get("deals") != deals


def main() -> int:
    try:
        deals, sources = load_deals()
        output_path = ROOT / "deals.json"
        existing_feed = load_existing_feed(output_path)
        if not catalog_changed(existing_feed, deals):
            print(f"ℹ️ لا يوجد تغير في كتالوج العروض: {len(deals)} عروض نشطة")
            return 0

        feed = {
            "schema_version": 1,
            "generated_at": utc_now_iso(),
            "total_count": len(deals),
            "sources": sources,
            "deals": deals,
        }
        atomic_write(output_path, feed)
        print(f"✅ تم تحديث deals.json: {len(deals)} عروض نشطة")
        return 0
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"❌ فشل إنشاء feed الواجهة: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
