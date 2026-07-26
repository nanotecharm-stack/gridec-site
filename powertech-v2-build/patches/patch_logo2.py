# -*- coding: utf-8 -*-
"""Two fixes and two new marks.

The screenshot over the pixel band shows the real failure: a paper chip carrying a
coral tile, sitting on a dark ground like a sticker. Two causes, both addressed:

  1  the lockup itself is two-tone and tile-filled, so it can never inherit a ground;
     the header now drops the two-tone in EVERY treatment.
  2  the titleblock strip and the chips were paper regardless of what is behind them;
     they now follow the same tone tag the rail already used, so over an ink section
     the plate is ink and its content milk.

And two marks drawn for single-colour use, since the current one was not:

  4  sag      a level line with one clean dip. It is the thing the company measures,
              it survives at 16px, and it rhymes with the chart in the contact plate.
  5  octagon  the hero's own figure reduced to a mark: eight sides, one centre node.
"""
import io

s = io.open('shell.html', encoding='utf-8').read()

# ---------------------------------------------------------------- the two new marks
old_brand = '</svg><span class="wm">Power<i>Tech</i></span></a>'
new_brand = ('</svg>'
             '<svg class="mark mark-sag" viewBox="0 0 40 40" fill="none" role="img" aria-label="PowerTech">'
             '<path d="M3 15 H14 V27 H26 V15 H37" stroke="currentColor" stroke-width="3.2" '
             'stroke-linecap="square" stroke-linejoin="miter" fill="none"/></svg>'
             '<svg class="mark mark-oct" viewBox="0 0 40 40" fill="none" role="img" aria-label="PowerTech">'
             '<path d="M14 4 H26 L36 14 V26 L26 36 H14 L4 26 V14 Z" stroke="currentColor" '
             'stroke-width="2.6" fill="none"/><rect x="17" y="17" width="6" height="6" fill="currentColor"/>'
             '</svg>'
             '<span class="wm">Power<i>Tech</i></span></a>')
assert old_brand in s
s = s.replace(old_brand, new_brand)

# ---------------------------------------------------------------- treatments
old_css = """html[data-logo] .brand .wm i{color:inherit;}"""
new_css = """/* the header never carries the two-tone word: one colour, whatever the ground */
.brand .wm i{color:inherit;}
.mark-sag,.mark-oct{display:none;}
html[data-logo="4"] .mark{display:none;} html[data-logo="4"] .mark-sag{display:block;}
html[data-logo="5"] .mark{display:none;} html[data-logo="5"] .mark-oct{display:block;}
html[data-logo="0"] .brand .wm i{color:var(--brand-ink);}   /* only the as-built comparison */"""
assert old_css in s
s = s.replace(old_css, new_css)

# ---------------------------------------------------------------- tone-aware plates
anchor = "/* ---- 3 instrument chips"
assert anchor in s
TONE = """/* the titleblock and the chips follow the ground as well: a paper plate on a dark
   band reads as a sticker, which is exactly what the review shot showed */
html[data-nav="1"] header[data-tone="ink"]{background:#14161C;box-shadow:0 1px 0 rgba(239,237,234,.18);}
html[data-nav="1"] header[data-tone="ink"] .brand,
html[data-nav="1"] header[data-tone="ink"] .ixb,
html[data-nav="1"] header[data-tone="ink"] .lang{color:#EFEDEA;}
html[data-nav="1"] header[data-tone="ink"] .ixb::before{background:rgba(239,237,234,.3);}
html[data-nav="1"] header[data-tone="ink"] .btn{background:#EFEDEA;color:#0D0E13;}
html[data-nav="1"] header[data-tone="ink"] .btn::before{background:#0D0E13;}
html[data-nav="1"] header[data-tone="ink"] .btn:hover span{color:#EFEDEA;}
html[data-nav="1"] header[data-tone="ink"] .btn i{background:rgba(13,14,19,.14);}
html[data-nav="3"] header[data-tone="ink"] .brand,
html[data-nav="3"] header[data-tone="ink"] .navr{background:#14161C;
  box-shadow:inset 0 0 0 1px rgba(239,237,234,.2);}
html[data-nav="3"] header[data-tone="ink"] .brand,
html[data-nav="3"] header[data-tone="ink"] .ixb,
html[data-nav="3"] header[data-tone="ink"] .lang{color:#EFEDEA;}
html[data-nav="3"] header[data-tone="ink"] .lang::before{background:rgba(239,237,234,.18);}
html[data-nav="3"] header[data-tone="ink"] .btn{background:#EFEDEA;color:#0D0E13;}
html[data-nav="3"] header[data-tone="ink"] .btn::before{background:#0D0E13;}
html[data-nav="3"] header[data-tone="ink"] .btn:hover span{color:#EFEDEA;}
html[data-nav="3"] header[data-tone="ink"] .btn i{background:rgba(13,14,19,.14);}
html[data-nav="1"] header,html[data-nav="1"] .btn,html[data-nav="3"] .brand,
html[data-nav="3"] .navr,html[data-nav="3"] .btn{
  transition:background .45s var(--e),color .45s var(--e),box-shadow .45s var(--e);}

""" + anchor
s = s.replace(anchor, TONE, 1)

# ---------------------------------------------------------------- switcher row
s = s.replace("var LOGOV=['0','1','2','3'],logoLabels=['as built','contour','wordmark','knockout'];",
              "var LOGOV=['0','1','2','3','4','5'],"
              "logoLabels=['as built','contour','wordmark','knockout','sag','octagon'];")

io.open('shell.html', 'w', encoding='utf-8').write(s)

print('new marks in the lockup :', s.count('mark-sag') and s.count('mark-oct'))
print('two-tone off by default :', ".brand .wm i{color:inherit;}" in s)
print('tone-aware titleblock   :', 'html[data-nav="1"] header[data-tone="ink"]{background:#14161C' in s)
print('tone-aware chips        :', 'html[data-nav="3"] header[data-tone="ink"] .navr{background:#14161C' in s)
print('switcher options        :', "'sag','octagon'" in s)
