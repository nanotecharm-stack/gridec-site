# 002 — Name the properties on the language switch instead of transitioning all

- **Status**: TODO
- **Commit**: 5dfb3ca
- **Severity**: MEDIUM
- **Category**: Performance (5)
- **Estimated scope**: 1 file, one declaration

## Problem

The language switch in the header declares a transition with no property list:

```css
/* powertech-v2-build/shell.html:238-240 — current */
.lang{font-family:%%MONOFONT%%;font-size:12px;letter-spacing:.12em;padding:9px 12px;
border-radius:2px;color:rgba(13,14,19,.82);box-shadow:inset 0 0 0 1px rgba(13,14,19,.12);
background:rgba(252,251,250,.9);-webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px);transition:.4s var(--e);}
```

`transition:.4s var(--e)` omits `transition-property`, which defaults to `all`. Every
animatable property on the element is therefore transitioned, including
`backdrop-filter: blur(14px)` — a compositing-expensive property that this element is
not trying to animate at all. The element's own hover rule changes only two things:

```css
/* powertech-v2-build/shell.html:241 — current */
.lang:hover{color:#0D0E13;box-shadow:inset 0 0 0 1px rgba(13,14,19,.26);}
```

and a separate rule adds a press transform:

```css
/* powertech-v2-build/shell.html:254-255 — current */
.lang:active,.alink:active,nav a:active,.md .x:active,.ic-go:active{transform:translateY(1px);}
.lang,.md .x{transition:transform .16s var(--e),background .35s var(--e),color .35s var(--e);}
```

Line 255 already declares a correct, named transition for `.lang`. Because it comes
later in the stylesheet with equal specificity, it currently wins for `transform`,
`background` and `color` — but line 240's `all` still governs every other property,
`backdrop-filter` among them. Two competing transition declarations on one element is
also a maintenance trap: whichever moves first silently changes behaviour.

Additionally the header changes tone on dark sections, and `.lang` colour is part of
that: `powertech-v2-build/shell.html:149` (`[data-tone="ink"] .lang{color:…}`). A blur
transition firing on every tone change is work for nothing.

## Target

Line 240 names its properties, and the duration matches the values already used on line
255 so the two declarations agree instead of competing:

```css
/* target — powertech-v2-build/shell.html:240 */
background:rgba(252,251,250,.9);-webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px);
transition:color .35s var(--e),box-shadow .35s var(--e),background .35s var(--e);
```

`transform` is deliberately absent here: line 255 owns it at 160 ms, which is the press
feedback budget (100-160 ms) and must not be lengthened to 350 ms.

`backdrop-filter` is absent, so the blur is applied once and never interpolated.

## Repo conventions to follow

- One easing token: `--e:cubic-bezier(.16,1,.3,1)`, declared at
  `powertech-v2-build/shell.html:3`. Always `var(--e)`.
- Named-property transitions are the norm in this file. Exemplar to imitate:
  `powertech-v2-build/shell.html:255` — `transition:transform .16s var(--e),background .35s var(--e),color .35s var(--e);`
- `.35s` is the established hover duration for header controls
  (`shell.html:55`, `:90`, `:255` all use it). Keep it.

## Steps

1. In `powertech-v2-build/shell.html:240`, replace `transition:.4s var(--e);` with
   `transition:color .35s var(--e),box-shadow .35s var(--e),background .35s var(--e);`.
2. Leave `shell.html:255` exactly as it is. It supplies the 160 ms `transform` for the
   press state, and duplicating `transform` in step 1 would override it with 350 ms.
3. Grep the file for any other transition shorthand with no property name:
   `grep -n "transition:\s*\.\?[0-9]" powertech-v2-build/shell.html`. Report anything
   found; do not fix additional occurrences under this plan.

## Boundaries

- Do NOT touch `shell.html:255` or the `:active` rule on `:254`.
- Do NOT remove `backdrop-filter` itself — the frosted look is intended, only its
  transition is not.
- Do NOT change the duration on any other rule, even if it looks inconsistent.
- Do NOT add dependencies.
- If line 240 no longer contains `transition:.4s var(--e)`, STOP and report drift since
  commit 5dfb3ca.

## Verification

- **Mechanical**: `grep -n "transition:.4s" powertech-v2-build/shell.html` returns
  nothing.
- **Feel check**: serve the build (`python .claude/serve-v2build.py`, then
  `http://localhost:8766/pt-gridec.html`):
  - Hover the `HY` control in the header: the outline and text colour still fade in over
    about a third of a second, unchanged to the eye.
  - Press and hold it: it still drops 1 px quickly, not slowly. If the press feels
    lazy, step 2 was violated and `transform` got the 350 ms duration.
  - Scroll so the header passes over a dark section: the tone change must not make the
    frosted background visibly re-blur or flicker.
  - In DevTools Performance, record a hover and confirm no `backdrop-filter` entry
    appears in the transition list for `.lang`.
- **Done when**: the only properties transitioning on `.lang` are `color`, `box-shadow`,
  `background` (350 ms) and `transform` (160 ms), and the element looks identical to
  before at normal speed.
