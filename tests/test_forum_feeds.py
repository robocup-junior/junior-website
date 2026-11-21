import importlib.util
import subprocess
import tempfile
import threading
import time
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("forum_feed_blocks", ROOT / "scripts/forum_feed_blocks.py")
forum_blocks = importlib.util.module_from_spec(spec)
spec.loader.exec_module(forum_blocks)

RSS = b"""<?xml version="1.0"?>
<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/"><channel><title>Test</title>
<item><title>New &amp; useful topic</title><link>https://example.org/topic</link>
<dc:creator>Alice</dc:creator><pubDate>Sun, 15 Nov 2026 01:53:46 +0000</pubDate></item>
</channel></rss>"""


class FeedHandler(BaseHTTPRequestHandler):
    body = RSS
    delay = 0

    def do_GET(self):
        time.sleep(type(self).delay)
        self.send_response(200)
        self.send_header("Content-Type", "application/rss+xml")
        self.end_headers()
        try:
            self.wfile.write(type(self).body)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def log_message(self, *args):
        pass


class ForumFeedsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), FeedHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for directory in ("layouts/_shortcodes", "content"):
            (self.root / directory).mkdir(parents=True)
        shortcode = (ROOT / "layouts/_shortcodes/forum-feed.html").read_text()
        shortcode = shortcode.replace(
            "https://junior.forum.robocup.org",
            f"http://127.0.0.1:{self.server.server_port}",
        )
        (self.root / "layouts/_shortcodes/forum-feed.html").write_text(shortcode)
        (self.root / "layouts/index.html").write_text("{{ .Content }}")
        (self.root / "content/_index.html").write_text(
            '---\ntitle: Test\n---\n{{< forum-feed "soccer" >}}'
            '<div id="captured-fallback">Offline fallback</div>{{< /forum-feed >}}'
        )
        (self.root / "hugo.toml").write_text(
            "baseURL = 'https://example.org/'\n"
            "[security]\nallowContent = ['! ^text/org$']\n"
            "[security.http]\nurls = ['^http://127\\.0\\.0\\.1:[0-9]+']\n"
            "[caches.getresource]\nmaxAge = '0s'\n"
        )
        FeedHandler.body = RSS
        FeedHandler.delay = 0

    def build(self):
        subprocess.run(
            ["hugo", "--source", str(self.root), "--quiet"],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return (self.root / "public/index.html").read_text()

    def test_live_feed_refreshes_on_subsequent_build(self):
        result = self.build()
        self.assertIn("New &amp; useful topic", result)
        self.assertIn("Date:  2026-11-14", result)
        self.assertIn("By Alice", result)
        self.assertNotIn("captured-fallback", result)
        FeedHandler.body = RSS.replace(b"New &amp; useful topic", b"Updated topic")
        self.assertIn("Updated topic", self.build())

    def test_bad_xml_and_timeout_use_captured_fallback(self):
        FeedHandler.body = b"not a valid feed"
        self.assertIn("captured-fallback", self.build())
        FeedHandler.body = RSS
        FeedHandler.delay = 4
        started = time.monotonic()
        self.assertIn("captured-fallback", self.build())
        self.assertLess(time.monotonic() - started, 5)

    def test_import_helper_wraps_once_and_preserves_fallback(self):
        filename = self.root / forum_blocks.FORUM_CONTENT_FILES[1]
        filename.parent.mkdir(parents=True, exist_ok=True)
        original = '<div class="wpra-display align"><div><ul><li>Saved</li></ul></div></div>'
        filename.write_text(original)
        forum_blocks.refresh_forum_blocks(self.root)
        wrapped = filename.read_text()
        self.assertIn('{{< forum-feed "soccer" >}}', wrapped)
        self.assertIn(original, wrapped)
        forum_blocks.refresh_forum_blocks(self.root)
        self.assertEqual(wrapped, filename.read_text())


if __name__ == "__main__":
    unittest.main()
