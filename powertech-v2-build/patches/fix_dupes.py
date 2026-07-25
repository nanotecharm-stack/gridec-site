# -*- coding: utf-8 -*-
"""Remove the block region my earlier reversed slice duplicated."""
import io

p = 'shell.html'
s = io.open(p, encoding='utf-8').read()

AR = '/* ============ APPROACH ROUTE'
EC = '/* ============ EVENT CHAIN'
IND = '/* ============ INDUSTRIES'
NAV = '/* ============ NAV'

before = {k: s.count(k) for k in (AR, EC, IND, NAV)}

# the duplicated run starts at the SECOND approach-route marker and ends at NAV
first_ar = s.index(AR)
second_ar = s.index(AR, first_ar + 1)
nav = s.index(NAV)
assert first_ar < second_ar < nav, 'unexpected marker order'

removed = s[second_ar:nav]
assert 'horizontal rail, detail on click' in removed, 'stale industries block not inside the cut'
assert 'a stepped rail of card plates' not in removed, 'the new block must survive'

s = s[:second_ar] + s[nav:]
io.open(p, 'w', encoding='utf-8').write(s)

after = {k: s.count(k) for k in (AR, EC, IND, NAV)}
print('removed chars:', len(removed))
for k in (AR, EC, IND, NAV):
    print(k.split('============ ')[1][:22], before[k], '->', after[k])
print('new industries kept:', 'a stepped rail of card plates' in s)
print('stale industries gone:', 'horizontal rail, detail on click' not in s)
