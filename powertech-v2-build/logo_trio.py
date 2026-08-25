# Три локапа Gridec в духе присланных логотипов (Volo, STDev, earlyone):
# серая шкала, геометрический гротеск, знак плюс имя. Буквы переводятся в кривые,
# поэтому файл не зависит от шрифта.
#
#   python logo_trio.py [путь к Outfit[wght].ttf]
#
# Пишет logo-trials/v1-volo.svg, v2-tile.svg, v3-earlyone.svg и index.html.
import io
import os
import sys

from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'logo-trials')
SCRATCH = (r"C:\Users\user\AppData\Local\Temp\claude"
           r"\C--Users-user-Desktop-CharGPT-cloude"
           r"\b11ae948-39af-41c2-8ab1-cca0270a34f7\scratchpad\Outfit.ttf")
TTF = sys.argv[1] if len(sys.argv) > 1 else SCRATCH

# --- знак: изокуб, три грани по 120°, шов — схема «звезда» --------------------
WALL_L = 'M-86.603 -50 L-6 -96.536 L-6 -3.464 L-86.603 43.072 Z'
WALL_R = 'M86.603 -50 L6 -96.536 L6 -3.464 L86.603 43.072 Z'
DIAMOND = 'M-86.603 56.928 L0 6.928 L86.603 56.928 L0 100 Z'
MARK_W, MARK_H = 173.205, 200.0

INK = '#141414'
GREY = '#9A9A9A'

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
    p = [WALL_L, WALL_R, DIAMOND]
    inner = ''.join('<path fill="%s" d="%s"/>' % (c, d) for c, d in zip(faces, p))
    return ('<g transform="translate(%s %s) scale(%s)">%s</g>'
            % (round(cx, 2), round(cy, 2), round(k, 5), inner))


def svg(w, h, body, label):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s %s" '
            'role="img" aria-label="%s">%s</svg>'
            % (round(w, 2), round(h, 2), label, body))


# --- v1 «Volo»: знак сверху по центру, имя прописными в разрядку --------------
def v1():
    cap, track = 52.0, 0.30
    paths, wide = word('GRIDEC', 500, cap, track, fill=INK)
    mh, gap, pad = 104.0, 52.0, 10.0
    w = max(wide, MARK_W / MARK_H * mh) + pad * 2
    h = pad + mh + gap + cap + pad
    # разрядка добавляет пустоту справа: оптический центр сдвигается влево
    x0 = (w - wide) / 2 - cap * track / 2
    body = mark(w / 2, pad + mh / 2, mh, ('#2E2E2E', '#7C7C7C', '#B0B0B0'))
    ps, _ = word('GRIDEC', 500, cap, track, x=x0, y=pad + mh + gap + cap, fill=INK)
    return svg(w, h, body + ''.join(ps), 'Gridec'), w, h


# --- v2 «STDev»: знак в плитке слева, имя и подпись справа --------------------
def v2():
    cap = 62.0
    tile = 104.0
    gap = 26.0
    pad = 10.0
    a, wa = word('GRID', 700, cap, 0.0, fill=INK)
    xb = wa + cap * 0.02
    b, wb = word('ec', 700, cap, 0.0, x=xb, fill=INK)
    wordw = xb + wb
    sub_cap = 15.0
    sub, subw = word('power quality engineering', 400, sub_cap, 0.10, fill='#8C8C8C')
    txtw = max(wordw, subw)
    w = pad + tile + gap + txtw + pad
    h = pad + tile + pad
    baseline = pad + tile * 0.58
    x0 = pad + tile + gap
    ps, _ = word('GRID', 700, cap, 0.0, x=x0, y=baseline, fill=INK)
    ps2, _ = word('ec', 700, cap, 0.0, x=x0 + xb, y=baseline, fill='#6E6E6E')
    ps3, _ = word('power quality engineering', 400, sub_cap, 0.10,
                  x=x0 + 2, y=baseline + 26, fill='#8C8C8C')
    grad = ('<defs><linearGradient id="g2" x1="0" y1="0" x2="1" y2="1">'
            '<stop offset="0" stop-color="#5F5F5F"/>'
            '<stop offset="1" stop-color="#C4C4C4"/></linearGradient></defs>')
    plate = ('<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="url(#g2)"/>'
             % (pad, pad, tile, tile, round(tile * 0.30, 1)))
    m = mark(pad + tile / 2, pad + tile / 2, tile * 0.60,
             ('#FFFFFF', '#FFFFFF', '#FFFFFF'))
    return svg(w, h, grad + plate + m + ''.join(ps + ps2 + ps3), 'Gridec'), w, h


# --- v3 «earlyone»: строчные, два тона, знак над хвостом имени ----------------
def v3():
    cap, track = 62.0, -0.005
    pad = 10.0
    _, wordw = word('gridec', 500, cap, track)
    _, headw = word('grid', 500, cap, track)
    tailw = wordw - headw            # ширина хвоста «ec» — над ним стоит знак
    sub_cap = 13.0
    _, subw = word('power quality measured under load', 400, sub_cap, 0.06)
    mh = 44.0
    gap = 13.0                       # просвет от знака до верха строчных
    w = pad + max(wordw, subw) + pad
    baseline = pad + mh + gap + cap
    h = baseline + 36 + sub_cap * 0.3 + pad
    ps, _ = word('gridec', 500, cap, track, x=pad, y=baseline,
                 fill=INK, split=4, split_fill='#A6A6A6')
    m = mark(pad + headw + tailw / 2, pad + mh / 2, mh,
             ('#8E8E8E', '#B8B8B8', '#D2D2D2'))
    sub, _ = word('power quality measured under load', 400, sub_cap, 0.06,
                  x=pad + 2, y=baseline + 36, fill='#9A9A9A')
    return svg(w, h, m + ''.join(ps + sub), 'Gridec'), w, h


os.path.isdir(OUT) or os.makedirs(OUT)
made = []
for name, fn in (('v1-volo', v1), ('v2-tile', v2), ('v3-earlyone', v3)):
    s, w, h = fn()
    io.open(os.path.join(OUT, name + '.svg'), 'w', encoding='utf-8').write(s)
    made.append((name, s, w, h))
    print('%-14s %4d x %3d  %d B' % (name, w, h, len(s)))

CARD = u'''<section class="card">
  <h2>%s</h2><p class="ref">%s</p>
  <div class="stage light">%s</div>
  <div class="stage dark">%s</div>
  <div class="stage light small">%s</div>
</section>'''
titles = [
    (u'Версия 1 — знак сверху, имя в разрядку', u'по образцу VOLO'),
    (u'Версия 2 — знак в плитке, имя и подпись', u'по образцу STDev'),
    (u'Версия 3 — строчные, два тона', u'по образцу earlyone'),
]
cards = []
for (name, s, w, h), (t, r) in zip(made, titles):
    big = s.replace('<svg ', '<svg style="height:%dpx" ' % min(150, h * 1.4), 1)
    inv = s.replace('#141414', '#FFFFFF').replace('#6E6E6E', '#D6D6D6')
    inv = inv.replace('<svg ', '<svg style="height:%dpx" ' % min(150, h * 1.4), 1)
    tiny = s.replace('<svg ', '<svg style="height:28px" ', 1)
    cards.append(CARD % (t, r, big, inv, tiny))

HTML = u'''<!doctype html><meta charset="utf-8"><title>Gridec — три версии знака</title>
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
<h1>Gridec — три версии знака</h1>
%s''' % '\n'.join(cards)
io.open(os.path.join(OUT, 'index.html'), 'w', encoding='utf-8').write(HTML)
print('index.html      %d B' % len(HTML))
