#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Collect active Steam games whose current discount is exactly 100%."""

from __future__ import annotations

import datetime
import json
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, urlunparse

import requests
from bs4 import BeautifulSoup, Tag
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from update_timestamp import atomic_write_json, utc_now_iso

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = ROOT / "free_goods_detail.json"
SEARCH_URL = "https://store.steampowered.com/search/results/"
APP_DETAILS_URL = "https://store.steampowered.com/api/appdetails"
SEARCH_PAGE_SIZE = 100
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
    try:
        parsed = urlparse(value.strip())
    except ValueError:
        return None
    if parsed.scheme != "https" or parsed.netloc.lower() != "store.steampowered.com":
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


def fetch_search_page(start: int) -> tuple[list[Tag], int]:
    params = {
        "specials": 1,
        "maxprice": "free",
        "category1": 998,
        "sort_by": "Price_ASC",
        "start": start,
        "count": SEARCH_PAGE_SIZE,
        "infinite": 1,
        "cc": "us",
        "l": "english",
    }
    try:
        with make_session() as session:
            response = session.get(
                SEARCH_URL,
                params=params,
                headers={**HEADERS, "Accept": "application/json"},
                timeout=25,
            )
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict) or payload.get("success") != 1:
            raise ValueError("invalid Steam search response")
        total = payload.get("total_count")
        html = payload.get("results_html")
        reported_start = payload.get("start")
        if (
            type(total) is not int or total < 0 or not isinstance(html, str)
            or (reported_start != start and not (reported_start == -1 and start >= total))
        ):
            raise ValueError("invalid Steam search pagination")
        rows = BeautifulSoup(html, "html.parser").select("a.search_result_row")
        if start < total and not rows:
            raise ValueError("Steam search returned an empty page before the end")
        return rows, total
    except (requests.RequestException, ValueError) as error:
        raise RuntimeError(f"تعذر جلب صفحة Steam عند {start}: {error}") from error


def parse_search_row(row: Tag) -> dict[str, str] | None:
    discount = row.select_one('.search_discount_block[data-discount="100"]')
    title = row.select_one("span.title")
    url = canonical_app_url(row.get("href"))
    appid = extract_appid(url)
    if not discount or not title or not url or not appid:
        return None

    final_price = discount.select_one(".discount_final_price")
    final_text = final_price.get_text(" ", strip=True).casefold() if final_price else ""
    if not is_zero_price(final_text):
        return None

    original = discount.select_one(".discount_original_price")
    original_price = original.get_text(" ", strip=True) if original else ""
    if not re.search(r"[1-9]", original_price):
        return None
    return {
        "appid": appid,
        "title": title.get_text(" ", strip=True),
        "url": url,
        "original_price": original_price,
        "current_price": "$0.00",
    }


def fetch_app_details(appid: str) -> dict[str, Any] | None:
    try:
        with make_session() as session:
            response = session.get(
                APP_DETAILS_URL,
                params={"appids": appid, "cc": "us", "l": "english"},
                headers=HEADERS,
                timeout=20,
            )
        response.raise_for_status()
        payload = response.json()
        entry = payload.get(appid) if isinstance(payload, dict) else None
        if not isinstance(entry, dict) or not entry.get("success") or not isinstance(entry.get("data"), dict):
            return None
        return entry["data"]
    except (requests.RequestException, ValueError):
        return None


def fetch_storefront(appid: str) -> str | None:
    try:
        with make_session() as session:
            response = session.get(
                f"https://store.steampowered.com/app/{appid}/",
                params={"cc": "us", "l": "english"},
                headers={**HEADERS, "Cookie": "timezoneOffset=0,0; birthtime=631152000; lastagecheckage=1-January-1990"},
                timeout=20,
            )
        response.raise_for_status()
        return response.text if extract_appid(response.url) == appid else None
    except requests.RequestException:
        return None


def is_zero_price(text: str) -> bool:
    return text.casefold() == "free" or bool(re.fullmatch(r"[$€£]?\s*0(?:[.,]00)?", text))


def giveaway_notices(html: str) -> list[str]:
    """Find notices attached to Steam's free-to-keep purchase blocks."""
    soup = BeautifulSoup(html, "html.parser")
    notices = []
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

        notice_text = notice.get_text(" ", strip=True)
        percent_text = re.sub(r"\s+", "", percent.get_text(" ", strip=True))
        original_text = original.get_text(" ", strip=True)
        final_text = final.get_text(" ", strip=True).casefold()
        if (
            "free to keep" in notice_text.casefold()
            and "before" in notice_text.casefold()
            and percent_text == "-100%"
            and re.search(r"[1-9]", original_text)
            and is_zero_price(final_text)
        ):
            notices.append(notice_text)
    return notices


def storefront_has_temporary_giveaway(html: str) -> bool:
    return bool(giveaway_notices(html))


def parse_storefront_giveaway_end(
    html: str, now: datetime.datetime | None = None
) -> str | None:
    return parse_giveaway_end(giveaway_notices(html), now)


