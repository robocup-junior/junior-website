# RoboCupJunior website style guide

This is the single reference for how junior.robocup.org looks, reads and is
built. Follow it for every new page, post or template change. The styles it
describes live in:

| File | What it holds |
|------|---------------|
| `assets/css/rcj-site.css` | Design tokens (colours, focus ring) and site-wide fixes. Loaded last, so it wins ties. |
| `assets/css/home.css` | The homepage only. |
| `assets/css/fonts.css`, `static/fonts/` | Self-hosted fonts. |
| `assets/css/reference-*.css`, `static/wp-content/themes/kahuna-plus/` | The original WordPress theme, kept for page content. Don't add new rules here. |

The guide came out of a review of the whole site at 8 screen widths (320 to
1920 px) and a contrast measurement of every text element. Problems it found
are listed under each rule as "Avoid", so they don't come back.

---

## 1. Voice and content

- **Audience first.** Students (up to age 19), parents, teachers and mentors.
  Write plainly; explain acronyms on first use (RoboCupJunior (RCJ),
  Workshop on Educational Robotics (WEROB)).
- **Say "regions", never "countries".** RoboCupJunior is organised by regions.
- **Page pattern.** Full-width text, an *italic tagline* under the main
  heading where a page has one, **bold lead-ins** on list items, and a row of
  buttons for the main actions.
- **Headings describe the content** ("Qualification and Competitions", not
  "More info"). Use sentence case for new headings.
- **Link text says where it goes** ("Soccer rules (PDF)", not "click here").
  Mark file links with the type: `(PDF)`, `(video)`.
- **Dates:** `2 January 2026` in text; ISO `2026-01-02` in `datetime`
  attributes (the templates do this for you).
- **Emails:** write them out as the site already does
  (`robocupjunior-soccer [ at ] robocup [ dot ] org`) to limit spam.

## 2. Colour

Use the tokens, never raw hex values, in new CSS. All pairs below are measured
against WCAG 2.2 AA: 4.5:1 for normal text, 3:1 for large text (24px+, or
19px+ bold) and for borders, icons and focus rings.

| Token | Hex | Use | Contrast |
|-------|-----|-----|----------|
| `--rcj-navy` | `#001242` | Body text, headings, navy bands, header text | 18.0:1 on white, 16.7:1 on surface |
| `--rcj-navy-deep` | `#000d3d` | Footer bottom bar only | – |
| `--rcj-ink` | `#32373c` | Dark buttons, chips, card accents (matches WordPress) | 12.0:1 with white |
| `--rcj-pink` | `#d40560` | Links, primary buttons, focus ring, accents | 5.26:1 on white; 4.87:1 on surface |
| `--rcj-pink-dark` | `#bb0047` | Pink hover / pressed | 6.55:1 with white |
| `--rcj-lavender-text` | `#3b4f91` | Link hover, current menu item | 7.74:1 on white, 6.77:1 on grey |
| `--rcj-lavender` | `#5d71b3` | Borders, large text and decoration **only** | 4.69:1 on white (too faint on grey) |
| `--rcj-muted` | `#4f5968` | Secondary text: dates, sources, captions, intros | 7.1:1 on white |
| `--rcj-surface` | `#f3f7f5` | Page background, light bands | – |
| `--rcj-surface-2` | `#eef0f2` | Chips, meta tags, table stripes | – |
| `--rcj-border` | `#dcdfe3` | Card and divider borders | – |
| `--rcj-white` | `#ffffff` | Cards, white bands, text on navy/pink | – |

Rules:

- **Text on navy is white**, with 88–92% opacity for secondary text.
- **Pink on navy is 3.42:1**: use it only for large text or decoration, never
  for body-size text on navy.
- **Text over photos** must sit on a solid or near-solid navy layer (at least
  `rgba(0,18,66,.85)` behind the text), never on the bare photo.
- **One colour per heading.** Don't split a heading into two colours.

Avoid:

- `#000`, `#00001a`, `#444`, `#555`, `#6678b7`, other pinks (`#c50051`,
  `#e51671` …) or greys (`#eee`, `#f0f0f0` …). Use the nearest token.
- `opacity` to make text lighter (the related-post dates dropped to 3.5:1).
  Use `--rcj-muted` instead.
- Lavender `#5d71b3` text on grey backgrounds (4.0–4.2:1, fails).

## 3. Typography

| Role | Font | Weight | Size |
|------|------|--------|------|
| Headings | Poppins | 700–800 | h1 `clamp(2.25rem, 6vw, 3.75rem)` on the homepage; theme sizes elsewhere |
| Body | Source Sans Pro | 400 | 17px (1.0625rem), line-height 1.6 |
| Small text | Source Sans Pro | 400 | Not below 15px (0.9375rem) |
| Buttons | Source Sans Pro | 700 | 16px; theme block buttons are uppercase |

