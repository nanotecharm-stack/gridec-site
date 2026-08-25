# -*- coding: utf-8 -*-
# Третий заход на локап: не узор за именем, а ОДНА мысль, сказанная одной линией.
#
# Общее правило всех трёх: линия одна, повороты только 45°, площадка одна и
# акцентная — она отмечает место, где что-то произошло. Всё одноцветное, кроме
# этой точки: логотип берёт цвет текста и живёт на любом грунте.
#
#   python logo_premium.py
#
# Пишет logo-v8/premium/*.svg и index.html.
import io
import os

from logo_lib import word

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'logo-v8', 'premium')

PAPER = '#F6F1E9'
INKB = '#0D2440'
ACC = '#2E5E99'
GLOW = '#4C8ACB'

W, H = 1720.0, 440.0
CAP = 150.0
TRACK = 0.13
LW = 9.0                      # волосяная линия: тоньше не выживет в шапке


def line(pts, w=LW, col='currentColor', op=1.0, cap='butt'):
    return ('<path fill="none" stroke="%s" stroke-opacity="%s" stroke-width="%s" '
            'stroke-linecap="%s" stroke-linejoin="miter" d="M%s"/>'
            % (col, op, w, cap,
               ' L'.join('%s %s' % (round(x, 1), round(y, 1)) for x, y in pts)))


def pad(x, y, r=15.0, hole=6.0, col='currentColor', op=1.0):
    return ('<path fill="%s" fill-opacity="%s" fill-rule="evenodd" d="'
            'M%s %s m-%s 0 a%s %s 0 1 0 %s 0 a%s %s 0 1 0 -%s 0 '
            'M%s %s m-%s 0 a%s %s 0 1 1 %s 0 a%s %s 0 1 1 -%s 0 Z"/>'
            % (col, op, x, y, r, r, r, 2 * r, r, r, 2 * r,
               x, y, hole, hole, hole, 2 * hole, hole, hole, 2 * hole))


def geometry():
    """Где стоит имя и где начинается «EC» — от этого пляшут все три."""
    _, wide = word('GRIDEC', 500, CAP, TRACK)
    _, w_grid = word('GRID', 500, CAP, TRACK)
    x0 = (W - wide) / 2
    base = H / 2 + CAP / 2
    return x0, wide, x0 + w_grid + CAP * TRACK, base


# ------------------------------------------------ 01 · событие на линии
def v_event(acc):
    """Ровная линия над именем проседает ровно над «EC» — и там точка замера.

    Смысл прямой: шина держит уровень, в одном месте уровень уходит, и это
    место отмечено. Ровно тем занята компания. Провал стоит над «EC», где
    имя и так меняет цвет: два разных языка говорят об одном месте.
    """
    x0, wide, x_ec, base = geometry()
    # просадка обязана пройти НАД прописными: на 6 единицах зазора
    # площадка садилась на «E» и читалась как опечатка
    top = base - CAP - 104
    depth = 52.0
    a, b = x_ec - 26, x0 + wide + 26
    pts = [(0, top), (a - depth, top), (a, top + depth), (b, top + depth),
           (b + depth, top), (W, top)]
    mid = (a + b) / 2
    return (line(pts) + pad(mid, top + depth, 15, 6, acc)
            + word_paths(acc))


# ------------------------------------------------ 02 · разъём и шина
def v_port(acc):
    """Слева разъём: четыре площадки на общей гребёнке. От него одна линия
    уходит под именем к правому краю. Имя стоит на шине, как компонент."""
    x0, wide, x_ec, base = geometry()
    y = base + 74
    # шина идёт сквозь весь локап, на ней три равноудалённые точки съёма;
    # стойки-иголки прежней версии читались как гребешок, а не как разъём
    out = [line([(0, y), (W, y)])]
    step = wide / 3.0
    for i in range(3):
        px = x0 + step * (i + 0.5)
        out.append(pad(px, y, 15, 6, acc if i == 1 else 'currentColor'))
    return ''.join(out) + word_paths(acc)


