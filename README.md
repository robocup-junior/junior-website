# junior.robocup.org

Static [Hugo](https://gohugo.io/) site for [RoboCupJunior](https://junior.robocup.org/).

## Local development

Install Hugo **0.169.0 extended** (the version CI uses; see
https://github.com/gohugoio/hugo/releases/tag/v0.169.0), then:

```sh
hugo server                              # http://localhost:1313, rebuilds on save
python3 -m unittest discover -s tests    # tests (CI runs them on every push and pull request)
```

Design rules (colours, type, layout, components, images, accessibility) are in
[STYLEGUIDE.md](STYLEGUIDE.md). Read it before changing styles or templates.

## Where things live

| Path | What |
|------|------|
| `content/*.md` | Pages |
| `content/posts/*.md` | News posts |
| `data/` | Page layout choices, post metadata and related-post selections |
| `hugo.toml` | Site settings and the main menu (desktop and mobile menus are both built from `[[menus.main]]`) |
| `layouts/` | Hugo templates |
| `assets/css/` | Site styles: `rcj-site.css` (colours and site-wide rules), `home.css` (homepage), plus styles copied from WordPress |
| `static/` | Images, PDFs, theme files and scripts |

New post: `hugo new content posts/my-post.md`, then set `draft: false` in
the settings at the top of the file when ready. Those settings are called
front matter. The new post uses YAML front matter between `---` lines.

Edit the text in the Markdown files with normal Markdown syntax. The fields at
the top control the title, date, URL and other page settings. Add a
`description` there to set the search-engine description for a page. Keep it
up to date when changing a page that already has one.
The homepage text, links and image descriptions are in the `home` fields in
`content/_index.md`. Its front matter uses JSON, so keep the quotation marks
and commas when editing it. Lists such as `buttons` and `cards` can have any
number of items. The news section shows the six newest posts in the `news`
category. The page layout is `layouts/_partials/home.html`.

Pages get their banner title from `banner_title` in front matter (or the page
title). Add `banner_image` for a photo banner; without one the page gets a
plain navy banner. Imported pages also read these from
`data/wordpress-pages.json`.

Some imported pages use Hugo shortcodes for images, columns, buttons and
other WordPress layouts. Edit the text between their opening and closing tags
as Markdown. Keep the tags and their parameters unless you intend to change
the layout. See `content/about.md` for examples. On pages with
`"type": "legacy-links"`, link titles such as `"newtab"` control link
attributes. For example, `"newtab"` opens a link in a new tab. Keep other
existing link titles when editing these pages. Ordinary Markdown links work
without a title. To open a link in a new tab, write
`[Link text](https://example.org/ "newtab")`.
For a heading that needs an anchor link, use the `wp-anchored-heading`
shortcode, as in `content/resources.md`. Headings inside `wp-prose` do not
automatically get anchors. Link to the shortcode's `id` with `#id`.
The Resources page also uses titles such as `"resource-year-2026"` to make
links filter the library by year. Keep the year in the title consistent with
the year shown in the link.
In Workshop on Educational Robotics (WEROB) schedules, such as
`content/workshop-on-educational-robotics-werob-2023.md`, separate cells with
` | `. Use `{empty}` for an empty cell and `{colspan=3}` at the start of a
cell that spans three columns. For example, `12:00 | {colspan=3}Lunch` is a
row with a time cell and a lunch cell spanning three columns.

Pages and posts use `/<slug>/`, based on their filename unless their front
matter sets a different `url` or `slug`. Categories use `/category/<slug>/`.

`data/wordpress-pages.json` stores the imported banner and layout settings,
keyed by WordPress page ID. `data/jetpack-related.json` and
`data/theme-related.json` store imported related-post selections, keyed by
post ID. Edit these files if those settings or selections need to change.
The `wordpress_id` field in each imported page or post gives its ID.
Homepage cards use saved excerpts and images while their posts match
`data/homepage-news-fingerprints.json`. Edited posts use generated cards, so
editors do not need to update the saved card data.
The Events page fetches upcoming and past events from RoboCup at build time.
If either listing cannot be fetched or parsed, the build uses its saved copy
in `data/robocup_events.json`. Rebuild and deploy the site to publish new
events. Edit that file if the saved copy needs updating.

To review a fresh export of published pages and posts from
`junior.robocup.org`, run
`python3 scripts/import-wordpress.py --output-dir /path/to/new-directory`.
The directory must not exist yet. The export contains HTML, media and metadata.
It does not convert content to Markdown. Compare it with the site and apply
the changes you need by hand. The importer reads the WordPress API at that
address, so it works only while WordPress is available there. It does not
refresh the page layout, homepage card or related-post snapshots.

Forum lists fetch recent topics during each build. If a feed cannot be
reached or parsed, the site uses the saved list in `data/forum_fallbacks.json`.

The news feed is `/index.xml` (posts only). GitHub Pages cannot redirect, so
before junior.robocup.org moves here, hosting must redirect `/feed/` to
`/index.xml` (for example with Cloudflare or Netlify). Old `/?p=<id>` and
`/?page_id=<id>` links are redirected by a script on the homepage.

The GitHub Pages copy is a staging site: `config/github-pages/hugo.toml` sets
`noindex` and points canonical links at junior.robocup.org. Remove those two
settings when the domain moves.

Forum lists and RoboCup events are fetched at build time (timeout set by
`remote_timeout`, default 15s). If a fetch fails, the build log shows a `WARN`
and the page uses the saved copy. CI rebuilds every 6 hours.
