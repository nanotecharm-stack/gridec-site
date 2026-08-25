# -*- coding: utf-8 -*-
# Заготовки знака: буквенные (из «G») и сигнальные (из формы кривой).
# Все рисуются в одном поле -100..100, тем же светом и на той же плашке,
# поэтому их можно честно сравнивать между собой.
#
#   python logo_marks.py
#
# Пишет logo-v8/marks/<имя>.svg и index.html — лист сравнения.
import io
import math
import os

from logo_lib import faces, word

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'logo-v8', 'marks')

PLATE = ('#162E52', '#0D2440')
LIGHT = '#F4F6F8'
BLUE = '#7BA4D0'
MID = '#A9BED6'
INK = '#141414'
TAIL = '#2E5E99'
SW = 19.0                       # толщина линии: читается на двадцати пикселях


def sine(x0, x1, amp, periods, phase=0.0, clip=None, n=64):
    """Синусоида точками. clip срезает гребень — это искажение формы."""
    pts = []
    for i in range(n + 1):
        t = i / n
        x = x0 + (x1 - x0) * t
        y = -amp * math.sin(2 * math.pi * periods * t + phase)
        if clip is not None:
            y = max(-clip, min(clip, y))
        pts.append('%s %s' % (round(x, 2), round(y, 2)))
    return 'M' + ' L'.join(pts)


def stroke(d, col=LIGHT, w=SW, cap='round'):
    return ('<path d="%s" fill="none" stroke="%s" stroke-width="%s" '
            'stroke-linecap="%s" stroke-linejoin="round"/>' % (d, col, w, cap))


def arc(r, a0, a1, large, sweep):
    p0 = (r * math.cos(math.radians(a0)), r * math.sin(math.radians(a0)))
    p1 = (r * math.cos(math.radians(a1)), r * math.sin(math.radians(a1)))
    return ('M%s %s A%s %s 0 %d %d %s %s'
            % (round(p0[0], 2), round(p0[1], 2), r, r, large, sweep,
               round(p1[0], 2), round(p1[1], 2)))


# ---------------------------------------------------------------- буквенные
#
# Буква берётся ИЗ ШРИФТА НАЗВАНИЯ, а не рисуется кругом с перекладиной. Круг
# читался как «e»: у «e» перекладина посередине, у «G» — ниже, и на двадцати
# пикселях эта разница пропадала. Глиф Outfit снимает вопрос: это ровно та же
# буква, что стоит в имени, и она узнаётся сама.
def glyph(ch, weight, cap_units, dx=0.0, dy=0.0, col=LIGHT):
    """Буква из шрифта, посаженная в центр поля -100..100."""
    ps, wide = word(ch, weight, cap_units, fill=col)
    return ('<g transform="translate(%s %s)">%s</g>'
            % (round(-wide / 2 + dx, 2), round(cap_units / 2 + dy, 2), ''.join(ps)))


def m_g():
    """«G» из Outfit — та же буква, что в имени."""
    return glyph('G', 600, 150)


def m_g_wave():
    """«G», в чаше — форма кривой: имя снаружи, дело внутри."""
    return glyph('G', 600, 150) + stroke(sine(-26, 40, 17, 1, phase=3.14), BLUE, 11)


def m_g_cut():
    """«G», разрезанная линией замера: буква и отсчёт в одном знаке."""
    return ('<defs><mask id="cut"><rect x="-100" y="-100" width="200" height="200" '
            'fill="#fff"/><rect x="-100" y="-9" width="200" height="18" '
            'fill="#000"/></mask></defs>'
            + '<g mask="url(#cut)">%s</g>' % glyph('G', 600, 150)
            + stroke('M-92 0 L92 0', BLUE, 9, cap='butt'))


def m_gc():
    """«G» и «C» — первая и последняя буквы имени, вложены друг в друга."""
    return glyph('C', 600, 150, col=BLUE) + glyph('G', 600, 96, dx=6)


# --------------------------------------------------------------- сигнальные
def w_clip():
    """Гребень срезан: форма кривой испорчена. Это и есть предмет работы."""
    return (stroke('M-88 0 L88 0', 'rgba(244,246,248,.28)', 7)
            + stroke(sine(-84, 84, 62, 1, clip=44), LIGHT, SW))


def w_dip():
    """Провал напряжения: линия держится, падает и возвращается."""
    return stroke('M-88 -40 L-30 -40 L-30 38 L26 38 L26 -40 L88 -40')


def w_star():
    """Звезда: три луча из центра под 120°. Схема соединения трёхфазной сети."""
    r, out = 78.0, []
    for i, a in enumerate((90, 210, 330)):
        x = round(r * math.cos(math.radians(a - 90)), 2)
        y = round(r * math.sin(math.radians(a - 90)), 2)
        out.append(stroke('M0 0 L%s %s' % (x, y), (BLUE if i == 0 else LIGHT), 20))
    return ''.join(out)


def w_grid():
    """Узел сети: перекрестье и точка замера на нём."""
    return (stroke('M-86 -30 L86 -30 M-86 30 L86 30 M-40 -86 L-40 86 '
                   'M40 -86 L40 86', 'rgba(244,246,248,.45)', 9)
            + '<circle cx="-40" cy="-30" r="21" fill="%s"/>' % BLUE)


