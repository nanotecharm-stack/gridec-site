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

Four outputs:

| file | what it is |
|---|---|
| `pt-en.html`, `pt-hy.html` | standalone, fonts and images inlined as base64. For local preview. |
| `../assets/v2/index.html`, `../assets/v2/hy.html` | the deploy pair, assets by relative URL, `noindex` |

`build.py` expects to sit one level below the site repo, so the deploy paths resolve
to `<site repo>/v2/`. In this session that repo was a git worktree of
`nanotecharm-stack/powertech-site` pinned to `origin/main`, checked out at
`<scratchpad>/assets`. Recreate it, or point the two output paths at wherever the
repo is.

## Deploy

Commit the two files under `v2/` in the site repo and push to `main`. GitHub Pages
serves them at `https://powertech.am/v2/` and `/v2/hy.html`.

Two things bit us repeatedly:

* **The Pages deploy can hang and then block every later push** ("Deployment request
  failed ... due to in progress deployment"). Cancel it and push again:
  `POST /repos/nanotecharm-stack/powertech-site/pages/deployments/<sha>/cancel`.
* **The browser caches `/v2/` hard.** Append any query string to see a fresh deploy.

## Before this goes anywhere near the live site

* The review switcher (bottom left, `BAR` and `LOGO` rows) is scaffolding. Delete
  `#navsw`, its CSS and its bootstrap once the variants are decided.
* `?hero=terracotta` and `?scroll=native` are comparison switches. Same treatment.
* The live pages at the repo root are untouched by all of this.
