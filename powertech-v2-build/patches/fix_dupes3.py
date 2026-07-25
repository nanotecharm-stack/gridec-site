# -*- coding: utf-8 -*-
"""Cut the duplicated span: second APPROACH ROUTE marker up to NAV."""
import io

p = 'shell.html'
s = io.open(p, encoding='utf-8').read()

AR = '/* ============ APPROACH ROUTE'
NAV = '/* ============ NAV'

first = s.index(AR)
second = s.index(AR, first + 1)
nav = s.index(NAV)
assert first < second < nav, 'unexpected marker order'

removed = s[second:nav]
assert 'function openInd' in removed, 'the duplicate detail block should be inside the cut'
assert 'function layoutSuite' not in removed, 'the pinned logic must survive'
assert 'CARDS.forEach' not in removed, 'the card builder must survive'

s = s[:second] + s[nav:]
io.open(p, 'w', encoding='utf-8').write(s)

keys = ['function cardArt', 'function openInd', 'var CARDS=', 'CARDS.forEach',
        'function layoutSuite', 'function railBar', 'function suiteUpd',
        AR, '/* ============ EVENT CHAIN', '/* ============ INDUSTRIES']
print('removed chars:', len(removed))
for k in keys:
    print('%-34s %d' % (k[:34], s.count(k)))
