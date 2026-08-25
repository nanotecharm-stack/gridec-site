# -*- coding: utf-8 -*-
# Локап на шине. Одна мысль на весь знак: шина входит слева на площадки,
# проходит ЗА именем и веером уходит вправо за край.
#
# Что сделано ровным против присланного фрагмента:
#   * площадки стоят столбиком с одинаковым шагом, а не вразнобой;
#   * дорожки — параллельный пучок: одна ломаная, сдвинутая на равный шаг,
#     то есть настоящая шина, а не набор случайных линий;
#   * повороты только 45°, углы срезаны фаской одной величины;
#   * ширина дорожки и радиус площадки одни на весь рисунок.
#
# За именем дорожки гаснут до подложки, у площадок — живые: у разъёма шина
# видна, под компонентом уходит в фон. Имя остаётся первым.
#
#   python logo_bus2.py
#
# Пишет logo-v8/bus2/*.svg и index.html.
import io
import os

from logo_bus import chamfer
from logo_lib import word

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'logo-v8', 'bus2')

PAPER = '#F6F1E9'
INKB = '#0D2440'
ACC = '#2E5E99'
GLOW = '#4C8ACB'

CH = 26.0            # фаска: одна на весь язык


def path(pts, w, c=CH, col='currentColor', op=1.0, clip=None):
    p = chamfer(pts, c)
    return ('<path%s fill="none" stroke="%s" stroke-opacity="%s" '
            'stroke-width="%s" stroke-linecap="butt" stroke-linejoin="miter" '
            'd="M%s"/>'
            % (' clip-path="url(#%s)"' % clip if clip else '', col, op, w,
               ' L'.join('%s %s' % (round(x, 1), round(y, 1)) for x, y in p)))


def pad(x, y, r, hole, col='currentColor', op=1.0):
    return ('<path fill="%s" fill-opacity="%s" fill-rule="evenodd" d="'
            'M%s %s m-%s 0 a%s %s 0 1 0 %s 0 a%s %s 0 1 0 -%s 0 '
            'M%s %s m-%s 0 a%s %s 0 1 1 %s 0 a%s %s 0 1 1 -%s 0 Z"/>'
            % (col, op, x, y, r, r, r, 2 * r, r, r, 2 * r,
               x, y, hole, hole, hole, 2 * hole, hole, hole, 2 * hole))


# --------------------------------------------------------------------- знак
def mark(n=4, w=13.0, acc=1, accent=ACC, span=200.0):
    """Пучок из n дорожек: площадка, прямой участок, подъём 45° за край.

    Шаг между дорожками один, поэтому пучок читается как шина, а не как
    набор линий. Число дорожек — параметр: мелким кадрам нужно меньше.
    """
    k = span / 200.0
    step = 112.0 / max(n - 1, 1)
    y0 = -56.0
    out = []
    for i in range(n):
        y = y0 + i * step
        col = accent if i == acc else 'currentColor'
        out.append(path([(-64, y), (-26, y), (-26 + 190, y - 190)], w, CH, col))
        out.append(pad(-64, y, w * 0.86, w * 0.34, col))
    return ('<g transform="scale(%s)" clip-path="url(#mk)">%s</g>'
            '<defs><clipPath id="mk"><rect x="%s" y="%s" width="%s" height="%s" '
            'rx="6"/></clipPath></defs>'
            % (round(k, 4), ''.join(out), -100 / k, -100 / k, 200 / k, 200 / k))


def mark_svg(px, col, bg, n=4):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-100 -100 200 200" '
            'style="height:%spx;width:%spx;background:%s;color:%s;'
            'border-radius:3px;padding:%spx;box-sizing:content-box">%s</svg>'
            % (px, px, bg, col, round(px * 0.18),
               mark(n, 13.0 if n > 2 else 17.0)))


