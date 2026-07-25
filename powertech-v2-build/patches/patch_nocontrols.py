# -*- coding: utf-8 -*-
"""Drop the dots and arrows: the pass is driven by scroll, so they are redundant.
   The thin progress bar stays — it shows how much of the pass is done."""
import io, re

p = 'shell.html'
s = io.open(p, encoding='utf-8').read()

# ---------------------------------------------------------------- markup
old_ctl = ('      <div style="display:flex;align-items:center;gap:14px;margin-top:16px">'
           '<div class="rail-dots" id="rdots"></div><div class="rail-nav">'
           '<button id="rprev" aria-label="prev">←</button>'
           '<button id="rnext" aria-label="next">→</button></div></div>\n')
if old_ctl in s:
    s = s.replace(old_ctl, '')
else:
    # fall back to a line-wise cut so a changed attribute order cannot block this
    lines = s.split('\n')
    keep = [l for l in lines if 'rail-dots' not in l or 'id="rdots"' not in l]
    assert len(keep) == len(lines) - 1, 'control row not matched'
    s = '\n'.join(keep)
assert 'id="rdots"' not in s, 'dots markup still present'
assert 'id="rprev"' not in s, 'arrow markup still present'

# ---------------------------------------------------------------- CSS
for pat in [r'\.rail-nav\{[^}]*\}\n', r'\.rail-nav button\{[^}]*\}\n',
            r'\.rail-nav button:hover\{[^}]*\}\n',
            r'\.rail-nav button\[disabled\]\{[^}]*\}\n',
            r'\.rail-nav button:hover:not\(:disabled\)\{[^}]*\}\n',
            r'\.rail-nav button:disabled\{[^}]*\}\n',
            r'\.rail-dots\{[^}]*\}\n', r'\.rail-dots button\{[^}]*\}\n',
            r'\.rail-dots button\.on\{[^}]*\}\n']:
    s = re.sub(pat, '', s)
# the multi-line variant of the nav button rule
s = re.sub(r'\.rail-nav button\{[^}]*?\n[^}]*?\}\n', '', s)
assert 'rail-dots' not in s, 'dots CSS left'
assert 'rail-nav' not in s, 'nav CSS left'

# ---------------------------------------------------------------- JS
s = s.replace("""var irail=document.getElementById('irail'),rbar=document.getElementById('rbar'),
    rprev=document.getElementById('rprev'),rnext=document.getElementById('rnext');""",
              "var irail=document.getElementById('irail'),rbar=document.getElementById('rbar');")

# railGo / railStep existed only for those controls
a = s.index('function railGo(i){')
b = s.index('function railBar(){')
removed = s[a:b]
assert 'rdots' in removed and 'railStep' in removed, 'unexpected block to remove'
s = s[:a] + s[b:]

s = s.replace("""  rprev.disabled=irail.scrollLeft<4;
  rnext.disabled=irail.scrollLeft>max-4;
  if(rdots){var cur=railIndex();
    for(var i=0;i<rdots.children.length;i++)rdots.children[i].classList.toggle('on',i===cur);}
""", "")

io.open(p, 'w', encoding='utf-8').write(s)

for k in ['rdots', 'rprev', 'rnext', 'railGo', 'railStep', 'rail-nav', 'rail-dots']:
    print('%-12s %d' % (k, s.count(k)))
print('progress bar kept:', s.count('railbar'), s.count("getElementById('rbar')"))
print('railIndex still used:', s.count('railIndex'))
