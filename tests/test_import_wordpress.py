import contextlib
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "import-wordpress.py"
spec = importlib.util.spec_from_file_location("import_wordpress", SCRIPT)
importer = importlib.util.module_from_spec(spec)
sys.path.insert(0, str(SCRIPT.parent))
try:
    spec.loader.exec_module(importer)
finally:
    sys.path.pop(0)


class Response(io.BytesIO):
    def __init__(self, body, pages):
        super().__init__(json.dumps(body).encode())
        self.headers = {"X-WP-TotalPages": str(pages)}


class ImportTests(unittest.TestCase):
    def test_staging_import_does_not_modify_site_or_reuse_destination(self):
        page = {
            "slug": "about", "title": {"rendered": "About"},
            "date": "2025-01-01", "link": importer.ORIGIN + "/about/",
            "id": 2, "featured_media": 0,
            "content": {"rendered": "<p>WordPress content</p>"},
        }
        collections = {"pages": [page], "posts?_embed=author,wp:term,wp:featuredmedia": [],
                       "categories": [], "media?_fields=id,source_url": []}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "site"
            root.mkdir()
            target = root / "content" / "about.md"
            target.parent.mkdir()
            target.write_text("Local Markdown edit")
            stage = Path(directory) / "wordpress-export"
            with (mock.patch.object(importer, "ROOT", root),
                  mock.patch.object(importer, "read_paginated", side_effect=lambda path: collections[path]),
                  contextlib.redirect_stdout(io.StringIO()),
                  contextlib.redirect_stderr(io.StringIO())):
                importer.main(["--output-dir", str(stage)])
                with self.assertRaises(SystemExit):
                    importer.main(["--output-dir", str(stage)])
            self.assertEqual(target.read_text(), "Local Markdown edit")
            self.assertIn("WordPress content", (stage / "content/about.html").read_text())
            self.assertFalse((root / "content/about.html").exists())

    def test_all_collection_pages_are_read_from_wordpress_page_count(self):
        calls = []

        def open_url(url, timeout):
            calls.append(url)
            page = int(url.split("page=")[-1])
            return Response([{"id": page}], 6)

        with mock.patch.object(importer.urllib.request, "urlopen", side_effect=open_url):
            items = importer.read_paginated("media?_fields=id,source_url")
        self.assertEqual([item["id"] for item in items], list(range(1, 7)))
        self.assertEqual(len(calls), 6)
        self.assertIn("_fields=id,source_url&per_page=100&page=6", calls[-1])

    def test_existing_markdown_page_also_requires_overwrite(self):
        page = {"slug": "about"}
        collections = {"pages": [page], "posts?_embed=author,wp:term,wp:featuredmedia": [],
                       "categories": []}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "content" / "about.md"
            target.parent.mkdir()
            target.write_text("Existing Markdown page")
            with (mock.patch.object(importer, "ROOT", root),
                  mock.patch.object(importer, "read_paginated", side_effect=lambda path: collections[path]),
                  contextlib.redirect_stderr(io.StringIO())):
                with self.assertRaises(SystemExit):
                    importer.main([])
                with self.assertRaises(SystemExit):
                    importer.main(["--overwrite"])
            self.assertEqual(target.read_text(), "Existing Markdown page")
            self.assertFalse(target.with_suffix(".html").exists())

    def test_renamed_markdown_page_requires_staged_import(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "content" / "renamed.md"
            target.parent.mkdir()
            target.write_text('{"url": "/about/"}\nLocal Markdown edit')
            with (mock.patch.object(importer, "ROOT", root),
                  mock.patch.object(importer, "read_paginated") as read,
                  contextlib.redirect_stderr(io.StringIO())):
                with self.assertRaises(SystemExit):
                    importer.main(["--overwrite"])
            read.assert_not_called()
            self.assertEqual(target.read_text(), '{"url": "/about/"}\nLocal Markdown edit')

    def test_existing_latest_posts_page_is_protected_when_missing_from_api(self):
        collections = {"pages": [], "posts?_embed=author,wp:term,wp:featuredmedia": [],
                       "categories": []}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "content" / "soccer.html"
            target.parent.mkdir()
            target.write_text("Local page")
            with (mock.patch.object(importer, "ROOT", root),
                  mock.patch.object(importer, "read_paginated", side_effect=lambda path: collections[path]),
                  contextlib.redirect_stderr(io.StringIO())):
                with self.assertRaises(SystemExit):
                    importer.main([])
            self.assertEqual(target.read_text(), "Local page")

    def test_existing_forum_page_is_protected_when_missing_from_api(self):
        collections = {"pages": [], "posts?_embed=author,wp:term,wp:featuredmedia": [],
                       "categories": []}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "content" / "rcj-rescue-line.html"
            target.parent.mkdir()
            target.write_text("Local page")
            with (mock.patch.object(importer, "ROOT", root),
                  mock.patch.object(importer, "read_paginated", side_effect=lambda path: collections[path]),
                  contextlib.redirect_stderr(io.StringIO())):
                with self.assertRaises(SystemExit):
                    importer.main([])
            self.assertEqual(target.read_text(), "Local page")

    def test_existing_forum_fallback_data_requires_overwrite(self):
        collections = {"pages": [], "posts?_embed=author,wp:term,wp:featuredmedia": [],
                       "categories": []}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / importer.FORUM_FALLBACK_FILE
            target.parent.mkdir()
            target.write_text('{"soccer": "Local fallback"}')
            with (mock.patch.object(importer, "ROOT", root),
                  mock.patch.object(importer, "read_paginated", side_effect=lambda path: collections[path]),
                  contextlib.redirect_stderr(io.StringIO())):
                with self.assertRaises(SystemExit):
                    importer.main([])
            self.assertEqual(target.read_text(), '{"soccer": "Local fallback"}')

    def test_existing_content_is_protected_and_protocol_relative_uploads_are_localized(self):
        page = {
            "slug": "about",
            "title": {"rendered": "About"},
            "date": "2025-01-01",
            "link": importer.ORIGIN + "/about/",
            "id": 2,
            "featured_media": 0,
            "content": {"rendered": (
                '<a href="//junior.robocup.org/wp-content/uploads/rules/a.pdf">A</a>'
                '<a href="//junior.robocup.org/wp-content/uploads/rules/missing.pdf">B</a>'
            )},
        }
        categories = [
            {"id": 1, "slug": "news", "name": "RoboCupJunior News", "parent": 0,
             "link": importer.ORIGIN + "/category/news/"},
            {"id": 2, "slug": "rescue-line", "name": "Rescue &amp; Line", "parent": 1,
             "link": importer.ORIGIN + "/category/rescue/rescue-line/"},
        ]
        collections = {"pages": [page], "posts?_embed=author,wp:term,wp:featuredmedia": [],
                       "categories": categories, "media?_fields=id,source_url": []}
        seen = []

        def download(url, root):
            seen.append(url)
            return (url, "not found" if url.endswith("missing.pdf") else None)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "content" / "about.html"
            target.parent.mkdir()
            target.write_text("Hugo-side edit")
            with (mock.patch.object(importer, "ROOT", root),
                  mock.patch.object(importer, "read_paginated", side_effect=lambda path: collections[path]),
                  mock.patch.object(importer, "download", side_effect=download),
                  mock.patch.object(importer, "refresh_latest_post_blocks") as refresh_latest,
                  mock.patch.object(importer, "refresh_forum_blocks") as refresh_forum,
                  contextlib.redirect_stderr(io.StringIO()),
                  contextlib.redirect_stdout(io.StringIO())):
                with self.assertRaises(SystemExit):
                    importer.main([])
                self.assertEqual(target.read_text(), "Hugo-side edit")
                self.assertFalse((root / "data").exists())
                self.assertEqual(seen, [])
                refresh_latest.assert_not_called()
                refresh_forum.assert_not_called()
                importer.main(["--overwrite"])
                refresh_latest.assert_called_once_with(root)
                refresh_forum.assert_called_once_with(root)
            body = target.read_text()
            self.assertIn('href="/wp-content/uploads/rules/a.pdf"', body)
            self.assertIn('href="//junior.robocup.org/wp-content/uploads/rules/missing.pdf"', body)
            self.assertIn("https://junior.robocup.org/wp-content/uploads/rules/a.pdf", seen)
            self.assertIn("https://junior.robocup.org/wp-content/uploads/rules/missing.pdf", seen)
            root_term = json.loads((root / "content/categories/news/_index.md").read_text())
            nested_term = json.loads((root / "content/categories/rescue-line/_index.md").read_text())
            self.assertEqual(root_term, {"title": "RoboCupJunior News", "url": "/category/news/"})
            self.assertEqual(nested_term, {"title": "Rescue & Line", "url": "/category/rescue/rescue-line/"})


if __name__ == "__main__":
    unittest.main()
