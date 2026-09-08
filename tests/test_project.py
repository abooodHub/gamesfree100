import datetime
import json
import tempfile
import unittest
from unittest.mock import patch, Mock

import steam
import epic
from pathlib import Path

from bs4 import BeautifulSoup

import build_public_feed
import update_timestamp


ROOT = Path(__file__).resolve().parents[1]


class DataValidationTests(unittest.TestCase):
    def test_current_source_files_are_valid(self):
        for name, relative_path in update_timestamp.SOURCE_FILES.items():
            result = update_timestamp.validate_source(name, str(ROOT / relative_path))
            self.assertGreaterEqual(result["total_count"], 0)
            self.assertIsInstance(result["updated_at"], datetime.datetime)
            self.assertIsNotNone(result["updated_at"].tzinfo)

    def test_parse_timestamp_supports_legacy_riyadh_and_utc(self):
        legacy = update_timestamp.parse_timestamp("2026-08-24 21:48:39")
        utc = update_timestamp.parse_timestamp("2026-08-24T18:48:39Z")
        self.assertEqual(legacy, utc)

    def test_atomic_write_json_produces_valid_json(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "result.json"
            update_timestamp.atomic_write_json(str(target), {"ok": True})
            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), {"ok": True})

    def test_public_feed_is_small_and_matches_its_declared_count(self):
        feed_path = ROOT / "deals.json"
        feed = json.loads(feed_path.read_text(encoding="utf-8"))
        self.assertEqual(feed["schema_version"], 1)
        self.assertEqual(feed["total_count"], len(feed["deals"]))
        self.assertLess(feed_path.stat().st_size, 2_000_000)
        for deal in feed["deals"]:
            self.assertIn(deal["store"], {"steam", "epic"})
            self.assertTrue(deal["url"].startswith("https://"))
            self.assertEqual(deal["discount_percent"], 0 if deal.get("offer_type") == "free_to_play" else 100)

    def test_catalog_comparison_ignores_volatile_metadata(self):
        deals = [{"id": "steam-1", "title": "Example"}]
        existing = {
            "schema_version": 1,
            "generated_at": "2026-01-01T00:00:00Z",
            "sources": {"steam": {"last_success": "2026-01-01T00:00:00Z"}},
            "deals": deals,
        }
        self.assertFalse(build_public_feed.catalog_changed(existing, deals.copy()))
        self.assertTrue(build_public_feed.catalog_changed(existing, deals + [{"id": "epic-2"}]))

    def test_store_url_removes_tracking_parameters(self):
        first = build_public_feed.canonical_store_url(
            "https://store.steampowered.com/app/123/Game/?snr=first#details", "steam"
        )
        second = build_public_feed.canonical_store_url(
            "https://store.steampowered.com/app/123/Game/?snr=second", "steam"
        )
        self.assertEqual(first, "https://store.steampowered.com/app/123/Game/")
        self.assertEqual(first, second)

    def test_unchanged_catalog_does_not_rewrite_feed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "deals.json"
            original = {"schema_version": 1, "generated_at": "old", "deals": []}
            build_public_feed.atomic_write(target, original)
            before = target.read_bytes()
            existing = build_public_feed.load_existing_feed(target)
            if build_public_feed.catalog_changed(existing, []):
                build_public_feed.atomic_write(target, {**original, "generated_at": "new"})
            self.assertEqual(target.read_bytes(), before)


class FrontendStructureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "index.html").read_text(encoding="utf-8")
        cls.script = (ROOT / "script.js").read_text(encoding="utf-8")
        cls.soup = BeautifulSoup(cls.html, "html.parser")

    def test_page_has_one_h1_and_core_landmarks(self):
        self.assertEqual(len(self.soup.find_all("h1")), 1)
        self.assertIsNotNone(self.soup.find("main"))
        self.assertIsNotNone(self.soup.find("footer"))

    def test_tabs_are_normal_keyboard_accessible_buttons(self):
        tabs = self.soup.select("button.tab")
        self.assertEqual(len(tabs), 3)
        self.assertTrue(all(tab.get("aria-pressed") in {"true", "false"} for tab in tabs))
        self.assertTrue(all(tab.get("tabindex") is None for tab in tabs))

    def test_consent_and_security_policy_exist(self):
        self.assertIsNotNone(self.soup.select_one("#cookieConsent"))
        self.assertIsNotNone(self.soup.find("meta", attrs={"http-equiv": "Content-Security-Policy"}))

    def test_frontend_does_not_use_html_injection_or_broken_service_worker(self):
        forbidden = ["innerHTML", "outerHTML", "insertAdjacentHTML", "serviceWorker.register", "onerror="]
        for token in forbidden:
            self.assertNotIn(token, self.script)

    def test_frontend_does_not_expire_steam_deals_by_feed_age(self):
        self.assertNotIn("STEAM_MISSING_END_MAX_AGE_MS", self.script)


