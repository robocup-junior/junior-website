import re
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DarkModeTest(unittest.TestCase):
    """Dark mode: theme applied before paint, toggle buttons, stylesheet order."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        out = Path(cls.tmp.name)
        subprocess.run(["hugo", "--source", str(ROOT), "--destination", str(out), "--quiet"],
                       check=True, capture_output=True, timeout=120)
        cls.home = (out / "index.html").read_text()
        cls.page = (out / "about" / "index.html").read_text()

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_theme_is_set_before_any_stylesheet(self):
        for html in (self.home, self.page):
            script = html.index('localStorage.getItem("rcj-theme")')
            self.assertLess(script, html.index('rel="stylesheet"'))
            self.assertIn('<meta name="color-scheme" content="light dark">', html)

    def test_dark_stylesheet_loads_last(self):
        links = re.findall(r'<link rel="stylesheet" href="([^"]+)"', self.home)
        self.assertRegex(links[-1], r"css/dark\.min\.[0-9a-f]+\.css")

    def test_toggle_buttons_are_accessible(self):
        for html in (self.home, self.page):
            buttons = re.findall(r'<button type="button" class="rcj-theme-toggle[^"]*"[^>]*>', html)
            self.assertEqual(len(buttons), 2)  # desktop menu item + mobile header
            for button in buttons:
                self.assertIn('aria-pressed="false"', button)
                self.assertIn('aria-label="Switch to dark mode"', button)
            self.assertIn("/js/theme.js", html)

    def test_dark_css_comments_are_valid(self):
        css = (ROOT / "assets/css/dark.css").read_text()
        self.assertNotRegex(css, r"(?m)^\s*//")
        self.assertEqual(css.count("/*"), css.count("*/"))


if __name__ == "__main__":
    unittest.main()
