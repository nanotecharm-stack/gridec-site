# -*- coding: utf-8 -*-
"""Дуотон фотографий, запечённый в файл вместо расчёта в браузере.

В вёрстке он собирался тремя действиями поверх снимка:
    filter: grayscale(.9) contrast(.84) brightness(1.08)
    сам снимок  mix-blend-mode: lighten   над подложкой #15171E
    слой сверху mix-blend-mode: darken    цветом  #EFEDEA
То есть чёрная точка поднята до #15171E, белая опущена до #EFEDEA.

Браузер пересчитывал это на КАЖДОМ кадре прокрутки — шесть кадров по 90 тысяч
пикселей, каждый в три действия. Здесь та же арифметика делается один раз при
сборке. Значения CSS-фильтров считаются в sRGB, поэтому арифметика простая.
"""
from PIL import Image

BLACK = (0x15, 0x17, 0x1E)      # подложка под снимком, lighten
WHITE = (0xEF, 0xED, 0xEA)      # слой поверх снимка, darken
GRAY = 0.9
CONTRAST = 0.84
BRIGHT = 1.08

def _matrix(s):
    """Матрица grayscale по спецификации: s = 1 - сила."""
    lr, lg, lb = 0.2126, 0.7152, 0.0722
    return (
        (lr + (1 - lr) * s, lg - lg * s, lb - lb * s),
        (lr - lr * s, lg + (1 - lg) * s, lb - lb * s),
        (lr - lr * s, lg - lg * s, lb + (1 - lb) * s),
    )

def _lut():
    """Таблица 256 значений на канал для contrast + brightness."""
    out = []
    for v in range(256):
        x = (v - 127.5) * CONTRAST + 127.5
        x *= BRIGHT
        out.append(0 if x < 0 else 255 if x > 255 else x)
    return out

def apply(im):
    im = im.convert('RGB')
    m = _matrix(1.0 - GRAY)
    # Pillow берёт матрицу 4x3 построчно: три коэффициента и смещение.
    im = im.convert('RGB', (m[0][0], m[0][1], m[0][2], 0,
                            m[1][0], m[1][1], m[1][2], 0,
                            m[2][0], m[2][1], m[2][2], 0))
    lut = _lut()
    tables = []
    for i in range(3):
        lo, hi = BLACK[i], WHITE[i]
        # lighten и darken — это max и min по каналу, их можно свернуть в ту же
        # таблицу: сначала кривая, потом ограничение снизу и сверху.
        tables.extend([min(hi, max(lo, int(round(v)))) for v in lut])
    return im.point(tables)

if __name__ == '__main__':
    import os
    src = os.path.join(os.path.dirname(__file__), '..', 'img',
                       '02_manufacturing_industrial_robot.jpg')
    im = apply(Image.open(src))
    p = os.path.join(os.path.dirname(__file__), 'duo-sample.png')
    im.resize((378, 252), Image.LANCZOS).save(p)
    ex = im.resize((60, 40)).convert('RGB')
    px = list(ex.get_flattened_data() if hasattr(ex, 'get_flattened_data') else ex.getdata())
    print('минимум по каналам:', [min(p[i] for p in px) for i in range(3)])
    print('максимум по каналам:', [max(p[i] for p in px) for i in range(3)])
    print('ожидалось не ниже', BLACK, 'и не выше', WHITE)
