# -*- coding: utf-8 -*-
"""Hero: a drawing sheet instead of a terracotta poster.

The brief asks for a light ground, graphite text and coral as an ACCENT; a
full-bleed terracotta first screen inverts that. So the panel becomes paper, the
string field is drawn in graphite hairlines, and terracotta is left to carry only
what means something: the emphasised word, the section mark, the travelling
light and the discharge. Nothing about the physics or the layout changes.

The old poster stays reachable at ?hero=terracotta for comparison.
"""
import io

s = io.open('shell.html', encoding='utf-8').read()

# ---------------------------------------------------------------- the panel
old = '.hero{position:relative;min-height:100svh;overflow:hidden;background:#C8603D;color:#FFFBF9;}'
new = ('/* a sheet, not a poster: paper that darkens a touch towards the fold, with the\n'
       '   faintest warm breath where the field lives on the right */\n'
       '.hero{position:relative;min-height:100svh;overflow:hidden;color:var(--fg);\n'
       '  background:linear-gradient(178deg,#F7F5F2 0%,#EFEDEA 58%,#E9E6E2 100%);}\n'
       '.hero::after{content:"";position:absolute;inset:0;pointer-events:none;z-index:1;\n'
       '  background:radial-gradient(58% 52% at 78% 46%,rgba(200,96,61,.055),transparent 70%);}')
assert old in s
s = s.replace(old, new)

# ---------------------------------------------------------------- type
pairs = [
    ('.hero h1{color:#FFFBF9;', '.hero h1{color:var(--fg);'),
    ('.hero h1 em{color:#2C1109;}', '.hero h1 em{color:var(--brand-ink);}'),
    ('color:rgba(255,251,249,.84);margin-top:30px;}', 'color:var(--fg-mid);margin-top:30px;}'),
    ('.hero .eyebrow{color:#2C1109;}', '.hero .eyebrow{color:var(--brand-ink);}'),
    ('.hero .eyebrow::before{background:#2C1109;}', '.hero .eyebrow::before{background:var(--brand-ink);}'),
]
for a, b in pairs:
    assert a in s, a
    s = s.replace(a, b)

# ---------------------------------------------------------------- buttons: the page's own pair
old_btn = """.hero .btn{background:#14161C;color:#fff;}
.hero .btn::before{background:#FFFBF9;}
.hero .btn:hover span{color:#14161C;}
.hero .btn i{background:rgba(255,255,255,.2);}
.hero .btn.gh{background:transparent;color:#FFFBF9;box-shadow:inset 0 0 0 1px rgba(255,251,249,.44);}"""
new_btn = """/* on paper the hero needs no special buttons — the page's own pair is right */"""
assert old_btn in s
s = s.replace(old_btn, new_btn)

# ---------------------------------------------------------------- the field's palette
old_stage = '  --wv-line:255,251,249;--wv-glow:255,255,255;}'
new_stage = ('  /* graphite hairlines; the light that travels them is the accent */\n'
             '  --wv-line:13,14,19;--wv-glow:200,96,61;}')
assert old_stage in s
s = s.replace(old_stage, new_stage)
# ink on paper needs a touch more weight than milk on terracotta, and the coral
# light has to read against it
s = s.replace("  line:.11,litHi:.30,core:.34,glide:.13,band:.30};",
              "  line:.15,litHi:.62,core:.34,glide:.13,band:.30};")

# ---------------------------------------------------------------- readouts
old_rd = """  font-family:%%MONOFONT%%;font-size:12px;color:rgba(255,251,249,.88);line-height:1.95;}
.rd b{color:#FFFBF9;font-variant-numeric:tabular-nums;font-weight:600;}
.rd .st{color:#2C1109;}"""
new_rd = """  font-family:%%MONOFONT%%;font-size:12px;color:var(--fg-soft);line-height:1.95;}
.rd b{color:var(--fg);font-variant-numeric:tabular-nums;font-weight:600;}
.rd .st{color:var(--brand-ink);}"""
assert old_rd in s
s = s.replace(old_rd, new_rd)

# ---------------------------------------------------------------- chrome + junction
s = s.replace("var darkSecs=[].slice.call(document.querySelectorAll('.hero,.plate2,.plate'));",
              "var darkSecs=[].slice.call(document.querySelectorAll('.plate2,.plate'));")
# the pixel band existed to cross a colour jump; paper meeting paper has none
old_band = '<div class="dith" data-dith="#C8603D,#EFEDEA,#E5825A"></div>\n'
assert old_band in s
s = s.replace(old_band, '')

# ---------------------------------------------------------------- keep the poster reachable
s = s.replace('.btn.gh{background:transparent;', """/* ?hero=terracotta restores the earlier poster, for comparison */
html[data-hero="terracotta"] .hero{background:#C8603D;color:#FFFBF9;}
html[data-hero="terracotta"] .hero::after{display:none;}
html[data-hero="terracotta"] .hero h1,html[data-hero="terracotta"] .rd b{color:#FFFBF9;}
html[data-hero="terracotta"] .hero h1 em,html[data-hero="terracotta"] .hero .eyebrow,
html[data-hero="terracotta"] .rd .st{color:#2C1109;}
html[data-hero="terracotta"] .hero .eyebrow::before{background:#2C1109;}
html[data-hero="terracotta"] .hero .hp{color:rgba(255,251,249,.88);}
html[data-hero="terracotta"] .rd{color:rgba(255,251,249,.88);}
html[data-hero="terracotta"] .hero .btn{background:#14161C;color:#fff;}
html[data-hero="terracotta"] .hero .btn::before{background:#FFFBF9;}
html[data-hero="terracotta"] .hero .btn:hover span{color:#14161C;}
html[data-hero="terracotta"] .hero .btn.gh{background:transparent;color:#FFFBF9;
  box-shadow:inset 0 0 0 1px rgba(255,251,249,.44);}
html[data-hero="terracotta"] .stage{--wv-line:255,251,249;--wv-glow:255,255,255;}
.btn.gh{background:transparent;""", 1)

# read the switch before the canvas reads its theme
old_boot = 'function readWaveTheme(){'
new_boot = """(function(){var m=/[?&]hero=([a-z]+)/.exec(location.search);
  if(m&&m[1]==='terracotta')document.documentElement.dataset.hero='terracotta';})();
function readWaveTheme(){"""
assert old_boot in s
s = s.replace(old_boot, new_boot, 1)

io.open('shell.html', 'w', encoding='utf-8').write(s)

print('paper panel      :', 'linear-gradient(178deg,#F7F5F2' in s)
print('field palette    :', '--wv-line:13,14,19' in s)
print('line weight      :', 'line:.15,litHi:.62' in s)
print('hero btn overrides removed:', '.hero .btn{background:#14161C' not in s)
print('header light over hero    :', "querySelectorAll('.plate2,.plate')" in s)
print('hero pixel band removed   :', '#C8603D,#EFEDEA,#E5825A' not in s)
print('poster fallback rules     :', s.count('html[data-hero="terracotta"]'))
