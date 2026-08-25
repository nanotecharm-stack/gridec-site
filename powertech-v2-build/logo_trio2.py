# Второй заход: спокойная типографика первой версии плюс плашка и разрез имени
# на GRID + EC. Серая шкала, буквы в кривых.
#
#   python logo_trio2.py [путь к Outfit[wght].ttf]
#
# Пишет logo-trials2/v4-plate.svg, v5-stack.svg, v6-outline.svg и index.html.
import os

from logo_lib import INK, MARK_H, MARK_W, mark, svg, word, write_all

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'logo-trials2')

TAIL = '#A6A6A6'          # «EC» — светлее имени, но ещё читается
PAD = 10.0


def plate_fill(idx, a, b):
    """Мягкая подложка: почти ровный тон, лёгкий уклон сверху вниз."""
    return ('<defs><linearGradient id="p%d" x1="0" y1="0" x2="0.55" y2="1">'
            '<stop offset="0" stop-color="%s"/>'
            '<stop offset="1" stop-color="%s"/></linearGradient></defs>' % (idx, a, b))


# --- v4: плашка слева, имя в разрядку, тонкая подпись -------------------------
def v4():
    tile, cap, sub_cap = 96.0, 38.0, 12.0
    gap, sub_gap = 24.0, 21.0
    _, w_head = word('GRID', 400, cap, 0.16)
    _, w_all = word('GRIDEC', 400, cap, 0.16)
    _, w_sub = word('power quality engineering', 400, sub_cap, 0.14)
    txtw = max(w_all, w_sub)
    w = PAD + tile + gap + txtw + PAD
    h = PAD + tile + PAD
    x0 = PAD + tile + gap
    centre = PAD + tile / 2
    baseline = centre + (cap - sub_gap) / 2
    body = plate_fill(4, '#7A7A7A', '#B9B9B9')
    body += ('<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="url(#p4)"/>'
             % (PAD, PAD, tile, tile, round(tile * 0.24, 1)))
    body += mark(PAD + tile / 2, centre, tile * 0.56, ('#FFFFFF',) * 3)
    ps, _ = word('GRIDEC', 400, cap, 0.16, x=x0, y=baseline,
                 fill=INK, split=4, split_fill=TAIL)
    sub, _ = word('power quality engineering', 400, sub_cap, 0.14,
                  x=x0 + 1, y=baseline + sub_gap, fill='#9A9A9A')
    return svg(w, h, body + ''.join(ps + sub)), w, h


# --- v5: плашка сверху по центру, имя под ней в широкую разрядку --------------
def v5():
    tile, cap, track = 92.0, 40.0, 0.28
    gap = 34.0
    _, wide = word('GRIDEC', 400, cap, track)
    w = max(wide, tile) + PAD * 2
    h = PAD + tile + gap + cap + PAD
    # хвост разрядки — пустота справа, поэтому имя сдвигается влево на полшага
    x0 = (w - wide) / 2 - cap * track / 2
    body = plate_fill(5, '#6F6F6F', '#B4B4B4')
    body += ('<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="url(#p5)"/>'
             % (round((w - tile) / 2, 2), PAD, tile, tile, round(tile * 0.26, 1)))
    body += mark(w / 2, PAD + tile / 2, tile * 0.56, ('#FFFFFF',) * 3)
    ps, _ = word('GRIDEC', 400, cap, track, x=x0, y=PAD + tile + gap + cap,
                 fill=INK, split=4, split_fill=TAIL)
    return svg(w, h, body + ''.join(ps)), w, h


# --- v6: плашка тонкой линией, знак внутри, разрез имени по весу и тону -------
def v6():
    tile, cap = 92.0, 40.0
    gap = 26.0
    sw = 1.6                                   # техническая линия рамки
    _, w_head = word('GRID', 500, cap, 0.10)
    xb = w_head + cap * 0.10
    _, w_tail = word('EC', 300, cap, 0.10, x=xb)
    txtw = xb + w_tail
    w = PAD + tile + gap + txtw + PAD
    h = PAD + tile + PAD
    centre = PAD + tile / 2
    x0 = PAD + tile + gap
    body = ('<rect x="%s" y="%s" width="%s" height="%s" rx="2" fill="none" '
            'stroke="#C6C6C6" stroke-width="%s"/>'
            % (PAD + sw / 2, PAD + sw / 2, tile - sw, tile - sw, sw))
    body += mark(PAD + tile / 2, centre, tile * 0.52, ('#3A3A3A', '#8A8A8A', '#B8B8B8'))
    a, _ = word('GRID', 500, cap, 0.10, x=x0, y=centre + cap / 2, fill=INK)
    b, _ = word('EC', 300, cap, 0.10, x=x0 + xb, y=centre + cap / 2, fill=TAIL)
    return svg(w, h, body + ''.join(a + b)), w, h


write_all(OUT, (('v4-plate', v4), ('v5-stack', v5), ('v6-outline', v6)),
          u'Gridec — второй заход: спокойствие плюс плашка и акцент на GRID',
          [(u'Версия 4 — плашка слева, имя в разрядку, подпись',
            u'спокойный вариант второй версии'),
           (u'Версия 5 — плашка сверху, имя под ней',
            u'первая версия плюс плашка и акцент'),
           (u'Версия 6 — рамка тонкой линией, разрез по весу',
            u'самый технический из трёх')],
          dark_swaps=(('#C6C6C6', '#4E4E4E'), ('#3A3A3A', '#D6D6D6')))
