import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from latest_posts import refresh_latest_post_blocks


class LatestPostsTest(unittest.TestCase):
    def test_imported_lists_follow_new_and_edited_posts(self):
        with tempfile.TemporaryDirectory() as temporary:
            site = Path(temporary)
            (site / "content" / "posts").mkdir(parents=True)
            (site / "layouts" / "_shortcodes").mkdir(parents=True)
            (site / "data").mkdir()
            (site / "hugo.toml").write_text(
                'baseURL = "https://example.test/"\n'
                '[security]\nallowContent = ["! ^text/org$"]\n',
                encoding="utf-8",
            )
            (site / "layouts" / "page.html").write_text("{{ .Content }}", encoding="utf-8")
            shutil.copy(
                ROOT / "layouts" / "_shortcodes" / "latest-posts.html",
                site / "layouts" / "_shortcodes" / "latest-posts.html",
            )
            (site / "data" / "wordpress-posts.json").write_text(
                json.dumps({str(i): {"author": "Editor"} for i in range(1, 4)}),
                encoding="utf-8",
            )
            for i, category in enumerate(("soccer", "rescue", "onstage"), 1):
                post = {
                    "title": f"Original {category}",
                    "date": "2025-01-01T12:00:00",
                    "url": f"/original-{category}/",
                    "wordpress_id": i,
                    "categories": [category],
                }
                extension = "md" if category == "soccer" else "html"
                body = "Original body.\n" if extension == "md" else "<p>Original body.</p>\n"
                (site / "content" / "posts" / f"original-{category}.{extension}").write_text(
                    json.dumps(post) + "\n" + body, encoding="utf-8"
                )
                page = (
                    json.dumps({"title": category.title()}) + "\n"
                    '<ul class="wp-block-latest-posts__list wp-block-latest-posts">'
                    '<li><a class="wp-block-latest-posts__post-title" '
                    f'href="/original-{category}/">Original {category}</a>'
                    '<div class="wp-block-latest-posts__post-excerpt">Captured excerpt</div>'
                    "</li></ul>\n"
                )
                (site / "content" / f"{category}.{extension}").write_text(page, encoding="utf-8")

            refresh_latest_post_blocks(site)
            for category in ("soccer", "rescue", "onstage"):
                member = "rescue-line" if category == "rescue" else category
                new_post = (
                    "---\n"
                    f'title: "New {category}"\n'
                    "date: 2026-01-01T12:00:00\n"
                    f'categories: ["{member}"]\n'
                    "---\nNew article text.\n"
                )
                (site / "content" / "posts" / f"new-{category}.md").write_text(
                    new_post, encoding="utf-8"
                )
            edited = site / "content" / "posts" / "original-soccer.md"
            edited.write_text(edited.read_text(encoding="utf-8").replace(
                "Original body.", "Updated original body."
            ), encoding="utf-8")

            subprocess.run(
                ["hugo", "--source", str(site), "--minify"],
                check=True, capture_output=True, text=True,
            )
            for category in ("soccer", "rescue", "onstage"):
                page = (site / "public" / category / "index.html").read_text(encoding="utf-8")
                self.assertLess(page.index(f"New {category}"), page.index(f"Original {category}"))
                if category == "soccer":
                    self.assertIn("Updated original body.", page)
                    self.assertNotIn("Captured excerpt", page)
                else:
                    self.assertIn("Captured excerpt", page)


if __name__ == "__main__":
    unittest.main()
