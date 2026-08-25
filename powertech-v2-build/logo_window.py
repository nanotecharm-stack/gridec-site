# -*- coding: utf-8 -*-
# Прототип «Measurement window», доведённый: красные засечки убраны, две
# внутренние линии опущены — тогда рамка с линиями читается как «G».
#
# Почему сдвиг вниз вообще работает: у «G» перекладина стоит НИЖЕ середины.
# На середине тот же рисунок читается как «E» или как окно со шкалой.
#
#   python logo_window.py
#
# Пишет logo-v8/window/<имя>.svg и index.html.
import io
import os

from logo_lib import word

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'logo-v8', 'window')

PAPER = '#F6F1E9'
INKB = '#0D2440'
TAIL = '#2E5E99'

S = 86.0          # половина поля знака
T = 28.0          # толщина штриха рамки
IN = S - T        # внутренний край рамки: 58


def bar(x0, y0, x1, y1):
    return ('<path fill="currentColor" d="M%s %s L%s %s L%s %s L%s %s Z"/>'
            % (round(x0, 1), round(y0, 1), round(x1, 1), round(y0, 1),
               round(x1, 1), round(y1, 1), round(x0, 1), round(y1, 1)))


def window(cross_y=-4.0, ticks=0, stub=True, cross_x=-6.0, tick_w=48.0,
           tick_t=15.0):
    """Квадратная рамка без правой стороны плюс перекладина ниже середины.

    Просто опустить две линии прототипа нельзя: нижняя упирается в нижний
    штрих и слипается с ним. Поэтому «G» собирается правильно — перекладина
    входит справа НИЖЕ середины, и от неё вниз идёт стойка к нижнему штриху.
    Прежние линии замера остаются, но выше, тонкими рисками.
    """
    out = [bar(-S, -S, S, -S + T),          # верх
           bar(-S, IN, S, S),               # низ
           bar(-S, -S, -S + T, S)]          # левая стойка
    out.append(bar(cross_x, cross_y, S, cross_y + T))       # перекладина «G»
    if stub:
        out.append(bar(S - T, cross_y + T, S, IN))          # стойка вниз
    for k in range(ticks):
        y = cross_y - 18.0 - tick_t - k * (tick_t + 14.0)
        out.append(bar(cross_x, y, cross_x + tick_w, y + tick_t))
    return ''.join(out)


VARIANTS = [
    ('g-clean', u'01 · Чистая G', u'рамка, перекладина ниже середины, стойка',
     dict()),
    ('g-tick1', u'02 · G с риской', u'одна тонкая риска замера выше перекладины',
     dict(ticks=1)),
    ('g-tick2', u'03 · G с двумя рисками', u'ближе всего к прототипу',
     dict(ticks=2, tick_t=13.0)),
    ('g-open', u'04 · G без стойки', u'перекладина без хвоста — тише, но слабее',
     dict(stub=False, ticks=1)),
    ('g-deep', u'05 · G, перекладина ниже', u'ещё ниже: буква явнее',
     dict(cross_y=8.0, ticks=1)),
]


def mark_svg(body, px, col, bg):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-100 -100 200 200" '
            'style="height:%spx;width:%spx;background:%s;color:%s;'
            'border-radius:3px;padding:%spx;box-sizing:content-box">%s</svg>'
            % (px, px, bg, col, round(px * 0.22), body))


def lock_svg(body, px, col, bg):
    cap, gap = 52.0, 46.0
    ps, wide = word('GRIDEC', 500, cap, 0.13, x=100 + gap, y=cap / 2,
                    fill='currentColor', split=4, split_fill=TAIL)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-100 -100 %s 200" '
            'style="height:%spx;background:%s;color:%s;border-radius:3px;'
            'padding:%spx">%s%s</svg>'
            % (round(100 + gap + wide + 20, 1), px, bg, col, round(px * 0.3),
               body, ''.join(ps)))


os.makedirs(OUT, exist_ok=True)
rows = []
for name, title, note, kw in VARIANTS:
    body = window(**kw)
    io.open(os.path.join(OUT, name + '.svg'), 'w', encoding='utf-8').write(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-100 -100 200 200" '
        'color="%s">%s</svg>' % (INKB, body))
    cells = [mark_svg(body, 92, INKB, PAPER), mark_svg(body, 92, PAPER, INKB),
             mark_svg(body, 24, INKB, PAPER), mark_svg(body, 24, PAPER, INKB),
             mark_svg(body, 16, INKB, PAPER), lock_svg(body, 34, INKB, PAPER)]
    rows.append(u'<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>'
                u'<td>%s</td><td class="n"><b>%s</b><br><span>%s</span></td></tr>'
                % tuple(cells + [title, note]))

HTML = (u'<!doctype html><meta charset="utf-8"><title>Gridec — окно замера</title>'
        u'<style>body{margin:0;padding:30px 34px;background:#EFEAE1;color:#2B2722;'
        u'font:14px/1.45 -apple-system,Segoe UI,sans-serif}'
        u'h1{font-size:19px;font-weight:600;margin:0 0 6px}'
        u'p.lead{color:#8A8378;margin:0 0 22px;max-width:680px}'
        u'table{border-collapse:collapse}'
        u'td{padding:11px 16px 11px 0;vertical-align:middle;'
        u'border-bottom:1px solid rgba(43,39,34,.10)}'
        u'.n{white-space:nowrap}.n span{color:#8A8378;font-size:13px}'
        u'th{font:600 12px/1 -apple-system,sans-serif;color:#8A8378;'
        u'text-align:left;padding:0 16px 10px 0;letter-spacing:.06em}</style>'
        u'<h1>Gridec — окно замера, сдвиг линий</h1>'
        u'<p class="lead">Засечки убраны. Знак одноцветный: берёт цвет текста, '
        u'поэтому одинаково держится на бумаге и на чернилах. Сверху вниз — '
        u'нарастающий сдвиг линий; чем ниже линии, тем сильнее читается «G».</p>'
        u'<table><tr><th>светлый</th><th>тёмный</th><th>24</th><th>24</th>'
        u'<th>16</th><th>с именем</th><th></th></tr>%s</table>' % ''.join(rows))
io.open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(HTML)
print('%d вариантов -> %s' % (len(VARIANTS), OUT))
