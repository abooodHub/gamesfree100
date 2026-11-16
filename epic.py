#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Collect currently active 100% discounts from Epic Games Store."""

from __future__ import annotations

import datetime
import re
import sys
from pathlib import Path
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from update_timestamp import atomic_write_json, utc_now_iso

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = ROOT / "epic_goods_detail.json"
ENDPOINTS = (
    "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions",
    "https://store-site-backend-static-ipv4.ak.epicgames.com/freeGamesPromotions",
)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124 Safari/537.36",
    "Accept": "application/json",
    "Accept-Language": "en-US,en;q=0.9",
}


def utc_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


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


def parse_utc(value: Any) -> datetime.datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=datetime.timezone.utc)
    return parsed.astimezone(datetime.timezone.utc)


def active_free_end(game: dict[str, Any], now: datetime.datetime | None = None) -> str | None:
    """Return the end timestamp for an active giveaway, never an upcoming offer."""
    now = now or utc_now()
    price = (game.get("price") or {}).get("totalPrice") or {}
    original = price.get("originalPrice")
    discount = price.get("discountPrice")
    if type(original) is not int or original <= 0 or type(discount) is not int or discount != 0:
        return None
    promotions = (game.get("promotions") or {}).get("promotionalOffers") or []
    ends = []
    for group in promotions:
        for promotion in group.get("promotionalOffers") or []:
            setting = promotion.get("discountSetting") or {}
            start = parse_utc(promotion.get("startDate"))
            end = parse_utc(promotion.get("endDate"))
            if (
                setting.get("discountType") == "PERCENTAGE"
                and type(setting.get("discountPercentage")) is int
                and setting["discountPercentage"] == 0
                and start is not None
                and end is not None
                and start <= now < end
            ):
                ends.append(end)
    return max(ends).isoformat(timespec="seconds").replace("+00:00", "Z") if ends else None


def game_url(game: dict[str, Any]) -> str | None:
    mappings = (game.get("catalogNs") or {}).get("mappings") or []
    slugs = [mapping.get("pageSlug") for mapping in mappings if mapping.get("pageType") in {None, "productHome"}]
    slugs.append(game.get("productSlug"))
    for value in slugs:
        if isinstance(value, str):
            slug = value.strip().removesuffix("/home")
            if re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", slug):
                return f"https://store.epicgames.com/en-US/p/{slug}"
    return None


def image_url(game: dict[str, Any]) -> str:
    preferred = ("OfferImageWide", "DieselStoreFrontWide", "Thumbnail", "DieselStoreFrontTall")
    images = game.get("keyImages") or []
    for image_type in preferred:
        for image in images:
            if image.get("type") == image_type and isinstance(image.get("url"), str):
                return image["url"]
    return ""


def normalize_game(game: dict[str, Any], now: datetime.datetime | None = None) -> list[Any] | None:
    offer_type = game.get("offerType")
    categories = {category.get("path") for category in game.get("categories") or []}
    if offer_type != "BASE_GAME" and not (offer_type == "BUNDLE" and "bundles/games" in categories):
        return None
    end_at = active_free_end(game, now)
    if not end_at:
        return None
    url = game_url(game)
    title = str(game.get("title") or "").strip()
    if not url or not title:
        raise ValueError("Active Epic promotion is missing a game title or store URL")
    price = game["price"]["totalPrice"]
    currency = str(price.get("currencyCode") or price.get("currency") or "USD")
    decimals = (price.get("currencyInfo") or {}).get("decimals", 2)
    original = f"{price['originalPrice'] / 10**decimals:.{decimals}f} {currency}"
    return [
        title,
        url,
        image_url(game),
        str(game.get("description") or game.get("longDescription") or ""),
        original,
        "Free",
        "خصم 100% - مجاني",
        end_at,
    ]


def fetch_catalog() -> list[dict[str, Any]] | None:
    with make_session() as session:
        for endpoint in ENDPOINTS:
            try:
                response = session.get(
                    endpoint,
                    params={"locale": "en-US", "country": "US", "allowCountries": "US"},
                    headers=HEADERS,
                    timeout=30,
                )
                response.raise_for_status()
                elements = response.json()["data"]["Catalog"]["searchStore"]["elements"]
                if not isinstance(elements, list) or not all(isinstance(game, dict) for game in elements):
                    raise ValueError("invalid Epic catalog")
                return elements
            except (requests.RequestException, KeyError, TypeError, ValueError) as error:
                print(f"⚠️ تعذر جلب Epic من {endpoint}: {error}")
    return None


def atomic_write(data: dict[str, Any]) -> None:
    atomic_write_json(OUTPUT_PATH, data)


def main() -> int:
    print("🔍 البحث عن عروض Epic النشطة ذات خصم 100% فقط...")
    catalog = fetch_catalog()
    if catalog is None:
        print("❌ فشل جلب Epic؛ لن يتم استبدال البيانات الحالية")
        return 1
    now = utc_now()
    try:
        games = [normalized for game in catalog if (normalized := normalize_game(game, now))]
    except (AttributeError, TypeError, ValueError) as error:
        print(f"❌ تعذر التحقق من بيانات Epic: {error}")
        return 1
    unique = {game[1]: game for game in sorted(games, key=lambda game: game[7])}
    games = sorted(unique.values(), key=lambda game: (str(game[7]), str(game[0]).casefold()))
    atomic_write({
        "total_count": len(games),
        "free_games": games,
        "discounted_games": [],
        "update_time": utc_now_iso(),
        "source": "Epic Games Store",
    })
    print(f"✅ تم حفظ {len(games)} عرض Epic نشط بخصم 100%")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
