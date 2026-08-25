# Точная настройка восьмой версии: свет, тень и объём.
#
# Приёмы:
#   * тень двумя слоями — короткая плотная у самого куба и длинная мягкая;
#   * каждая грань темнеет к шву, это затенение в углу, оно и даёт объём;
#   * тонкий блик по верхним рёбрам — свет сверху слева;
#   * на плашке уклон тона плюс мягкое затемнение к правому нижнему углу.
#
#   python logo_v8_tune.py [путь к Outfit[wght].ttf]
#
# Пишет logo-v8/v8a-soft.svg, v8b-cut.svg, v8c-deep.svg и index.html.
import os

from logo_lib import (DIAMOND, INK, MARK_H, PAGE, WALL_L, WALL_R, svg, word)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'logo-v8')

TAIL = '#A6A6A6'
PAD = 10.0
FACES = (WALL_L, WALL_R, DIAMOND)
# Верхние рёбра: по ним ложится блик. Порядок тот же, что у граней.
EDGES = ('M-86.603 -50 L-6 -96.536',
         'M6 -96.536 L86.603 -50',
         'M-86.603 56.928 L0 6.928 L86.603 56.928')


def grad(gid, c1, c2, vec):
    x1, y1, x2, y2 = vec
    return ('<linearGradient id="%s" x1="%s" y1="%s" x2="%s" y2="%s">'
            '<stop offset="0" stop-color="%s"/>'
            '<stop offset="1" stop-color="%s"/></linearGradient>'
            % (gid, x1, y1, x2, y2, c1, c2))


def build(pfx, tile, ramps, shadows, edge, plate_ramp, sheen, vignette,
          cap=38.0, track=0.16):
    """Плашка слева, имя справа. Возвращает (svg, ширина, высота)."""
    gap = tile * 0.28
    _, wide = word('GRIDEC', 400, cap, track)
    w = PAD + tile + gap + wide + PAD
    h = PAD + tile + PAD
    cx = cy = PAD + tile / 2
    mh = tile * 0.56
    k = mh / MARK_H
    r = round(tile * 0.24, 1)
    rect = 'x="%s" y="%s" width="%s" height="%s" rx="%s"' % (PAD, PAD, tile, tile, r)

    # --- заготовки цвета -----------------------------------------------------
    vecs = ((0, 0, 1, 0.4), (1, 0, 0, 0.4), (0.5, 0, 0.5, 1))
    defs = [grad(pfx + '_bg', plate_ramp[0], plate_ramp[1], (0, 0, 0.55, 1))]
    defs += [grad('%s_f%d' % (pfx, i), c1, c2, v)
             for i, ((c1, c2), v) in enumerate(zip(ramps, vecs))]
    defs.append('<linearGradient id="%s_sn" x1="0" y1="0" x2="0" y2="1">'
                '<stop offset="0" stop-color="#FFFFFF" stop-opacity="%s"/>'
                '<stop offset="0.5" stop-color="#FFFFFF" stop-opacity="0"/>'
                '<stop offset="1" stop-color="#000000" stop-opacity="%s"/>'
                '</linearGradient>' % (pfx, sheen[0], sheen[1]))
    # затемнение к правому нижнему углу: источник света сверху слева
    defs.append('<radialGradient id="%s_vg" cx="0.28" cy="0.22" r="0.95">'
                '<stop offset="0" stop-color="#FFFFFF" stop-opacity="%s"/>'
                '<stop offset="0.55" stop-color="#000000" stop-opacity="0"/>'
                '<stop offset="1" stop-color="#000000" stop-opacity="%s"/>'
                '</radialGradient>' % (pfx, vignette[0], vignette[1]))
    for i, (dev, dy, op, col) in enumerate(shadows):
        defs.append('<filter id="%s_s%d" x="-50%%" y="-50%%" width="200%%" '
                    'height="200%%"><feGaussianBlur stdDeviation="%s"/></filter>'
                    % (pfx, i, round(mh * dev, 2)))

    # --- сборка --------------------------------------------------------------
    body = ['<rect %s fill="url(#%s_bg)"/>' % (rect, pfx)]
    drop = ''.join('<path d="%s"/>' % d for d in FACES)
    for i, (dev, dy, op, col) in enumerate(shadows):
        body.append('<g transform="translate(%s %s) scale(%s)" fill="%s" '
                    'fill-opacity="%s" filter="url(#%s_s%d)">%s</g>'
                    % (cx, round(cy + mh * dy, 2), round(k, 5), col, op, pfx, i, drop))
    faces = ''.join('<path fill="url(#%s_f%d)" d="%s"/>' % (pfx, i, d)
                    for i, d in enumerate(FACES))
    if edge:
        col, op, sw = edge
        faces += ''.join('<path d="%s" fill="none" stroke="%s" stroke-opacity="%s" '
                         'stroke-width="%s" stroke-linecap="round" '
                         'stroke-linejoin="round"/>' % (d, col, op, sw)
                         for d in EDGES)
    body.append('<g transform="translate(%s %s) scale(%s)">%s</g>'
                % (cx, cy, round(k, 5), faces))
    body.append('<rect %s fill="url(#%s_sn)"/>' % (rect, pfx))
    body.append('<rect %s fill="url(#%s_vg)"/>' % (rect, pfx))
    ps, _ = word('GRIDEC', 400, cap, track, x=PAD + tile + gap,
                 y=cy + cap / 2, fill=INK, split=4, split_fill=TAIL)
    body.append(''.join(ps))
    return svg(w, h, '<defs>%s</defs>%s' % (''.join(defs), ''.join(body))), w, h