def parse_giveaway_end(notices: list[str], now: datetime.datetime | None = None) -> str | None:
    """Parse Steam's English free-to-keep deadline as UTC.

    ``fetch_storefront`` pins Steam's display timezone to UTC. Steam omits the
    year in this label. December offers can end in January of the next year.
    """
    for notice_text in notices:
        month_first = re.search(
            r"free to keep.+?before\s+(?P<month>[a-z]{3,9})\s+"
            r"(?P<day>\d{1,2})\s*@\s*(?P<hour>\d{1,2}):"
            r"(?P<minute>\d{2})\s*(?P<meridiem>am|pm)",
            notice_text,
            flags=re.IGNORECASE,
        )
        day_first = re.search(
            r"free to keep.+?before\s+(?P<day>\d{1,2})\s+"
            r"(?P<month>[a-z]{3,9})\s*@\s*(?P<hour>\d{1,2}):"
            r"(?P<minute>\d{2})\s*(?P<meridiem>am|pm)",
            notice_text,
            flags=re.IGNORECASE,
        )
        match = month_first or day_first
        if match is None:
            continue
        try:
            month = datetime.datetime.strptime(match.group("month")[:3], "%b").month
            day = int(match.group("day"))
            hour = int(match.group("hour"))
            if not 1 <= hour <= 12:
                continue
            minute = int(match.group("minute"))
            meridiem = match.group("meridiem").casefold()
            hour = hour % 12 + (12 if meridiem == "pm" else 0)
            current = now or datetime.datetime.now(datetime.timezone.utc)
            if current.tzinfo is None:
                current = current.replace(tzinfo=datetime.timezone.utc)
            else:
                current = current.astimezone(datetime.timezone.utc)
            end = datetime.datetime(
                current.year, month, day, hour, minute, tzinfo=datetime.timezone.utc
            )
            if current.month == 12 and month == 1:
                end = end.replace(year=current.year + 1)
            if current.month == 1 and month == 12:
                end = end.replace(year=current.year - 1)
            return end.isoformat(timespec="seconds").replace("+00:00", "Z")
        except ValueError:
            continue
    return None


def inspect_discount(appid: str, now: datetime.datetime | None = None) -> tuple[str, str | None]:
    """Check a Steam app and get its deadline from the same storefront response."""
    data = fetch_app_details(appid)
    if data and data.get("type") and data["type"] != "game":
        return EXPIRED, None
    price = data.get("price_overview") if data else None
    api_active = (
        isinstance(price, dict)
        and price.get("discount_percent") == 100
        and price.get("final") == 0
    )
    storefront = fetch_storefront(appid)
    if storefront is None:
        return (ACTIVE if api_active else UNKNOWN), None

    notices = giveaway_notices(storefront)
    if notices:
        now = now or datetime.datetime.now(datetime.timezone.utc)
        end = parse_giveaway_end(notices, now)
        if end and datetime.datetime.fromisoformat(end) <= now:
            return EXPIRED, None
        return ACTIVE, end
    if api_active:
        return ACTIVE, parse_discount_expiration(storefront)
    if data and data.get("type") == "game" and BeautifulSoup(storefront, "html.parser").select_one(".game_area_purchase_game"):
        return EXPIRED, None
    return UNKNOWN, None


def parse_discount_expiration(html: str) -> str | None:
    timestamps = set(re.findall(r'"discount_expiration"\s*:\s*(\d+)', html))
    if len(timestamps) != 1:
        return None
    try:
        timestamp = int(timestamps.pop())
        if timestamp > 10**12:
            timestamp //= 1000
        end = datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc)
        if end > datetime.datetime.now(datetime.timezone.utc):
            return end.isoformat(timespec="seconds").replace("+00:00", "Z")
    except (OSError, OverflowError, ValueError):
        return None
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


def load_previous_catalog() -> dict[str, Any]:
    try:
        data = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def atomic_write(data: dict[str, Any]) -> None:
    atomic_write_json(OUTPUT_PATH, data)


def collect(previous: list[Any]) -> tuple[list[list[Any]], bool]:
    first_page, total = fetch_search_page(0)
    candidates: dict[str, dict[str, str]] = {}
    start, rows = 0, first_page
    while True:
        for row in rows:
            candidate = parse_search_row(row)
            if candidate:
                candidates[candidate["appid"]] = candidate
        start += SEARCH_PAGE_SIZE
        if start >= total:
            break
        rows, total = fetch_search_page(start)

    previous_by_appid = {
        appid: game for game in previous
        if isinstance(game, list) and len(game) >= 7 and game[6] == "100%"
        and (appid := extract_appid(game[1]))
    }
    ids_to_verify = sorted(set(candidates) | set(previous_by_appid))
    active: list[list[Any]] = []
    complete = True
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = executor.map(inspect_discount, ids_to_verify)
        for appid, (status, end_at) in zip(ids_to_verify, results, strict=True):
            previous_game = previous_by_appid.get(appid)
            if status == UNKNOWN:
                complete = False
                print(f"⚠️ تعذر التحقق من عرض Steam للتطبيق {appid}")
                if previous_game:
                    active.append(previous_game)
            elif status == ACTIVE:
                candidate = candidates.get(appid)
                if candidate:
                    previous_end = previous_game[7] if previous_game and len(previous_game) > 7 else None
                    active.append(candidate_to_row(candidate, end_at or previous_end))
                elif previous_game:
                    active.append([*previous_game[:7], end_at] if end_at else previous_game)

    return sorted(active, key=lambda game: (str(game[0]).casefold(), str(game[1]))), complete


def main() -> int:
    print("🔍 البحث عن ألعاب Steam ذات خصم 100% فقط...")
    previous = load_previous_catalog()
    previous_games = previous.get("discounted_games")
    try:
        games, complete = collect(previous_games if isinstance(previous_games, list) else [])
    except RuntimeError as error:
        print(f"❌ {error}")
        return 1
    atomic_write({
        "total_count": len(games),
        "free_games": [],
        "discounted_games": games,
        "status": "ok" if complete else "partial",
        "update_time": utc_now_iso() if complete else previous.get("update_time") or utc_now_iso(),
    })
    print(f"✅ تم حفظ {len(games)} عرض Steam نشط بخصم 100%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