- Fonts are **self-hosted** (`static/fonts/`, Latin and Latin Extended).
  Don't add Google Fonts or other font CDNs. They send visitor data to a third
  party and break the offline build.
- Available weights: Source Sans Pro 300, 400, 600, 700, 900; Poppins 400,
  700, 800. Using another weight makes the browser fake it.
- Body text is left-aligned. **Don't justify text** (it leaves large gaps on
  phones).
- Keep line length readable: at most about 75 characters (`max-width: 62ch`
  for intro paragraphs).
- Use `clamp()` for large headings, with a minimum that fits a 320px screen.
  The old homepage heading had a 2.4rem floor and was cut off ("RoboCupJunio…").

## 4. Layout and spacing

- **Content width:** 1200px column on the homepage (`.rcjh-inner`); the theme
  container (max 1440px) on other pages.
- **Gutters:** 24px, and 16px below 600px.
- **Section spacing:** 64px between homepage bands (48px on phones); 32px under
  a section heading; 24px between cards.
- **Breakpoints** (use these, not new ones):

  | Width | What changes |
  |-------|--------------|
  | ≤ 600px | Single column; buttons full width; 16px gutters |
  | ≤ 800px | Theme mobile layout; homepage news becomes a list |
  | ≤ 1024px | Sidebar hidden; 4-column grids become 2 |
  | ≤ 1100px | Menu collapses to the mobile (hamburger) menu |
  | 1101–1439px | Menu items get tighter padding to fit one row |
  | > 1152px | The menu bar is fixed (75px); offset content below it |

- **No horizontal scrolling at any width from 320px.** Wide tables go inside
  `figure.wp-block-table`, which scrolls on its own.
- **Bands alternate** on the homepage (white, light, navy) so each section is
  clearly separate.

Avoid:

- Fixed `nowrap` rows of people or images; let them wrap on phones.
- Placing absolutely positioned or `visibility:hidden` dropdowns past the
  right edge (this caused sideways scroll at 1024px). The last two menus open
  leftwards.

## 5. Components

### Buttons

| Kind | Look | Where |
|------|------|-------|
| Block button (default) | Charcoal `--rcj-ink` fill, white uppercase text | Rows of actions in page content (`wp-button` shortcode) |
| Block button, accent | Pink fill, white text | The main action of a section (`accent="true"`) |
| Homepage primary | Pink pill, white text | Hero and closing actions |
| Homepage ghost | White outline pill on navy | Secondary action on navy |
| Homepage dark / outline | Navy pill / navy outline pill | Actions on light backgrounds |

- **Hover and focus:** block buttons turn navy with white text. Homepage
  buttons darken (pink → pink-dark) or invert (outline → filled).
- **Lock the text colour** (`color: … !important`) in every state. The theme
  recolours link text on hover, which made button text disappear on the live
  site.
- At least **44 × 44px** tap target (homepage pills are 48px tall).
- Up to three buttons in a row. On phones they stack, full width.

Avoid:

- `color: inherit` or `background-color: inherit` on button hover. Buttons
  took on the surrounding colours and their text vanished.
- Leaving out the text colour on a new button style. Links are pink, so a pink
  button with no text colour is pink-on-pink (39 buttons were invisible).

### Links

- Body links are pink and underlined; hover is `--rcj-lavender-text`.
- To open a link in a new tab on a legacy page, use the `"newtab"` link title
  (see README). Other pages don't support it yet.
- Never use a `javascript:` URL. Remote data (the resource finder) only allows
  `https:`, site paths and `#anchors`.

### Focus

- Every interactive element shows `outline: 3px solid var(--rcj-pink)` with a
  2–3px offset (white on navy and photo backgrounds).
- Never set `outline: 0` without a visible replacement.

### Page banner

- Every page except the homepage has **one `h1`**: the banner title. It comes
  from front matter `banner_title` (or the page `title`), and category pages
  show "Category: …".
- Pages with `banner_image` show the photo behind a dark title box; pages
  without one get a plain navy banner. Never leave a page without a visible
  title.
- The site name in the header is not a heading.

### Cards

- White background, 1px `--rcj-border`, 12px radius, 20–24px padding.
- **Text sits on the card, not on the photo.** Images go on top at a fixed
  ratio (3:2 leagues, 16:9 or 16:7 news) with `object-fit: cover`.
- The whole card may be one link; the title is the link text and decorative
  "Read more →" text is `aria-hidden`.
- Hover: soft shadow `0 8px 24px rgba(0,18,66,.12)` and a pink title. No
  scaling or jumping on hover.
- Journey steps are numbered 1–4 in navy circles and use an ordered list.

### News

