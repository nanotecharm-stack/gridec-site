# -*- coding: utf-8 -*-
"""Знак с картинки владельца — в кривых и на своих местах.

Владелец прислал готовый знак: три широкие стрелки из центра через 120°, у
каждой пятка срезана внутрь — «ласточкин хвост». Скрипт повторяет его геометрией,
а не картинкой: одна фигура на стрелку, ни обводок, ни полутонов. Дальше знак
подставляется в НАСТОЯЩУЮ страницу — в самодостаточную сборку pt-en.html, где
шрифты и снимки уже вшиты, — поэтому смотреть можно без сервера.

Две пробы:
  solid — пятки сходятся в центре, середина сплошная;
  void  — между пятками остаётся треугольный просвет, как на присланной картинке.
Просвет и есть спорное место: на 24 пикселях он тоньше двух и сереет.
"""
import io, os, re, math

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'logo-arrows')

TIP = 100.0     # вылет стрелки от центра
CORNER = 16.0   # где стоит внешний угол головы (пятка крыла)
JUNC = 34.0     # где голова переходит в древко
HEADW = 50.0    # половина ширины головы
SHAFTW = 19.0   # половина ширины древка


def dart(ang, tail):
    a = math.radians(ang)
    ux, uy = math.cos(a), -math.sin(a)
    px, py = -uy, ux
    def P(al, ac):
        return (ux * al + px * ac, uy * al + py * ac)
    pts = [P(TIP, 0), P(CORNER, HEADW), P(JUNC, SHAFTW), P(tail, SHAFTW),
           P(tail, -SHAFTW), P(JUNC, -SHAFTW), P(CORNER, -HEADW)]
    return 'M' + 'L'.join('%.2f %.2f' % p for p in pts) + 'Z'


def mark(tail):
    return ' '.join(dart(a, tail) for a in (90, 210, 330))


MARKS = {'solid': mark(-6.0), 'void': mark(15.0)}

# Габарит знака: вершины на 100, две нижние на y=+50 — фигура НЕ по центру,
# и середину надо сдвинуть, иначе знак сядет в плашке слишком высоко.
SCALE = 0.35
TY = 56.0 + 25.0 * SCALE

os.makedirs(OUT, exist_ok=True)

# ------------------------------------------------- подмена знака в локапе
# Куб нарисован тремя гранями и повторён трижды: две копии — тени, третья —
# сам знак с обводкой рёбер. Всё это уходит целиком: у плоской фигуры теней нет.
CUBE = re.compile(
    r'<g transform="translate\(56\.0 61\.7\) scale\(0\.3168\)".*?</g>'
    r'<g transform="translate\(56\.0 57\.9\) scale\(0\.3168\)".*?</g>'
    r'<g transform="translate\(56\.0 56\.0\) scale\(0\.3168\)".*?</g>', re.S)


def swap(html, d):
    new = ('<g transform="translate(56.0 %.2f) scale(%.4f)">'
           '<path fill="#FFFFFF" d="%s"/></g>' % (TY, SCALE, d))
    out, n = CUBE.subn(new, html)
    return out, n


src = io.open(os.path.join(HERE, 'pt-en.html'), encoding='utf-8').read()
for key, d in MARKS.items():
    page, n = swap(src, d)
    assert n == 1, 'локап не найден (%d)' % n
    path = os.path.join(OUT, 'site-%s.html' % key)
    io.open(path, 'w', encoding='utf-8').write(page)
    print(path, n)

# --------------------------------------------------------- отдельный знак
for key, d in MARKS.items():
    io.open(os.path.join(OUT, 'mark-%s.svg' % key), 'w', encoding='utf-8').write(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-100 -100 200 150">'
        '<path fill="#0D2440" d="%s"/></svg>' % d)

# ------------------------------------------------ проверка малых размеров
SIZES = [(16, 12), (24, 8), (32, 6), (48, 4)]
PLATE = '#0D2440'
PAPER = '#EFEDEA'


def svg_src(d, color, plate=None):
    inner = '<path fill="%s" d="%s"/>' % (color, d)
    bg = ('<rect x="-100" y="-100" width="200" height="150" fill="%s" rx="30"/>'
          % plate) if plate else ''
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-100 -100 200 150">'
            '%s%s</svg>' % (bg, inner))


rows = []
for key, title in (('void', 'С просветом — как на вашей картинке'),
                   ('solid', 'Сплошная середина')):
    d = MARKS[key]
    grounds = []
    for bg, fg, lab in ((PAPER, PLATE, 'на бумаге'), (PLATE, PAPER, 'на плашке')):
        cells = ''.join(
            '<div class="sz"><canvas data-src="%s" data-size="%d" data-zoom="%d" '
            'style="background:%s"></canvas><b>%dpx</b></div>'
            % (svg_src(d, fg).replace('"', '&quot;'), s, z, bg, s)
            for s, z in SIZES)
        grounds.append('<div class="ground"><span class="lab">%s</span>'
                       '<div class="row">%s</div></div>' % (lab, cells))
    rows.append('<section><h2>%s</h2>%s</section>' % (title, ''.join(grounds)))

page = u"""<!doctype html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Знак — малые размеры</title><style>
*{box-sizing:border-box}
body{margin:0;padding:40px 28px 60px;background:#F6F5F3;color:#0D0E13;
  font:15px/1.6 -apple-system,Segoe UI,Roboto,sans-serif}
h1{font-size:22px;margin:0 0 30px}
section{background:#fff;border:1px solid #E3E0DB;padding:22px 24px;
  margin-bottom:20px;max-width:900px;border-radius:3px}
h2{font-size:16px;margin:0 0 14px}
.lab,.sz b{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.1em;
  text-transform:uppercase;color:#8A8F96}
.row{display:flex;align-items:flex-end;gap:20px;margin-top:8px}
.sz{text-align:center}
canvas{display:block;border:1px solid #E3E0DB;image-rendering:pixelated}
.sz b{display:block;margin-top:6px}
.ground{margin-bottom:14px}
</style></head><body><h1>Знак в настоящих размерах, увеличено без сглаживания</h1>
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
    var x=c.getContext('2d'); x.imageSmoothingEnabled=false;
    x.drawImage(off,0,0,size,size,0,0,size*zoom,size*zoom);
  };
  img.src='data:image/svg+xml;charset=utf-8,'+encodeURIComponent(c.dataset.src);
});
</script></body></html>""" % ''.join(rows)
p = os.path.join(OUT, 'mark-sizes.html')
io.open(p, 'w', encoding='utf-8').write(page)
print(p)
