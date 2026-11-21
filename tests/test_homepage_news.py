import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class HomepageNewsTest(unittest.TestCase):
    def test_snapshots_expire_after_post_edits_and_new_posts_are_rendered(self):
        with tempfile.TemporaryDirectory() as temporary:
            site = Path(temporary)
            (site / "content" / "posts").mkdir(parents=True)
            (site / "layouts" / "_partials").mkdir(parents=True)
            (site / "data").mkdir()
            (site / "hugo.toml").write_text(
                'baseURL = "https://example.test/"\n'
                '[security]\nallowContent = ["! ^text/org$"]\n',
                encoding="utf-8",
            )
            (site / "layouts" / "home.html").write_text(
                '{{ partial "home-reference.html" . }}', encoding="utf-8"
            )
            shutil.copy(
                ROOT / "layouts" / "_partials" / "home-reference.html",
                site / "layouts" / "_partials" / "home-reference.html",
            )
            original = {
                "title": "Original news",
                "date": "2025-01-01T12:00:00",
                "url": "/original-news/",
                "categories": ["news"],
                "featured_image": "/original.jpg",
                "wordpress_excerpt": "<p>Current excerpt marker.</p>",
            }
            body = "<p>Original article content.</p>\n"
            post = site / "content" / "posts" / "original.html"
            def write_post(front, content):
                post.write_text(json.dumps(front) + "\n" + content, encoding="utf-8")
            write_post(original, body)
            key = "/original-news/"
            snapshots = {
                "homepage-news-fingerprints": {key: {
                    "content_hash": hashlib.md5(body.encode()).hexdigest(),
                    "title": original["title"],
                    "image": original["featured_image"],
                    "excerpt": original["wordpress_excerpt"],
                }},
                "homepage-news-excerpts": {key: "Captured excerpt marker."},
                "homepage-news-images": {key: "/captured-crop.jpg"},
            }
            for name, data in snapshots.items():
                (site / "data" / f"{name}.json").write_text(json.dumps(data), encoding="utf-8")

            def build():
                subprocess.run(
                    ["hugo", "--source", str(site)],
                    check=True, capture_output=True, text=True,
                )
                return (site / "public" / "index.html").read_text(encoding="utf-8")

            unchanged = build()
            self.assertIn("Captured excerpt marker.", unchanged)
            self.assertIn("/captured-crop.jpg", unchanged)
            for field in ("title", "featured_image", "wordpress_excerpt", "body"):
                with self.subTest(edited=field):
                    front = dict(original)
                    content = body
                    if field == "body":
                        content = "<p>Changed article content.</p>\n"
                    else:
                        front[field] = {
                            "title": "Edited news",
                            "featured_image": "/new-image.jpg",
                            "wordpress_excerpt": "<p>Updated excerpt marker.</p>",
                        }[field]
                    write_post(front, content)
                    rendered = build()
                    self.assertNotIn("Captured excerpt marker.", rendered)
                    self.assertNotIn("/captured-crop.jpg", rendered)
                    expected_excerpt = {
                        "wordpress_excerpt": "Updated excerpt marker.",
                        "body": "Changed article content.",
                    }.get(field, "Current excerpt marker.")
                    self.assertIn(expected_excerpt, rendered)
                    self.assertIn("/new-image.jpg" if field == "featured_image" else "/original.jpg", rendered)

            changed_excerpt = dict(original, wordpress_excerpt="<p>Explicit new excerpt.</p>")
            write_post(changed_excerpt, "<p>Changed article content.</p>\n")
            self.assertIn("Explicit new excerpt.", build())

            write_post(original, body)
            (site / "content" / "posts" / "new.md").write_text(
                '---\ntitle: "New news"\ndate: 2026-01-01T12:00:00\n'
                'categories: ["news"]\nfeatured_image: "/new-post.jpg"\n'
                '---\nFresh new content.\n', encoding="utf-8",
            )
            rendered = build()
            self.assertIn("New news", rendered)
            self.assertIn("Fresh new content.", rendered)
            self.assertIn("/new-post.jpg", rendered)
            self.assertLess(rendered.index("New news"), rendered.index("Original news"))


if __name__ == "__main__":
    unittest.main()
