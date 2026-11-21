#!/usr/bin/env python3
"""Import published WordPress content and referenced uploads into Hugo."""
import argparse
import concurrent.futures
import html
import json
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from latest_posts import SETTINGS as LATEST_POST_CATEGORIES, refresh_latest_post_blocks
from forum_feed_blocks import FORUM_CONTENT_FILES, refresh_forum_blocks

ORIGIN = 'https://junior.robocup.org'
ROOT = Path(__file__).resolve().parent.parent
UPLOAD_RE = re.compile(r'(?<![\w:])(?:https?:)?//junior\.robocup\.org/wp-content/uploads/[^\s\"\'<>),]+')
POST_IMAGE_SIZES = ('kahuna-featured', 'kahuna-featured-half', 'kahuna-featured-third')

def read_json(path):
    with urllib.request.urlopen(ORIGIN + '/wp-json/wp/v2/' + path, timeout=45) as response:
        return json.load(response)

def read_paginated(path):
    """Read all WordPress collection pages using the server's page count."""
    separator = '&' if '?' in path else '?'
    first_path = f'{path}{separator}per_page=100&page=1'
    with urllib.request.urlopen(ORIGIN + '/wp-json/wp/v2/' + first_path, timeout=45) as response:
        items = json.load(response)
        total_pages = int(response.headers.get('X-WP-TotalPages', '1'))
    for page in range(2, total_pages + 1):
        items.extend(read_json(f'{path}{separator}per_page=100&page={page}'))
    return items

def normalize_upload_url(url):
    return 'https:' + url if url.startswith('//') else url

def upload_path(url):
    return urllib.parse.unquote(urllib.parse.urlsplit(url).path).lstrip('/')

def download(url):
    path = ROOT / 'static' / upload_path(url)
    if path.is_file() and path.stat().st_size:
        return url, None
    try:
        request_url = urllib.parse.quote(url.replace('http://', 'https://', 1), safe=':/%?&=+#')
        with urllib.request.urlopen(request_url, timeout=45) as response:
            data = response.read()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return url, None
    except Exception as exc:
        return url, str(exc)

