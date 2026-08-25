# -*- coding: utf-8 -*-
"""Слово GRIDEC в кандидатах на гарнитуру.

Показываем ровно то, что решается выбором шрифта: НАБОР. Знак рядом стоит один
и тот же — кольцо с поднятыми весами, нынешний фаворит, — чтобы глаз сравнивал
буквы, а не всё сразу.

Шесть гарнитур тянутся с Google Fonts, Departure Mono и нынешний Overused
Grotesk лежат в fonts/ рядом. Monaspace, Switzer и Redaction на Google Fonts не
раздаются: их надо скачивать файлами, и это делается только с разрешения
владельца.

Каждая строка показана трижды: крупно, в размере шапки и на тёмной плашке.
Мелкий размер здесь не украшение — набор с тонкими штрихами разваливается в
шапке ровно так же, как разваливался знак.
"""
import io, os, math

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'logo-arrows')

PLATE = '#0D2440'
PAPER = '#EFEDEA'
INK = '#0D2440'

GF = ('https://fonts.googleapis.com/css2'
      '?family=Geist:wght@100..900'
      '&family=Martian+Mono:wght@100..800'
      '&family=Bricolage+Grotesque:opsz,wght@12..96,200..800'
      '&family=Anybody:wdth,wght@50..150,100..900'
      '&family=Unbounded:wght@200..900'
      '&family=Instrument+Serif:ital@0;1'
      '&display=swap')

# гарнитура, подпись, семейство CSS, вес, трекинг слова, откуда
FONTS = [
    ('Overused Grotesk', 'нынешний — для сравнения', "'Overused Grotesk'",
     600, '.14em', 'локально'),
    ('Geist', 'сухой техничный гротеск, Vercel', "'Geist'",
     600, '.14em', 'Google Fonts'),
    ('Martian Mono', 'узкий моно, Evil Martians', "'Martian Mono'",
     600, '.06em', 'Google Fonts'),
    ('Departure Mono', 'пиксельный моно, экран прибора', "'Departure Mono'",
     400, '.10em', 'локально'),
    ('Bricolage Grotesque', 'гротеск с норовом', "'Bricolage Grotesque'",
     700, '.12em', 'Google Fonts'),
    ('Anybody', 'переменная ширина, техно-дисплей', "'Anybody'",
     700, '.10em', 'Google Fonts'),
    ('Unbounded', 'геометрический дисплей', "'Unbounded'",
     500, '.10em', 'Google Fonts'),
    ('Instrument Serif', 'контрастная антиква', "'Instrument Serif'",
     400, '.10em', 'Google Fonts'),
]


# ------------------------------------------------------------------- знак
def dart(ang, r0, tip, corner, junc, headw, shaftw):
    a = math.radians(ang)
    ux, uy = math.cos(a), -math.sin(a)
    px, py = -uy, ux
    def P(al, ac):
        return (ux * al + px * ac, uy * al + py * ac)
    pts = [P(tip, 0), P(corner, headw), P(junc, shaftw), P(r0, shaftw),
           P(r0, -shaftw), P(junc, -shaftw), P(corner, -headw)]
    return 'M' + 'L'.join('%.2f %.2f' % p for p in pts) + 'Z'


def ring(ro, ri):
    def circle(r, sweep):
        return ('M%.2f 0A%.2f %.2f 0 1 %d %.2f 0A%.2f %.2f 0 1 %d %.2f 0Z'
                % (r, r, r, sweep, -r, r, r, sweep, r))
    return circle(ro, 1) + circle(ri, 0)


MARK = (' '.join(dart(a, 20, 100, 32, 56, 48, 14) for a in (90, 210, 330))
        + ' ' + ring(37, 15))


def mark_svg(h, color):
    return ('<svg viewBox="-100 -100 200 150" height="%d" width="%d" '
            'style="display:block;flex:0 0 auto"><path fill="%s" d="%s"/></svg>'
            % (h, int(h * 200 / 150.0), color, MARK))


