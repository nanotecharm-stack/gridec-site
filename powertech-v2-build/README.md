# powertech.am /v2/ - build sources

The v2 preview is generated, not hand-edited. These are its sources, moved here out
of the session scratchpad so they survive.

## What builds what

```
shell.html      one template for both languages, %%TOKEN%% placeholders,
                all CSS and JS inline
build.py        the EN and HY content dictionaries plus the assembler
img/            source photography for the base64 (local preview) build
tfonts.json     what the Armenian type trial produced
fonts_try.py    the type-trial builder (download, subset, specimen pages)
patches/        every change applied to shell.html this session, one file each,
                each with its own assertions. History, not part of the build.
```

## Rebuild

```bash
python build.py
```

`build.py` reads the real fonts from the site repo and writes the deploy pages into it.
By default it expects that repo one level up under `assets/`; **`PT_SITE` points it
anywhere**, which is how you build against a worktree:

```bash
PT_SITE=/path/to/powertech-site-worktree python build.py
```

Outputs:

| file | what it is |
|---|---|
| `pt-en.html`, `pt-hy.html` | standalone, fonts and images inlined as base64. For local preview. |
| `pt-en-mint.html`, `pt-en-warm.html` | the same, in the two review palettes |
| `<site>/v2/index.html`, `<site>/v2/hy.html` | the deploy pair, assets by relative URL, `noindex` |
| `<site>/v2/mint.html`, `<site>/v2/warm.html` | the review palettes, same treatment |

## Palette variants

**Paused 2026-07-28: the company is being renamed, so the palette is not chosen yet.**
Three are ready to compare on identical markup; open the standalone builds side by side.

| | ground | plates | accent on light | accent on plates |
|---|---|---|---|---|
| as built | `#EFEDEA` warm milk | near-black `#0D0E13` | `#C8603D` / text `#AC4A29` | `#D4714E` |
| `warm` — quiet warm | `#F4F5F5` neutral | graphite `#25272C` | `#9D5B43` (4.79:1) | `#C8856A` (4.99:1) |
| `mint` — graphite + sky mint | `#F3F6F5` | graphite `#25272C` | `#18624C` (6.68:1) | `#B8F7E4` (12.43:1) |

A palette is a **post-pass over the finished page**, not a branch of the CSS: `PALETTES`
holds the target colours, `palette_map()` pairs them with the terracotta literals the
template actually contains, `PAL_CSS` adds the ground-aware `--brand` / `--brand-ink` /
`--brand-on` trio, and `palette_pass(name)` returns the function `render*()` applies.
Consequences worth keeping in mind:

* `index.html` and `hy.html` stay byte-identical to what is live — no variant can leak
  into the deployed pair.
* Adding a fourth palette is one dict entry plus two `render*` lines.
* The pass asserts that no terracotta literal survives, so a colour added to
  `shell.html` without a mapping fails the build instead of shipping half-converted.
* **Sky mint cannot be an accent on light paper (1.11:1).** That is why every palette
  declares two depths. If a variant ever needs one value for both grounds it has to sit
  between roughly L 0.16 and 0.27 — see the note in `build.py`.

## Icon specimen sheet

```bash
python icons_sheet.py
```

Writes `icons-sheet.html`: all eight `MEAS_ICONS` at their real 52×34 and enlarged, on
light and on graphite, in every palette. It parses the icon list out of `build.py`, so
the sheet cannot drift from the build. `OUT=<path>` puts it elsewhere.

## Deploy

Commit the two files under `v2/` in the site repo and push to `main`. GitHub Pages
serves them at `https://powertech.am/v2/` and `/v2/hy.html`.

Two things bit us repeatedly:

* **The Pages deploy can hang and then block every later push** ("Deployment request
  failed ... due to in progress deployment"). Cancel it and push again:
  `POST /repos/nanotecharm-stack/powertech-site/pages/deployments/<sha>/cancel`.
* **The browser caches `/v2/` hard.** Append any query string to see a fresh deploy.

## Before this goes anywhere near the live site

* **The company name is changing** (PowerTech failed a check). Nothing carrying the name
  — wordmark, `<title>`, metadata, the mark itself — is final until it lands. Order of
  decisions: name → palette → mark.
* The review switcher (bottom left, `BAR` and `LOGO` rows) is scaffolding. Delete
  `#navsw`, its CSS and its bootstrap once the variants are decided.
* `?hero=terracotta` and `?scroll=native` are comparison switches. Same treatment.
* The live pages at the repo root are untouched by all of this.
