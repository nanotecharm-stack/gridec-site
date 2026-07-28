# -*- coding: utf-8 -*-
"""Specimen sheet for MEAS_ICONS: every icon at its real 52x34 and enlarged, on the
light ground and on the graphite plate, in each palette. Reads the icon list straight
out of build.py so the sheet cannot drift from the build.

    python icons_sheet.py            -> icons-sheet.html next to this file
    OUT=/path/x.html python icons_sheet.py
"""
import io, re, os
HERE = os.path.dirname(os.path.abspath(__file__))
src = io.open(os.path.join(HERE, 'build.py'), encoding='utf-8').read()
m = re.search(r'MEAS_ICONS = \[(.*?)\n\]', src, re.S)
icons = eval('[' + m.group(1) + ']')
labels = ['Voltage & Current','Harmonics & Interharmonics','Flicker','Voltage Dips',
          'Unbalance','Power & Energy','Events','Risk Indicators']
def row(i, ic, lb):
    return ('<div class="cell%s"><span class="ix">%02d</span>'
            '<svg viewBox="0 0 44 30">%s</svg>'
            '<svg class="big" viewBox="0 0 44 30">%s</svg>'
            '<span class="lb">%s</span></div>' % (' alt' if i==7 else '', i+1, ic, ic, lb))
cells = ''.join(row(i, ic, labels[i]) for i, ic in enumerate(icons))
html = u"""<!doctype html><meta charset=utf-8><title>PowerTech · measurement icons</title>
<style>
*{box-sizing:border-box}
body{margin:0;font:14px/1.45 system-ui,sans-serif}
section{padding:34px 40px 46px}
h2{font:600 11px/1 system-ui;letter-spacing:.18em;text-transform:uppercase;margin:0 0 22px;opacity:.55}
.grid{display:grid;grid-template-columns:repeat(4,1fr);border-top:1px solid var(--hair)}
.cell{position:relative;padding:24px 22px 26px;border-left:1px solid var(--hair);
  display:flex;flex-direction:column;gap:14px}
.cell:nth-child(4n+1){border-left:none}
.cell:nth-child(n+5){border-top:1px solid var(--hair)}
.ix{position:absolute;top:24px;right:22px;font:10px/1 ui-monospace,monospace;letter-spacing:.14em;opacity:.5}
svg{width:52px;height:34px;display:block;overflow:visible;color:var(--fg)}
svg.big{width:156px;height:102px;opacity:.9}
.lb{font-size:14px}
.alt{border-left-style:dashed;background:var(--wash)}
.alt:nth-child(n+5){border-top-style:dashed}
.alt::before{content:"";position:absolute;top:0;left:0;width:26px;height:2px;background:var(--brand)}
.alt .ix{color:var(--brandink);opacity:1}
/* terracotta */
.t-light{--fg:#0D0E13;--brand:#C8603D;--brandink:#AC4A29;--hair:rgba(13,14,19,.13);--wash:rgba(200,96,61,.045);background:#EFEDEA;color:#0D0E13}
.t-dark{--fg:#EFEDEA;--brand:#C8603D;--brandink:#D4714E;--hair:rgba(239,237,234,.13);--wash:rgba(200,96,61,.09);background:linear-gradient(180deg,#0D0E13,#14161C);color:#EFEDEA}
/* mint */
.m-light{--fg:#25272C;--brand:#18624C;--brandink:#18624C;--hair:rgba(37,39,44,.13);--wash:rgba(24,98,76,.05);background:#F3F6F5;color:#25272C}
.m-dark{--fg:#F3F6F5;--brand:#B8F7E4;--brandink:#B8F7E4;--hair:rgba(243,246,245,.13);--wash:rgba(184,247,228,.07);background:linear-gradient(180deg,#25272C,#2E3138);color:#F3F6F5}
</style>
<section class="t-light"><h2>terracotta · light</h2><div class="grid">%(c)s</div></section>
<section class="t-dark"><h2>terracotta · graphite plate</h2><div class="grid">%(c)s</div></section>
<section class="m-light"><h2>mint · light</h2><div class="grid">%(c)s</div></section>
<section class="m-dark"><h2>mint · graphite plate</h2><div class="grid">%(c)s</div></section>
""" % {'c': cells}
out = os.environ.get('OUT') or os.path.join(HERE, 'icons-sheet.html')
io.open(out, 'w', encoding='utf-8').write(html)
print(out, len(icons), 'icons')
