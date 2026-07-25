# -*- coding: utf-8 -*-
"""Cut the region the reversed slice duplicated a second time."""
import io

p = 'shell.html'
s = io.open(p, encoding='utf-8').read()

MARK = 'CARDS.forEach(function(o,i){'
NAV = '/* ============ NAV'

n = s.count(MARK)
print('card builders before:', n)
assert n == 2, 'expected exactly one duplicate'

first = s.index(MARK)
second = s.index(MARK, first + 1)
nav = s.index(NAV)
assert first < second < nav, 'unexpected order'

removed = s[second:nav]
# the stale copy must contain the retired tween, and none of the pinned logic
assert 'var RAIL_MS=800' in removed, 'stale tween not in the cut'
assert 'function layoutSuite' not in removed, 'pinned logic must survive'

s = s[:second] + s[nav:]
io.open(p, 'w', encoding='utf-8').write(s)

checks = {
    'CARDS.forEach': s.count(MARK),
    'function railBar': s.count('function railBar'),
    'function cardStride': s.count('function cardStride'),
    'function railGo': s.count('function railGo'),
    'function layoutSuite': s.count('function layoutSuite'),
    'var RAIL_MS': s.count('var RAIL_MS'),
    'function railTo': s.count('function railTo'),
}
print('removed chars:', len(removed))
for k, v in checks.items():
    print('%-22s %d' % (k, v))
