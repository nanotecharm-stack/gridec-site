# Общая кухня для сборки локапов Gridec: шрифт в кривые, знак, обёртка svg.
import os
import sys

from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

SCRATCH = (r"C:\Users\user\AppData\Local\Temp\claude"
           r"\C--Users-user-Desktop-CharGPT-cloude"
           r"\b11ae948-39af-41c2-8ab1-cca0270a34f7\scratchpad\Outfit.ttf")
TTF = sys.argv[1] if len(sys.argv) > 1 else SCRATCH

# --- знак: изокуб, три грани по 120°, шов — схема «звезда» --------------------
#
# Зазор d задаётся, а не вбит в цифры: на бумаге хватает шести единиц, а в шапке
# знак живёт двадцатью пикселями, и там шов такой ширины просто затекает. Ширина
# шва — это видимость смысла: три грани сходятся в центре звездой, как три фазы.
MARK_W, MARK_H = 173.205, 200.0
HX = 86.603                    # половина ширины: R*cos(30°)


def faces(d=6.0):
    """Три грани при зазоре d от осей шва. Возвращает (левая, правая, ромб)."""
    a = round(0.57735 * d, 3)          # снос вдоль ребра по вертикали
    b = round(1.15470 * d, 3)          # снос по нижним швам
    return ('M-%s -50 L-%s -%s L-%s -%s L-%s %s Z'
            % (HX, d, round(100 - a, 3), d, a, HX, round(50 - b, 3)),
            'M%s -50 L%s -%s L%s -%s L%s %s Z'
            % (HX, d, round(100 - a, 3), d, a, HX, round(50 - b, 3)),
            'M-%s %s L0 %s L%s %s L0 100 Z'
            % (HX, round(50 + b, 3), b, HX, round(50 + b, 3)))


WALL_L, WALL_R, DIAMOND = faces(6.0)

INK = '#141414'

_cache = {}


def font(weight):
    if weight not in _cache:
        f = TTFont(TTF)
        instantiateVariableFont(f, {'wght': weight}, inplace=True,
                                updateFontNames=False)
        _cache[weight] = f
    return _cache[weight]


def word(text, weight, cap_px, track_em=0.0, x=0.0, y=0.0, fill=None,
         split=None, split_fill=None):
    """Слово в кривых. Возвращает (список path, ширина в px).

    split — сколько первых букв красится основным цветом, остальные split_fill.
    """
    f = font(weight)
    upem = f['head'].unitsPerEm
    cap = getattr(f['OS/2'], 'sCapHeight', 0) or int(upem * 0.7)
    cmap, gs = f.getBestCmap(), f.getGlyphSet()
    s = cap_px / cap
    track = track_em * upem
    out, adv = [], 0.0
    for i, ch in enumerate(text):
        name = cmap[ord(ch)]
        rec = DecomposingRecordingPen(gs)
        gs[name].draw(rec)
        pen = SVGPathPen(gs, ntos=lambda v: repr(round(v, 1)))
        rec.replay(pen)
        d = pen.getCommands()
        col = fill
        if split is not None and i >= split:
            col = split_fill
        if d:
            out.append('<path%s transform="translate(%s %s) scale(%s %s)" d="%s"/>'
                       % (' fill="%s"' % col if col else '',
                          round(x + adv * s, 2), round(y, 2),
                          round(s, 5), round(-s, 5), d))
        adv += gs[name].width + track
    return out, (adv - track) * s


def mark(cx, cy, h, faces):
    """Знак с центром в (cx, cy) и высотой h. faces — три цвета граней."""
    k = h / MARK_H
    inner = ''.join('<path fill="%s" d="%s"/>' % (c, d)
                    for c, d in zip(faces, (WALL_L, WALL_R, DIAMOND)))
    return ('<g transform="translate(%s %s) scale(%s)">%s</g>'
            % (round(cx, 2), round(cy, 2), round(k, 5), inner))


def svg(w, h, body, label='Gridec'):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s %s" '
            'role="img" aria-label="%s">%s</svg>'
            % (round(w, 2), round(h, 2), label, body))


PAGE = u'''<!doctype html><meta charset="utf-8"><title>%s</title>
<style>
 body{margin:0;padding:40px;background:#F4F4F4;color:#141414;
   font:15px/1.5 -apple-system,Segoe UI,Roboto,sans-serif}
 h1{font-size:20px;font-weight:600;margin:0 0 28px}
 .card{background:#fff;border:1px solid #E2E2E2;border-radius:6px;
   padding:22px 26px;margin:0 0 20px;max-width:960px}
 h2{font-size:15px;font-weight:600;margin:0 0 2px}
 .ref{margin:0 0 18px;color:#8C8C8C;font-size:13px}
 .stage{display:flex;align-items:center;justify-content:center;
   padding:26px;border-radius:4px;margin-bottom:10px}
 .light{background:#FAFAFA;border:1px solid #ECECEC}
 .dark{background:#1A1A1A}
 .small{padding:14px}
</style>
<h1>%s</h1>
%s'''

CARD = u'''<section class="card">
  <h2>%s</h2><p class="ref">%s</p>
  <div class="stage light">%s</div>
  <div class="stage dark">%s</div>
  <div class="stage light small">%s</div>
</section>'''


def page(title, made, titles, dark_swaps=()):
    """Страница просмотра: каждый локап на светлом, на тёмном и мелко."""
    cards = []
    for (name, s, w, h), (t, r) in zip(made, titles):
        big = s.replace('<svg ', '<svg style="height:%dpx" ' % min(150, h * 1.4), 1)
        inv = s
        for a, b in (('#141414', '#FFFFFF'),) + tuple(dark_swaps):
            inv = inv.replace(a, b)
        inv = inv.replace('<svg ', '<svg style="height:%dpx" ' % min(150, h * 1.4), 1)
        tiny = s.replace('<svg ', '<svg style="height:28px" ', 1)
        cards.append(CARD % (t, r, big, inv, tiny))
    return PAGE % (title, title, '\n'.join(cards))


def write_all(out_dir, items, title, titles, dark_swaps=()):
    os.path.isdir(out_dir) or os.makedirs(out_dir)
    made = []
    for name, fn in items:
        s, w, h = fn()
        open(os.path.join(out_dir, name + '.svg'), 'w', encoding='utf-8').write(s)
        made.append((name, s, w, h))
        print('%-16s %4d x %3d  %d B' % (name, w, h, len(s)))
    html = page(title, made, titles, dark_swaps)
    open(os.path.join(out_dir, 'index.html'), 'w', encoding='utf-8').write(html)
    print('index.html       %d B' % len(html))
