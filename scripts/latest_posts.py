"""Keep WordPress latest-post blocks dynamic after importing pages."""
import hashlib
import html
import json
import re
from pathlib import Path
from urllib.parse import urlsplit


BLOCK = re.compile(
    r'<ul class="(wp-block-latest-posts__list[^"]*)"[^>]*>.*?</ul>',
    re.DOTALL,
)
ITEM = re.compile(r'<li>.*?</li>', re.DOTALL)
POST_LINK = re.compile(
    r'<a class="wp-block-latest-posts__post-title" href="([^"]+)"'
)
SETTINGS = {
    "soccer": {"limit": 5, "excerpt_words": 55},
    "rescue": {"limit": 5, "excerpt_words": 40},
    "onstage": {"limit": 5, "excerpt_words": 40},
}


def _post_metadata(root):
    metadata_file = root / "data" / "wordpress-posts.json"
    authors = json.loads(metadata_file.read_text(encoding="utf-8")) if metadata_file.exists() else {}
    posts = {}
    for path in (root / "content" / "posts").glob("*.html"):
        text = path.read_text(encoding="utf-8")
        try:
            front, end = json.JSONDecoder().raw_decode(text)
        except json.JSONDecodeError:
            # Manually created Hugo posts may use YAML or TOML front matter.
            continue
        body = text[end:]
        if body.startswith("\n"):
            body = body[1:]
        details = authors.get(str(front.get("wordpress_id")), {})
        posts[front.get("url", "").lower()] = {
            "content_hash": hashlib.md5(body.encode("utf-8")).hexdigest(),
            "title": front.get("title", ""),
            "date": front.get("date", ""),
            "image": front.get("featured_image", ""),
            "author": details.get("author", ""),
        }
    return posts


def refresh_latest_post_blocks(root):
    """Replace imported lists with shortcodes and save matching original cards."""
    root = Path(root)
    posts = _post_metadata(root)
    data_path = root / "data" / "latest-posts.json"
    data = json.loads(data_path.read_text(encoding="utf-8")) if data_path.exists() else {}
    for category, settings in SETTINGS.items():
        path = root / "content" / f"{category}.html"
        if not path.exists():
            continue
        source = path.read_text(encoding="utf-8")
        block = BLOCK.search(source)
        if not block:
            continue
        cards = {}
        for item in ITEM.findall(block.group()):
            match = POST_LINK.search(item)
            if not match:
                continue
            url = urlsplit(html.unescape(match.group(1))).path.lower()
            if url in posts:
                cards[url] = {**posts[url], "html": item}
        data[category] = {
            **settings,
            "classes": block.group(1),
            "items": cards,
        }
        shortcode = '{{< latest-posts category="' + category + '" >}}'
        path.write_text(source[:block.start()] + shortcode + source[block.end():], encoding="utf-8")
    data_path.parent.mkdir(parents=True, exist_ok=True)
    data_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
