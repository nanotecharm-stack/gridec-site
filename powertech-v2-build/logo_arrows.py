# -*- coding: utf-8 -*-
"""Три стрелки для знака Gridec — концепты на показ.

Владелец попросил «три стрелки, как у инженеров принято». В электротехнике это
векторная диаграмма трёхфазной сети: три вектора одной длины через 120°. Знак
такого рода не иллюстрирует ток, он ЦИТИРУЕТ чертёж, и человек, который такие
чертежи читает, узнаёт его без подписи.

Скрипт только рисует и складывает варианты на страницу сравнения. В сайт ничего
не попадает: сборка берёт локап из своего источника, и подмена знака — отдельный
шаг, уже после выбора.
"""
import io, os, math

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'logo-arrows')

INK = '#0D2440'      # плашка шапки, тёмный край
PAPER = '#EFEDEA'    # грунт страницы
BLUE = '#2E5E99'     # синий набора


def pt(cx, cy, r, ang):
    """Точка на радиусе r под углом ang (градусы, отсчёт против часовой)."""
    a = math.radians(ang)
    return (cx + r * math.cos(a), cy - r * math.sin(a))


def arrow(cx, cy, ang, r0, r1, tip, half, head):
    """Одна стрелка как ОДИН многоугольник: древко и голова слиты.

    Контур, а не обводка с треугольником сверху: обводка на маленьком размере
    округляется по-своему в каждом браузере, а залитая фигура остаётся той же
    формой на 16 пикселях и на баннере.
    """
    a = math.radians(ang)
    ux, uy = math.cos(a), -math.sin(a)      # вдоль стрелки
    px, py = -uy, ux                        # поперёк
    def P(along, across):
        return (cx + ux * along + px * across, cy + uy * along + py * across)
    pts = [P(r0, -half), P(r1, -half), P(r1, -head), P(tip, 0),
           P(r1, head), P(r1, half), P(r0, half)]
    return 'M' + 'L'.join('%.2f %.2f' % p for p in pts) + 'Z'


def star(cx=50, cy=50, scale=1.0, angles=(90, 210, 330)):
    """Векторная звезда: три стрелки из общего центра через 120°."""
    s = scale
    return ' '.join(arrow(cx, cy, a, 13 * s, 30 * s, 46 * s, 4.6 * s, 12.5 * s)
                    for a in angles)


def hexagon(cx=50, cy=50, r=46):
    pts = [pt(cx, cy, r, 90 + 60 * i) for i in range(6)]
    return 'M' + 'L'.join('%.2f %.2f' % p for p in pts) + 'Z'


def flow(cx=50, cy=50):
    """Три стрелки в ряд — направление потока, как на однолинейной схеме."""
    d = []
    for row, y in enumerate((26, 50, 74)):
        a = math.radians(0)
        ux, uy = math.cos(a), -math.sin(a)
        px, py = -uy, ux
        def P(along, across, y=y):
            return (14 + ux * along + px * across, y + uy * along + py * across)
        pts = [P(0, -4.6), P(46, -4.6), P(46, -12.5), P(72, 0),
               P(46, 12.5), P(46, 4.6), P(0, 4.6)]
        d.append('M' + 'L'.join('%.2f %.2f' % p for p in pts) + 'Z')
    return ' '.join(d)


# ---------------------------------------------------------------- варианты
def v_star():
    return '<path d="%s" fill="currentColor"/>' % star()


def v_star_hex():
    """Звезда внутри шестигранника — силуэт нынешнего знака сохраняется.

    Полезно тем, что значок в закладке и плашка в шапке не меняют габарит:
    меняется только то, что внутри.
    """
    return ('<path d="%s" fill="none" stroke="currentColor" stroke-width="5.5"'
            ' stroke-linejoin="miter"/>\n<path d="%s" fill="currentColor"/>'
            % (hexagon(), star(scale=0.62)))


def v_star_ring():
    """Звезда в круге — приборная шкала, а не коробка."""
    return ('<circle cx="50" cy="50" r="44" fill="none" stroke="currentColor"'
            ' stroke-width="5.5"/>\n<path d="%s" fill="currentColor"/>'
            % star(scale=0.66))


