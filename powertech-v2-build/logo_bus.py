# -*- coding: utf-8 -*-
# Шина как язык знака. Из ориентира взята мысль, а не картинка: проводник,
# фаска 45°, площадка на конце. Правила разводки соблюдаются как на плате —
# только 0°, 45° и 90°, углы срезаны, ширина одна на всю дорожку.
#
# Отсюда два применения:
#   ЗНАК — буква «G» разведена одной дорожкой, на концах площадки;
#   ПОДЛОЖКА — веер дорожек за именем, гаснущий к центру, чтобы имя читалось.
#
# Знак одноцветный: берёт цвет текста и потому одинаково живёт на бумаге и на
# чернилах. Подложка задаётся прозрачностью от того же цвета — она не знает,
# светлый под ней фон или тёмный.
#
#   python logo_bus.py
#
# Пишет logo-v8/bus/*.svg и index.html.
import io
import math
import os

from logo_lib import word

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'logo-v8', 'bus')

PAPER = '#F6F1E9'
INKB = '#0D2440'
ACC = '#4C8ACB'
TAIL = '#2E5E99'


def chamfer(pts, c):
    """Полилиния со срезанными углами: настоящая разводка не знает прямых углов."""
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        p0, p1, p2 = pts[i - 1], pts[i], pts[i + 1]
        # порядок важен: сперва точка со стороны ВХОДА, потом со стороны выхода
        for q in (p0, p2):
            dx, dy = q[0] - p1[0], q[1] - p1[1]
            L = math.hypot(dx, dy)
            k = min(c, L / 2) / L
            out.append((round(p1[0] + dx * k, 2), round(p1[1] + dy * k, 2)))
    out.append(pts[-1])
    return out


def trace(pts, w=22.0, c=20.0, col='currentColor', op=1.0, cap='butt'):
    p = chamfer(pts, c)
    d = 'M' + ' L'.join('%s %s' % (x, y) for x, y in p)
    return ('<path fill="none" stroke="%s" stroke-opacity="%s" stroke-width="%s" '
            'stroke-linecap="%s" stroke-linejoin="miter" d="%s"/>'
            % (col, op, w, cap, d))


def pad(x, y, r=17.0, hole=7.0, col='currentColor', op=1.0):
    """Площадка с отверстием — переходное отверстие платы."""
    return ('<path fill="%s" fill-opacity="%s" fill-rule="evenodd" d="'
            'M%s %s m-%s 0 a%s %s 0 1 0 %s 0 a%s %s 0 1 0 -%s 0 '
            'M%s %s m-%s 0 a%s %s 0 1 1 %s 0 a%s %s 0 1 1 -%s 0 Z"/>'
            % (col, op, x, y, r, r, r, 2 * r, r, r, 2 * r,
               x, y, hole, hole, hole, 2 * hole, hole, hole, 2 * hole))


def dot(x, y, r=11.0, col='currentColor', op=1.0):
    return '<circle cx="%s" cy="%s" r="%s" fill="%s" fill-opacity="%s"/>' % (
        x, y, r, col, op)


# ------------------------------------------------------------------- знак
G_PATH = [(60, -60), (-58, -60), (-58, 60), (60, 60), (60, 6), (-4, 6)]


def m_g_trace(w=22.0, c=22.0, pads=True):
    """«G» одной дорожкой: сверху направо открыта, углы срезаны."""
    out = [trace(G_PATH, w, c)]
    if pads:
        out.append(pad(60, -60))
        out.append(pad(-4, 6))
    return ''.join(out)


def m_g_via():
    """То же, но конец перекладины — площадка в акценте: точка замера."""
    return (trace(G_PATH, 22.0, 22.0) + pad(60, -60)
            + pad(-4, 6, col=ACC) + dot(-4, 6, 6, col=ACC))


def m_node():
    """Узел шины: три дорожки сходятся на одной площадке."""
    return (trace([(-88, -44), (-30, -44), (0, -14), (0, 0)], 20, 18)
            + trace([(88, -44), (30, -44), (0, -14)], 20, 18)
            + trace([(0, 0), (0, 62)], 20, 18)
            + pad(0, 0, 22, 9) + dot(-88, -44, 10) + dot(88, -44, 10)
            + dot(0, 62, 10))


MARKS = [('bus-g', u'01 · G дорожкой', u'буква имени, разведённая как шина',
          m_g_trace),
         ('bus-g-via', u'02 · G с точкой замера', u'конец перекладины — площадка',
          m_g_via),
         ('bus-node', u'03 · Узел шины', u'три дорожки на одной площадке', m_node)]


