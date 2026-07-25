# -*- coding: utf-8 -*-
"""Findings from the redesign-skill audit, applied.

1 type scale: the label role carried four sizes inside 1.5px (9.5/10/10.5/11) and
  body copy seven inside 3px — collapsed to 10/11 for labels and 12/13.5/14/16 for text.
2 colour: the form's error red sat at 87% saturation, louder than the brand itself.
3 states: no pressed feedback anywhere, and the primary buttons had no transition.
4 motion: two hover transitions animated layout properties (padding-left, width).
5 alt text: the sector photos shipped alt="" though they carry content.
6 <main> was missing; one static inline font-size moved into a class.
"""
import io, re

s = io.open('shell.html', encoding='utf-8').read()

# ---------------------------------------------------------------- 1 type scale
STEPS = [('9.5px', '10px', 6), ('10.5px', '11px', 10), ('13px', '13.5px', 6),
         ('14.5px', '14px', 3), ('15px', '16px', 1), ('15.5px', '16px', 2),
         ('12.5px', '12px', 1)]
for old, new, n in STEPS:
    pat = 'font-size:' + old
    got = s.count(pat)
    assert got == n, 'expected %d of %s, found %d' % (n, pat, got)
    s = s.replace(pat, 'font-size:' + new)

# ---------------------------------------------------------------- 2 error colour
# a darker, redder signal: reads as a warning, cannot be mistaken for the brand
# NB the lowercase '#c5280d' is a stop in the logo gradient — untouched. The
# uppercase four are the error/destructive signals, which had borrowed the logo's
# darkest stop, so a failed field looked like branding.
assert s.count('#C5280D') == 4, s.count('#C5280D')
s = s.replace('#C5280D', '#A8341F')

# ---------------------------------------------------------------- 4 motion off layout props
old_list = """  border-bottom:1px solid var(--hair2);transition:padding-left .45s var(--e);}
.list div:hover{padding-left:8px;}"""
new_list = """  border-bottom:1px solid var(--hair2);transition:transform .45s var(--e);}
.list div:hover{transform:translateX(8px);}"""
assert old_list in s
s = s.replace(old_list, new_list)

old_asg = """.asg .card::before{content:"";position:absolute;top:-1px;left:0;width:44px;height:1px;background:var(--brand);
  transition:width .55s var(--e);}
.asg .card:hover::before{width:100%;}"""
new_asg = """.asg .card::before{content:"";position:absolute;top:-1px;left:0;width:100%;height:1px;background:var(--brand);
  transform:scaleX(.09);transform-origin:left;transition:transform .55s var(--e);}
.asg .card:hover::before{transform:scaleX(1);}"""
assert old_asg in s
s = s.replace(old_asg, new_asg)

# ---------------------------------------------------------------- 3 pressed feedback
anchor = '.btn.gh{background:transparent;'
assert anchor in s
s = s.replace(anchor, """/* the surface has to answer the press — nothing here had an :active state */
.btn{transition:transform .16s var(--e);}
.btn:active{transform:translateY(1px) scale(.995);}
.lang:active,.alink:active,nav a:active,.md .x:active,.ic-go:active{transform:translateY(1px);}
.lang,.md .x{transition:transform .16s var(--e),background .35s var(--e),color .35s var(--e);}
""" + anchor)

# ---------------------------------------------------------------- 5 alt text
old_img = """    ? '<img alt="" src="'+PT.imgs[o.img]+'">'"""
new_img = """    ? '<img alt="'+o.title+'" src="'+PT.imgs[o.img]+'">'"""
assert old_img in s
s = s.replace(old_img, new_img)

old_mod = """  if(o.img!==undefined&&PT.imgs[o.img]){img.src=PT.imgs[o.img];ph.style.display='';}"""
new_mod = """  if(o.img!==undefined&&PT.imgs[o.img]){img.src=PT.imgs[o.img];img.alt=o.title;ph.style.display='';}"""
assert old_mod in s
s = s.replace(old_mod, new_mod)

# ---------------------------------------------------------------- 6 <main> + inline style
assert s.count('</header>\n') == 1
s = s.replace('</header>\n', '</header>\n<main>\n', 1)
assert s.count('<footer>') == 1
s = s.replace('<footer>', '</main>\n<footer>', 1)

old_lede = '<div style="max-width:40ch"><p class="lede" style="margin-top:0;font-size:14px;line-height:1.65">'
if old_lede in s:
    s = s.replace(old_lede, '<div class="lede-w"><p class="lede lede-sm">')
    s = s.replace('.lede{max-width:46ch;',
                  '.lede-w{max-width:40ch;}\n.lede-sm{margin-top:0;font-size:14px;line-height:1.65;}\n'
                  '.lede{max-width:46ch;')

io.open('shell.html', 'w', encoding='utf-8').write(s)

sizes = sorted({float(x) for x in re.findall(r'font-size:([\d.]+)px', s)})
print('px steps now      :', sizes)
print('label tier        :', [x for x in sizes if x <= 12])
print('main wrapper      :', s.count('<main>'), s.count('</main>'))
print('layout transitions:', len(re.findall(r'transition:[^;]*(?:width|height|padding-left|top|left)[^;]*;', s)))
print('active rules      :', s.count(':active'))
print('alt on card img   :', "alt=\"'+o.title+'\"" in s)
print('error red         :', s.count('#A8341F'))
