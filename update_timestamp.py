#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""التحقق من ملفات المصادر وإنشاء ملخص لآخر تحديث ناجح."""

import datetime
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


ROOT = Path(__file__).resolve().parent
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


def load_validated_source(name: str, filepath: str) -> tuple[dict[str, Any], dict[str, Any]]:
    with open(filepath, "r", encoding="utf-8") as source_file:
        data = json.load(source_file)

    if not isinstance(data, dict):
        raise ValueError(f"تنسيق غير صحيح في {filepath}")

    free_games = data.get("free_games", [])
    discounted_games = data.get("discounted_games", [])
    if not isinstance(free_games, list) or not isinstance(discounted_games, list):
        raise ValueError(f"قوائم الألعاب غير صالحة في {filepath}")

    expected_total = len(free_games) + len(discounted_games)
    if type(data.get("total_count")) is not int or data["total_count"] != expected_total:
        raise ValueError(
            f"total_count غير متطابق في {filepath}: "
            f"{data.get('total_count')} != {expected_total}"
        )

    updated_at = parse_timestamp(data.get("update_time"))
    if updated_at is None:
        raise ValueError(f"update_time غير صالح في {filepath}")

    status = "partial" if data.get("status") == "partial" else "ok"
    if os.environ.get(f"{name.upper()}_OUTCOME") == "failure":
        status = "failed"
    return data, {
        "name": name,
        "file": filepath,
        "updated_at": updated_at,
        "total_count": expected_total,
        "free_count": len(free_games),
        "discounted_count": len(discounted_games),
        "status": status,
    }


def validate_source(name: str, filepath: str) -> dict[str, Any]:
    return load_validated_source(name, filepath)[1]


def atomic_write_json(filepath: str | Path, data: dict[str, Any], *, compact: bool = False) -> None:
    target = Path(filepath).resolve()
    temp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", newline="\n", dir=target.parent, delete=False
        ) as output_file:
            temp_path = Path(output_file.name)
            if compact:
                json.dump(data, output_file, ensure_ascii=False, separators=(",", ":"))
            else:
                json.dump(data, output_file, ensure_ascii=False, indent=2)
            output_file.write("\n")
            output_file.flush()
            os.fsync(output_file.fileno())
        os.replace(temp_path, target)
    finally:
        if temp_path:
            temp_path.unlink(missing_ok=True)


def main() -> int:
    print("🔍 التحقق من ملفات مصادر الألعاب...")
    sources: dict[str, dict[str, Any]] = {}
    latest_success: datetime.datetime | None = None

    try:
        for name, filepath in SOURCE_FILES.items():
            result = validate_source(name, str(ROOT / filepath))
            updated_at = result.pop("updated_at")
            latest_success = max(latest_success, updated_at) if latest_success else updated_at
            sources[name] = {
                **result,
                "file": filepath,
                "last_success": updated_at.isoformat(timespec="seconds").replace("+00:00", "Z"),
            }
            print(f"{name}: {sources[name]['total_count']} ({sources[name]['status']})")
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"❌ فشل التحقق من البيانات: {error}")
        return 1

    summary = {
        "last_attempt": utc_now_iso(),
        "last_update": latest_success.isoformat(timespec="seconds").replace("+00:00", "Z"),
        "sources": sources,
        "updated_files": sum(source["status"] == "ok" for source in sources.values()),
        "total_files": len(SOURCE_FILES),
    }
    atomic_write_json(ROOT / "update_timestamp.json", summary)
    print("✅ تم إنشاء update_timestamp.json من أوقات نجاح المصادر")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