def v_flow():
    return '<path d="%s" fill="currentColor"/>' % flow()


VARIANTS = [
    ('star', 'Векторная звезда',
     'Три вектора одной длины через 120° — так трёхфазную сеть рисуют на бумаге. '
     'Знак ничем не занят, кроме самого себя.'),
    ('star-hex', 'Звезда в шестиграннике',
     'Тот же знак внутри силуэта нынешнего куба. Габарит в шапке и в закладке '
     'не меняется — меняется только начинка.'),
    ('star-ring', 'Звезда в круге',
     'Кольцо вместо грани: ближе к шкале прибора, чем к коробке.'),
    ('flow', 'Поток',
     'Три стрелки в ряд — направление, как на однолинейной схеме. '
     'Читается как «поток», а не как «три фазы».'),
]
BODY = {'star': v_star, 'star-hex': v_star_hex, 'star-ring': v_star_ring,
        'flow': v_flow}


def svg(name, size, color):
    return ('<svg viewBox="0 0 100 100" width="%d" height="%d" '
            'style="color:%s;display:block" xmlns="http://www.w3.org/2000/svg">'
            '%s</svg>' % (size, size, color, BODY[name]()))


os.makedirs(OUT, exist_ok=True)
for name, _, _ in VARIANTS:
    io.open(os.path.join(OUT, name + '.svg'), 'w', encoding='utf-8').write(
        '<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">%s</svg>'
        % BODY[name]().replace('currentColor', INK))

rows = []
for name, title, note in VARIANTS:
    cells = []
    # на бумаге и на плашке — оба грунта, на которых знак реально живёт
    for bg, fg, lab in ((PAPER, INK, 'на бумаге'), (INK, PAPER, 'на плашке')):
        sizes = ''.join(
            '<div class="sz"><div class="box" style="background:%s">%s</div>'
            '<b>%dpx</b></div>' % (bg, svg(name, s, fg), s)
            for s in (72, 40, 24, 16))
        cells.append('<div class="ground"><span class="lab">%s</span>'
                     '<div class="row">%s</div></div>' % (lab, sizes))
    rows.append(
        '<section><h2>%s</h2><p>%s</p>%s</section>' % (title, note, ''.join(cells)))

page = u"""<!doctype html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Gridec — три стрелки</title>
<style>
*{box-sizing:border-box}
body{margin:0;padding:40px 28px 80px;background:#F6F5F3;color:#0D0E13;
  font:15px/1.6 -apple-system,Segoe UI,Roboto,sans-serif}
h1{font-size:22px;margin:0 0 6px;letter-spacing:-.01em}
.sub{max-width:62ch;margin:0 0 38px;color:#5A5F66}
section{background:#fff;border:1px solid #E3E0DB;border-radius:3px;
  padding:22px 24px 26px;margin-bottom:22px;max-width:900px}
h2{font-size:16px;margin:0 0 4px}
section>p{margin:0 0 20px;color:#5A5F66;max-width:60ch;font-size:13.5px}
.ground{margin-bottom:14px}
.lab{font:11px/1 ui-monospace,Menlo,monospace;letter-spacing:.12em;
  text-transform:uppercase;color:#8A8F96}
.row{display:flex;align-items:flex-end;gap:22px;margin-top:8px}
.sz{text-align:center}
.box{display:flex;align-items:center;justify-content:center;
  width:104px;height:104px;border:1px solid #E3E0DB;border-radius:2px}
.sz b{display:block;margin-top:6px;font:11px/1 ui-monospace,Menlo,monospace;
  color:#8A8F96;font-weight:400}
</style></head><body>
<h1>Три стрелки — четыре подхода</h1>
<p class="sub">Каждый знак показан на бумаге и на тёмной плашке шапки, в четырёх
размерах. 24px — это размер в шапке сайта, 16px — значок вкладки браузера.
Если знак разваливается на 16, он не годится.</p>
%s
</body></html>""" % ''.join(rows)

path = os.path.join(OUT, 'preview.html')
io.open(path, 'w', encoding='utf-8').write(page)
print(path)
