import datetime
import json
import tempfile
import unittest
from pathlib import Path

from bs4 import BeautifulSoup

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


if __name__ == "__main__":
    unittest.main()
