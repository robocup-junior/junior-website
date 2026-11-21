import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("prepare_pages", ROOT / "scripts/prepare-pages.py")
prepare_pages = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prepare_pages)
BASE_URL = "https://robocup-junior.github.io/junior-website/"


class PagesBuildTest(unittest.TestCase):
    def test_prefixes_embeds_and_object_data_without_changing_external_urls(self):
        original = (
            '<a href="/history/">History</a><img src="/icon.png" '
            'srcset="/small.png 1x, /large.png 2x">'
            '<object data="/file.pdf"></object><a href="//example.com/">External</a>'
        )
        result = prepare_pages.prefix_urls(original, "/junior-website/")
        self.assertIn('href="/junior-website/history/"', result)
        self.assertIn('src="/junior-website/icon.png"', result)
        self.assertIn('srcset="/junior-website/small.png 1x, /junior-website/large.png 2x"', result)
        self.assertIn('data="/junior-website/file.pdf"', result)
        self.assertIn('href="//example.com/"', result)
        self.assertEqual(prepare_pages.prefix_urls(result, "/junior-website/"), result)
        self.assertEqual(prepare_pages.prefix_urls(original, "/"), original)

    def test_project_site_builds_with_prefixed_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "site"
            subprocess.run(
                ["hugo", "--source", str(ROOT), "--destination", str(output),
                 "--environment", "github-pages", "--baseURL", BASE_URL, "--quiet"],
                check=True, capture_output=True, timeout=60,
            )
            subprocess.run(
                ["python3", str(ROOT / "scripts/prepare-pages.py"), str(output), BASE_URL],
                check=True, capture_output=True, timeout=20,
            )
            home = (output / "index.html").read_text()
            soccer = (output / "soccer/index.html").read_text()
            resource = (output / "resources/index.html").read_text()
            educators = (output / "for-educators/index.html").read_text()
            redirect = (output / "werob/index.html").read_text()
            embed = (output / "history/embed/index.html").read_text()
            post = (output / "inaugural-robocupjunior-americas-superregional/index.html").read_text()
            self.assertIn(BASE_URL + "wp-content/themes/kahuna-plus/style.css", home)
            self.assertIn(BASE_URL + "soccer/", home)
            self.assertIn(BASE_URL + "wp-content/uploads/2017/12/DSC04977.jpg", soccer)
            self.assertIn('var siteRoot="' + BASE_URL + '"', resource)
            self.assertIn('m.href="' + BASE_URL + 'resources/"', educators)
            self.assertIn('location.replace("' + BASE_URL + 'rcj-werob/"', redirect)
            self.assertIn('href="/junior-website/history/"', embed)
            self.assertIn('srcset="/junior-website/wp-content/', embed)
            self.assertIn('data="/junior-website/wp-content/', post)


if __name__ == "__main__":
    unittest.main()
