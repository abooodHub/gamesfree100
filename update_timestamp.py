#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""التحقق من ملفات المصادر وإنشاء ملخص لآخر تحديث ناجح."""

import datetime
import json
import os
import sys
import tempfile
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


SOURCE_FILES = {
    "steam": "free_goods_detail.json",
    "epic": "epic_goods_detail.json",
}


def utc_now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_timestamp(value: Any) -> datetime.datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None

    text = value.strip()
    try:
        if text.endswith("Z"):
            return datetime.datetime.fromisoformat(text[:-1] + "+00:00")
        parsed = datetime.datetime.fromisoformat(text.replace(" ", "T"))
        if parsed.tzinfo is None:
            # التوقيت القديم في ملفات المشروع كان بتوقيت الرياض.
            parsed = parsed.replace(tzinfo=datetime.timezone(datetime.timedelta(hours=3)))
        return parsed.astimezone(datetime.timezone.utc)
    except ValueError:
        return None


def validate_source(name: str, filepath: str) -> dict[str, Any]:
    if not os.path.exists(filepath):
        raise ValueError(f"الملف غير موجود: {filepath}")

    with open(filepath, "r", encoding="utf-8") as source_file:
        data = json.load(source_file)

    if not isinstance(data, dict):
        raise ValueError(f"تنسيق غير صحيح في {filepath}")

    free_games = data.get("free_games", [])
    discounted_games = data.get("discounted_games", [])
    if not isinstance(free_games, list) or not isinstance(discounted_games, list):
        raise ValueError(f"قوائم الألعاب غير صالحة في {filepath}")

    expected_total = len(free_games) + len(discounted_games)
    if data.get("total_count") != expected_total:
        raise ValueError(
            f"total_count غير متطابق في {filepath}: "
            f"{data.get('total_count')} != {expected_total}"
        )

    updated_at = parse_timestamp(data.get("update_time"))
    if updated_at is None:
        raise ValueError(f"update_time غير صالح في {filepath}")

    return {
        "name": name,
        "file": filepath,
        "updated_at": updated_at,
        "total_count": expected_total,
        "free_count": len(free_games),
        "discounted_count": len(discounted_games),
    }


def atomic_write_json(filepath: str, data: dict[str, Any]) -> None:
    target_path = os.path.abspath(filepath)
    target_dir = os.path.dirname(target_path)
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=target_dir, delete=False
        ) as output_file:
            json.dump(data, output_file, ensure_ascii=False, indent=2)
            output_file.flush()
            os.fsync(output_file.fileno())
            temp_path = output_file.name
        os.replace(temp_path, target_path)
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)


def source_status(name, filepath, outcome=None, attempted_at=None, previous=None):
    previous = previous or {}
    last_success = previous.get("last_success")
    status = previous.get("status", "unknown")
    try:
        result = validate_source(name, filepath)
        last_success = result["updated_at"].isoformat(timespec="seconds").replace("+00:00", "Z")
        valid = True
    except (OSError, ValueError, TypeError):
        valid = False
    if outcome is not None:
        status = "ok" if outcome == "success" and valid else "error"
    elif not valid:
        status = "error"
    return {
        "last_success": last_success,
        "last_attempt": attempted_at if outcome is not None else previous.get("last_attempt"),
        "status": status,
    }


def main() -> int:
    try:
        with open("update_timestamp.json", encoding="utf-8") as source_file:
            previous = json.load(source_file).get("sources", {})
    except (OSError, ValueError, AttributeError):
        previous = {}
    now = utc_now_iso()
    sources = {
        name: source_status(name, filepath, os.environ.get(f"{name.upper()}_OUTCOME"),
                            now, previous.get(name))
        for name, filepath in SOURCE_FILES.items()
    }
    summary = {
        "schema_version": 1,
        "sources": sources,
    }
    atomic_write_json("update_timestamp.json", summary)
    print("✅ تم حفظ حالة التحقق لكل متجر")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
