# -*- coding: utf-8 -*-
"""Finishing pass: complete the numbering, rebuild the report sheet,
   readable footnote, visible focus, head metadata."""
import io

p = 'shell.html'
s = io.open(p, encoding='utf-8').read()

# ---------------------------------------------------------------- 1. numbering runs 01..08
s = s.replace('<div class="rv"><div class="eyebrow">%%SVC_EYEBROW%%</div>',
              '<div class="rv"><div class="cnt">03</div><div class="eyebrow">%%SVC_EYEBROW%%</div>')
s = s.replace('<div class="rv"><div class="eyebrow">%%CO_EYEBROW%%</div>',
              '<div class="rv"><div class="cnt">07</div><div class="eyebrow">%%CO_EYEBROW%%</div>')
old_contact = '<section class="plate" id="contact"><div class="wrap">\n  <div class="rv">'
assert old_contact in s, 'contact opening not found'
s = s.replace(old_contact, '<section class="plate" id="contact"><div class="wrap">\n  <div class="rv"><div class="cnt">08</div>')

# the counter needs to sit on the dark plates too
s = s.replace('.cnt{font-family:',
              '.plate .cnt,.plate2 .cnt{color:rgba(239,237,234,.5);}\n'
              '.plate .cnt::after,.plate2 .cnt::after{background:rgba(239,237,234,.16);}\n'
              '.cnt{font-family:')

# ---------------------------------------------------------------- 2. the report becomes a sheet, not a white box
s = s.replace(""".list{background:var(--panel);box-shadow:inset 0 0 0 1px var(--hair2);padding:clamp(22px,2.6vw,36px);border-radius:2px;}
.list div{display:flex;gap:14px;align-items:baseline;padding:12px 0;font-size:15px;line-height:1.6;color:var(--fg);}
.list div+div{border-top:1px solid var(--hair2);}
.list em{font-style:normal;width:6px;height:6px;background:var(--brand);flex:0 0 auto;transform:translateY(-1px);}
.note{font-size:13.5px;line-height:1.75;color:var(--fg-soft);margin-top:26px;max-width:52ch;}""",
"""/* what the report contains, read as a numbered sheet rather than a panel */
.list{border-top:1px solid var(--hair);}
.list div{display:grid;grid-template-columns:34px 1fr;gap:0 16px;align-items:baseline;
  padding:15px 0;font-size:15.5px;line-height:1.55;color:var(--fg);
  border-bottom:1px solid var(--hair2);transition:padding-left .45s var(--e);}
.list div:hover{padding-left:8px;}
.list .n{font-family:'Martian Mono',%%MONOFALL%%;font-size:10px;letter-spacing:.14em;color:var(--brand);}
/* the standards footnote: quiet, but legible — it carries the method */
.note{font-size:13px;line-height:1.7;color:var(--fg-mid);margin-top:30px;padding-top:16px;
  border-top:1px solid var(--hair2);max-width:54ch;}""")

# ---------------------------------------------------------------- 3. keyboard focus must be visible
s = s.replace('*{box-sizing:border-box;}',
              '*{box-sizing:border-box;}\n'
              'a:focus-visible,button:focus-visible,input:focus-visible,textarea:focus-visible,\n'
              'select:focus-visible,[tabindex]:focus-visible{outline:2px solid var(--brand);\n'
              '  outline-offset:3px;border-radius:2px;}\n'
              '.hero a:focus-visible,.hero button:focus-visible,.plate a:focus-visible,\n'
              '.plate button:focus-visible,.plate2 a:focus-visible,.plate2 button:focus-visible,\n'
              '.ic:focus-visible{outline-color:#FFFBF9;}')

io.open(p, 'w', encoding='utf-8').write(s)

print('counters in markup:', s.count('class="cnt"'))
print('report sheet:', '.list{border-top' in s)
print('note readable:', 'color:var(--fg-mid);margin-top:30px' in s)
print('focus ring:', ':focus-visible' in s)
