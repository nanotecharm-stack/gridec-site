# 001 — Scope the card photo's 1.15s transform transition to hover only

- **Status**: TODO
- **Commit**: 5dfb3ca
- **Severity**: HIGH
- **Category**: Performance (5)
- **Estimated scope**: 1 file, one CSS rule split in two

## Problem

The industry-card photograph carries a 1.15 second transition on `transform`:

```css
/* powertech-v2-build/shell.html:433-436 — current */
.ic-art img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block;
transform:scale(1.04);transform-origin:52% 45%;
transition:transform 1.15s cubic-bezier(.16,1,.3,1),filter .7s var(--e);
filter:saturate(.85) contrast(1.03);}
```

The horizontal industries rail writes that same property on that same element **on
every animation frame** while the section is pinned:

```js
/* powertech-v2-build/shell.html:1687-1689 — current */
    var im=shells[i].querySelector('.ic-art img');
    if(im){var rel=(centre-SX.focus)/SX.focus;
      im.style.transform='scale(1.06) translateX('+Math.round(-rel*12)+'px)';}
```

A CSS transition retargets from the current computed value whenever the property
changes. Rewriting `transform` every frame against a 1150 ms curve means the browser
is permanently interpolating toward a target it is given a new version of 16 ms later:
the parallax offset lags roughly a second behind the scroll position and never
arrives. The intended effect — the photograph shifting slightly as its card passes the
focus point — is smeared into a slow drift that reads as sluggishness, and every frame
of the pinned scroll pays for an interpolation that is thrown away.

The 1.15 s curve is correct for what it was written for: the slow zoom when a card is
hovered. It only has to stop applying to the scroll-driven writes.

## Target

The base rule carries no transform transition. The long curve moves to a hover-scoped
rule, so the per-frame writes land immediately and the hover zoom keeps its character:

```css
/* target */
.ic-art img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block;
transform:scale(1.04);transform-origin:52% 45%;
transition:filter .7s var(--e);
filter:saturate(.85) contrast(1.03);}

@media (hover:hover) and (pointer:fine){
  .ic:hover .ic-art img{transition:transform 1.15s cubic-bezier(.16,1,.3,1),filter .7s var(--e);}
}
```

`filter` keeps its own transition on the base rule: nothing writes `filter` per frame,
so it is unaffected by this problem.

The hover rule is wrapped in `@media (hover:hover) and (pointer:fine)` because touch
devices fire a false hover on tap, which would re-introduce the 1.15 s transition on
exactly the devices where the rail runs as a native scroll list.

## Repo conventions to follow

- There is exactly one easing token, declared at `powertech-v2-build/shell.html:3`:
  `--e:cubic-bezier(.16,1,.3,1)`. Use `var(--e)` for new declarations. The existing
  rule spells the same curve out literally on line 435; keep it spelled out there so
  the diff stays minimal, or switch it to `var(--e)` — both are acceptable.
- Hover motion is already gated on pointer capability elsewhere in this file. Exemplar:
  `powertech-v2-build/shell.html:390` region, `@media (max-width:980px),(hover:none),(pointer:coarse){ … }`,
  which turns the pinned rail into a native scroll list on touch.
- All CSS lives inline in the single `<style>` block of `shell.html`. Do not create new
  files.

## Steps

1. In `powertech-v2-build/shell.html`, edit the `.ic-art img` rule (lines 433-436):
   change `transition:transform 1.15s cubic-bezier(.16,1,.3,1),filter .7s var(--e);`
   to `transition:filter .7s var(--e);`. Leave every other declaration in that rule
   untouched.
2. Immediately after that rule, add:
   ```css
   /* The rail rewrites this transform every frame while the section is pinned; a long
      transition there would interpolate toward a target that changes each frame and
      the parallax would lag about a second behind the scroll. The slow zoom belongs to
      hover only. */
   @media (hover:hover) and (pointer:fine){
     .ic:hover .ic-art img{transition:transform 1.15s var(--e),filter .7s var(--e);}
   }
   ```
3. Do not touch `sxRender` (around `shell.html:1680-1690`). The JS is correct; only the
   CSS was fighting it.

## Boundaries

- Do NOT touch the rail's JavaScript (`SX`, `sxRender`, `suiteUpd`, `layoutSuite`).
- Do NOT touch `.icard`, `.ic`, `.ic-art` or `.ic-art::after` — the photograph's `img`
  rule and the new hover rule only.
- Do NOT change the scale values (`1.04` base, `1.06` in JS) or `transform-origin`.
- Do NOT add dependencies; there are none in this project.
- If line 435 no longer contains `transition:transform 1.15s`, STOP and report: the file
  has drifted since commit 5dfb3ca.

## Verification

- **Mechanical**: `python powertech-v2-build/logo_on_palettes.py` must complete and print
  four lines ending with `pt-gridec.html`. Note that this script patches already-built
  pages; it does not read `shell.html`, so it will NOT prove the change reached a page.
  To see the change in a built page you must also apply the same two-line CSS edit
  through that script's patch mechanism, or rebuild with `build.py` where the v2 font set
  is available. State clearly in the hand-off which of the two you did.
- **Feel check**: serve the build (`python .claude/serve-v2build.py`, then
  `http://localhost:8766/pt-gridec.html`) and scroll into the industries section:
  - While scrolling through the rail, each photograph's horizontal shift must track the
    scroll immediately. Before the fix it drifts on for about a second after you stop.
  - Stop mid-rail and hover a card: the photograph must still zoom slowly and smoothly
    over roughly a second.
  - In DevTools open the Animations panel, set playback to 10%, and scroll: no long
    transform interpolation should be listed for `.ic-art img` during scrolling.
  - Toggle `prefers-reduced-motion: reduce` in the Rendering panel: the rail stops
    transforming entirely (existing rule at `shell.html:393-396`), and no error appears.
- **Done when**: the photograph's parallax offset changes in the same frame as the
  scroll, the hover zoom is unchanged in duration and curve, and touch emulation
  (DevTools device mode) shows no transform transition on tap.
