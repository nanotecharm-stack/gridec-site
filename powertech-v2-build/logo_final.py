# Финал по выбранной настройке 8b. Два локапа:
#   * с плашкой — плашка держит грунт, знак одинаков на любом фоне;
#   * без плашки — только знак и имя, грани в графите (для светлого фона)
#     и в светлых тонах (для тёмного).
#
# Имя набрано Outfit и переведено в кривые: шрифт грузить не надо.
# В варианте для шапки «GRID» красится currentColor и следует за цветом текста,
# «EC» держит серый — он читается и на светлом, и на тёмном.
#
#   python logo_final.py [путь к Outfit[wght].ttf]
#
# Пишет logo-v8/final/*.svg, *.frag и index.html.
import io
import os

from logo_lib import HX, INK, MARK_H, MARK_W, PAGE, faces, svg, word

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'logo-v8', 'final')

# Силуэт всего куба: подложка под грани. Когда она залита цветом, шов между
# гранями перестаёт быть дырой и становится линией — звезда видна.
SIL = ('M0 -100 L%s -50 L%s 50 L0 100 L-%s 50 L-%s -50 Z' % ((HX,) * 4))


def edges(d):
    """Верхние рёбра при зазоре d: по ним ложится блик."""
    a = round(0.57735 * d, 3)
    b = round(1.1547 * d, 3)
    return ('M-%s -50 L-%s -%s' % (HX, d, round(100 - a, 3)),
            'M%s -%s L%s -50' % (d, round(100 - a, 3), HX),
            'M-%s %s L0 %s L%s %s' % (HX, round(50 + b, 3), b, HX, round(50 + b, 3)))
VECS = ((0, 0, 1, 0.4), (1, 0, 0, 0.4), (0.5, 0, 0.5, 1))
# Цвета синей палитры сайта. Для шапки берутся ИСХОДНЫЕ терракотовые литералы:
# палитровый пост-проход сборки переводит их в цвет выбранной палитры, и локап
# не приходится править отдельно под каждую.
BLUE_PLATE = ('#162E52', '#0D2440')       # ink3 -> ink
BLUE_TAIL = '#2E5E99'                     # light: синий акцент, им набрано PERFORMS
SRC_PLATE = ('#14161C', '#0D0E13')
SRC_TAIL = '#AC4A29'
PAD = 8.0

# Настройка 8b: тень двумя слоями, тонкий блик по верхним рёбрам.
RAMPS_LIGHT = (('#ADADAD', '#7E7E7E'), ('#EDEDED', '#B6B6B6'),
               ('#FFFFFF', '#CFCFCF'))
# На синей плашке грани светлее: мелкий кадр съедает середину тона, и знак
# должен отличаться от грунта силой света, а не оттенком.
RAMPS_PLATE = (('#C6C6C6', '#9A9A9A'), ('#F6F6F6', '#D2D2D2'),
               ('#FFFFFF', '#E4E4E4'))
RAMPS_DARK = (('#4E4E4E', '#2A2A2A'), ('#8E8E8E', '#5E5E5E'),
              ('#C2C2C2', '#8E8E8E'))
SHADOWS = ((0.13, 0.09, 0.38), (0.035, 0.03, 0.45))
EDGE = ('#FFFFFF', 0.55, 2.6)


def grad(gid, c1, c2, vec):
    return ('<linearGradient id="%s" x1="%s" y1="%s" x2="%s" y2="%s">'
            '<stop offset="0" stop-color="%s"/>'
            '<stop offset="1" stop-color="%s"/></linearGradient>'
            % ((gid,) + tuple(vec) + (c1, c2)))