# ------------------------------------------------------------------ вёрстка
rows = []
for name, note, fam, wt, track, where in FONTS:
    def lock(cap, color, mark_h, tag=True):
        tagline = ('<div class="tag" style="font-family:%s;font-size:%.1fpx">'
                   'POWER QUALITY MONITORING</div>' % (fam, cap * 0.30)) if tag else ''
        return ('<div class="lk"><div class="mk">%s</div><div>'
                '<div class="wd" style="font-family:%s;font-weight:%d;'
                'font-size:%dpx;letter-spacing:%s;color:%s">GRIDEC</div>%s</div></div>'
                % (mark_svg(mark_h, color), fam, wt, cap, track, color, tagline))
    rows.append(
        '<section>'
        '<header><h2>%s</h2><span class="src">%s · %s</span></header>'
        '<div class="big">%s</div>'
        '<div class="pair">'
        '<div class="cell light"><span class="lab">в шапке, 24px</span>%s</div>'
        '<div class="cell dark"><span class="lab">на плашке</span>%s</div>'
        '</div></section>'
        % (name, note, where,
           lock(52, INK, 62),
           lock(17, INK, 24, tag=False),
           lock(17, PAPER, 24, tag=False)))

page = u"""<!doctype html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>GRIDEC — гарнитуры</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="%s">
<style>
@font-face{font-family:'Overused Grotesk';font-weight:100 900;
  src:url(../fonts/overused-grotesk-latin.woff2) format('woff2');font-display:swap}
@font-face{font-family:'Departure Mono';font-weight:100 900;
  src:url(../fonts/departure-mono.woff2) format('woff2');font-display:swap}
*{box-sizing:border-box}
body{margin:0;padding:40px 28px 70px;background:#F6F5F3;color:#0D0E13;
  font:15px/1.6 -apple-system,Segoe UI,Roboto,sans-serif}
h1{font-size:22px;margin:0 0 6px}
.sub{max-width:64ch;margin:0 0 30px;color:#5A5F66}
section{background:#fff;border:1px solid #E3E0DB;border-radius:3px;
  padding:20px 24px 22px;margin-bottom:18px;max-width:940px}
header{display:flex;align-items:baseline;gap:12px;margin-bottom:16px}
h2{font-size:15px;margin:0}
.src{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.1em;
  text-transform:uppercase;color:#8A8F96}
.lk{display:flex;align-items:center;gap:18px}
.mk{display:flex;align-items:center}
.wd{line-height:1;white-space:nowrap}
.tag{margin-top:8px;letter-spacing:.34em;color:#8A8F96;line-height:1;
  white-space:nowrap}
.big{padding:18px 0 22px;border-bottom:1px dashed #E3E0DB;margin-bottom:16px;
  overflow-x:auto}
.pair{display:flex;gap:14px;flex-wrap:wrap}
.cell{flex:1 1 300px;padding:16px 18px;border:1px solid #E3E0DB;border-radius:2px}
.cell.light{background:%s}
.cell.dark{background:%s;border-color:transparent}
.lab{display:block;margin-bottom:10px;font:11px/1 ui-monospace,Menlo,monospace;
  letter-spacing:.12em;text-transform:uppercase;color:#8A8F96}
.cell.dark .lab{color:rgba(239,237,234,.5)}
</style></head><body>
<h1>Слово GRIDEC в восьми гарнитурах</h1>
<p class="sub">Знак рядом один и тот же — кольцо с поднятыми весами, — чтобы глаз
сравнивал буквы, а не всё сразу. Первая строка каждой карточки крупная, дальше
тот же набор в размере шапки: на светлом и на тёмном. Гарнитура, которая
разваливается на 24 пикселях, в шапке работать не будет.</p>
%s
</body></html>""" % (GF, PAPER, PLATE, ''.join(rows))

p = os.path.join(OUT, 'fonts.html')
io.open(p, 'w', encoding='utf-8').write(page)
print(p)
