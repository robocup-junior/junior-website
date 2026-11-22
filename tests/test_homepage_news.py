import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class HomepageTest(unittest.TestCase):
    """The homepage (layouts/_partials/home.html) renders from content/_index.md
    and lists the newest news posts, newest first, with small thumbnails."""

    def build_site(self, posts, home_overrides=None):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        site = Path(temporary.name)
        (site / "content" / "posts").mkdir(parents=True)
        (site / "layouts" / "_partials").mkdir(parents=True)
        (site / "data").mkdir()
        (site / "hugo.toml").write_text('baseURL = "https://example.test/"\n', encoding="utf-8")
        (site / "layouts" / "home.html").write_text('{{ partial "home.html" . }}', encoding="utf-8")
        shutil.copy(ROOT / "layouts" / "_partials" / "home.html", site / "layouts" / "_partials" / "home.html")
        (site / "data" / "wordpress-posts.json").write_text("{}", encoding="utf-8")
        front, _ = json.JSONDecoder().raw_decode((ROOT / "content" / "_index.md").read_text(encoding="utf-8"))
        if home_overrides:
            front["home"].update(home_overrides)
        (site / "content" / "_index.md").write_text(json.dumps(front), encoding="utf-8")
        for index, (title, date, categories) in enumerate(posts):
            (site / "content" / "posts" / f"post{index}.md").write_text(
                f'---\ntitle: "{title}"\ndate: {date}\ncategories: {json.dumps(categories)}\n'
                f'featured_image: "/img{index}.jpg"\n---\nBody {index}.\n', encoding="utf-8")
        subprocess.run(["hugo", "--source", str(site), "--quiet"], check=True, capture_output=True, text=True, timeout=60)
        return (site / "public" / "index.html").read_text(encoding="utf-8")

    def test_news_lists_six_newest_news_posts(self):
        posts = [(f"News {i}", f"2026-01-{i + 1:02d}T12:00:00", ["news"]) for i in range(8)]
        posts.append(("Soccer only", "2026-02-01T12:00:00", ["soccer"]))
        html = self.build_site(posts)
        news = html[html.index('id="rcjh-news"'):]
        titles = re.findall(r'<h3><a href="[^"]+">([^<]+)</a></h3>', news)
        self.assertEqual(titles, [f"News {i}" for i in range(7, 1, -1)])
        self.assertNotIn("Soccer only", news)
        self.assertIn('src="/img7.jpg" alt="" loading="lazy"', news)

    def test_single_h1_and_labelled_sections(self):
        html = self.build_site([("News", "2026-01-01T12:00:00", ["news"])])
        self.assertEqual(html.count("<h1"), 1)
        for section in re.findall(r'<section [^>]*aria-labelledby="([^"]+)"', html):
            self.assertIn(f'id="{section}"', html)

    def test_extra_or_missing_buttons_do_not_break_the_build(self):
        html = self.build_site([], home_overrides={"closing": {
            "heading": "Join us", "text": "Text",
            "buttons": [{"url": "/a/", "label": "A"}, {"url": "/b/", "label": "B"}, {"url": "/c/", "label": "C"}],
        }})
        self.assertIn(">C</a>", html)
        self.assertNotIn('id="rcjh-news"', html)  # no posts, no empty news section


if __name__ == "__main__":
    unittest.main()