# --- 8a «мягкая»: тень рассеяна, рёбра без блика ------------------------------
def v8a():
    return build('a', 96.0,
                 (('#A8A8A8', '#8A8A8A'), ('#E4E4E4', '#BEBEBE'),
                  ('#F6F6F6', '#D4D4D4')),
                 ((0.10, 0.06, 0.40, '#000000'),),
                 None, ('#3C3C3C', '#181818'), (0.13, 0.16), (0.05, 0.16))


# --- 8b «точёная»: тень двумя слоями, тонкий блик по верхним рёбрам -----------
def v8b():
    return build('b', 96.0,
                 (('#ADADAD', '#7E7E7E'), ('#EDEDED', '#B6B6B6'),
                  ('#FFFFFF', '#CFCFCF')),
                 ((0.13, 0.09, 0.38, '#000000'), (0.035, 0.03, 0.45, '#000000')),
                 ('#FFFFFF', 0.55, 2.6), ('#414141', '#141414'),
                 (0.16, 0.20), (0.07, 0.22))


# --- 8c «глубокая»: контраст граней выше, тень плотнее, блик ярче -------------
def v8c():
    return build('c', 96.0,
                 (('#9E9E9E', '#5E5E5E'), ('#F2F2F2', '#A6A6A6'),
                  ('#FFFFFF', '#C2C2C2')),
                 ((0.16, 0.11, 0.46, '#000000'), (0.03, 0.025, 0.55, '#000000')),
                 ('#FFFFFF', 0.75, 3.0), ('#4A4A4A', '#0E0E0E'),
                 (0.20, 0.26), (0.09, 0.30))


CARD = u'''<section class="card">
  <h2>%s</h2><p class="ref">%s</p>
  <div class="stage light">%s</div>
  <div class="stage dark">%s</div>
  <div class="stage light row">%s %s %s</div>
</section>'''

os.path.isdir(OUT) or os.makedirs(OUT)
made = []
for name, fn in (('v8a-soft', v8a), ('v8b-cut', v8b), ('v8c-deep', v8c)):
    s, w, h = fn()
    open(os.path.join(OUT, name + '.svg'), 'w', encoding='utf-8').write(s)
    made.append((name, s, w, h))
    print('%-12s %4d x %3d  %d B' % (name, w, h, len(s)))

titles = [(u'8a — мягкая', u'тень одним слоем, рёбра без блика'),
          (u'8b — точёная', u'тень двумя слоями, тонкий блик по верхним рёбрам'),
          (u'8c — глубокая', u'контраст граней выше, тень плотнее, блик ярче')]
cards = []
for (name, s, w, h), (t, r) in zip(made, titles):
    big = s.replace('<svg ', '<svg style="height:150px" ', 1)
    inv = s.replace('#141414', '#FFFFFF').replace('#A6A6A6', '#B8B8B8')
    inv = inv.replace('<svg ', '<svg style="height:150px" ', 1)
    row = [s.replace('<svg ', '<svg style="height:%dpx" ' % px, 1)
           for px in (40, 24, 16)]
    cards.append(CARD % ((t, r, big, inv) + tuple(row)))

title = u'Gridec — восьмая версия, три настройки света и тени'
html = (PAGE % (title, title, '\n'.join(cards))).replace(
    '.small{padding:14px}', '.row{gap:34px;padding:16px}')
open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(html)
print('index.html   %d B' % len(html))
