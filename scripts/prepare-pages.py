#!/usr/bin/env python3
"""Prefix root-relative links left in static embeds and object elements."""
import argparse
import re
from pathlib import Path
from urllib.parse import urlsplit


ROOT_ATTRIBUTE = re.compile(r'''(?i)(?<![\w:-])(?:href|src|data)\s*=\s*["']?/(?!/)''')
SRCSET = re.compile(r'''(?i)(?<![\w:-])srcset\s*=\s*(["'])(.*?)\1''', re.DOTALL)


def prefix_urls(html, prefix):
    if prefix == "/":
        return html
    html = ROOT_ATTRIBUTE.sub(
        lambda match: match.group() if html[match.end() - 1:].startswith(prefix)
        else match.group()[:-1] + prefix,
        html,
    )

    def fix_srcset(match):
        candidates = re.sub(
            r'(^|,\s*)/(?!/)',
            lambda m: m.group() if match.group(2)[m.end() - 1:].startswith(prefix)
            else m.group(1) + prefix,
            match.group(2),
        )
        return match.group(0).replace(match.group(2), candidates, 1)

    return SRCSET.sub(fix_srcset, html)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    parser.add_argument("base_url")
    args = parser.parse_args()
    prefix = urlsplit(args.base_url).path.rstrip("/") + "/"
    for path in args.directory.rglob("*.html"):
        original = path.read_text(encoding="utf-8")
        rewritten = prefix_urls(original, prefix)
        if rewritten != original:
            path.write_text(rewritten, encoding="utf-8")


if __name__ == "__main__":
    main()
