#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Collect active Steam games whose current discount is exactly 100%."""

from __future__ import annotations

import datetime
import json
import os
import re
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, urlunparse

import requests
from bs4 import BeautifulSoup, Tag
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = ROOT / "free_goods_detail.json"
SEARCH_URL = "https://store.steampowered.com/search/results/"
APP_DETAILS_URL = "https://store.steampowered.com/api/appdetails"
SEARCH_STARTS = (0, 100, 200)
ACTIVE = "active"
EXPIRED = "expired"
UNKNOWN = "unknown"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}


def make_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        status=3,
        backoff_factor=0.7,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
        respect_retry_after_header=True,
    )
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


def canonical_app_url(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    parsed = urlparse(value.strip())
    if parsed.scheme != "https" or parsed.hostname != "store.steampowered.com":
        return None
    if not re.match(r"^/app/\d+(?:/[^/]*)?/?$", parsed.path):
        return None
    return urlunparse(("https", "store.steampowered.com", parsed.path, "", "", ""))


def extract_appid(value: Any) -> str | None:
    url = canonical_app_url(value)
    if not url:
        return None
    match = re.search(r"/app/(\d+)", url)
    return match.group(1) if match else None


def fetch_search_page(start: int) -> list[Tag] | None:
    params = {
        "specials": 1,
        "sort_by": "Price_ASC",
        "start": start,
        "count": 100,
        "infinite": 1,
        "cc": "us",
        "l": "english",
    }
    try:
        response = make_session().get(
            SEARCH_URL,
            params=params,
            headers={**HEADERS, "Accept": "application/json"},
            timeout=25,
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("success") != 1 or not isinstance(payload.get("results_html"), str):
            raise ValueError("invalid Steam search response")
        return BeautifulSoup(payload["results_html"], "html.parser").select("a.search_result_row")
    except (requests.RequestException, ValueError, json.JSONDecodeError) as error:
        print(f"⚠️ تعذر جلب صفحة Steam عند {start}: {error}")
        return None


def parse_search_row(row: Tag) -> dict[str, str] | None:
    discount = row.select_one('.search_discount_block[data-discount="100"]')
    title = row.select_one("span.title")
    url = canonical_app_url(row.get("href"))
    appid = extract_appid(url)
    if not discount or not title or not url or not appid:
        return None

    final_price = discount.select_one(".discount_final_price")
    final_text = final_price.get_text(" ", strip=True).casefold() if final_price else ""
    if final_text and not ("free" in final_text or re.fullmatch(r"[$€£]?\s*0(?:[.,]00)?", final_text)):
        return None

    original = discount.select_one(".discount_original_price")
    return {
        "appid": appid,
        "title": title.get_text(" ", strip=True),
        "url": url,
        "original_price": original.get_text(" ", strip=True) if original else "",
        "current_price": "$0.00",
    }


def fetch_app_details(appid: str) -> dict[str, Any] | None:
    try:
        response = make_session().get(
            APP_DETAILS_URL,
            params={"appids": appid, "cc": "us", "l": "english"},
            headers=HEADERS,
            timeout=20,
        )
        response.raise_for_status()
        entry = response.json().get(appid, {})
        if not entry.get("success") or not isinstance(entry.get("data"), dict):
            return None
        return entry["data"]
    except (requests.RequestException, ValueError, json.JSONDecodeError):
        return None


def fetch_storefront(appid: str) -> str | None:
    try:
        response = make_session().get(
            f"https://store.steampowered.com/app/{appid}/",
            params={"cc": "us", "l": "english"},
            headers={**HEADERS, "Cookie": "timezoneOffset=0,0"},
            timeout=20,
        )
        response.raise_for_status()
        return response.text
    except requests.RequestException:
        return None


def storefront_has_temporary_giveaway(html: str) -> bool:
    """Recognize Steam's temporary free-to-keep purchase block.

    Steam sets ``is_free`` to true in appdetails during some limited giveaways,
    exactly as it does for permanently free games. The storefront purchase
    block carries the information needed to distinguish the two cases.
    """
    soup = BeautifulSoup(html, "html.parser")
    for purchase in soup.select(".game_area_purchase_game"):
        license_form = purchase.select_one(
            'form[action*="/freelicense/addfreelicense/"]'
        )
        notice = purchase.select_one(".game_purchase_discount_quantity")
        percent = purchase.select_one(".discount_pct")
        original = purchase.select_one(".discount_original_price")
        final = purchase.select_one(".discount_final_price")
        if not all((license_form, notice, percent, original, final)):
            continue

        notice_text = notice.get_text(" ", strip=True).casefold()
        percent_text = re.sub(r"\s+", "", percent.get_text(" ", strip=True))
        original_text = original.get_text(" ", strip=True)
        final_text = final.get_text(" ", strip=True).casefold()
        is_zero = "free" in final_text or bool(
            re.fullmatch(r"[$€£]?\s*0(?:[.,]00)?", final_text)
        )
        if (
            "free to keep" in notice_text
            and "before" in notice_text
            and percent_text == "-100%"
            and re.search(r"[1-9]", original_text)
            and is_zero
        ):
            return True
    return False


def parse_storefront_giveaway_end(
    html: str, now: datetime.datetime | None = None
) -> str | None:
    """Parse Steam's English free-to-keep deadline as UTC.

    ``fetch_storefront`` pins Steam's display timezone to UTC. Steam omits the
    year in this label, so an already-passed month/day belongs to the next year.
    """
    soup = BeautifulSoup(html, "html.parser")
    for purchase in soup.select(".game_area_purchase_game"):
        if not storefront_has_temporary_giveaway(str(purchase)):
            continue
        notice = purchase.select_one(".game_purchase_discount_quantity")
        match = re.search(
            r"free to keep.+?before\s+([a-z]{3,9})\s+(\d{1,2})\s*@\s*"
            r"(\d{1,2}):(\d{2})\s*(am|pm)",
            notice.get_text(" ", strip=True),
            flags=re.IGNORECASE,
        )
        if not match:
            continue
        try:
            month = datetime.datetime.strptime(match.group(1)[:3], "%b").month
            day, hour, minute = map(int, match.group(2, 3, 4))
            meridiem = match.group(5).casefold()
            hour = hour % 12 + (12 if meridiem == "pm" else 0)
            current = now or datetime.datetime.now(datetime.timezone.utc)
            if current.tzinfo is None:
                current = current.replace(tzinfo=datetime.timezone.utc)
            else:
                current = current.astimezone(datetime.timezone.utc)
            end = datetime.datetime(
                current.year, month, day, hour, minute, tzinfo=datetime.timezone.utc
            )
            if end <= current:
                end = end.replace(year=current.year + 1)
            return end.isoformat(timespec="seconds").replace("+00:00", "Z")
        except ValueError:
            continue
    return None


def discount_status(appid: str) -> str:
    """Return ACTIVE only for a game with an exact 100% temporary discount."""
    data = fetch_app_details(appid)
    if data is not None and data.get("type") != "game":
        return EXPIRED
    if data is not None:
        price = data.get("price_overview")
        if (
            isinstance(price, dict)
            and price.get("discount_percent") == 100
            and price.get("final") == 0
        ):
            return ACTIVE

    storefront = fetch_storefront(appid)
    if storefront is None:
        return UNKNOWN
    return ACTIVE if storefront_has_temporary_giveaway(storefront) else EXPIRED


def fetch_discount_end(appid: str) -> str | None:
    html = fetch_storefront(appid)
    if html is None:
        return None
    match = re.search(r'"discount_expiration"\s*:\s*(\d+)', html)
    if not match:
        return parse_storefront_giveaway_end(html)
    try:
        timestamp = int(match.group(1))
        if timestamp > 10**12:
            timestamp //= 1000
        return datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).isoformat(
            timespec="seconds"
        ).replace("+00:00", "Z")
    except (OSError, ValueError):
        return None


def candidate_to_row(candidate: dict[str, str], end_at: str | None = None) -> list[Any]:
    appid = candidate["appid"]
    return [
        candidate["title"],
        candidate["url"],
        f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg",
        f"https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/capsule_616x353.jpg",
        candidate.get("original_price", ""),
        candidate.get("current_price", "$0.00"),
        "100%",
        end_at,
    ]


def load_previous_games() -> list[list[Any]]:
    try:
        data = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
        games = data.get("discounted_games", [])
        return [
            game for game in games
            if isinstance(game, list) and len(game) >= 7 and game[6] == "100%"
        ]
    except (OSError, ValueError, json.JSONDecodeError):
        return []


def atomic_write(data: dict[str, Any]) -> None:
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=ROOT, delete=False) as output:
            json.dump(data, output, ensure_ascii=False, indent=2)
            output.flush()
            os.fsync(output.fileno())
            temp_path = Path(output.name)
        os.replace(temp_path, OUTPUT_PATH)
    finally:
        if temp_path and temp_path.exists():
            temp_path.unlink()


