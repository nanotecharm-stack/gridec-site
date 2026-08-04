# Собирает логотип Gridec в кривые: знак плюс имя одним вектором, без шрифта.
#
# Логотип не должен зависеть от загрузки шрифта — пока файл летит, на месте имени
# либо пусто, либо системная подмена, то есть логотип мигает. Шесть букв в кривых
# весят около килобайта, рисунок фиксируется навсегда и не поедет от версии шрифта.
#
#   python logo_vector.py [путь к Outfit[wght].ttf]
#
# Пишет gridec-logo.svg (с акцентной гранью), gridec-logo-mono.svg (одноцветный)
# и gridec-lockup.frag — фрагмент для вклейки в шапку.
import io
import os
import sys

from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = (r"C:\Users\user\AppData\Local\Temp\claude"
           r"\C--Users-user-Desktop-CharGPT-cloude"
           r"\b11ae948-39af-41c2-8ab1-cca0270a34f7\scratchpad\Outfit.ttf")
TTF = sys.argv[1] if len(sys.argv) > 1 else SCRATCH

WORD = 'Gridec'
WEIGHT = 500          # Outfit 500 — то начертание, что выбрано на странице
ACCENT = '#2E5E99'    # акцент синей палитры на светлом грунте

# --- знак: изокуб, три грани по 120°, зазор 12 единиц при радиусе 100 ----------
WALL_L = 'M-86.603 -50 L-6 -96.536 L-6 -3.464 L-86.603 43.072 Z'
WALL_R = 'M86.603 -50 L6 -96.536 L6 -3.464 L86.603 43.072 Z'
DIAMOND = 'M-86.603 56.928 L0 6.928 L86.603 56.928 L0 100 Z'
MARK_W, MARK_H = 173.205, 200.0

# Пропорции сняты с одобренного локапа: куб выше прописной в 1,53 раза,
# просвет до имени — 0,44 ширины куба.
CAP_RATIO = 1.53
GAP_RATIO = 0.44


def load():
    f = TTFont(TTF)
    instantiateVariableFont(f, {'wght': WEIGHT}, inplace=True, updateFontNames=False)
    return f


def glyph_paths(font):
    """Очертания букв в единицах шрифта плюс их ширины."""
    upem = font['head'].unitsPerEm
    cap = getattr(font['OS/2'], 'sCapHeight', 0) or int(upem * 0.7)
    cmap = font.getBestCmap()
    gs = font.getGlyphSet()
    out, adv = [], 0.0
    for ch in WORD:
        name = cmap[ord(ch)]
        # DecomposingRecordingPen разворачивает составные глифы в контуры
        rec = DecomposingRecordingPen(gs)
        gs[name].draw(rec)
        pen = SVGPathPen(gs, ntos=lambda v: repr(round(v, 1)))
        rec.replay(pen)
        out.append((ch, adv, pen.getCommands()))
        adv += gs[name].width
    return upem, cap, out, adv


def build(font):
    upem, cap, glyphs, adv_total = glyph_paths(font)
    cap_target = MARK_H / CAP_RATIO           # высота прописной в единицах знака
    s = cap_target / cap                      # масштаб из единиц шрифта
    gap = MARK_W * GAP_RATIO
    x0 = MARK_W + gap                         # имя начинается здесь
    baseline = cap_target / 2                 # оптический центр: середина прописной

    word = []
    for ch, adv, d in glyphs:
        if not d:
            continue
        word.append('    <path transform="translate(%s %s) scale(%s %s)" d="%s"/>'
                    % (round(x0 + adv * s, 2), round(baseline, 2),
                       round(s, 5), round(-s, 5), d))

    total_w = x0 + adv_total * s
    # знак нарисован вокруг своего центра, а локап отсчитывается от нуля,
    # поэтому куб сдвигается на свой полурадиус
    shift = '  <g transform="translate(%s 0)">\n%%s\n  </g>' % (MARK_W / 2)
    body_marks = {
        'accent': shift % ('    <path d="%s"/>\n'
                           '    <path style="fill:var(--acc,%s)" d="%s"/>\n'
                           '    <path d="%s"/>' % (WALL_L, ACCENT, WALL_R, DIAMOND)),
        'mono': shift % ('    <path d="%s"/>\n    <path d="%s"/>\n    <path d="%s"/>'
                         % (WALL_L, WALL_R, DIAMOND)),
    }

    files = {}
    for kind, marks in body_marks.items():
        files[kind] = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 %s %s %s"\n'
            '     fill="currentColor" role="img" aria-label="Gridec">\n'
            '  <!-- Знак: три грани по 120°, шов — схема «звезда». Имя: Outfit %d\n'
            '       в кривых, шрифт не нужен. Пропорция куба к прописной 1:%s. -->\n'
            '%s\n  <g>\n%s\n  </g>\n</svg>\n'
            % (-MARK_H / 2, round(total_w, 2), MARK_H, WEIGHT, CAP_RATIO,
               marks, '\n'.join(word)))

    frag = ('<svg class="lock" viewBox="0 %s %s %s" aria-hidden="true">\n%s\n<g>\n%s\n</g>\n</svg>'
            % (-MARK_H / 2, round(total_w, 2), MARK_H,
               body_marks['accent'], '\n'.join(word)))
    return files, frag, dict(upem=upem, cap=cap, scale=s, total_w=total_w,
                             adv_em=adv_total / upem, cap_target=cap_target)


font = load()
files, frag, m = build(font)
for kind, name in (('accent', 'gridec-logo.svg'), ('mono', 'gridec-logo-mono.svg')):
    io.open(os.path.join(HERE, name), 'w', encoding='utf-8').write(files[kind])
    print('%-24s %d B' % (name, len(files[kind])))
io.open(os.path.join(HERE, 'gridec-lockup.frag'), 'w', encoding='utf-8').write(frag)
print('%-24s %d B' % ('gridec-lockup.frag', len(frag)))
print('upem %(upem)d  capHeight %(cap)d  scale %(scale).5f' % m)
print('ширина имени %(adv_em).4f em  локап %(total_w).1f x 200 единиц' % m)
print('пропорция куба к прописной 200 / %(cap_target).1f = %(r).2f'
      % dict(m, r=MARK_H / m['cap_target']))