# ------------------------------------------------------------------- локап
def lockup(px, col, bg, back=True):
    """Площадки слева, имя по центру, шина проходит за именем и уходит вправо."""
    W, H = 1720.0, 460.0
    cap = 150.0
    cy = H / 2
    ps, wide = word('GRIDEC', 500, cap, 0.13)
    mk = 300.0                      # поле знака слева
    x_name = 150.0 + mk + 96.0
    base = cy + cap / 2
    acc = ACC if bg == PAPER else GLOW

    body = ['<defs>'
            '<clipPath id="live"><rect x="0" y="0" width="%s" height="%s"/>'
            '</clipPath>'
            '<clipPath id="under"><rect x="%s" y="0" width="%s" height="%s"/>'
            '</clipPath></defs>' % (x_name - 40, H, x_name - 40,
                                    W - x_name + 40, H)]
    # пять дорожек с ОДНИМ шагом: две проходят выше прописных, две ниже
    # базовой линии, средняя идёт прямо за именем — она и делает подложку
    n = 5
    step = 67.0
    for i in range(n):
        y = cy - 2 * step + i * step
        col_i = acc if i == 1 else 'currentColor'
        # одна ломаная: прямой участок до конца имени, затем подъём 45°
        turn = x_name + wide + 34 + i * 62
        pts = [(150.0, y), (turn, y), (turn + 420, y - 420)]
        # у площадок дорожка живая, дальше — подложка
        body.append(path(pts, 11.0, CH, col_i, 0.92, clip='live'))
        if back:
            # за именем дорожка гаснет; средняя — сильнее прочих, она идёт
            # прямо по буквам, и на 0.3 читалась бы как зачёркивание
            dim = 0.24 if col_i == 'currentColor' else 0.34
            if i == 2:
                dim *= 0.62
            body.append(path(pts, 11.0, CH, col_i, round(dim, 2), clip='under'))
        body.append(pad(150.0, y, 15.0, 6.0, col_i, 0.92))
    ps, _ = word('GRIDEC', 500, cap, 0.13, x=x_name, y=base,
                 fill='currentColor', split=4, split_fill=acc)
    body.append(''.join(ps))
    style = 'background:%s;color:%s;border-radius:4px' % (bg, col)
    if px:
        style = 'height:%spx;%s' % (px, style)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s %s" '
            'style="%s">%s</svg>' % (W, H, style, ''.join(body)))


os.makedirs(OUT, exist_ok=True)
for name, col, bg in (('lockup-light', INKB, PAPER), ('lockup-dark', PAPER, INKB)):
    io.open(os.path.join(OUT, name + '.svg'), 'w', encoding='utf-8').write(
        lockup(0, col, bg))
for name, col, n in (('mark', INKB, 4), ('mark-small', INKB, 2)):
    io.open(os.path.join(OUT, name + '.svg'), 'w', encoding='utf-8').write(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-100 -100 200 200" '
        'color="%s">%s</svg>' % (col, mark(n, 13.0 if n > 2 else 17.0)))
print('локап и знак -> %s' % OUT)

HTML = (u'<!doctype html><meta charset="utf-8"><title>Gridec — шина</title>'
        u'<style>body{margin:0;padding:28px 32px;background:#EFEAE1;color:#2B2722;'
        u'font:14px/1.45 -apple-system,Segoe UI,sans-serif}'
        u'h1{font-size:19px;font-weight:600;margin:0 0 6px}'
        u'h2{font-size:15px;font-weight:600;margin:26px 0 10px}'
        u'p{color:#8A8378;margin:0 0 18px;max-width:720px}'
        u'.col{display:flex;flex-direction:column;gap:16px;max-width:980px}'
        u'.row{display:flex;gap:16px;align-items:center;flex-wrap:wrap}</style>'
        u'<h1>Gridec — шина за именем</h1>'
        u'<p>Шина входит слева на площадки, проходит за именем и веером уходит '
        u'вправо. У площадок дорожки живые, под именем гаснут до подложки — имя '
        u'остаётся первым. Повороты только 45°, фаска одна, шаг между дорожками '
        u'один: это пучок, а не набор линий.</p>'
        u'<div class="col">%s%s</div>'
        u'<h2>В размере шапки</h2><div class="row">%s%s</div>'
        u'<h2>Знак отдельно: 92, 40, 24 и 16 пикселей</h2><div class="row">'
        u'%s%s%s%s %s%s</div>'
        u'<p>На 16 пикселях четыре дорожки сливаются, поэтому для иконок есть '
        u'урезанный кадр — две дорожки и площадки крупнее.</p>'
        % (lockup(190, INKB, PAPER), lockup(190, PAPER, INKB),
           lockup(46, INKB, PAPER), lockup(46, PAPER, INKB),
           mark_svg(92, INKB, PAPER), mark_svg(92, PAPER, INKB),
           mark_svg(40, INKB, PAPER), mark_svg(24, INKB, PAPER),
           mark_svg(16, INKB, PAPER), mark_svg(16, INKB, PAPER, n=2)))
io.open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(HTML)
print('index.html')
