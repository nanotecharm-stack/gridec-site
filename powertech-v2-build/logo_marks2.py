# -*- coding: utf-8 -*-
# Разбор присланных досок C и D. Ведущее направление — 08 «angular phase»:
# три лопасти под 120°, зазор в центре. Оно и есть схема «звезда» трёхфазной
# сети, только сказанная плотной формой, а не тонкой линией.
#
# Три требования владельца проверяются прямо в листе:
#   * знак читается и на светлом, и на тёмном — поэтому он ОДНОЦВЕТНЫЙ
#     (currentColor) и не зависит ни от плашки, ни от градиента;
#   * не теряется мелко — в листе есть кадры 24 и 16 пикселей;
#   * без имени даёт ассоциацию — три фазы, звезда, ротор.
#
#   python logo_marks2.py
#
# Пишет logo-v8/marks2/<имя>.svg и index.html.
import io
import math
import os

from logo_lib import word

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'logo-v8', 'marks2')

PAPER = '#F6F1E9'
INKB = '#0D2440'
ACC = '#4C8ACB'          # glow синей палитры: держится и на бумаге, и на чернилах
INK = '#141414'
TAIL = '#2E5E99'


def rot(p, a):
    c, s = math.cos(math.radians(a)), math.sin(math.radians(a))
    return (p[0] * c - p[1] * s, p[0] * s + p[1] * c)


def blade(a, r0=24.0, r1=98.0, w0=13.0, w1=30.0, tip=0.0):
    """Лопасть от центра наружу. tip срезает наружный угол — фаска."""
    pts = [(r0, -w0 / 2), (r1 - tip, -w1 / 2), (r1, -w1 / 2 + tip),
           (r1, w1 / 2 - tip), (r1 - tip, w1 / 2), (r0, w0 / 2)]
    pts = [rot(p, a) for p in pts]
    return ('M' + ' L'.join('%s %s' % (round(x, 2), round(y, 2)) for x, y in pts)
            + ' Z')


def fan(angles, col=None, **kw):
    f = ' fill="%s"' % col if col else ''
    return ''.join('<path%s d="%s"/>' % (f, blade(a, **kw)) for a in angles)


def ring_gap(r, w, gaps, rot0=0.0, col=None):
    """Кольцо с вырезами: дуги по кругу через равные промежутки."""
    out, n = [], len(gaps)
    f = ' fill="none" stroke="%s"' % col if col else ' fill="none" stroke="currentColor"'
    for a0, a1 in gaps:
        p0 = (r * math.cos(math.radians(a0 + rot0)), r * math.sin(math.radians(a0 + rot0)))
        p1 = (r * math.cos(math.radians(a1 + rot0)), r * math.sin(math.radians(a1 + rot0)))
        out.append('<path%s stroke-width="%s" stroke-linecap="butt" d="M%s %s '
                   'A%s %s 0 %d 1 %s %s"/>'
                   % (f, w, round(p0[0], 2), round(p0[1], 2), r, r,
                      1 if a1 - a0 > 180 else 0, round(p1[0], 2), round(p1[1], 2)))
    return ''.join(out)


# ------------------------------------------------------------------ варианты
def m_phase():
    """08 доведённая: одна лопасть вверх, две вниз. Зазор в центре — звезда."""
    return fan((-90, 30, 150))


def m_wye():
    """То же, повёрнуто: две лопасти вверх, одна вниз — буква «Y», схема звезды."""
    return fan((90, -30, -150))


def m_phase_acc():
    """Одна фаза выделена: акцент говорит, что фазы меряются по одной."""
    return fan((30, 150)) + fan((-90,), col=ACC)


def m_phase_short():
    """Одна лопасть короче: перекос фаз — то, что и ищет замер."""
    return fan((30, 150)) + fan((-90,), r1=70.0, w1=38.0)


def m_fold():
    """C-04 доведённая: три уровня, средний со ступенью. Отклонение по фазе."""
    return ('<path fill="currentColor" d="M-88 -62 L88 -62 L88 -40 L-88 -40 Z"/>'
            '<path fill="currentColor" d="M-88 -11 L18 -11 L54 25 L88 25 L88 47 '
            'L45 47 L9 11 L-88 11 Z"/>'
            '<path fill="currentColor" d="M-88 62 L40 62 L40 84 L-88 84 Z"/>')


