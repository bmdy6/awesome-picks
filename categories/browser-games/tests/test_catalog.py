import json
from pathlib import Path
import subprocess
import sys
import unittest
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DATA = json.loads((ROOT / "data" / "games.json").read_text(encoding="utf-8"))


class CatalogTests(unittest.TestCase):
    def test_categories_and_game_ids(self):
        categories = DATA["categories"]
        keys = [c["id"] for c in categories]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(keys[0], "all")
        ids = [g["id"] for g in DATA["games"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(ids), 20)
        self.assertTrue({g["category"] for g in DATA["games"]}.issubset(set(keys) - {"all"}))

    def test_play_links_and_licenses(self):
        plays = [g["play_url"].rstrip("/") for g in DATA["games"]]
        self.assertEqual(len(plays), len(set(plays)))
        for game in DATA["games"]:
            self.assertEqual(urlparse(game["play_url"]).scheme, "https", game["id"])
            if game["source_url"]:
                self.assertEqual(urlparse(game["source_url"]).scheme, "https", game["id"])
            if game["cover_url"]:
                self.assertEqual(urlparse(game["cover_url"]).scheme, "https", game["id"])
            self.assertIn(game["source_status"], {"open", "closed", "unknown", "unavailable"})
            self.assertIn(game["zh_status"], {"yes", "partial", "unknown"})
            self.assertTrue(game["summary"])
            self.assertFalse(game["playtested"], "Not yet manually browser playtested")

    def test_requested_games_are_present(self):
        ids = {game["id"] for game in DATA["games"]}
        for id in ("inkwave", "claude-of-tanks", "openfront", "voxel-musou", "chrono-divide"):
            self.assertIn(id, ids)

    def test_web_has_accessible_filter_structure(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        js = (ROOT / "assets" / "app.js").read_text(encoding="utf-8")
        for id in ("game-grid", "featured-grid", "category-filters", "only-source", "only-zh", "search"):
            self.assertIn('id="' + id + '"', html)
        self.assertIn('fetch("data/games.json"', js)
        self.assertIn('aria-pressed', js)
        self.assertNotIn("innerHTML", js)

    def test_readme_matches_data(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "generate_readme.py"), "--check"],
            cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
