"""Getting Started section: shared styles stay in sync, linked anchors survive."""
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGES = ["gettingstarted", "robocup-beginners-guide", "qualification",
         "your-first-competition", "for-educators", "robocupjunior-spirit"]
# Anchors that other pages, the resource finder or the homepage link to.
ANCHORS = {
    "gettingstarted": ["league-soccer", "league-rescue", "league-onstage"],
    "robocup-beginners-guide": ["competing-beyond-your-region", "tips", "resources"],
    "qualification": ["bringing-robocupjunior-to-a-new-region", "making-the-most-of-competitions"],
    "for-educators": ["resources-for-educators", "educator-resources", "pathway-to-2050"],
}


class GettingStartedStylesTest(unittest.TestCase):
    def test_section_stylesheets_are_identical(self):
        css = ROOT / "assets/css/pages"
        source = (css / "gettingstarted.css").read_text()
        for page in PAGES[1:]:
            self.assertEqual((css / f"{page}.css").read_text(), source,
                             f"{page}.css must be a copy of gettingstarted.css")

    def test_no_inline_style_blocks_in_section_shortcodes(self):
        for name in ["league-cards", "league-card", "educator-resources"]:
            text = (ROOT / f"layouts/_shortcodes/{name}.html").read_text()
            self.assertNotIn("<style", text, name)


class GettingStartedBuildTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.out = Path(cls.tmp.name)
        subprocess.run(["hugo", "--source", str(ROOT), "--destination", str(cls.out), "--quiet"],
                       check=True, capture_output=True, timeout=120)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def html(self, page):
        return (self.out / page / "index.html").read_text()

    def test_one_h1_and_page_stylesheet(self):
        for page in PAGES:
            html = self.html(page)
            self.assertEqual(len(re.findall(r"<h1[\s>]", html)), 1, page)
            self.assertRegex(html, rf'css/pages/{re.escape(page)}\.min\.[0-9a-f]+\.css', page)

    def test_linked_anchors_exist(self):
        for page, ids in ANCHORS.items():
            html = self.html(page)
            for anchor in ids:
                self.assertIn(f'id="{anchor}"', html, f"/{page}/#{anchor}")

    def test_resource_finder_deep_links_kept(self):
        html = self.html("gettingstarted") + self.html("robocup-beginners-guide")
        for anchor in ["rf-soccer", "rf-line", "rf-maze", "rf-sim", "rf-onstage", "rf-field"]:
            self.assertIn(f"/resources/#{anchor}", html)


if __name__ == "__main__":
    unittest.main()
