# -*- coding: utf-8 -*-
"""Логотип без знака: одно слово GRIDEC в шапке.

Владелец просит посмотреть три гарнитуры — Anybody, Departure Mono, Sora — и
БЕЗ знака. Значит из локапа уходит вся картинка: и куб, и его плашка внутри
svg. Остаётся плашка шапки (её рисует .brand::after) и слово на ней.

Размер слова взят от прежнего локапа, а не назначен: в нём высота прописной
буквы равна 52 единицам из 112, то есть при высоте локапа 38px прописная имеет
17.6px. Под это число и подбирается кегль каждой гарнитуры — иначе одна будет
казаться крупнее другой при одинаковом кегле, потому что доля прописной у всех
разная. Множители сняты замером в браузере, а не взяты из головы.
"""
import io, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'logo-arrows')

CAP_TARGET = 17.6      # высота прописной при локапе 38px — как было

# доля прописной от кегля, замерено канвасом в браузере
FONTS = [
    # Доли сняты канвасом на кегле 400px: на мелком кегле растеризатор
    # округляет высоту до целого пикселя, и замер пляшет на 15%.
    ('anybody', 'Anybody', "'Anybody'", 700, '.12em', 0.6875, True),
    ('departure', 'Departure Mono', "'Departure Mono'", 400, '.10em', 0.7344, False),
    ('sora', 'Sora', "'Sora'", 600, '.13em', 0.7500, True),
]

GF = ('https://fonts.googleapis.com/css2'
      '?family=Anybody:wdth,wght@50..150,100..900'
      '&family=Sora:wght@100..800&display=swap')

LOCK = re.compile(r'<svg class="lock".*?</svg>', re.S)

src = io.open(os.path.join(HERE, 'pt-en.html'), encoding='utf-8').read()

"""Departure Mono ложится на сетку, а не на кегль.

Шрифт пиксельный: буква занимает 7 единиц из 11, поэтому её ширина целая только
при кегле, кратном 11. На прежних 23.96px ширина выходила 15.25 пикселя, края
букв падали между пикселями, и округление ложилось то влево, то вправо —
замер дал просветы 6, 5, 6, 5, 6. На 22px ширина ровно 14, просветы ровно
по 6 — все пять.

Трекинг тоже в пикселях, а не в долях кегля: .10em дало бы те же 2.4 пикселя и
ту же пляску. Последний просвет снимается отрицательным полем справа — CSS
добавляет трекинг и ПОСЛЕ последней буквы, и слово съезжало на плашке влево.

Кегль один на все ширины. Уменьшать его на телефоне нельзя: следующая ступень
сетки — 11px, вдвое мельче. Запас в шапке это позволяет: без знака он 43px.
"""
PIXEL_GRID = {
    'departure': {'size': 22, 'track': 3},
}

for key, title, fam, wt, track, cap_ratio, needs_gf in FONTS:
    size = CAP_TARGET / cap_ratio
    grid = PIXEL_GRID.get(key)
    if grid:
        css = ('<style>.brand .wm{font-family:%s;font-weight:%d;font-size:%dpx;'
               'letter-spacing:%dpx;margin-right:-%dpx;line-height:1;'
               'white-space:nowrap;display:block}</style>'
               % (fam, wt, grid['size'], grid['track'], grid['track']))
        page = LOCK.sub('<span class="wm">GRIDEC</span>', src, count=1)
        page = page.replace('</head>', css + '</head>', 1)
        p = os.path.join(OUT, 'word-%s.html' % key)
        io.open(p, 'w', encoding='utf-8').write(page)
        print(p, 'pixel grid %dpx/%dpx' % (grid['size'], grid['track']))
        continue
    css = (
        '<style>'
        # Слово встаёт на место локапа и наследует его высоту: плашка шапки
        # меряется по .brand, и если слово выпадет из потока, плашка схлопнется.
        '.brand .wm{font-family:%s;font-weight:%d;font-size:%.2fpx;'
        'letter-spacing:%s;line-height:1;white-space:nowrap;display:block;'
        'padding-inline:2px}'
        # На узком экране локап уменьшался с 38 до 34 и 30 — слово идёт следом,
        # иначе шапка на телефоне снова упрётся в кромку.
        '@media (max-width:900px){.brand .wm{font-size:%.2fpx}}'
        '@media (max-width:337px){.brand .wm{font-size:%.2fpx}}'
        '</style>' % (fam, wt, size, track, size * 34 / 38.0, size * 30 / 38.0))
    link = ('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link rel="stylesheet" href="%s">' % GF) if needs_gf else ''
    page = LOCK.sub('<span class="wm">GRIDEC</span>', src, count=1)
    page = page.replace('</head>', link + css + '</head>', 1)
    p = os.path.join(OUT, 'word-%s.html' % key)
    io.open(p, 'w', encoding='utf-8').write(page)
    print(p)