class WorkflowStructureTests(unittest.TestCase):
    def test_update_workflow_publishes_status_even_without_catalog_changes(self):
        workflow = (ROOT / ".github" / "workflows" / "update.yml").read_text(encoding="utf-8")
        self.assertIn("git diff --quiet -- deals.json update_timestamp.json", workflow)
        self.assertIn("No catalog or status changes; skipping commit", workflow)
        self.assertNotIn("git add .", workflow)

    def test_ci_runs_without_store_scrapers(self):
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertIn("pull_request:", workflow)
        self.assertIn("python -m unittest", workflow)
        self.assertNotIn("python steam.py", workflow)
        self.assertNotIn("python epic.py", workflow)



class CollectorRegressionTests(unittest.TestCase):
    def test_steam_modern_free_price_with_paid_upgrade(self):
        html = '<a class="search_result_row" href="https://store.steampowered.com/app/730/"><span class="title">Counter-Strike 2</span><div data-price-final="1499"><div class="discount_final_price free">Free</div></div></a>'
        with patch.object(steam, "fetch_Steam_json_response", return_value={"results_html": html}):
            self.assertEqual(steam.get_free_goods(0, use_free_to_play=True), 1)

    def test_missing_steam_price_is_unknown(self):
        response = Mock(status_code=200)
        response.json.return_value = {"123": {"success": True, "data": {}}}
        with patch.object(steam, "make_session") as session:
            session.return_value.get.return_value = response
            self.assertEqual(steam.verify_discount_still_active_via_api("123", "Test"), steam.UNKNOWN)

    def test_free_to_play_is_not_a_fake_discount(self):
        row = ["Test", "https://store.steampowered.com/app/123/", "", "", "", "Free"]
        deal = build_public_feed.normalize_game(row, "steam", free_to_play=True)
        self.assertEqual(deal["offer_type"], "free_to_play")
        self.assertEqual(deal["discount_percent"], 0)
        self.assertIsNone(build_public_feed.normalize_game(row, "steam"))

    def test_paid_and_expired_discounts_are_excluded(self):
        row = ["Test", "https://store.steampowered.com/app/123/", "", "", "$10", "$1", "90%", None]
        self.assertIsNone(build_public_feed.normalize_game(row, "steam"))
        row[6:] = ["100%", "2000-01-01T00:00:00Z"]
        self.assertIsNone(build_public_feed.normalize_game(row, "steam"))

    def test_epic_requires_current_promotion_and_zero_price(self):
        now = datetime.datetime(2026, 9, 8, tzinfo=datetime.timezone.utc)
        promo = {"startDate": "2026-09-01T00:00:00Z", "endDate": "2026-09-10T00:00:00Z", "discountSetting": {"discountType": "PERCENTAGE", "discountPercentage": 0}}
        game = {"price": {"totalPrice": {"discountPrice": 0, "originalPrice": 1000}}, "promotions": {"promotionalOffers": [{"promotionalOffers": [promo]}]}}
        self.assertEqual(epic.active_free_promotion(game, now), promo["endDate"])
        game["price"]["totalPrice"]["discountPrice"] = 100
        self.assertIsNone(epic.active_free_promotion(game, now))
        game["price"]["totalPrice"]["discountPrice"] = 0
        promo["startDate"] = "2026-09-09T00:00:00Z"
        self.assertIsNone(epic.active_free_promotion(game, now))


class StoreStatusTests(unittest.TestCase):
    def test_failed_refresh_preserves_last_success(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "source.json"
            target.write_text(json.dumps({"free_games": [], "discounted_games": [], "total_count": 0, "update_time": "2026-09-08T01:00:00Z"}))
            result = update_timestamp.source_status("steam", str(target), "failure", "2026-09-08T07:00:00Z")
            self.assertEqual(result, {"last_success": "2026-09-08T01:00:00Z", "last_attempt": "2026-09-08T07:00:00Z", "status": "error"})
            recovered = update_timestamp.source_status("steam", str(target), "success", "2026-09-08T08:00:00Z", result)
            self.assertEqual(recovered["status"], "ok")

    def test_corrupt_source_does_not_erase_previous_success(self):
        previous = {"last_success": "2026-09-08T01:00:00Z", "status": "ok"}
        result = update_timestamp.source_status("steam", "missing-file.json", "success", "2026-09-08T07:00:00Z", previous)
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["last_success"], previous["last_success"])

    def test_validation_without_fetch_does_not_claim_success(self):
        result = update_timestamp.source_status("steam", str(ROOT / "free_goods_detail.json"))
        self.assertEqual(result["status"], "unknown")
        self.assertIsNone(result["last_attempt"])

    def test_workflow_records_independent_outcomes(self):
        workflow = (ROOT / ".github/workflows/update.yml").read_text(encoding="utf-8")
        self.assertEqual(workflow.count("continue-on-error: true"), 2)
        self.assertIn("STEAM_OUTCOME: ${{ steps.steam.outcome }}", workflow)
        self.assertIn("EPIC_OUTCOME: ${{ steps.epic.outcome }}", workflow)


if __name__ == "__main__":
    unittest.main()