def collect() -> list[list[Any]]:
    pages: list[list[Tag]] = []
    with ThreadPoolExecutor(max_workers=len(SEARCH_STARTS)) as executor:
        futures = {executor.submit(fetch_search_page, start): start for start in SEARCH_STARTS}
        for future in as_completed(futures):
            rows = future.result()
            if rows is not None:
                pages.append(rows)
    if not pages:
        raise RuntimeError("فشلت جميع طلبات بحث Steam؛ لن يتم استبدال البيانات الحالية")

    candidates: dict[str, dict[str, str]] = {}
    for rows in pages:
        for row in rows:
            candidate = parse_search_row(row)
            if candidate:
                candidates[candidate["appid"]] = candidate

    previous = load_previous_games()
    previous_by_appid = {
        appid: game for game in previous if (appid := extract_appid(game[1]))
    }
    ids_to_verify = set(candidates) | set(previous_by_appid)
    statuses: dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(discount_status, appid): appid for appid in ids_to_verify}
        for future in as_completed(futures):
            statuses[futures[future]] = future.result()

    active: list[list[Any]] = []
    for appid, candidate in candidates.items():
        if statuses.get(appid) == ACTIVE:
            active.append(candidate_to_row(candidate, fetch_discount_end(appid)))

    for appid, game in previous_by_appid.items():
        if appid in candidates:
            continue
        status = statuses.get(appid, UNKNOWN)
        if status in {ACTIVE, UNKNOWN}:
            active.append(game)
            if status == UNKNOWN:
                print(f"⚠️ تعذر التحقق من {game[0]}؛ تم الاحتفاظ به مؤقتاً")
        else:
            print(f"🗑️ أزيل العرض غير النشط: {game[0]}")

    unique = {extract_appid(game[1]): game for game in active}
    return sorted(unique.values(), key=lambda game: (str(game[0]).casefold(), str(game[1])))


def main() -> int:
    print("🔍 البحث عن ألعاب Steam ذات خصم 100% فقط...")
    try:
        games = collect()
    except RuntimeError as error:
        print(f"❌ {error}")
        return 1
    atomic_write({
        "total_count": len(games),
        "free_games": [],
        "discounted_games": games,
        "update_time": datetime.datetime.now(datetime.timezone.utc).isoformat(
            timespec="seconds"
        ).replace("+00:00", "Z"),
    })
    print(f"✅ تم حفظ {len(games)} عرض Steam نشط بخصم 100%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
