# Animation plans — Gridec one-pager

Produced by `improve-animations` against `powertech-v2-build/shell.html` at commit
`5dfb3ca`. Each plan is self-contained: exact file, exact lines, exact curves and
durations. An executor needs nothing from the conversation that produced them.

| # | Plan | Severity | Category | Status |
|---|---|---|---|---|
| 001 | [Scope the card photo's 1.15s transform transition to hover only](001-scope-card-photo-transition-to-hover.md) | HIGH | Performance | TODO |
| 002 | [Name the properties on the language switch instead of transitioning all](002-replace-transition-all-on-lang-switch.md) | MEDIUM | Performance | TODO |
| 003 | [Open the section index without animating max-height](003-stop-animating-max-height-on-index-panel.md) | MEDIUM | Performance | TODO |

## Recommended order

**001 → 002 → 003.**

001 first: it is the only one that changes how the page *feels* rather than how it
performs. The industries rail currently writes `transform` on the card photograph every
frame while a 1150 ms transition on that same property is active, so the parallax lags
about a second behind the scroll. Fixing it is two lines and is visible immediately.

002 and 003 are independent of 001 and of each other; either order works. 002 is the
smaller of the two (one declaration) and is a good warm-up for the file.

## Dependencies

None between the three. They touch disjoint rules:

- 001 — `.ic-art img` (`shell.html:433-436`) plus one new hover rule
- 002 — `.lang` (`shell.html:240`)
- 003 — `.ixp` (`shell.html:111-112`)

## One thing every executor must know about this build

`shell.html` is a template, not a served page. `build.py` assembles the served pages from
it, but **`build.py` cannot run in this checkout**: it inlines the v2 fonts as base64
from `../assets/fonts/`, and that directory holds the live site's fonts, not the v2 set
(Big Shoulders, Archivo, Martian Mono, Arian AMU are absent). It expects a separate site
worktree pointed at by `PT_SITE`.

Consequence: editing `shell.html` alone will **not** change anything you can open in a
browser here. The served preview pages are produced by `logo_on_palettes.py`, which
patches the already-built `pt-en.html`. Any change that has to be visible before a real
rebuild must therefore be applied twice — once in `shell.html` (the durable fix) and once
as a patch in `logo_on_palettes.py` (so it reaches `pt-gridec.html`). Several existing
patches in that file are marked as exactly this kind of temporary duplicate.

State in your hand-off which of the two you did. A plan verified only against
`shell.html` has not been seen running.

## Findings that were audited and deliberately not planned

- **The custom eased scroll** (`shell.html:2100-2120`) — a rAF lerp loop replacing native
  scrolling, i.e. motion on the single most frequent interaction on the page. Left
  unplanned pending a check in a real browser window: do anchor links, Ctrl+F scrolling
  and PageDown still work? If they do, it is a taste question and the author's choice
  stands. If they do not, it outranks all three plans above.
- **`.rv` reveals at 900 ms with no stagger** (`shell.html:32`) — over the UI budget, but
  this is a marketing page where longer reveals are permitted, and the value is
  consistent across every section. A change here is a design decision, not a defect fix.
- **`prefers-reduced-motion` implemented as a total kill switch** (`shell.html:762`,
  `*{animation:none!important;transition:none!important}`) — the playbook asks for fewer
  and gentler motion rather than none, keeping opacity and colour feedback. Worth doing,
  but it touches every animated element on the page and belongs in its own pass.
- **`#wipe i{transform:scale(0)}`** (`shell.html:341`) — not a finding. The "never
  `scale(0)`" rule addresses interface elements appearing from nothing; this is a
  full-bleed circular page-transition wipe, the same class of exemption the playbook
  grants modals for `transform-origin: center`.