- Homepage: the six newest **news** posts as compact cards (thumbnail 16:7,
  date, title). Below 800px they become a list with 96px square thumbnails.
- Archive pages (`/category/…`): one card per row with a 240px thumbnail,
  date, title and excerpt in a 960px column; below 800px the same 96px list.
- **Single posts:** the featured photo as a banner with the title on a solid
  navy panel (pink left edge); posts without a photo get a plain navy banner.
  Under it, a meta row (author, date, category chips: navy on
  `--rcj-surface-2`, white on navy on hover). Post text sits in a 52rem (18px)
  reading column. "Related posts" shows 3 compact cards, like homepage news.
- **Pagination:** dark "Newer posts" / "Older posts" buttons with "Page x of y".

Avoid:

- Full-width or square-cropped news images. They pushed real content far
  down the page, and many featured images are logos that crop badly.

### Menus

- The **only** place to edit the menu is `[[menus.main]]` in `hugo.toml`.
  Desktop and mobile menus are both generated from it.
- Each dropdown toggle is labelled "<Menu name> submenu". Escape closes menus
  and returns focus to the toggle.
- The current page is marked with `aria-current="page"` (only the deepest
  matching item).

### Embeds

- YouTube: use the `wp-youtube` shortcode (privacy-enhanced
  `youtube-nocookie.com`, lazy-loaded, 16:9).
- Every `iframe` needs a `title` describing its content.

## 6. Images

- **Size before uploading:** no wider than 1600px for page images, 600px for
  headshots, and 512px for post thumbnails. Aim for under 300 KB per image
  (JPEG quality around 82). Photos are JPEG; logos and graphics are PNG or SVG.
- Always include `width` and `height` (or a fixed `aspect-ratio`) so the page
  doesn't jump while loading. Use `loading="lazy"` for everything below the
  first screen.
- **Alt text:** describe what matters ("Students preparing a Rescue robot").
  Use `alt=""` when the image is decorative or repeats nearby text (league
  card photos, news thumbnails, the banner photo).
- Images of text (posters, flyers) need the important text written on the
  page too.
- Featured images for posts are also used for link previews (Open Graph).
  Choose ones that read well at 1200 × 630.

Avoid:

- 2–4 MB originals shown at 250px (the Community page loaded 14 MB).
- Small images stretched to full width (300px thumbnails were shown at
  1219px).

## 7. Accessibility checklist

Before publishing a page or template change, check:

- [ ] One `h1`; headings go in order (h2 → h3, no skipping).
- [ ] All text passes contrast, including hover, focus and visited states.
- [ ] Everything works with the keyboard alone, with a visible focus ring.
- [ ] No horizontal scroll at 320, 375, 768, 1024 and 1440px.
- [ ] Images have suitable alt text; iframes have titles.
- [ ] Links make sense out of context.
- [ ] Nothing important depends on animation; `prefers-reduced-motion` turns
      animation off. (The theme fades titles in from opacity 0, and
      rcj-site.css makes sure they still show.)

## 8. Writing CSS and templates

- Where styles go:
  - site-wide: `rcj-site.css`, under the matching numbered section
  - homepage: `home.css`
  - a group of pages: `assets/css/sections/<name>.css`, loaded by front
    matter `"section_css": "<name>"` (e.g. the six Getting Started pages use
    `getting-started`)
  - one page: `assets/css/pages/<content file name>.css`, loaded
    automatically (e.g. `pages/history.css` for `content/history.md`)
  - a component used across sections: keep its CSS with the shortcode that
    uses it (`league-intro` loads `league.css`; `werob-intro` loads
    `werob.css`)
  Don't add inline `<style>` blocks to content.
- `hugo server` only notices a newly created stylesheet after a restart.
- Section shortcodes are prefixed by section: `about-`, `league-`, `gs-`,
  `rules-`, `werob-`. Reuse them before writing new ones.
- Use **slash-star comments only**. A `//` comment silently drops the next
  rule, and a `*/` inside a comment ends it early (both happened here).
- When overriding the theme, prefer `:not()` and an extra class over
  `!important`. Use `!important` only to lock text colours against the
  theme's hover rules.
- Template data must not assume a fixed count: use `range`, not
  `index … 0`, so editors can add or remove items safely.
- Asset URLs in CSS must be relative (`../fonts/…`) so the site also works
  under the GitHub Pages sub-path.

## 9. Checks to run

```sh
hugo server                              # preview at http://localhost:1313
python3 -m unittest discover -s tests    # template and build tests (CI runs these too)
```

Use Hugo 0.169.0 extended, the version CI uses.

CI rebuilds every 6 hours. If a forum feed or the RoboCup events page can't be
reached, the build log shows a `WARN` and the page uses the saved copy in
`data/`.
