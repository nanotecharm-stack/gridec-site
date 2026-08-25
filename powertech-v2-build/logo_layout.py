# -*- coding: utf-8 -*-
# Макет по присланному ориентиру, пересобранный в языке сайта.
#
# Что изменено против ориентира и почему:
#   * дорожки идут только по 0°, 45° и 90°, углы срезаны фаской — так их
#     разводят на плате; в ориентире углы случайные, и это читается как клипарт;
#   * вокруг имени зона отстройки: ни одна дорожка её не пересекает. В ориентире
#     линии идут поверх букв, и имя тонет;
#   * дорожки НЕ висят в воздухе: каждая начинается площадкой на границе зоны и
#     уходит за край поля — шины отходят от узла, а не рассыпаны по фону;
#   * плотность снижена: десять дорожек вместо трёх десятков;
#   * цвет — палитра сайта, одна дорожка акцентная.
#
#   python logo_layout.py
#
# Пишет logo-v8/layout/*.svg и index.html.
import io
import math
import os

from logo_bus import chamfer  # правило фаски одно на весь язык
from logo_lib import word

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'logo-v8', 'layout')

PAPER = '#F6F1E9'
INKB = '#0D2440'
ACC = '#2E5E99'
GLOW = '#4C8ACB'

W = H = 1200.0
CAP = 132.0
TRACK = 0.13
KEEP = 76.0          # зона отстройки вокруг имени
TW = 6.0             # ширина дорожки


def trace(pts, w=TW, c=34.0, col='currentColor', op=1.0):
    p = chamfer(pts, c)
    return ('<path fill="none" stroke="%s" stroke-opacity="%s" stroke-width="%s" '
            'stroke-linecap="butt" stroke-linejoin="miter" d="M%s"/>'
            % (col, op, w, ' L'.join('%s %s' % (x, y) for x, y in p)))


def pad(x, y, r=11.0, hole=4.6, col='currentColor', op=1.0):
    return ('<path fill="%s" fill-opacity="%s" fill-rule="evenodd" d="'
            'M%s %s m-%s 0 a%s %s 0 1 0 %s 0 a%s %s 0 1 0 -%s 0 '
            'M%s %s m-%s 0 a%s %s 0 1 1 %s 0 a%s %s 0 1 1 -%s 0 Z"/>'
            % (col, op, x, y, r, r, r, 2 * r, r, r, 2 * r,
               x, y, hole, hole, hole, 2 * hole, hole, hole, 2 * hole))


def bus(x0, y0, run, sx, sy, col, op):
    """Дорожка от площадки: сперва по горизонтали, потом 45° за край поля."""
    x1 = x0 + sx * run
    reach = (W + 200) if sx > 0 else (x1 + 200)
    d = abs(reach - x1) if sx > 0 else (x1 + 200)
    x2, y2 = x1 + sx * d, y0 + sy * d
    return trace([(x0, y0), (x1, y0), (round(x2), round(y2))], col=col, op=op) \
        + pad(x0, y0, col=col, op=op)


def layout(col, bg, sub=True):
    ps, wide = word('GRIDEC', 500, CAP, TRACK, fill='currentColor', split=4,
                    split_fill=ACC if bg == PAPER else GLOW)
    x0 = (W - wide) / 2
    base = H / 2 + CAP / 2
    kx0, kx1 = x0 - KEEP, x0 + wide + KEEP
    # низ зоны считается ПО ПОДПИСИ, а не по имени: иначе нижний пучок
    # проходит прямо по строке «power quality monitoring»
    ky0 = base - CAP - KEEP
    ky1 = base + (92 + 26 if sub else 0) + KEEP

    body = []
    acc = ACC if bg == PAPER else GLOW
    # верхний пучок уходит влево-вверх, нижний — вправо-вниз
    for i in range(5):
        c, o = ('currentColor', 0.26) if i != 1 else (acc, 0.85)
        # площадки со ступенькой: на одной прямой они читались гребёнкой
        body.append(bus(kx0 + 46 + i * 104, ky0 - i * 20,
                        -1 * (40 + i * 46), -1, -1, c, o))
    for i in range(5):
        c, o = ('currentColor', 0.26) if i != 3 else (acc, 0.85)
        body.append(bus(kx1 - 46 - i * 104, ky1 + i * 20,
                        40 + i * 46, 1, 1, c, o))
    # две длинные дорожки без площадок — они проходят мимо, а не оканчиваются
    body.append(trace([(-100, ky0 - 150), (kx0 - 190, ky0 - 150),
                       (kx0 - 190 + 400, ky0 - 150 - 400)], op=0.14))
    body.append(trace([(W + 100, ky1 + 150), (kx1 + 190, ky1 + 150),
                       (kx1 + 190 - 400, ky1 + 150 + 400)], op=0.14))

    ps, _ = word('GRIDEC', 500, CAP, TRACK, x=x0, y=base, fill='currentColor',
                 split=4, split_fill=acc)
    body.append(''.join(ps))
    if sub:
        cps, cw = word('POWER QUALITY MONITORING', 500, 17.0, 0.42)
        cps, _ = word('POWER QUALITY MONITORING', 500, 17.0, 0.42,
                      x=(W - cw) / 2, y=base + 92, fill='currentColor')
        body.append('<g opacity="0.5">%s</g>' % ''.join(cps))
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s %s" '
            'style="background:%s;color:%s">%s</svg>'
            % (W, H, bg, col, ''.join(body)))


os.makedirs(OUT, exist_ok=True)
files = [('layout-light', INKB, PAPER), ('layout-dark', PAPER, INKB)]
for name, col, bg in files:
    io.open(os.path.join(OUT, name + '.svg'), 'w', encoding='utf-8').write(
        layout(col, bg))
    print(name + '.svg')

HTML = (u'<!doctype html><meta charset="utf-8"><title>Gridec — макет</title>'
        u'<style>body{margin:0;padding:28px;background:#EFEAE1;color:#2B2722;'
        u'font:14px/1.45 -apple-system,Segoe UI,sans-serif}'
        u'h1{font-size:19px;font-weight:600;margin:0 0 6px}'
        u'p{color:#8A8378;margin:0 0 18px;max-width:720px}'
        u'.row{display:flex;gap:20px;flex-wrap:wrap}'
        u'.row svg{width:520px;height:520px;border-radius:4px}</style>'
        u'<h1>Gridec — макет ориентира в языке сайта</h1>'
        u'<p>Дорожки идут только по 0°, 45° и 90°, углы срезаны фаской. Вокруг '
        u'имени зона отстройки — ни одна дорожка её не пересекает. Каждая '
        u'начинается площадкой у имени и уходит за край: шины отходят от узла. '
        u'Одна дорожка в каждом пучке — акцентная.</p>'
        u'<div class="row">%s%s</div>'
        % (layout(INKB, PAPER), layout(PAPER, INKB)))
io.open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(HTML)
print('index.html')