def download_avatar(author_id, url):
    """Save the high-resolution WordPress avatar used in post bylines."""
    parsed = urllib.parse.urlsplit(url)
    query = dict(urllib.parse.parse_qsl(parsed.query))
    query['s'] = '192'
    url = urllib.parse.urlunsplit(parsed._replace(query=urllib.parse.urlencode(query)))
    try:
        with urllib.request.urlopen(url, timeout=45) as response:
            data = response.read()
            content_type = response.headers.get_content_type()
        extension = {'image/jpeg': 'jpg', 'image/png': 'png', 'image/webp': 'webp'}.get(content_type, 'img')
        path = ROOT / 'static' / 'images' / 'avatars' / f'{author_id}.{extension}'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return f'/images/avatars/{author_id}.{extension}', None
    except Exception as exc:
        return url, str(exc)

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--overwrite', action='store_true',
                        help='replace existing imported content and metadata')
    args = parser.parse_args(argv)
    pages = read_paginated('pages')
    posts = read_paginated('posts?_embed=author,wp:term,wp:featuredmedia')
    category_items = read_paginated('categories')
    categories = {c['id']: c['slug'] for c in category_items}
    paths = [ROOT / 'data' / 'wordpress-posts.json',
             ROOT / 'data' / 'latest-posts.json']
    markdown_paths = []
    for typ, group in [('page', pages), ('post', posts)]:
        for item in group:
            slug = item['slug']
            directory = ROOT / 'content' / ('posts' if typ == 'post' else '')
            path = directory / ('_index.html' if typ == 'page' and slug == 'index'
                                else slug + '.html')
            paths.append(path)
            markdown_paths.append(path.with_suffix('.md'))
    paths.extend(ROOT / 'content' / 'categories' / category['slug'] / '_index.md'
                 for category in category_items)
    paths.extend(ROOT / 'content' / f'{category}.html'
                 for category in LATEST_POST_CATEGORIES)
    paths.extend(ROOT / filename for filename in FORUM_CONTENT_FILES)
    markdown_conflicts = [path for path in markdown_paths if path.exists()]
    if markdown_conflicts:
        parser.error(f'{len(markdown_conflicts)} Markdown content files conflict with '
                     'the import; move or rename them before importing')
    existing = [path for path in set(paths) if path.exists()]
    if existing and not args.overwrite:
        parser.error(f'{len(existing)} import targets already exist; '
                     'use --overwrite to replace existing content and metadata')
    # Explicit terms retain WordPress names and URLs even with no published posts.
    for category in category_items:
        term = ROOT / 'content' / 'categories' / category['slug'] / '_index.md'
        term.parent.mkdir(parents=True, exist_ok=True)
        term.write_text(json.dumps({'title': html.unescape(category['name']),
                                    'url': urllib.parse.urlsplit(category['link']).path},
                                   ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    media = {}
    for item in read_paginated('media?_fields=id,source_url'):
        media[item['id']] = item['source_url']
    items = pages + posts
    urls = set()
    for item in items:
        content = html.unescape(item['content']['rendered'])
        urls.update(normalize_upload_url(u.rstrip('.,;')) for u in UPLOAD_RE.findall(content))
        urls.update(ORIGIN + u.rstrip('.,;') for u in re.findall(r'(?<![\w:])(/wp-content/uploads/[^\s\"\'<>),]+)', content))
        featured = media.get(item['featured_media'])
        if featured:
            urls.add(featured)
    # Post templates use WordPress author/category labels and cropped theme images.
    post_metadata = {}
    avatars = {}
    for post in posts:
        embedded = post.get('_embedded', {})
        authors = embedded.get('author', [])
        term_groups = embedded.get('wp:term', [])
        terms = term_groups[0] if term_groups else []
        featured_media = embedded.get('wp:featuredmedia', [])
        author = authors[0] if authors else {}
        avatar_url = author.get('avatar_urls', {}).get('96')
        if avatar_url:
            avatars[post['author']] = avatar_url
        sizes = featured_media[0].get('media_details', {}).get('sizes', {}) if featured_media else {}
        images = {name: sizes[name]['source_url'] for name in POST_IMAGE_SIZES
                  if sizes.get(name, {}).get('source_url')}
        urls.update(images.values())
        post_metadata[str(post['id'])] = {
            'id': post['id'],
            'author': author.get('name'),
            'author_id': post['author'],
            'terms': [{'name': html.unescape(term['name']), 'slug': term['slug'], 'link': term['link']}
                      for term in terms],
            'images': images,
        }
    print(f'Downloading {len(urls)} referenced uploads', flush=True)
    failures = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        for i, (url, error) in enumerate(pool.map(download, sorted(urls)), 1):
            if error:
                failures[url] = error
            if i % 50 == 0:
                print(f'{i}/{len(urls)} downloads attempted', flush=True)
    for post in post_metadata.values():
        for size, url in post['images'].items():
            if url not in failures:
                post['images'][size] = '/' + urllib.parse.quote(upload_path(url), safe='/')
    for author_id, avatar_url in avatars.items():
        avatar, error = download_avatar(author_id, avatar_url)
        if error:
            failures[avatar_url] = error
        for post in post_metadata.values():
            if post['author_id'] == author_id:
                post['avatar'] = avatar
    metadata_path = ROOT / 'data' / 'wordpress-posts.json'
    metadata_path.parent.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(json.dumps(post_metadata, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    def localize(content):
        def replace(match):
            url = html.unescape(match.group(0))
            trimmed = url.rstrip('.,;')
            if normalize_upload_url(trimmed) in failures:
                return match.group(0)
            return '/' + urllib.parse.quote(upload_path(trimmed), safe='/') + url[len(trimmed):]
        content = UPLOAD_RE.sub(replace, content)
        return re.sub(r'https?://junior\.robocup\.org(?=/(?!wp-content/uploads/))', '', content)
    for typ, group in [('page', pages), ('post', posts)]:
        for item in group:
            slug = item['slug']
            filename = 'index' if typ == 'page' and slug == 'index' else slug
            directory = ROOT / 'content' / ('posts' if typ == 'post' else '')
            directory.mkdir(parents=True, exist_ok=True)
            if typ == 'page' and slug == 'index':
                path = directory / '_index.html'
            else:
                path = directory / (filename + '.html')
            featured = media.get(item['featured_media'])
            front = {'title': html.unescape(item['title']['rendered']), 'date': item['date'],
                     'url': urllib.parse.unquote(urllib.parse.urlsplit(item['link']).path),
                     'wordpress_id': item['id']}
            if typ == 'post':
                front['categories'] = [categories[x] for x in item['categories'] if x in categories]
                front['wordpress_excerpt'] = item['excerpt']['rendered']
            if featured:
                front['featured_image'] = featured if featured in failures else '/' + urllib.parse.quote(upload_path(featured), safe='/')
            # JSON front matter preserves Unicode and avoids YAML scalar ambiguities.
            body = '' if typ == 'page' and slug == 'events' else localize(item['content']['rendered'])
            if 'class="wp-embedded-content"' in body:
                body += '\n<script src="/js/wp-embed.min.js" defer></script>'
            path.write_text(json.dumps(front, ensure_ascii=False, indent=2) + '\n' + body + '\n', encoding='utf-8')
    refresh_latest_post_blocks(ROOT)
    refresh_forum_blocks(ROOT)
    print(f'Imported {len(pages)} pages and {len(posts)} posts; {len(failures)} downloads failed')
    for url, error in failures.items():
        print(f'FAILED {url}: {error}')

if __name__ == '__main__':
    main()
