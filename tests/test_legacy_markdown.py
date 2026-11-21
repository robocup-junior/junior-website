import json
import shutil
import subprocess
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Elements(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.starts = []

    def handle_starttag(self, tag, attrs):
        self.starts.append((tag, dict(attrs)))


class LegacyMarkdownTest(unittest.TestCase):
    def test_replaced_portrait_keeps_a_fixed_crop(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            for path in ("content", "data", "layouts/_shortcodes", "layouts/_default"):
                (site / path).mkdir(parents=True, exist_ok=True)
            shutil.copy(ROOT / "layouts/_shortcodes/wp-person.html", site / "layouts/_shortcodes/")
            (site / "hugo.toml").write_text("baseURL='https://example.org/'\n")
            (site / "layouts/_default/single.html").write_text("{{ .Content }}")
            (site / "data/wp_images.json").write_text(json.dumps({
                "/original.jpg": {"style": "object-fit:cover;width:200px;height:200px"}
            }))
            (site / "content/people.md").write_text(
                '---\ntitle: People\n---\n'
                '{{< wp-person image="/original.jpg" name="Original" >}}\n'
                '{{< wp-person image="/replacement.jpg" name="Replacement" >}}\n'
            )
            subprocess.run(["hugo", "--source", str(site), "--quiet"], check=True, capture_output=True)
            result = Elements()
            result.feed((site / "public/people/index.html").read_text())
            images = {attrs["src"]: attrs for tag, attrs in result.starts if tag == "img"}
            self.assertEqual(images["/original.jpg"]["style"], "object-fit:cover;width:200px;height:200px")
            self.assertEqual(images["/replacement.jpg"]["style"], "object-fit:cover;width:250px;height:250px")

    def test_schedule_empty_cells_and_scoped_link_attributes(self):
        with tempfile.TemporaryDirectory() as directory:
            site = Path(directory)
            for path in ("content", "layouts/_shortcodes", "layouts/_default", "layouts/legacy-links/_markup"):
                (site / path).mkdir(parents=True, exist_ok=True)
            shutil.copy(ROOT / "layouts/_shortcodes/werob-schedule.html", site / "layouts/_shortcodes/")
            shutil.copy(ROOT / "layouts/legacy-links/_markup/render-link.html", site / "layouts/legacy-links/_markup/")
            (site / "hugo.toml").write_text("baseURL='https://example.org/'\n")
            (site / "layouts/_default/single.html").write_text("{{ .Content }}")
            (site / "content/scoped.md").write_text(
                '+++\ntitle="Scoped"\ntype="legacy-links"\n+++\n'
                '{{< werob-schedule striped="true" >}}\n'
                '{empty} | **Type** | {empty} | [slides](https://example.org/ "newtab-break")\n'
                '10:00 | {colspan=3}Lunch\n'
                '{{< /werob-schedule >}}\n\n'
                '[8 in the library](#rf-werob "resource-year-2026")\n\n'
                '[ordinary](https://example.org/)\n'
            )
            (site / "content/control.md").write_text(
                '+++\ntitle="Control"\n+++\n[Link](https://example.org/ "newtab")\n'
            )
            subprocess.run(["hugo", "--source", str(site), "--quiet"], check=True, capture_output=True)
            scoped = Elements()
            scoped.feed((site / "public/scoped/index.html").read_text())
            cells = [attrs for tag, attrs in scoped.starts if tag == "td"]
            self.assertEqual(cells, [{}, {}, {}, {}, {}, {"colspan": "3"}])
            links = [attrs for tag, attrs in scoped.starts if tag == "a"]
            self.assertEqual(links[0], {"href": "https://example.org/", "target": "_blank", "rel": "noreferrer noopener"})
            self.assertEqual(links[1], {"href": "#rf-werob", "class": "rcjrf-year", "data-year": "2026"})
            self.assertEqual(links[2], {"href": "https://example.org/"})
            self.assertEqual(sum(tag == "br" for tag, _ in scoped.starts), 1)
            control = Elements()
            control.feed((site / "public/control/index.html").read_text())
            self.assertEqual([attrs for tag, attrs in control.starts if tag == "a"],
                             [{"href": "https://example.org/", "title": "newtab"}])


if __name__ == "__main__":
    unittest.main()
