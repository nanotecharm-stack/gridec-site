# -*- coding: utf-8 -*-
"""Знак Gridec из ВЕКТОРА, а не из набора текста.

Почему не текстом. Departure Mono — пиксельный шрифт: em равен 550 единицам,
сетка — 50 единиц, то есть 11 точек на em. Литера ровно 8 точек в высоту,
знакоместо 7 точек, все контуры прямые, все точки строго на сетке (проверено).
Но растеризатор ставит глиф по дробным координатам, и каждый край получает серую
кайму — на литере 72 знак «посыпался».

Здесь контуры берутся пером и заливаются полигонами по ЦЕЛЫМ координатам, в
режиме «1» — сглаживания нет вовсе, значит нет и каймы. Заливка чётно-нечётная
(контуры складываются исключающим ИЛИ), поэтому внутренние просветы литер
остаются просветами.

Ограничение размеров. Трекинг официального знака — ПОЛТОРЫ точки сетки, поэтому
целым числом пикселей он выходит только при чётном размере точки d. Отсюда
допустимы литеры 8*d при чётном d: 48, 64, 80, 96. Литера 72 (d=9) даёт трекинг
13,5 пикселя и запрещена — именно на ней знак и рассыпался.

Пропорции сняты с brand/gridec-logo.png: поля по бокам 6.5 точки, сверху и снизу
7.5 точки, трекинг 1.5 точки. На литере 48 отсюда выходит ровно 363x138 —
совпадение с официальным файлом проверяет check().
"""
import os
from PIL import Image, ImageChops, ImageDraw
from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
PLATE = (13, 36, 64)
WHITE = (255, 255, 255)

WORD = 'GRIDEC'
PAD_X = 6.5      # в точках сетки
PAD_Y = 7.5
TRACK = 1.5
CAP = 8          # высота литеры в точках сетки

_font = None

def _contours():
    """Контуры букв в точках сетки: [(advance, [[(x, y), ...], ...]), ...]"""
    global _font
    if _font is None:
        _font = TTFont(os.path.join(HERE, 'mono.ttf'))
    f = _font
    grid = f['head'].unitsPerEm / 11.0
    gs = f.getGlyphSet()
    cmap = f.getBestCmap()
    out = []
    for ch in WORD:
        gn = cmap[ord(ch)]
        pen = RecordingPen()
        gs[gn].draw(pen)
        cs, cur = [], []
        for op, args in pen.value:
            if op == 'moveTo':
                if cur:
                    cs.append(cur)
                cur = [args[0]]
            elif op == 'lineTo':
                cur.append(args[0])
            elif op in ('closePath', 'endPath'):
                if cur:
                    cs.append(cur); cur = []
        if cur:
            cs.append(cur)
        cs = [[(x / grid, y / grid) for x, y in c] for c in cs]
        out.append((gs[gn].width / grid, cs))
    return out

def valid_caps():
    return [8 * d for d in range(2, 26, 2)]

def render(cap=48):
    if cap % 16:
        raise ValueError('литера %d недопустима: размер точки должен быть чётным, '
                         'иначе трекinг в 1.5 точки даёт дробный пиксель. '
                         'Допустимо: %s' % (cap, valid_caps()))
    d = cap // CAP
    glyphs = _contours()

    # Координата по вертикали считается сразу в системе картинки. Раньше буквы
    # рисовались от базовой линии и картинка переворачивалась — при этом сдвиг
    # обратно выходил нулевым, и слово садилось на дно плашки.
    pad_y = int(round(PAD_Y * d))
    pen_x = PAD_X * d
    ink_left = None
    placed = []
    for adv, cs in glyphs:
        for c in cs:
            poly = [(int(round(pen_x + x * d)), pad_y + cap - int(round(y * d)))
                    for x, y in c]
            xs = [p[0] for p in poly]
            ink_left = min(xs) if ink_left is None else min(ink_left, min(xs))
            placed.append(poly)
        pen_x += (adv + TRACK) * d

    # Боковое поле считается от ЧЕРНИЛ, а не от знакоместа: у глифа есть свой
    # левый отступ в одну точку, и без поправки поле слева выходило бы шире.
    shift = int(round(PAD_X * d)) - ink_left
    placed = [[(x + shift, y) for x, y in p] for p in placed]

    all_x = [x for p in placed for x, _ in p]
    ink_w = max(all_x) - min(all_x)
    W = ink_w + 2 * int(round(PAD_X * d))
    H = cap + 2 * pad_y

    letters = Image.new('1', (W, H), 0)
    for poly in placed:
        one = Image.new('1', (W, H), 0)
        ImageDraw.Draw(one).polygon(poly, fill=1)
        letters = ImageChops.logical_xor(letters, one)

    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    rad = max(1, int(round(0.667 * d)))
    ImageDraw.Draw(img).rounded_rectangle([0, 0, W - 1, H - 1], radius=rad,
                                          fill=PLATE + (255,))
    img.paste(WHITE + (255,), (0, 0), letters)
    return img

def crisp(img):
    """Сколько разных цветов внутри плашки. Два — знак чистый: белила и грунт.
    Больше — появилась серая кайма, то есть где-то дробная координата."""
    inner = img.crop((6, 6, img.width - 6, img.height - 6)).convert('RGB')
    return len(set(inner.getdata()))

def check():
    ref = Image.open(os.path.join(HERE, '..', 'brand', 'gridec-logo.png')).convert('RGBA')
    mine = render(48)
    print('официальный %s   мой %s' % (ref.size, mine.size))
    if ref.size == mine.size:
        rp, mp = ref.convert('RGB').load(), mine.convert('RGB').load()
        diff = n = 0
        for yy in range(ref.height):
            for xx in range(ref.width):
                a, b = rp[xx, yy], mp[xx, yy]
                diff += sum(abs(a[i] - b[i]) for i in range(3)); n += 3
        print('расхождение с официальным: %.2f из 255 на канал' % (diff / float(n)))
    for cap in (48, 64, 80):
        im = render(cap)
        print('литера %2d -> плашка %-10s цветов внутри: %d' % (cap, im.size, crisp(im)))

if __name__ == '__main__':
    check()