# ------------------------------------------------ 03 · окно замера
def v_window(acc):
    """Имя внутри тонкой рамки с разрывами: рамка — окно прибора, разрывы —
    входы шины. В правом нижнем углу одна площадка: точка съёма."""
    x0, wide, x_ec, base = geometry()
    l, r = x0 - 96, x0 + wide + 96
    t, bo = base - CAP - 74, base + 74
    g = 92.0                                   # разрыв посередине сторон
    out = [line([(l, (t + bo) / 2 + g / 2), (l, bo), (l + 150, bo)]),
           line([(r, (t + bo) / 2 - g / 2), (r, t), (r - 150, t)]),
           line([(l, (t + bo) / 2 - g / 2), (l, t), (l + 150, t)], LW,
                'currentColor', 0.34),
           line([(r, (t + bo) / 2 + g / 2), (r, bo), (r - 150, bo)], LW,
                'currentColor', 0.34),
           line([(0, bo), (l - 46, bo), (l, bo)], LW, 'currentColor', 0.34),
           line([(r, t), (W, t)], LW, 'currentColor', 0.34),
           pad(r, bo, 15, 6, acc)]
    return ''.join(out) + word_paths(acc)


def word_paths(acc):
    x0, wide, x_ec, base = geometry()
    ps, _ = word('GRIDEC', 500, CAP, TRACK, x=x0, y=base, fill='currentColor',
                 split=4, split_fill=acc)
    return ''.join(ps)


VARIANTS = [('01-event', u'01 · Событие на линии',
             u'ровная линия проседает над «EC», там точка замера', v_event),
            ('02-port', u'02 · Имя на шине',
             u'имя стоит на шине, на ней три точки съёма', v_port),
            ('03-window', u'03 · Окно замера',
             u'рамка прибора с входами шины', v_window)]


def svg(fn, col, bg, px=0):
    acc = ACC if bg == PAPER else GLOW
    style = 'background:%s;color:%s;border-radius:4px' % (bg, col)
    if px:
        style = 'height:%spx;%s' % (px, style)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s %s" '
            'style="%s">%s</svg>' % (W, H, style, fn(acc)))


os.makedirs(OUT, exist_ok=True)
rows = []
for name, title, note, fn in VARIANTS:
    io.open(os.path.join(OUT, name + '.svg'), 'w', encoding='utf-8').write(
        svg(fn, INKB, PAPER))
    io.open(os.path.join(OUT, name + '-dark.svg'), 'w', encoding='utf-8').write(
        svg(fn, PAPER, INKB))
    rows.append(u'<section><h2>%s</h2><p>%s</p>%s%s'
                u'<div class="row">%s%s</div></section>'
                % (title, note, svg(fn, INKB, PAPER, 170),
                   svg(fn, PAPER, INKB, 170),
                   svg(fn, INKB, PAPER, 44), svg(fn, PAPER, INKB, 44)))
    print(name)

HTML = (u'<!doctype html><meta charset="utf-8"><title>Gridec — локап</title>'
        u'<style>body{margin:0;padding:30px 34px;background:#EFEAE1;color:#2B2722;'
        u'font:14px/1.45 -apple-system,Segoe UI,sans-serif}'
        u'h1{font-size:19px;font-weight:600;margin:0 0 6px}'
        u'h2{font-size:15px;font-weight:600;margin:0 0 2px}'
        u'section{margin:0 0 34px;max-width:1000px}'
        u'section p{color:#8A8378;margin:0 0 12px}'
        u'section svg{display:block;margin-bottom:10px;max-width:100%%}'
        u'.row{display:flex;gap:14px;flex-wrap:wrap;margin-top:4px}'
        u'.row svg{margin:0}'
        u'p.lead{color:#8A8378;margin:0 0 24px;max-width:720px}</style>'
        u'<h1>Gridec — локап: одна линия, одна мысль</h1>'
        u'<p class="lead">Ни узора, ни плашки. В каждом варианте линия одна, '
        u'повороты только 45°, и ровно одна площадка — акцентная. Логотип берёт '
        u'цвет текста, поэтому живёт на любом грунте. Под каждым — тот же локап '
        u'в размере шапки.</p>%s' % ''.join(rows))
io.open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(HTML)
print('index.html')
