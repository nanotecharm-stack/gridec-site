# Третий заход: плашка и имя в одну линию, без подписи. Знак объёмный —
# у каждой грани свой уклон тона, под кубом мягкая тень. Плашка — постоянный
# грунт: на светлом и на тёмном фоне линии знака выглядят одинаково.
#
#   python logo_trio3.py [путь к Outfit[wght].ttf]
#
# Пишет logo-trials3/v7-light-plate.svg, v8-graphite.svg, v9-paper.svg
# и index.html.
import os

from logo_lib import (DIAMOND, INK, WALL_L, WALL_R, MARK_H, svg, word,
                      write_all)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'logo-trials3')

TAIL = '#A6A6A6'          # «EC» светлее имени, но ещё читается
PAD = 10.0
FACES = (WALL_L, WALL_R, DIAMOND)   # левая стенка, правая стенка, нижний ромб


def grad(gid, c1, c2, vec=(0, 0, 1, 1)):
    x1, y1, x2, y2 = vec
    return ('<linearGradient id="%s" x1="%s" y1="%s" x2="%s" y2="%s">'
            '<stop offset="0" stop-color="%s"/>'
            '<stop offset="1" stop-color="%s"/></linearGradient>'
            % (gid, x1, y1, x2, y2, c1, c2))


def solid(pfx, cx, cy, h, ramps, shadow=None):
    """Знак с уклоном тона на каждой грани и мягкой тенью под ним.

    ramps — три пары цветов: свет и тень для левой стенки, правой и ромба.
    """
    k = h / MARK_H
    vecs = ((0, 0, 1, 0.4), (1, 0, 0, 0.4), (0.5, 0, 0.5, 1))
    defs = ''.join(grad('%s_f%d' % (pfx, i), c1, c2, v)
                   for i, ((c1, c2), v) in enumerate(zip(ramps, vecs)))
    defs += ('<filter id="%s_sh" x="-40%%" y="-40%%" width="180%%" height="180%%">'
             '<feGaussianBlur stdDeviation="%s"/></filter>' % (pfx, round(h * 0.045, 2)))
    inner = ''.join('<path fill="url(#%s_f%d)" d="%s"/>' % (pfx, i, d)
                    for i, d in enumerate(FACES))
    place = 'transform="translate(%s %s) scale(%s)"' % (round(cx, 2), round(cy, 2),
                                                        round(k, 5))
    body = ''
    if shadow:
        col, op, dy = shadow
        drop = ''.join('<path d="%s"/>' % d for d in FACES)
        body += ('<g transform="translate(%s %s) scale(%s)" fill="%s" '
                 'fill-opacity="%s" filter="url(#%s_sh)">%s</g>'
                 % (round(cx, 2), round(cy + dy, 2), round(k, 5), col, op, pfx, drop))
    body += '<g %s>%s</g>' % (place, inner)
    return defs, body


def plate(pfx, x, y, size, c1, c2, radius=0.24, border=None, sheen=0.20):
    """Подложка: мягкий уклон, стеклянный блик сверху, при нужде тонкий кант."""
    r = round(size * radius, 1)
    defs = grad(pfx + '_bg', c1, c2, (0, 0, 0.55, 1))
    defs += ('<linearGradient id="%s_sn" x1="0" y1="0" x2="0" y2="1">'
             '<stop offset="0" stop-color="#FFFFFF" stop-opacity="%s"/>'
             '<stop offset="0.55" stop-color="#FFFFFF" stop-opacity="0"/>'
             '<stop offset="1" stop-color="#000000" stop-opacity="0.10"/>'
             '</linearGradient>' % (pfx, sheen))
    rect = 'x="%s" y="%s" width="%s" height="%s" rx="%s"' % (x, y, size, size, r)
    body = '<rect %s fill="url(#%s_bg)"/>' % (rect, pfx)
    if border:
        body += ('<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="none" '
                 'stroke="%s" stroke-width="1.2"/>'
                 % (x + 0.6, y + 0.6, size - 1.2, size - 1.2, r, border))
    return defs, body, '<rect %s fill="url(#%s_sn)"/>' % (rect, pfx)


def lockup(pfx, plate_args, ramps, shadow, tile=96.0, cap=38.0, track=0.16):
    """Плашка слева, имя справа, всё в одну линию."""
    gap = tile * 0.28
    _, wide = word('GRIDEC', 400, cap, track)
    w = PAD + tile + gap + wide + PAD
    h = PAD + tile + PAD
    centre = PAD + tile / 2
    d1, b1, sheen = plate(pfx, PAD, PAD, tile, *plate_args)
    d2, b2 = solid(pfx, PAD + tile / 2, centre, tile * 0.56, ramps, shadow)
    ps, _ = word('GRIDEC', 400, cap, track, x=PAD + tile + gap,
                 y=centre + cap / 2, fill=INK, split=4, split_fill=TAIL)
    body = '<defs>%s%s</defs>%s%s%s%s' % (d1, d2, b1, b2, sheen, ''.join(ps))
    return svg(w, h, body), w, h


# --- v7: серая плашка, знак светлый — ближе всего к STDev ---------------------
def v7():
    return lockup('a', ('#8E8E8E', '#C2C2C2', 0.24, None, 0.26),
                  (('#F2F2F2', '#D8D8D8'), ('#FFFFFF', '#EDEDED'),
                   ('#FFFFFF', '#F6F6F6')),
                  ('#2A2A2A', 0.30, 3.0))


# --- v8: графитовая плашка, знак светлый — самый контрастный ------------------
def v8():
    return lockup('b', ('#3A3A3A', '#171717', 0.24, None, 0.14),
                  (('#B4B4B4', '#8E8E8E'), ('#EDEDED', '#C4C4C4'),
                   ('#FFFFFF', '#DCDCDC')),
                  ('#000000', 0.45, 3.0))


# --- v9: светлая плашка-бумага с кантом, знак графитовый ----------------------
def v9():
    return lockup('c', ('#FFFFFF', '#ECECEC', 0.24, '#D8D8D8', 0.55),
                  (('#4A4A4A', '#2B2B2B'), ('#8A8A8A', '#6A6A6A'),
                   ('#C0C0C0', '#A2A2A2')),
                  ('#3A3A3A', 0.22, 3.0))


write_all(OUT, (('v7-light-plate', v7), ('v8-graphite', v8), ('v9-paper', v9)),
          u'Gridec — третий заход: объём, плашка и имя в одну линию',
          [(u'Версия 7 — серая плашка, знак светлый', u'ближе всего к STDev'),
           (u'Версия 8 — графитовая плашка', u'самый контрастный'),
           (u'Версия 9 — светлая плашка с кантом, знак графитовый',
            u'самый спокойный')])
