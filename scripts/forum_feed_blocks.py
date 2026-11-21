"""Extract imported forum lists so Hugo can refresh them at build time."""

import json
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
FORUM_FALLBACK_FILE = "data/forum_fallbacks.json"

_FORUM_BLOCK = re.compile(
    r'<div class="wpra-display\b[^>]*>.*?</ul>\s*</div>\s*</div>',
    re.DOTALL,
)
_WRAPPED = re.compile(
    r'{{< forum-feed "([^"]+)" >}}\s*(.*?)\s*{{< /forum-feed >}}',
    re.DOTALL,
)
_SHORTCODE = '{{{{< forum-feed "{}" >}}}}'


def refresh_forum_blocks(root: Path) -> None:
    """Extract WordPress's rendered lists as offline fallback data."""
    data_path = root / FORUM_FALLBACK_FILE
    fallbacks = json.loads(data_path.read_text(encoding="utf-8")) if data_path.exists() else {}
    updates = {}
    filenames = (variant for name in FORUM_CONTENT_FILES
                 for variant in (name, str(Path(name).with_suffix(".md"))))
    for filename in filenames:
        path = root / filename
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        key = path.stem
        opening = _SHORTCODE.format(key)
        wrapped = list(_WRAPPED.finditer(content))
        if len(wrapped) > 1:
            raise ValueError(f"Expected at most one forum list in {filename}, found {len(wrapped)}")
        if wrapped:
            match = wrapped[0]
            if match.group(1) != key:
                raise ValueError(f"Unexpected forum key in {filename}: {match.group(1)}")
            fallbacks[key] = match.group(2)
            content = content[:match.start()] + opening + content[match.end():]
        elif opening not in content:
            matches = list(_FORUM_BLOCK.finditer(content))
            if len(matches) > 1:
                raise ValueError(f"Expected at most one forum list in {filename}, found {len(matches)}")
            if matches:
                match = matches[0]
                fallbacks[key] = match.group(0)
                content = content[:match.start()] + opening + content[match.end():]
        if content != path.read_text(encoding="utf-8"):
            updates[path] = content
    if updates:
        data_path.parent.mkdir(parents=True, exist_ok=True)
        data_path.write_text(json.dumps(fallbacks, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        for path, content in updates.items():
            path.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    refresh_forum_blocks(Path(__file__).resolve().parent.parent)