# --------------------------------------------------------------- подложка
def field(w, h, op=0.16, acc_op=0.5):
    """Веер дорожек. Гаснет к середине — там стоит имя."""
    out = ['<defs><radialGradient id="fade" cx="0.5" cy="0.5" r="0.62">'
           '<stop offset="0" stop-color="#000"/>'
           '<stop offset="0.42" stop-color="#000"/>'
           '<stop offset="1" stop-color="#fff"/></radialGradient>'
           '<mask id="mf"><rect x="0" y="0" width="%s" height="%s" '
           'fill="url(#fade)"/></mask></defs><g mask="url(#mf)">' % (w, h)]
    cx, cy = w / 2, h / 2
    # дорожки уходят по диагонали от центра: слева вверх, справа вниз
    plan = [(-1, -1, 0.86, 0), (-1, -1, 0.62, 74), (-1, -1, 0.44, 150),
            (-1, 1, 0.78, 40), (-1, 1, 0.52, 116),
            (1, 1, 0.86, 0), (1, 1, 0.62, 74), (1, 1, 0.44, 150),
            (1, -1, 0.78, 40), (1, -1, 0.52, 116)]
    for i, (sx, sy, reach, off) in enumerate(plan):
        x0 = cx + sx * (140 + off)
        y0 = cy + sy * 26
        d = reach * cx
        x1 = x0 + sx * d * 0.42
        y1 = y0 + sy * d * 0.42
        x2 = x1 + sx * d * 0.58
        y2 = y1
        col = ACC if i in (1, 6) else 'currentColor'
        o = acc_op if col == ACC else op
        out.append(trace([(round(x0), round(y0)), (round(x1), round(y1)),
                          (round(x2), round(y2))], 7.0, 22.0, col, o))
        out.append(dot(round(x2), round(y2), 7, col, o))
    out.append('</g>')
    return ''.join(out)


def lockup(px, col, bg, mark=m_g_trace, back=True):
    """Имя, знак и — при back — веер дорожек за ними."""
    W, H = 1180.0, 380.0
    cap, gap = 132.0, 74.0
    ps, wide = word('GRIDEC', 500, cap, 0.13, fill='currentColor',
                    split=4, split_fill=TAIL)
    mw = 196.0
    total = mw + gap + wide
    x0 = (W - total) / 2
    body = field(W, H) if back else ''
    body += ('<g transform="translate(%s %s) scale(%s)">%s</g>'
             % (round(x0 + mw / 2, 1), H / 2, round(mw / 200.0, 4), mark()))
    ps, _ = word('GRIDEC', 500, cap, 0.13, x=x0 + mw + gap, y=H / 2 + cap / 2,
                 fill='currentColor', split=4, split_fill=TAIL)
    body += ''.join(ps)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s %s" '
            'style="height:%spx;background:%s;color:%s;border-radius:4px">%s</svg>'
            % (W, H, px, bg, col, body))


def mark_svg(body, px, col, bg):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-100 -100 200 200" '
            'style="height:%spx;width:%spx;background:%s;color:%s;'
            'border-radius:3px;padding:%spx;box-sizing:content-box">%s</svg>'
            % (px, px, bg, col, round(px * 0.2), body))


os.makedirs(OUT, exist_ok=True)
rows = []
for name, title, note, fn in MARKS:
    body = fn()
    io.open(os.path.join(OUT, name + '.svg'), 'w', encoding='utf-8').write(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-100 -100 200 200" '
        'color="%s">%s</svg>' % (INKB, body))
    cells = [mark_svg(body, 92, INKB, PAPER), mark_svg(body, 92, PAPER, INKB),
             mark_svg(body, 24, INKB, PAPER), mark_svg(body, 24, PAPER, INKB),
             mark_svg(body, 16, INKB, PAPER)]
    rows.append(u'<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>'
                u'<td class="n"><b>%s</b><br><span>%s</span></td></tr>'
                % tuple(cells + [title, note]))

for name, col, bg in (('lockup-light', INKB, PAPER), ('lockup-dark', PAPER, INKB)):
    io.open(os.path.join(OUT, name + '.svg'), 'w', encoding='utf-8').write(
        lockup(0, col, bg).replace('style="height:0px;', 'style="'))

HTML = (u'<!doctype html><meta charset="utf-8"><title>Gridec — шина</title>'
        u'<style>body{margin:0;padding:30px 34px;background:#EFEAE1;color:#2B2722;'
        u'font:14px/1.45 -apple-system,Segoe UI,sans-serif}'
        u'h1{font-size:19px;font-weight:600;margin:0 0 6px}'
        u'h2{font-size:15px;font-weight:600;margin:28px 0 10px}'
        u'p.lead{color:#8A8378;margin:0 0 22px;max-width:700px}'
        u'table{border-collapse:collapse}'
        u'td{padding:11px 16px 11px 0;vertical-align:middle;'
        u'border-bottom:1px solid rgba(43,39,34,.10)}'
        u'.n{white-space:nowrap}.n span{color:#8A8378;font-size:13px}'
        u'th{font:600 12px/1 -apple-system,sans-serif;color:#8A8378;'
        u'text-align:left;padding:0 16px 10px 0;letter-spacing:.06em}'
        u'.row{display:flex;gap:18px;flex-wrap:wrap;align-items:center}</style>'
        u'<h1>Gridec — шина: знак и подложка</h1>'
        u'<p class="lead">Правила разводки соблюдены: только 0°, 45° и 90°, углы '
        u'срезаны фаской, ширина дорожки одна. Знак одноцветный — берёт цвет '
        u'текста. Подложка задана прозрачностью того же цвета и гаснет к центру, '
        u'чтобы имя оставалось первым.</p>'
        u'<h2>Знак</h2>'
        u'<table><tr><th>светлый</th><th>тёмный</th><th>24</th><th>24</th>'
        u'<th>16</th><th></th></tr>%s</table>'
        u'<h2>Подложка с именем</h2><div class="row">%s%s</div>'
        u'<h2>То же в размере шапки</h2><div class="row">%s%s</div>'
        % (''.join(rows),
           lockup(140, INKB, PAPER), lockup(140, PAPER, INKB),
           lockup(46, INKB, PAPER), lockup(46, PAPER, INKB)))
io.open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(HTML)
print('знак + подложка -> %s' % OUT)