def render(pfx, plate=True, ramps=RAMPS_LIGHT, edge=EDGE, shadows=SHADOWS,
           ink=INK, tile=96.0, cap=52.0, track=0.13, weight=500, frag=False,
           plate_ramp=BLUE_PLATE, tail=BLUE_TAIL, seam=12.0, wye=None):
    """Локап в одну линию. plate=False — только знак и имя."""
    FACES = faces(seam)
    mh = tile * (0.66 if plate else 0.56)
    mw = MARK_W / MARK_H * mh
    k = mh / MARK_H
    gap = tile * 0.28 if plate else mw * 0.46
    _, wide = word('GRIDEC', weight, cap, track)
    left = tile if plate else mw
    w = PAD + left + gap + wide + PAD
    h = PAD + tile + PAD
    cy = PAD + tile / 2
    cx = PAD + left / 2

    defs = [grad('%s_f%d' % (pfx, i), c1, c2, v)
            for i, ((c1, c2), v) in enumerate(zip(ramps, VECS))]
    body = []
    if plate:
        r = round(tile * 0.24, 1)
        rect = ('x="%s" y="%s" width="%s" height="%s" rx="%s"'
                % (PAD, PAD, tile, tile, r))
        defs.append(grad(pfx + '_bg', plate_ramp[0], plate_ramp[1], (0, 0, 0.55, 1)))
        defs.append('<linearGradient id="%s_sn" x1="0" y1="0" x2="0" y2="1">'
                    '<stop offset="0" stop-color="#FFFFFF" stop-opacity="0.16"/>'
                    '<stop offset="0.5" stop-color="#FFFFFF" stop-opacity="0"/>'
                    '<stop offset="1" stop-color="#000000" stop-opacity="0.20"/>'
                    '</linearGradient>' % pfx)
        defs.append('<radialGradient id="%s_vg" cx="0.28" cy="0.22" r="0.95">'
                    '<stop offset="0" stop-color="#FFFFFF" stop-opacity="0.07"/>'
                    '<stop offset="0.55" stop-color="#000000" stop-opacity="0"/>'
                    '<stop offset="1" stop-color="#000000" stop-opacity="0.22"/>'
                    '</radialGradient>' % pfx)
        body.append('<rect %s fill="url(#%s_bg)"/>' % (rect, pfx))

    drop = ''.join('<path d="%s"/>' % d for d in FACES)
    for i, (dev, dy, op) in enumerate(shadows):
        defs.append('<filter id="%s_s%d" x="-50%%" y="-50%%" width="200%%" '
                    'height="200%%"><feGaussianBlur stdDeviation="%s"/></filter>'
                    % (pfx, i, round(mh * dev, 2)))
        body.append('<g transform="translate(%s %s) scale(%s)" fill-opacity="%s" '
                    'filter="url(#%s_s%d)">%s</g>'
                    % (round(cx, 2), round(cy + mh * dy, 2), round(k, 5),
                       op, pfx, i, drop))

    face_ps = '<path fill="%s" d="%s"/>' % (wye, SIL) if wye else ''
    face_ps += ''.join('<path fill="url(#%s_f%d)" d="%s"/>' % (pfx, i, d)
                       for i, d in enumerate(FACES))
    if edge:
        col, op, sw = edge
        face_ps += ''.join('<path d="%s" fill="none" stroke="%s" stroke-opacity="%s"'
                         ' stroke-width="%s" stroke-linecap="round" '
                         'stroke-linejoin="round"/>' % (d, col, op, sw)
                         for d in edges(seam))
    body.append('<g transform="translate(%s %s) scale(%s)">%s</g>'
                % (round(cx, 2), round(cy, 2), round(k, 5), face_ps))
    if plate:
        body.append('<rect %s fill="url(#%s_sn)"/>' % (rect, pfx))
        body.append('<rect %s fill="url(#%s_vg)"/>' % (rect, pfx))
    ps, _ = word('GRIDEC', weight, cap, track, x=PAD + left + gap, y=cy + cap / 2,
                 fill=ink, split=4, split_fill=tail)
    body.append(''.join(ps))
    core = '<defs>%s</defs>%s' % (''.join(defs), ''.join(body))
    if frag:
        return ('<svg class="lock" viewBox="0 0 %s %s" aria-hidden="true">%s</svg>'
                % (round(w, 2), round(h, 2), core))
    return svg(w, h, core), w, h


FILES = (
    # знак с плашкой: один файл на любой фон, имя чёрное
    ('gridec-plate', dict(pfx='p1', ramps=RAMPS_PLATE), u'С плашкой — основной'),
    # без плашки: графит для светлого фона
    ('gridec-plain', dict(pfx='p2', plate=False, ramps=RAMPS_DARK,
                          edge=('#FFFFFF', 0.34, 2.2),
                          shadows=((0.11, 0.10, 0.17),)),
     u'Без плашки — для светлого фона'),
    # без плашки: светлые грани для тёмного фона
    ('gridec-plain-inv', dict(pfx='p3', plate=False, ramps=RAMPS_LIGHT,
                              edge=('#FFFFFF', 0.5, 2.2),
                              shadows=((0.11, 0.10, 0.35),), ink='#FFFFFF'),
     u'Без плашки — для тёмного фона'),
)

os.path.isdir(OUT) or os.makedirs(OUT)
made = []
for name, kw, title in FILES:
    s, w, h = render(**kw)
    io.open(os.path.join(OUT, name + '.svg'), 'w', encoding='utf-8').write(s)
    made.append((name, s, w, h, title))
    print('%-18s %4d x %3d  %d B' % (name, w, h, len(s)))

# фрагменты для шапки: «GRID» идёт за цветом текста
for name, kw in (('lock-plate', dict(pfx='h1', ramps=RAMPS_PLATE)),
                 ('lock-plain', dict(pfx='h2', plate=False, ramps=RAMPS_DARK,
                                     edge=('#FFFFFF', 0.34, 2.2),
                                     shadows=((0.11, 0.10, 0.17),)))):
    f = render(ink='currentColor', frag=True, plate_ramp=SRC_PLATE,
               tail=SRC_TAIL, **kw)
    io.open(os.path.join(OUT, name + '.frag'), 'w', encoding='utf-8').write(f)
    print('%-18s %d B' % (name + '.frag', len(f)))

CARD = u'''<section class="card"><h2>%s</h2><p class="ref">%s</p>
  <div class="stage light">%s</div><div class="stage dark">%s</div>
  <div class="stage light row">%s %s %s</div></section>'''
cards = []
for name, s, w, h, title in made:
    big = s.replace('<svg ', '<svg style="height:150px" ', 1)
    inv = s.replace(INK, '#FFFFFF').replace('<svg ', '<svg style="height:150px" ', 1)
    row = [s.replace('<svg ', '<svg style="height:%dpx" ' % px, 1)
           for px in (40, 24, 16)]
    cards.append(CARD % ((title, name + '.svg', big, inv) + tuple(row)))
title = u'Gridec — 8b в векторе: с плашкой и без'
html = (PAGE % (title, title, '\n'.join(cards))).replace(
    '.small{padding:14px}', '.row{gap:34px;padding:16px}')
io.open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(html)
print('index.html         %d B' % len(html))
