# junior.robocup.org

Static [Hugo](https://gohugo.io/) site for [RoboCupJunior](https://junior.robocup.org/),
replacing the old WordPress install.

## Local development

```sh
brew install hugo   # or see https://gohugo.io/installation/
hugo server         # http://localhost:1313, rebuilds on save
```

## Where things live

| Path | What |
|------|------|
| `content/*.md` | Pages, served at `/<file-name>/` |
| `content/posts/*.md` | News posts, served at `/<slug>/` |
| `hugo.toml` | Site settings and the main menu |
| `layouts/` | HTML templates |
| `assets/css/main.css` | Styles |
| `static/` | Files copied as-is (images, PDFs) |

New post: `hugo new content posts/my-post.md`, then set `draft: false` when ready.

URLs match the WordPress site: pages and posts at `/<slug>/`, categories at `/category/<slug>/`.
