# -*- coding: utf-8 -*-
"""Три стрелки — весовой проход. Почему знак мылит на 24px и что с этим делать.

Замечание владельца: на 24 пикселях все четыре концепта смазываются.

Причина не в идее, а в ВЕСЕ линии. У первой звезды древко 9 единиц из 100 —
на 24 пикселях это 2.2 физических пикселя, а просвет в центре 26 единиц даёт
6 пикселей на ТРИ зазора. Экран не умеет рисовать половину пикселя: он гасит
её серым, и три серых луча сливаются в пятно. То же и с обводкой шестигранника
в 5.5 единиц — это 1.3 пикселя.

Порог, ниже которого фигура перестаёт держаться: линия тоньше ~3 физических
пикселей и просвет тоньше ~2. Отсюда и правки: древко толще, просветы шире,
рамки нет, а для значка вкладки — отдельный рисунок.

Про визитку отдельно. Печать идёт не в экранных пикселях: знак 8 мм при 300 dpi
это 94 пикселя, вчетверо больше, чем в шапке сайта. На бумаге плохо не будет —
плохо на ЭКРАНЕ, и лечить надо экран.

Страница показывает не «как задумано», а как есть: каждый знак рисуется в свой
настоящий размер на холст и увеличивается БЕЗ сглаживания. Видно каждый пиксель.
"""
import io, os, math

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'logo-arrows')

INK = '#0D2440'
PAPER = '#EFEDEA'


def arrow(cx, cy, ang, r0, r1, tip, half, head):
    a = math.radians(ang)
    ux, uy = math.cos(a), -math.sin(a)
    px, py = -uy, ux
    def P(along, across):
        return (cx + ux * along + px * across, cy + uy * along + py * across)
    pts = [P(r0, -half), P(r1, -half), P(r1, -head), P(tip, 0),
           P(r1, head), P(r1, half), P(r0, half)]
    return 'M' + 'L'.join('%.2f %.2f' % p for p in pts) + 'Z'


def star(r0, r1, tip, half, head, cx=50, cy=50):
    return ' '.join(arrow(cx, cy, a, r0, r1, tip, half, head)
                    for a in (90, 210, 330))


# --------------------------------------------------------------- кандидаты
# Числа подобраны от ПИКСЕЛЯ, а не от красоты: доля × 24 должна давать
# целое число пикселей, иначе край попадает на половину и сереет.
CAND = [
    ('was', 'Как было',
     star(13, 30, 46, 4.6, 12.5),
     'Древко 9 единиц — 2.2 пикселя на 24. Это и есть мыло.'),
    ('heavy', 'Тяжёлая звезда',
     star(17, 28, 48, 7.2, 17.5),
     'Древко 14.4 единиц — 3.5 пикселя. Просвет в центре шире, головы крупнее.'),
    ('wye', 'Сплошной Y',
     star(0, 28, 48, 7.8, 18),
     'Стрелки сходятся в центре: дырки нет вовсе, ломаться нечему.'),
    ('micro', 'Отдельный рисунок для значка',
     star(0, 25, 50, 9.5, 21),
     'Толще и короче — только для 16 и 24. В печати и в шапке идёт крупный.'),
]

SIZES = [(16, 12), (24, 8), (32, 6), (48, 4)]


def svg_src(d, color):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            '<path d="%s" fill="%s"/></svg>' % (d, color))


os.makedirs(OUT, exist_ok=True)

rows = []
for key, title, d, note in CAND:
    grounds = []
    for bg, fg, lab in ((PAPER, INK, 'на бумаге'), (INK, PAPER, 'на плашке')):
        cells = ''.join(
            '<div class="sz"><canvas data-src="%s" data-size="%d" data-zoom="%d" '
            'style="background:%s"></canvas><b>%dpx</b></div>'
            % (svg_src(d, fg).replace('"', '&quot;'), s, z, bg, s)
            for s, z in SIZES)
        grounds.append('<div class="ground"><span class="lab">%s</span>'
                       '<div class="row">%s</div></div>' % (lab, cells))
    card = ('<div class="real"><div class="rbox" style="background:%s">'
            '<svg viewBox="0 0 100 100" width="94" height="94">'
            '<path d="%s" fill="%s"/></svg></div>'
            '<b>визитка: 8&nbsp;мм при 300&nbsp;dpi = 94&nbsp;px</b></div>'
            % (PAPER, d, INK))
    rows.append('<section><h2>%s</h2><p>%s</p>%s%s</section>'
                % (title, note, ''.join(grounds), card))

page = u"""<!doctype html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Gridec — вес линии</title>
<style>
*{box-sizing:border-box}
body{margin:0;padding:40px 28px 80px;background:#F6F5F3;color:#0D0E13;
  font:15px/1.6 -apple-system,Segoe UI,Roboto,sans-serif}
h1{font-size:22px;margin:0 0 6px;letter-spacing:-.01em}
.sub{max-width:64ch;margin:0 0 34px;color:#5A5F66}
section{background:#fff;border:1px solid #E3E0DB;border-radius:3px;
  padding:22px 24px 26px;margin-bottom:22px;max-width:940px}
h2{font-size:16px;margin:0 0 4px}
section>p{margin:0 0 20px;color:#5A5F66;max-width:62ch;font-size:13.5px}
.ground{margin-bottom:16px}
.lab,.sz b,.real b{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.1em;
  text-transform:uppercase;color:#8A8F96;font-weight:400}
.row{display:flex;align-items:flex-end;gap:20px;margin-top:8px;flex-wrap:wrap}
.sz{text-align:center}
canvas{display:block;border:1px solid #E3E0DB;image-rendering:pixelated}
.sz b{display:block;margin-top:6px}
.real{margin-top:20px;padding-top:18px;border-top:1px dashed #E3E0DB;
  display:flex;align-items:center;gap:16px}
.rbox{display:flex;align-items:center;justify-content:center;width:124px;
  height:124px;border:1px solid #E3E0DB}
</style></head><body>
<h1>Почему мылит и что помогает</h1>
<p class="sub">Каждый знак нарисован в свой НАСТОЯЩИЙ размер и увеличен без
сглаживания — вы видите те самые пиксели, что видит экран. Первая строка «как
было» показывает изъян, три следующие — лечение. Внизу каждой карточки размер
для визитки: печать в четыре раза подробнее шапки сайта.</p>
%s
<script>
document.querySelectorAll('canvas').forEach(function(c){
  var size=+c.dataset.size, zoom=+c.dataset.zoom;
  c.width=size*zoom; c.height=size*zoom;
  c.style.width=(size*zoom)+'px'; c.style.height=(size*zoom)+'px';
  var img=new Image(), off=document.createElement('canvas');
  off.width=size; off.height=size;
  img.onload=function(){
    off.getContext('2d').drawImage(img,0,0,size,size);
    var x=c.getContext('2d');
    x.imageSmoothingEnabled=false;
    x.drawImage(off,0,0,size,size,0,0,size*zoom,size*zoom);
  };
  img.src='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(c.dataset.src);
});
</script>
</body></html>""" % ''.join(rows)

path = os.path.join(OUT, 'weight.html')
io.open(path, 'w', encoding='utf-8').write(page)
print(path)
