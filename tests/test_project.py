import datetime
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from bs4 import BeautifulSoup

import build_public_feed
import epic
import steam
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
            if deal["store"] == "epic" or deal["end_at"] is not None:
                self.assertIsNotNone(deal["end_at"])
                self.assertIsNotNone(datetime.datetime.fromisoformat(deal["end_at"]).tzinfo)

    def test_catalog_comparison_ignores_volatile_metadata(self):
        deals = [{"id": "steam-1", "title": "Example"}]
        existing = {
            "schema_version": 1,
            "generated_at": "2026-01-01T00:00:00Z",
            "total_count": 1,
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
        for url in (
            "https://[broken",
            "https://user@store.steampowered.com/app/123/",
            "https://store.steampowered.com:8080/app/123/",
            "https://store.steampowered.com\\@example.com/app/123/",
        ):
            with self.subTest(url=url):
                self.assertIsNone(build_public_feed.canonical_store_url(url, "steam"))

    def test_discount_label_must_be_exactly_100_percent(self):
        row = ["Game", "https://store.steampowered.com/app/123/Game/", "", "", "$10", "$0", "1100%", None]
        self.assertIsNone(build_public_feed.normalize_game(row, "steam"))
        row[6] = "خصم 100% - مجاني"
        self.assertIsNotNone(build_public_feed.normalize_game(row, "steam"))

    def test_unchanged_catalog_publishes_new_success_time_and_store_status(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "deals.json"
            original = {
                "schema_version": 1,
                "generated_at": "old",
                "total_count": 0,
                "deals": [],
                "sources": {"steam": {"status": "ok", "last_success": "previous"}},
            }
            build_public_feed.atomic_write(target, original)
            before = target.read_bytes()
            steam_source = {"status": "ok", "last_success": "previous"}
            with patch.object(build_public_feed, "ROOT", target.parent), patch.object(
                build_public_feed, "load_deals", return_value=([], {"steam": steam_source})
            ):
                self.assertEqual(build_public_feed.main(), 0)
                self.assertEqual(target.read_bytes(), before)
                steam_source["last_success"] = "new"
                self.assertEqual(build_public_feed.main(), 0)
                updated = build_public_feed.load_existing_feed(target)
                self.assertEqual(updated["generated_at"], original["generated_at"])
                self.assertEqual(updated["deals"], original["deals"])
                self.assertEqual(updated["sources"]["steam"]["last_success"], "new")
                steam_source["status"] = "failed"
                self.assertEqual(build_public_feed.main(), 0)
                changed = build_public_feed.load_existing_feed(target)
                self.assertEqual(changed["generated_at"], original["generated_at"])
                self.assertEqual(changed["sources"]["steam"]["status"], "failed")
                self.assertEqual(changed["sources"]["steam"]["last_success"], "new")
                steam_source["status"] = "ok"
                self.assertEqual(build_public_feed.main(), 0)
                self.assertEqual(build_public_feed.load_existing_feed(target)["sources"]["steam"]["status"], "ok")

    def test_store_outcome_overrides_saved_source_status(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "data.json"
            update_timestamp.atomic_write_json(path, {
                "total_count": 0, "status": "partial", "update_time": "2026-01-01T00:00:00Z",
            })
            with patch.dict("os.environ", {"STEAM_OUTCOME": "success"}):
                self.assertEqual(update_timestamp.validate_source("steam", str(path))["status"], "partial")
            with patch.dict("os.environ", {"STEAM_OUTCOME": "failure"}):
                self.assertEqual(update_timestamp.validate_source("steam", str(path))["status"], "failed")


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
        skip_target = self.soup.select_one(".skip-link")["href"]
        self.assertEqual(self.soup.select_one(skip_target)["tabindex"], "-1")

    def test_tabs_are_normal_keyboard_accessible_buttons(self):
        tabs = self.soup.select("button.tab")
        self.assertEqual(len(tabs), 3)
        self.assertTrue(all(tab.get("aria-pressed") in {"true", "false"} for tab in tabs))
        self.assertTrue(all(tab.get("tabindex") is None for tab in tabs))

    def test_analytics_and_consent_banner_are_removed(self):
        self.assertIsNone(self.soup.select_one("#cookieConsent"))
        self.assertIsNotNone(self.soup.find("meta", attrs={"http-equiv": "Content-Security-Policy"}))
        self.assertNotIn("googletagmanager", self.html)
        self.assertNotIn("google-analytics", self.html)
        self.assertNotIn("ANALYTICS_ID", self.script)

    def test_frontend_does_not_use_html_injection_or_broken_service_worker(self):
        forbidden = ["innerHTML", "outerHTML", "insertAdjacentHTML", "serviceWorker.register", "onerror="]
        for token in forbidden:
            self.assertNotIn(token, self.script)

    def test_frontend_does_not_expire_steam_deals_by_feed_age(self):
        self.assertNotIn("STEAM_MISSING_END_MAX_AGE_MS", self.script)

    def test_frontend_accepts_only_100_percent_deals(self):
        self.assertIn("rawDeal.discount_percent !== 100", self.script)

    def test_frontend_loads_on_project_subpaths(self):
        self.assertIn("Boolean(document.getElementById('gamesGrid'))", self.script)

    def test_each_card_gets_a_live_countdown(self):
        self.assertIn("time.end-date-value[datetime]", self.script)
        self.assertIn("updateDealCountdowns()", self.script)
        self.assertIn("minutesLeft", self.script)


class WorkflowStructureTests(unittest.TestCase):
    def test_update_workflow_commits_public_feed_changes(self):
        workflow = (ROOT / ".github" / "workflows" / "update.yml").read_text(encoding="utf-8")
        self.assertIn("git diff --quiet -- deals.json", workflow)
        self.assertIn("No public feed changes; skipping commit", workflow)
        self.assertIn("workflows/update.yml/runs?status=completed", workflow)
        self.assertNotIn("git add .", workflow)

    def test_store_collectors_run_independently(self):
        workflow = (ROOT / ".github" / "workflows" / "update.yml").read_text(encoding="utf-8")
        self.assertIn("id: steam", workflow)
        self.assertIn("id: epic", workflow)
        self.assertEqual(workflow.count("continue-on-error: true"), 2)
        self.assertIn("steps.steam.outcome == 'failure' && steps.epic.outcome == 'failure'", workflow)

    def test_ci_runs_without_store_scrapers(self):
        workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
        self.assertIn("pull_request:", workflow)
        self.assertIn("python -m unittest", workflow)
        self.assertNotIn("python steam.py", workflow)
        self.assertNotIn("python epic.py", workflow)


class CollectorTests(unittest.TestCase):
    def test_steam_row_requires_exact_100_percent_discount(self):
        html = '''
        <a class="search_result_row" href="https://store.steampowered.com/app/123/Game/?snr=test">
          <span class="title">Game</span>
          <div class="search_discount_block" data-discount="100">
            <div class="discount_original_price">$10</div>
            <div class="discount_final_price">Free</div>
          </div>
        </a>'''
        row = BeautifulSoup(html, "html.parser").select_one("a")
        parsed = steam.parse_search_row(row)
        self.assertEqual(parsed["appid"], "123")
        self.assertEqual(parsed["url"], "https://store.steampowered.com/app/123/Game/")
        row.select_one(".search_discount_block")["data-discount"] = "90"
        self.assertIsNone(steam.parse_search_row(row))

    def test_steam_distinguishes_temporary_giveaway_from_permanent_free(self):
        giveaway_html = '''
        <div class="game_area_purchase_game">
          <form action="https://store.steampowered.com/freelicense/addfreelicense/"></form>
          <p class="game_purchase_discount_quantity">
            Free to keep when you get it before Sep 21 @ 11:59pm.
          </p>
          <div class="discount_pct">-100%</div>
          <div class="discount_original_price">$19.99</div>
          <div class="discount_final_price">$0.00</div>
        </div>'''
        self.assertTrue(steam.storefront_has_temporary_giveaway(giveaway_html))
        self.assertEqual(
            steam.parse_storefront_giveaway_end(
                giveaway_html,
                datetime.datetime(2026, 9, 14, tzinfo=datetime.timezone.utc),
            ),
            "2026-09-21T23:59:00Z",
        )
        day_first_html = giveaway_html.replace(
            "Sep 21 @ 11:59pm", "22 Sep @ 9:59am"
        )
        self.assertEqual(
            steam.parse_storefront_giveaway_end(
                day_first_html,
                datetime.datetime(2026, 9, 14, tzinfo=datetime.timezone.utc),
            ),
            "2026-09-22T09:59:00Z",
        )
        self.assertFalse(steam.storefront_has_temporary_giveaway(
            '<div class="game_area_purchase_game"><div>Free To Play</div></div>'
        ))

        details = {"type": "game", "is_free": True}
        now = datetime.datetime(2026, 9, 14, tzinfo=datetime.timezone.utc)
        with patch.object(steam, "fetch_app_details", return_value=details), patch.object(
            steam, "fetch_storefront", return_value=giveaway_html
        ):
            self.assertEqual(steam.inspect_discount("123", now), (steam.ACTIVE, "2026-09-21T23:59:00Z"))
            self.assertEqual(steam.inspect_discount("123", now.replace(day=22)), (steam.EXPIRED, None))
        with patch.object(steam, "fetch_app_details", return_value=details), patch.object(
            steam, "fetch_storefront", return_value='<div class="game_area_purchase_game">Free To Play</div>'
        ):
            self.assertEqual(steam.inspect_discount("123"), (steam.EXPIRED, None))
        with patch.object(steam, "fetch_app_details", return_value=details), patch.object(
            steam, "fetch_storefront", return_value="<html>Age verification</html>"
        ):
            self.assertEqual(steam.inspect_discount("123"), (steam.UNKNOWN, None))

        active = {"type": "game", "is_free": False, "price_overview": {"discount_percent": 100, "final": 0}}
        with patch.object(steam, "fetch_app_details", return_value=active), patch.object(
            steam, "fetch_storefront", return_value=None
        ):
            self.assertEqual(steam.inspect_discount("123"), (steam.ACTIVE, None))

    def test_steam_empty_search_accepts_the_store_sentinel(self):
        with patch.object(steam, "make_session") as make_session:
            response = Mock()
            make_session.return_value.__enter__.return_value.get.return_value = response
            response.json.return_value = {"success": 1, "start": -1, "total_count": 0, "results_html": ""}
            self.assertEqual(steam.fetch_search_page(0), ([], 0))
            response.json.return_value["total_count"] = 1
            with self.assertRaises(RuntimeError):
                steam.fetch_search_page(0)

    def test_steam_preserves_rediscovered_deal_when_verification_fails(self):
        candidate = {"appid": "123", "title": "Game", "url": "https://store.steampowered.com/app/123/Game/"}
        existing = steam.candidate_to_row(candidate, "2026-12-01T12:00:00Z")
        with patch.object(steam, "fetch_search_page", return_value=([Mock()], 1)), patch.object(
            steam, "parse_search_row", return_value=candidate
        ), patch.object(steam, "inspect_discount", return_value=(steam.UNKNOWN, None)):
            self.assertEqual(steam.collect([existing]), ([existing], False))
        with patch.object(steam, "fetch_search_page", return_value=([], 0)), patch.object(
            steam, "inspect_discount", return_value=(steam.ACTIVE, "2026-12-02T12:00:00Z")
        ):
            games, complete = steam.collect([existing])
            self.assertTrue(complete)
            self.assertEqual(games[0][7], "2026-12-02T12:00:00Z")

    def test_epic_uses_current_promotion_only(self):
        now = datetime.datetime(2026, 9, 13, 12, tzinfo=datetime.timezone.utc)
        promotion = {
            "startDate": "2026-09-12T00:00:00Z",
            "endDate": "2026-09-14T00:00:00Z",
            "discountSetting": {"discountType": "PERCENTAGE", "discountPercentage": 0},
        }
        game = {
            "price": {"totalPrice": {"originalPrice": 1000, "discountPrice": 0}},
            "promotions": {"promotionalOffers": [{"promotionalOffers": [promotion]}]},
        }
        self.assertEqual(epic.active_free_end(game, now), "2026-09-14T00:00:00Z")
        promotion["startDate"] = "2026-09-14T00:00:00Z"
        self.assertIsNone(epic.active_free_end(game, now))
        promotion["startDate"] = "2026-09-12T00:00:00Z"
        game["price"]["totalPrice"]["originalPrice"] = 0
        self.assertIsNone(epic.active_free_end(game, now))

    def test_epic_only_publishes_games_and_uses_valid_product_mapping(self):
        now = datetime.datetime(2026, 9, 13, 12, tzinfo=datetime.timezone.utc)
        game = {
            "offerType": "ADD_ON", "title": "Game", "productSlug": "example/home",
            "catalogNs": {"mappings": [{"pageSlug": "../free-games", "pageType": "productHome"}]},
            "price": {"totalPrice": {"originalPrice": 1000, "discountPrice": 0}},
            "promotions": {"promotionalOffers": [{"promotionalOffers": [{
                "startDate": "2026-09-12T00:00:00Z",
                "endDate": "2026-09-14T00:00:00Z",
                "discountSetting": {"discountType": "PERCENTAGE", "discountPercentage": 0},
            }]}]},
        }
        self.assertIsNone(epic.normalize_game(game, now))
        game["offerType"] = "BASE_GAME"
        self.assertEqual(epic.normalize_game(game, now)[1], "https://store.epicgames.com/en-US/p/example")

    def test_epic_supports_bundles_null_decimals_and_partial_skip(self):
        now = datetime.datetime(2026, 9, 13, 12, tzinfo=datetime.timezone.utc)
        promo = [{
            "promotionalOffers": [{
                "startDate": "2026-09-12T00:00:00Z",
                "endDate": "2026-09-14T00:00:00Z",
                "discountSetting": {"discountType": "PERCENTAGE", "discountPercentage": 0},
            }]
        }]
        bundle = {
            "offerType": "BUNDLE",
            "title": "Bundle Game",
            "categories": [{"path": "bundles/games"}],
            "productSlug": "bundle-game",
            "price": {"totalPrice": {"originalPrice": 1500, "discountPrice": 0, "currencyInfo": {"decimals": None}}},
            "promotions": {"promotionalOffers": promo},
        }
        normalized = epic.normalize_game(bundle, now)
        self.assertEqual(normalized[1], "https://store.epicgames.com/en-US/bundles/bundle-game")
        self.assertEqual(normalized[4], "15.00 USD")

        broken = {
            "offerType": "BASE_GAME",
            "title": "",
            "price": {"totalPrice": {"originalPrice": 1000, "discountPrice": 0}},
            "promotions": {"promotionalOffers": promo},
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "epic_goods_detail.json"
            with patch.object(epic, "OUTPUT_PATH", output_path), patch.object(
                epic, "utc_now", return_value=now
            ), patch.object(epic, "fetch_catalog", return_value=[bundle, broken]):
                self.assertEqual(epic.main(), 0)
            saved = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(saved["status"], "partial")
            self.assertEqual(saved["total_count"], 1)

            with patch.object(epic, "OUTPUT_PATH", output_path), patch.object(
                epic, "utc_now", return_value=now
            ), patch.object(epic, "fetch_catalog", return_value=[broken]):
                self.assertEqual(epic.main(), 1)

    def test_steam_hardening_cookies_naive_now_prices_and_expiration(self):
        self.assertTrue(steam.is_zero_price("Free"))
        self.assertTrue(steam.is_zero_price("$0.00"))
        self.assertTrue(steam.is_zero_price("0,00€"))
        self.assertFalse(steam.is_zero_price("$0.49"))

        future_ts = int((datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=2)).timestamp())
        past_ts = int((datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)).timestamp())
        self.assertIsNotNone(steam.parse_discount_expiration(f'"discount_expiration": {future_ts}'))
        self.assertIsNone(steam.parse_discount_expiration(f'"discount_expiration": {past_ts}'))
        self.assertIsNone(steam.parse_discount_expiration(
            f'"discount_expiration": {future_ts}, "discount_expiration": {future_ts + 60}'
        ))

        with patch.object(steam, "make_session") as make_session:
            response = Mock(url="https://store.steampowered.com/app/123/Game/", text="<html></html>")
            session = make_session.return_value.__enter__.return_value
            session.get.return_value = response
            self.assertEqual(steam.fetch_storefront("123"), "<html></html>")
            cookie = session.get.call_args.kwargs["headers"]["Cookie"]
            self.assertIn("wants_mature_content=1", cookie)

        with patch.object(steam, "make_session") as make_session:
            session = Mock()
            search_resp = Mock()
            search_resp.json.return_value = {"success": 1, "start": -1, "total_count": 0, "results_html": ""}
            app_resp = Mock()
            app_resp.json.return_value = {"123": {"success": True, "data": {"type": "game"}}}
            store_resp = Mock(
                url="https://store.steampowered.com/app/123/Game/",
                text='<div class="game_area_purchase_game">Free To Play</div>',
            )
            session.get.side_effect = [search_resp, app_resp, store_resp]
            make_session.return_value = session
            candidate = {"appid": "123", "title": "Game", "url": "https://store.steampowered.com/app/123/Game/"}
            existing = steam.candidate_to_row(candidate, "2026-12-01T12:00:00Z")
            self.assertEqual(steam.collect([existing]), ([], True))
            self.assertLessEqual(make_session.call_count, 2)
            self.assertGreaterEqual(session.close.call_count, 1)

        giveaway_html = '''
        <div class="game_area_purchase_game">
          <form action="https://store.steampowered.com/freelicense/addfreelicense/"></form>
          <p class="game_purchase_discount_quantity">Free to keep when you get it before Sep 21 @ 11:59pm.</p>
          <div class="discount_pct">-100%</div>
          <div class="discount_original_price">$9.99</div>
          <div class="discount_final_price">$0.00</div>
        </div>'''
        with patch.object(steam, "fetch_app_details", return_value={"type": "game"}), patch.object(
            steam, "fetch_storefront", return_value=giveaway_html
        ):
            self.assertEqual(
                steam.inspect_discount("123", datetime.datetime(2026, 9, 14, 12, 0)),
                (steam.ACTIVE, "2026-09-21T23:59:00Z"),
            )

    def test_build_public_feed_filters_invalid_urls_and_expired_deals(self):
        self.assertIsNone(build_public_feed.valid_https_url("https://store.steampowered.com:/app/123/"))
        future = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)).isoformat()
        past = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)).isoformat()
        self.assertIsNone(build_public_feed.normalize_game(
            ["Game", "https://store.steampowered.com/app/123/", "", "", "$10", "Free", "100%", past],
            "steam",
        ))
        self.assertIsNone(build_public_feed.normalize_game(
            ["Game", "https://store.steampowered.com/app/123/", "", "", "$10", "Free", "100% coming soon", future],
            "steam",
        ))
        self.assertIsNone(build_public_feed.normalize_game(
            ["Game", "https://store.steampowered.com/app/123/", "", "", "$10", "Free", "100% مجاني دائماً", future],
            "steam",
        ))

    def test_frontend_script_runtime_helpers(self):
        if shutil.which("node") is None:
            self.skipTest("node is not installed")
        js_check = r"""
        const fs = require('fs');
        const vm = require('vm');
        const code = fs.readFileSync('script.js', 'utf8');
        const storage = new Map();
        const noop = () => {};
        const sandbox = {
          window: {
            location: { href: 'https://gamesfree100.online/', search: '' },
            history: { replaceState: noop },
            setTimeout, clearTimeout, setInterval,
          },
          document: {
            addEventListener: noop,
            documentElement: { setAttribute: noop },
            getElementById: () => null,
            querySelectorAll: () => [],
            querySelector: () => null,
          },
          localStorage: {
            getItem: k => storage.get(k) ?? null,
            setItem: (k, v) => storage.set(k, String(v)),
          },
          URL, URLSearchParams, Intl, Date, console,
        };
        const ctx = vm.createContext(sandbox);
        vm.runInContext(code, ctx);
        const assert = (cond, msg) => { if (!cond) throw new Error(msg); };
        assert(
          ctx.safeHttpsUrl('https://cdn.example.com/a.jpg') === 'https://cdn.example.com/a.jpg',
          'valid https failed'
        );
        assert(ctx.safeHttpsUrl('https://user@cdn.example.com/a.jpg') === null, 'userinfo should fail');
        assert(ctx.safeStoreUrl('https://store.steampowered.com/app/1/', 'epic') === null, 'cross-store failed');
        assert(ctx.normalizePublicDeal({
          store: 'epic', title: 'Test', url: 'https://store.epicgames.com/en-US/p/test',
          discount_percent: 100, end_at: '2099-01-01T00:00:00Z'
        }) !== null, 'valid epic deal rejected');
        assert(ctx.normalizePublicDeal({
          store: 'epic', title: 'NoEnd', url: 'https://store.epicgames.com/en-US/p/test',
          discount_percent: 100, end_at: null
        }) === null, 'epic deal without end_at should be rejected');
        vm.runInContext("lang = 'en'", ctx);
        assert(ctx.formatTimeLeft(2 * 60 * 60 * 1000 + 60 * 1000) === '2 hours, 1 minute', 'en plural failed');
        vm.runInContext("lang = 'ar'", ctx);
        assert(ctx.formatTimeLeft(2 * 86400000 + 5 * 3600000) === 'يومان و5 ساعات', 'ar dual/plural failed');
        """
        result = subprocess.run(["node", "-e", js_check], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, msg=result.stderr or result.stdout)


if __name__ == "__main__":
    unittest.main()
