import json
import shutil
import subprocess
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def listing(title, path, start, end, excerpt, image=""):
    picture = f'<img src="{image}">' if image else ""
    return f'''<html><body><nav>Navigation outside the event</nav>
<h4><a href="{path}">{title}</a></h4>
<div class="blog-info blog-date">From <strong>{start}</strong> To <strong>{end}</strong></div>
<div class="gdlr-space" style="margin-top: 30px;"></div>{picture}
<div class="gdlr-space" style="margin-top: 30px;"></div><div>{excerpt}</div>
<div class="clear"></div><a href="{path}">Read More</a>
</body></html>'''.encode()


class EventsHandler(BaseHTTPRequestHandler):
    pages = {}

    def do_GET(self):
        status, body = type(self).pages.get(self.path, (404, b"missing"))
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


class RoboCupEventsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), EventsHandler)
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
        for folder in ("content", "data", "layouts/_shortcodes", "layouts/_partials"):
            (self.root / folder).mkdir(parents=True)
        for path in ("layouts/_shortcodes/robocup-events.html", "layouts/_partials/robocup-events-fetch.html"):
            shutil.copy(ROOT / path, self.root / path)
        (self.root / "layouts/index.html").write_text("{{ .Content }}", encoding="utf-8")
        (self.root / "content/_index.md").write_text('---\ntitle: Test\n---\n{{< robocup-events >}}', encoding="utf-8")
        self.snapshot = {
            "upcoming": [{"title": "Saved upcoming", "url": "https://www.robocup.org/events/1", "start": "2026-01-01", "end": "2026-01-02", "image": "", "excerpt": "Saved upcoming description"}],
            "past": [{"title": "Saved past", "url": "https://www.robocup.org/events/2", "start": "2025-01-01", "end": "2025-01-02", "image": "", "excerpt": "Saved past description"}],
        }
        (self.root / "data/robocup_events.json").write_text(json.dumps(self.snapshot), encoding="utf-8")
        port = self.server.server_port
        (self.root / "hugo.toml").write_text(
            "baseURL = 'https://example.test/'\n"
            "[params]\n"
            "remote_timeout = '2s'\n"
            f"events_upcoming_url = 'http://127.0.0.1:{port}/upcoming'\n"
            f"events_past_url = 'http://127.0.0.1:{port}/past'\n"
            "[security]\nallowContent = ['! ^text/org$']\n"
            "[security.http]\nurls = ['^http://127\\.0\\.0\\.1:[0-9]+']\n"
            "[caches.getresource]\nmaxAge = '0s'\n", encoding="utf-8"
        )
        EventsHandler.pages = {
            "/upcoming": (200, listing("New &amp; upcoming", "/events/101", "16 Apr 2027", "18 Apr 2027", "Fresh description", "/system/events/images/101.jpg")),
            "/past": (200, listing("Past event", "/events/99", "3 Jun 2026", "6 Jun 2026", "Past description")),
        }

    def build(self):
        result = subprocess.run(["hugo", "--source", str(self.root)],
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return (self.root / "public/index.html").read_text(encoding="utf-8")

    def test_upstream_events_refresh_each_build(self):
        result = self.build()
        self.assertIn("New &amp; upcoming", result)
        self.assertIn('href="https://www.robocup.org/events/101"', result)
        self.assertIn('src="https://www.robocup.org/system/events/images/101.jpg"', result)
        self.assertIn('datetime="2027-04-16"', result)
        self.assertIn('datetime="2027-04-18"', result)
        self.assertIn("Fresh description", result)
        self.assertNotIn("Navigation outside the event", result)
        self.assertNotIn("Saved upcoming", result)
        EventsHandler.pages["/upcoming"] = (200, listing("Updated event", "/events/101", "16 Apr 2027", "18 Apr 2027", "New text"))
        updated = self.build()
        self.assertIn("Updated event", updated)
        self.assertNotIn("New &amp; upcoming", updated)

    def test_failed_or_unrecognized_source_uses_its_snapshot(self):
        EventsHandler.pages["/upcoming"] = (503, b"unavailable")
        EventsHandler.pages["/past"] = (200, b"<html>unexpected page format</html>")
        result = self.build()
        self.assertIn("Saved upcoming", result)
        self.assertIn("Saved past", result)
        self.assertNotIn("unexpected page format", result)

    def test_one_failed_source_does_not_hide_other_live_events(self):
        EventsHandler.pages["/past"] = (503, b"unavailable")
        result = self.build()
        self.assertIn("New &amp; upcoming", result)
        self.assertIn("Saved past", result)
        self.assertNotIn("Saved upcoming", result)

    def test_empty_listing_does_not_show_obsolete_upcoming_events(self):
        EventsHandler.pages["/upcoming"] = (200, b'<html><div class="gdlr-blog-content"></div></html>')
        result = self.build()
        self.assertNotIn("Saved upcoming", result)
        self.assertNotIn("New &amp; upcoming", result)
        self.assertIn("Past event", result)


if __name__ == "__main__":
    unittest.main()
