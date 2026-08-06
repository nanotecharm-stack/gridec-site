# 003 — Open the section index without animating max-height

- **Status**: TODO
- **Commit**: 5dfb3ca
- **Severity**: MEDIUM
- **Category**: Performance (5)
- **Estimated scope**: 1 file, two CSS rules

## Problem

The section index — the panel behind the `01 / 08` button in the header, and the only
navigation the chosen `chips` header variant offers — opens by animating `max-height`:

```css
/* powertech-v2-build/shell.html:110-113 — current */
/* motion: a sheet sliding out from under the bar, nothing bouncing */
.ixp{max-height:0;transition:max-height .34s var(--e);}
.ixp.on{max-height:70svh;overflow-y:auto;}
@media (prefers-reduced-motion:reduce){.ixp{transition:none;}}
```

`max-height` is a layout property: every frame of that 340 ms triggers layout, paint and
composite for the panel and everything it affects, instead of a composited transform.
On a page that also runs a rAF scroll loop and a canvas field, that is avoidable main-
thread work on the one control a visitor uses to move around the page.

There is a second, subtler cost: because the animation runs to a fixed `70svh` ceiling
rather than to the content's height, the panel's motion speed depends on how much
shorter than `70svh` the list actually is. With eight sections the list is well under
that ceiling, so the visible part of the animation finishes early and the remaining
duration is spent animating empty space that is already invisible. The panel therefore
appears to open faster than 340 ms and then sit still — the curve the author wrote is
not the curve the visitor sees.

## Target

Animate `grid-template-rows` between `0fr` and `1fr` on a grid wrapper, which the
browser can interpolate without a hard-coded ceiling, and keep the height driven by the
content. `grid-template-rows` is still a layout property, but it removes the fixed
ceiling and the dead tail of the current curve, and it is the standard technique when
the open height is unknown.

```css
/* target */
.ixp{display:grid;grid-template-rows:0fr;transition:grid-template-rows .34s var(--e);}
.ixp.on{grid-template-rows:1fr;}
.ixp>*{min-height:0;overflow:hidden;}
.ixp.on>*{overflow-y:auto;max-height:70svh;}
@media (prefers-reduced-motion:reduce){.ixp{transition:none;}}
```

If the executor finds that `grid-template-rows` interpolation is not acceptable here for
a reason visible in the markup (for example `.ixp` already being a grid with several
tracks, or its child count varying), the fallback target is a composited reveal instead:

```css
/* fallback target */
.ixp{clip-path:inset(0 0 100% 0);transition:clip-path .34s var(--e);max-height:70svh;overflow-y:auto;}
.ixp.on{clip-path:inset(0 0 0 0);}
```

`clip-path` is composited and needs no height maths, at the cost of the panel occupying
its full height in layout while closed — which is only acceptable if `.ixp` is
absolutely positioned. Check that before choosing the fallback.

## Repo conventions to follow

- One easing token: `--e:cubic-bezier(.16,1,.3,1)` at `powertech-v2-build/shell.html:3`.
  Keep `var(--e)` and keep the duration at `.34s` — it is within the dropdown budget
  (150-250 ms) only loosely, but it is the author's deliberate "sheet sliding out from
  under the bar" pacing and this plan does not re-time it.
- The reduced-motion guard at `shell.html:113` already exists for this element and must
  survive whichever target is chosen.
- All CSS is inline in the single `<style>` block of `shell.html`.

## Steps

1. Read the markup for `.ixp` — search `shell.html` for `id="ixp"` — and record whether
   it is absolutely positioned, how many direct children it has, and whether it is
   already a grid or flex container. Write that down in the hand-off.
2. If `.ixp` has a single element child and is not already a multi-track grid, apply the
   primary target: replace lines 111-112 with the four rules in the Target section
   (`.ixp`, `.ixp.on`, `.ixp>*`, `.ixp.on>*`).
3. If step 1 showed it is absolutely positioned and the grid approach conflicts with its
   existing layout, apply the fallback target instead and say so in the hand-off.
4. Leave the reduced-motion rule on line 113 in place, unmodified.
5. Confirm the panel still scrolls internally when the list is taller than the viewport:
   the `overflow-y:auto` and `70svh` ceiling must end up on whichever element actually
   holds the list.

## Boundaries

- Do NOT change the duration (`.34s`) or the easing.
- Do NOT touch the index's JavaScript: `ixOpen`, `ixSpy`, `ixItems`, or the click and
  Escape handlers (`shell.html` around `:1990-2010`).
- Do NOT change the `70svh` ceiling value.
- Do NOT alter the markup structure unless step 2 requires adding no elements — this
  plan adds CSS only. If the primary target needs a new wrapper element, STOP and report
  instead of adding one.
- If lines 111-112 no longer read as quoted, STOP and report drift since commit 5dfb3ca.

## Verification

- **Mechanical**: `grep -n "transition:max-height" powertech-v2-build/shell.html`
  returns nothing.
- **Feel check**: serve the build (`python .claude/serve-v2build.py`, then
  `http://localhost:8766/pt-gridec.html`) and click the `01 / 08` control in the header:
  - The panel opens to the height of its eight rows, with no dead pause at the end of
    the motion. Before the fix the visible part finishes early.
  - Click it again: it closes over the same duration, and clicking rapidly retargets
    from wherever it is rather than jumping (CSS transitions retarget; confirm by
    clicking twice within 150 ms).
  - Press Escape while open: it closes (handler must be untouched).
  - In DevTools Performance, record one open: the frames should show no layout work for
    the page body outside the panel itself.
  - Toggle `prefers-reduced-motion: reduce` in the Rendering panel: the panel appears
    and disappears instantly, with no movement, and remains usable.
- **Done when**: the panel's open height follows its content, no `max-height` transition
  remains, the eight links are all reachable and the internal scroll still works when the
  window is short (test at 500 px viewport height).
