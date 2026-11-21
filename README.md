# junior.robocup.org

Static [Hugo](https://gohugo.io/) site for [RoboCupJunior](https://junior.robocup.org/).

## Local development

```sh
brew install hugo   # or see https://gohugo.io/installation/
hugo server         # http://localhost:1313, rebuilds on save
```

## Where things live

| Path | What |
|------|------|
| `content/*.html` | Imported WordPress pages |
| `content/posts/*.html` | Imported news posts |
| `data/` | Page layout choices, post metadata and related-post selections |
| `hugo.toml` | Site settings and the main menu |
| `layouts/` | Hugo templates |
| `assets/css/` | Site and WordPress theme styles |
| `static/` | Images, PDFs, theme files and scripts |

New post: `hugo new content posts/my-post.md`, then set `draft: false` in
the post's front matter when ready.

Pages and posts use `/<slug>/`. Categories use `/category/<slug>/`.

The JSON files `data/wordpress-pages.json`, `data/jetpack-related.json`
and `data/theme-related.json` hold snapshots from WordPress. Update them
manually when the corresponding WordPress content changes. Homepage card
snapshots are used only while their posts remain unchanged. The Events page
is empty because its WordPress feed was removed from this migration.

To import published pages and posts from `junior.robocup.org`, run
`python3 scripts/import-wordpress.py`. The importer refuses to replace
existing content and post metadata unless you pass `--overwrite`. Review
local edits before using that option. It also stops if a Markdown file would
conflict with an imported HTML page. Move or rename that file before importing.
The importer does not refresh the page layout, homepage card or related-post
snapshots.

Forum lists fetch recent topics during each build. If a feed cannot be
reached or parsed, the site uses the saved WordPress list for that page.

When configuring hosting, redirect `/feed/` to `/index.xml` so existing
WordPress RSS subscribers can follow the feed.
