import datetime
import json
import tempfile
import unittest
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
        self.assertLess(feed_path.stat().st_size, 50_000)
        for deal in feed["deals"]:
            self.assertIn(deal["store"], {"steam", "epic"})
            self.assertTrue(deal["url"].startswith("https://"))
            self.assertEqual(deal["discount_percent"], 100)

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
    def test_update_workflow_commits_only_catalog_changes(self):
        workflow = (ROOT / ".github" / "workflows" / "update.yml").read_text(encoding="utf-8")
        self.assertIn("git diff --quiet -- deals.json", workflow)
        self.assertIn("No catalog changes; skipping commit", workflow)
        self.assertNotIn("git add .", workflow)

    def test_ci_runs_without_store_scrapers(self):
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertIn("pull_request:", workflow)
        self.assertIn("python -m unittest", workflow)
        self.assertNotIn("python steam.py", workflow)
        self.assertNotIn("python epic.py", workflow)


if __name__ == "__main__":
    unittest.main()
