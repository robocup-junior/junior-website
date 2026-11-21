"""Wrap imported forum lists so Hugo can refresh them at build time."""

import re
from pathlib import Path


FORUM_CONTENT_FILES = (
    "content/gettingstarted.html",
    "content/soccer.html",
    "content/onstage.html",
    "content/rcj-rescue-line.html",
    "content/rcj-rescue-maze.html",
    "content/rcj-rescue-sim.html",
)

_FORUM_BLOCK = re.compile(
    r'<div class="wpra-display\b[^>]*>.*?</ul>\s*</div>\s*</div>',
    re.DOTALL,
)
_SHORTCODE = '{{{{< forum-feed "{}" >}}}}'


def refresh_forum_blocks(root: Path) -> None:
    """Keep WordPress's rendered forum list as a shortcode fallback."""
    for filename in FORUM_CONTENT_FILES:
        path = root / filename
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        key = path.stem
        opening = _SHORTCODE.format(key)
        if opening in content:
            continue
        content, count = _FORUM_BLOCK.subn(
            lambda match: opening + "\n" + match.group(0) + "\n{{< /forum-feed >}}",
            content,
        )
        if count > 1:
            raise ValueError(f"Expected at most one forum list in {filename}, found {count}")
        if count:
            path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    refresh_forum_blocks(Path(__file__).resolve().parent.parent)