def cube():
    """Нынешний знак — для сравнения."""
    cols = (('#C6C6C6', '#9A9A9A'), ('#F6F6F6', '#D2D2D2'), ('#FFFFFF', '#E4E4E4'))
    return ''.join('<path fill="%s" d="%s"/>' % (c[1], d)
                   for c, d in zip(cols, faces(12.0)))


MARKS = [
    ('cube', u'Нынешний знак — куб', u'три грани, звезда в центре', cube),
    ('m-g', u'G из шрифта имени', u'знак без имени = буква имени', m_g),
    ('m-g-wave', u'G, в чаше кривая', u'имя снаружи, дело внутри', m_g_wave),
    ('m-g-cut', u'G, разрезанная линией замера', u'буква и отсчёт в одном', m_g_cut),
    ('m-gc', u'G в C', u'первая и последняя буквы имени', m_gc),
    ('w-clip', u'Срезанный гребень', u'испорченная форма кривой', w_clip),
    ('w-dip', u'Провал напряжения', u'то же, что показывает герой сайта', w_dip),
    ('w-star', u'Звезда', u'три луча из центра: схема «звезда»', w_star),
    ('w-grid', u'Узел сети', u'перекрестье и точка замера', w_grid),
]

TILE, PAD, CAP = 96.0, 8.0, 52.0
GRAD = ('<defs><linearGradient id="bg" x1="0" y1="0" x2="0.55" y2="1">'
        '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/>'
        '</linearGradient>'
        '<linearGradient id="sn" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#FFFFFF" stop-opacity="0.16"/>'
        '<stop offset="0.5" stop-color="#FFFFFF" stop-opacity="0"/>'
        '<stop offset="1" stop-color="#000000" stop-opacity="0.20"/>'
        '</linearGradient></defs>' % PLATE)


def plate_svg(body, size=0.66, wordmark=False):
    """Знак на плашке; при wordmark — плюс имя справа, как в шапке."""
    k = TILE * size / 200.0
    c = PAD + TILE / 2
    rect = 'x="%s" y="%s" width="%s" height="%s" rx="%s"' % (PAD, PAD, TILE, TILE,
                                                            round(TILE * .24, 1))
    out = [GRAD, '<rect %s fill="url(#bg)"/>' % rect,
           '<g transform="translate(%s %s) scale(%s)">%s</g>'
           % (c, c, round(k, 5), body),
           '<rect %s fill="url(#sn)"/>' % rect]
    w = PAD + TILE + PAD
    if wordmark:
        gap = TILE * 0.28
        ps, wide = word('GRIDEC', 500, CAP, 0.13, x=PAD + TILE + gap,
                        y=c + CAP / 2, fill=INK, split=4, split_fill=TAIL)
        out.append(''.join(ps))
        w = PAD + TILE + gap + wide + PAD
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s %s">%s</svg>'
            % (round(w, 2), PAD * 2 + TILE, ''.join(out)))


os.makedirs(OUT, exist_ok=True)
rows = []
for name, title, note, fn in MARKS:
    body = fn()
    io.open(os.path.join(OUT, name + '.svg'), 'w', encoding='utf-8').write(
        plate_svg(body))
    big = plate_svg(body).replace('<svg ', '<svg style="height:92px" ', 1)
    line = plate_svg(body, wordmark=True).replace(
        '<svg ', '<svg style="height:38px" ', 1)
    tiny = plate_svg(body).replace('<svg ', '<svg style="height:22px" ', 1)
    rows.append(u'<tr><td>%s</td><td>%s</td><td>%s</td>'
                u'<td class="n"><b>%s</b><br><span>%s</span></td></tr>'
                % (big, line, tiny, title, note))

HTML = (u'<!doctype html><meta charset="utf-8"><title>Gridec — заготовки знака</title>'
        u'<style>body{margin:0;padding:30px 34px;background:#F6F1E9;color:#2B2722;'
        u'font:14px/1.45 -apple-system,Segoe UI,sans-serif}'
        u'h1{font-size:19px;font-weight:600;margin:0 0 6px}'
        u'p.lead{color:#8A8378;margin:0 0 22px;max-width:640px}'
        u'table{border-collapse:collapse}'
        u'td{padding:12px 20px 12px 0;vertical-align:middle;'
        u'border-bottom:1px solid rgba(43,39,34,.10)}'
        u'.n{white-space:nowrap}.n span{color:#8A8378;font-size:13px}</style>'
        u'<h1>Gridec — заготовки знака</h1>'
        u'<p class="lead">Слева направо: знак крупно, знак с именем в размере шапки, '
        u'знак в 22 пикселя. Верхние четыре — буквенные: знак без имени читается '
        u'как «G». Нижние четыре — сигнальные: знак говорит о предмете работы.</p>'
        u'<table>%s</table>' % ''.join(rows))
io.open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(HTML)
print('%d заготовок -> %s' % (len(MARKS), OUT))
