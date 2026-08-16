# -*- coding: utf-8 -*-
"""Значок вкладки: буква G из того же шрифта, той же пиксельной сеткой.

В шапке сайта куба больше нет, а во вкладке он всё ещё стоял. Значок заменяется
буквой — той САМОЙ буквой G из Departure Mono, а не похожей: её сетка снята
растеризацией глифа и записана ниже как есть, 5 на 8.

Рисуем прямоугольниками, а не шрифтом. У значка нет доступа к нашему шрифту, и
на 16 пикселях сглаживание всё равно съело бы рисунок; квадраты же ложатся на
пиксель точно и остаются собой в любом размере.

Одно правило держит все размеры вместе: высота буквы — ровно половина значка,
клетка — размер значка, делённый на шестнадцать. Поэтому 16, 32 и 180 выглядят
одинаково, а не «каждый по-своему».
"""
import io, os, struct

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))

# Снято растеризацией глифа «G» из Departure Mono: клетка шрифта = клетка здесь.
G = [
    '.###.',
    '#...#',
    '#....',
    '#....',
    '#..##',
    '#...#',
    '#...#',
    '.###.',
]
GW, GH = len(G[0]), len(G)

PLATE = (13, 36, 64, 255)      # #0D2440
FG = (246, 241, 233, 255)      # #F6F1E9


def runs():
    """Горизонтальные отрезки закрашенных клеток — чтобы фигур было меньше."""
    for r, row in enumerate(G):
        c = 0
        while c < GW:
            if row[c] == '#':
                s = c
                while c < GW and row[c] == '#':
                    c += 1
                yield s, r, c - s
            else:
                c += 1


# ------------------------------------------------------------------- SVG
def svg():
    rects = ''.join(
        '<rect x="%d" y="%d" width="%d" height="1" fill="#F6F1E9"/>'
        % (5 + s, 4 + r, w) for s, r, w in runs())
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" '
            'shape-rendering="crispEdges">'
            '<rect width="16" height="16" rx="2" fill="#0D2440"/>%s</svg>' % rects)


# ------------------------------------------------------------------- PNG
from PIL import Image, ImageDraw


def png(size, radius=None):
    """Значок в заданном размере. Клетка — size/16, буква — половина высоты."""
    u = size / 16.0
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if radius is None:
        radius = max(1, int(round(2 * u)))
    if radius:
        d.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=PLATE)
    else:
        d.rectangle([0, 0, size - 1, size - 1], fill=PLATE)
    # Начало буквы считаем в КЛЕТКАХ и только потом переводим в пиксели: так
    # рисунок садится на сетку в каждом размере, а не только в шестнадцати.
    x0, y0 = (16 - GW) // 2, (16 - GH) // 2
    for s, r, w in runs():
        x = int(round((x0 + s) * u))
        y = int(round((y0 + r) * u))
        d.rectangle([x, y, int(round((x0 + s + w) * u)) - 1,
                     int(round((y0 + r + 1) * u)) - 1], fill=FG)
    return img


def ico(path, sizes=(16, 32, 48)):
    """Файл .ico кадрами PNG — так его читают все нынешние браузеры."""
    frames = []
    for s in sizes:
        b = io.BytesIO()
        png(s).save(b, format='PNG')
        frames.append((s, b.getvalue()))
    out = io.BytesIO()
    out.write(struct.pack('<HHH', 0, 1, len(frames)))
    off = 6 + 16 * len(frames)
    for s, data in frames:
        out.write(struct.pack('<BBBBHHII', s if s < 256 else 0,
                              s if s < 256 else 0, 0, 0, 1, 32,
                              len(data), off))
        off += len(data)
    for _, data in frames:
        out.write(data)
    io.open(path, 'wb').write(out.getvalue())


io.open(os.path.join(ROOT, 'favicon.svg'), 'w', encoding='utf-8').write(svg())
ico(os.path.join(ROOT, 'favicon.ico'))
# apple-touch-icon: iOS сам скругляет углы, поэтому плашка здесь квадратная.
png(180, radius=0).save(os.path.join(ROOT, 'apple-touch-icon.png'))

for p in ('favicon.svg', 'favicon.ico', 'apple-touch-icon.png'):
    print(p, os.path.getsize(os.path.join(ROOT, p)), 'bytes')

# Кадры разворота — те же квадраты, но столбцы открываются слева направо.
# Отдаём их в разметку строкой, чтобы страница не считала их сама.
frames = []
for k in range(GW + 1):
    rects = ''.join(
        '<rect x="%d" y="%d" width="%d" height="1" fill="#F6F1E9"/>'
        % (5 + s, 4 + r, min(w, k - s))
        for s, r, w in runs() if s < k)
    frames.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 16 16" '
                  'shape-rendering="crispEdges">'
                  '<rect width="16" height="16" rx="2" fill="#0D2440"/>%s</svg>'
                  % rects)
io.open(os.path.join(HERE, 'logo-arrows', '_favicon-frames.txt'), 'w',
        encoding='utf-8').write('\n'.join(frames))
print('кадров разворота:', len(frames))