def m_ref():
    """D-09 доведённая: эталон и факт. Верхняя линия ровная, нижняя ушла."""
    return ('<path fill="currentColor" d="M-90 -46 L90 -46 L90 -25 L-90 -25 Z"/>'
            '<path fill="none" stroke="currentColor" stroke-width="21" '
            'stroke-linecap="butt" d="M-90 22 L-16 22 Q14 22 26 46 Q38 70 68 70 L90 70"/>')


def m_gap():
    """07 доведённая: рамка с зазорами — поле замера, а не коробка."""
    return ('<path fill="none" stroke="currentColor" stroke-width="19" '
            'stroke-linecap="butt" d="M-30 -84 L54 -84 A30 30 0 0 1 84 -54 L84 30 '
            'M30 84 L-54 84 A30 30 0 0 1 -84 54 L-84 -30"/>')


def m_shift():
    """10 доведённая: угол сдвинут — отклонение от нормы, видимое глазом."""
    return ('<path fill="none" stroke="currentColor" stroke-width="19" '
            'stroke-linecap="butt" stroke-linejoin="miter" '
            'd="M-84 -60 L-84 84 L60 84 M-60 -84 L84 -84 L84 60"/>')


MARKS = [
    ('phase', u'01 · Фаза', u'08 доведённая: лопасть вверх, зазор в центре', m_phase),
    ('wye', u'02 · Звезда Y', u'повёрнута: читается как «Y» и как схема звезды', m_wye),
    ('phase-acc', u'03 · Фаза с акцентом', u'одна фаза выделена цветом', m_phase_acc),
    ('phase-short', u'04 · Перекос', u'одна лопасть короче — отклонение', m_phase_short),
    ('fold', u'05 · Ступень', u'три уровня, средний со ступенью', m_fold),
    ('ref', u'06 · Эталон и факт', u'ровная линия и ушедшая', m_ref),
    ('gap', u'07 · Зазор', u'07 доведённая: рамка с разрывами', m_gap),
    ('shift', u'08 · Сдвиг', u'10 доведённая: угол ушёл', m_shift),
]


def mark_svg(body, px, col, bg):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-100 -100 200 200" '
            'style="height:%spx;width:%spx;background:%s;color:%s;fill:currentColor;'
            'border-radius:3px;padding:%spx;box-sizing:content-box">%s</svg>'
            % (px, px, bg, col, round(px * 0.22), body))


def lock_svg(body, px, col, bg):
    """Знак плюс имя — как в шапке, одним цветом."""
    cap, gap = 52.0, 40.0
    ps, wide = word('GRIDEC', 500, cap, 0.13, x=200 + gap, y=cap / 2,
                    fill='currentColor', split=4, split_fill=TAIL)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-100 -100 %s 200" '
            'style="height:%spx;background:%s;color:%s;fill:currentColor;'
            'border-radius:3px;padding:%spx">%s%s</svg>'
            % (round(200 + gap + wide + 20, 1), px, bg, col, round(px * 0.3),
               body, ''.join(ps)))


os.makedirs(OUT, exist_ok=True)
rows = []
for name, title, note, fn in MARKS:
    body = fn()
    io.open(os.path.join(OUT, name + '.svg'), 'w', encoding='utf-8').write(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-100 -100 200 200" '
        'fill="%s">%s</svg>' % (INKB, body))
    cells = [mark_svg(body, 88, INKB, PAPER), mark_svg(body, 88, PAPER, INKB),
             mark_svg(body, 24, INKB, PAPER), mark_svg(body, 24, PAPER, INKB),
             mark_svg(body, 16, INKB, PAPER),
             lock_svg(body, 34, INKB, PAPER)]
    rows.append(u'<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td>'
                u'<td>%s</td><td class="n"><b>%s</b><br><span>%s</span></td></tr>'
                % tuple(cells + [title, note]))

HTML = (u'<!doctype html><meta charset="utf-8"><title>Gridec — знак, доработка</title>'
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
        u'<h1>Gridec — знак, доработка направления 08</h1>'
        u'<p class="lead">Знак ОДНОЦВЕТНЫЙ: ни плашки, ни градиента. Поэтому он '
        u'одинаково держится на бумаге и на чернилах и не зависит от фона. '
        u'Колонки: крупно на светлом, крупно на тёмном, 24 пикселя на обоих, '
        u'16 пикселей, и с именем в размере шапки.</p>'
        u'<table><tr><th>светлый</th><th>тёмный</th><th>24</th><th>24</th>'
        u'<th>16</th><th>с именем</th><th></th></tr>%s</table>' % ''.join(rows))
io.open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(HTML)
print('%d вариантов -> %s' % (len(MARKS), OUT))
