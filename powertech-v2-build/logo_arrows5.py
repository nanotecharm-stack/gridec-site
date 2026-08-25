# -*- coding: utf-8 -*-
"""Знак с кольцом: три стрелки из точки замера.

Владелец прислал второй вариант: три стрелки через 120° и КОЛЬЦО в середине.
По смыслу это лучше прежних. Кольцо — точка замера, из неё расходятся фазы; и
оно же снимает прочтение «оси координат», потому что у осей ступицы не бывает.

Слабое место у него ровно одно: кольцо. Стенка кольца и просвет внутри — две
самые тонкие детали знака, а именно тонкие детали и сереют на 24 пикселях.
Порог из прошлого прохода: линия толще трёх физических пикселей, просвет толще
двух. На 24 пикселях это 25 и 17 единиц из 200.

Три пробы:
  as-drawn — пропорции как на присланной картинке;
  tuned    — те же формы, веса подняты до порога;
  dot      — кольцо закрыто в точку: хрупкой детали нет вовсе.
"""
import io, os, re, math

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'logo-arrows')

PLATE = '#0D2440'
PAPER = '#EFEDEA'


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
    """Кольцо одной фигурой: внешний круг по часовой, внутренний против.

    Два круга в одном контуре с правилом evenodd дали бы дырку и без разворота,
    но правило пришлось бы объявлять на КАЖДОЙ вставке знака. Разворот делает
    фигуру самодостаточной: она даёт дырку в любом окружении.
    """
    def circle(r, sweep):
        return ('M%.2f 0A%.2f %.2f 0 1 %d %.2f 0A%.2f %.2f 0 1 %d %.2f 0Z'
                % (r, r, r, sweep, -r, r, r, sweep, r))
    return circle(ro, 1) + circle(ri, 0)


def build(r0, tip, corner, junc, headw, shaftw, ro, ri):
    arms = ' '.join(dart(a, r0, tip, corner, junc, headw, shaftw)
                    for a in (90, 210, 330))
    return arms + ' ' + (ring(ro, ri) if ri else
                         'M%.2f 0A%.2f %.2f 0 1 1 %.2f 0A%.2f %.2f 0 1 1 %.2f 0Z'
                         % (ro, ro, ro, -ro, ro, ro, ro))


# r0 — где начинается древко; ставим его внутрь кольца, чтобы стыка не было видно
MARKS = {
    # как на картинке: тонкие древки, узкая стенка кольца
    'as-drawn': build(r0=18, tip=100, corner=30, junc=54, headw=44,
                      shaftw=9, ro=27, ri=13),
    # те же формы, веса подняты до порога читаемости
    'tuned':    build(r0=20, tip=100, corner=32, junc=56, headw=48,
                      shaftw=14, ro=37, ri=15),
    # кольцо закрыто: ломаться нечему
    'dot':      build(r0=16, tip=100, corner=32, junc=56, headw=48,
                      shaftw=14, ro=30, ri=0),
}
TITLES = [
    ('as-drawn', 'Как на вашей картинке',
     'Стенка кольца 14 единиц — 1.7 пикселя на 24. Просвет 26 — 3.1.'),
    ('tuned', 'Веса подняты',
     'Стенка 22 единицы — 2.6 пикселя, просвет 30 — 3.6, древко 28 — 3.4.'),
    ('dot', 'Кольцо закрыто в точку',
     'Тонких деталей нет. Точка замера читается, дырка не сереет.'),
]

# ------------------------------------------------- подмена знака в локапе
SCALE = 0.35
TY = 56.0 + 25.0 * SCALE
CUBE = re.compile(
    r'<g transform="translate\(56\.0 61\.7\) scale\(0\.3168\)".*?</g>'
    r'<g transform="translate\(56\.0 57\.9\) scale\(0\.3168\)".*?</g>'
    r'<g transform="translate\(56\.0 56\.0\) scale\(0\.3168\)".*?</g>', re.S)

os.makedirs(OUT, exist_ok=True)
src = io.open(os.path.join(HERE, 'pt-en.html'), encoding='utf-8').read()
for key, d in MARKS.items():
    new = ('<g transform="translate(56.0 %.2f) scale(%.4f)">'
           '<path fill="#FFFFFF" d="%s"/></g>' % (TY, SCALE, d))
    page, n = CUBE.subn(new, src)
    assert n == 1
    io.open(os.path.join(OUT, 'ring-site-%s.html' % key), 'w',
            encoding='utf-8').write(page)
    io.open(os.path.join(OUT, 'ring-%s.svg' % key), 'w', encoding='utf-8').write(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="-100 -100 200 150">'
        '<path fill="%s" d="%s"/></svg>' % (PLATE, d))
    print('ring-site-%s.html' % key, n)

# ------------------------------------------------ проверка малых размеров
SIZES = [(16, 12), (24, 8), (32, 6), (48, 4)]


def svg_src(d, color):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-100 -100 200 150">'
            '<path fill="%s" d="%s"/></svg>' % (color, d))


rows = []
for key, title, note in TITLES:
    d = MARKS[key]
    grounds = []
    for bg, fg, lab in ((PAPER, PLATE, 'на бумаге'), (PLATE, PAPER, 'на плашке')):
        cells = ''.join(
            '<div class="sz"><canvas data-key="%s" data-src="%s" data-size="%d" '
            'data-zoom="%d" style="background:%s"></canvas><b>%dpx</b></div>'
            % (key, svg_src(d, fg).replace('"', '&quot;'), s, z, bg, s)
            for s, z in SIZES)
        grounds.append('<div class="ground"><span class="lab">%s</span>'
                       '<div class="row">%s</div></div>' % (lab, cells))
    big = ('<div class="real"><div class="rbox" style="background:%s">'
           '<svg viewBox="-100 -100 200 150" width="130" height="98">'
           '<path fill="%s" d="%s"/></svg></div>'
           '<b>крупно: визитка, бланк</b></div>' % (PAPER, PLATE, d))
    rows.append('<section><h2>%s</h2><p>%s</p>%s%s</section>'
                % (title, note, ''.join(grounds), big))

page = u"""<!doctype html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Знак с кольцом — размеры</title><style>
*{box-sizing:border-box}
body{margin:0;padding:40px 28px 60px;background:#F6F5F3;color:#0D0E13;
  font:15px/1.6 -apple-system,Segoe UI,Roboto,sans-serif}
h1{font-size:22px;margin:0 0 6px}
.sub{max-width:64ch;margin:0 0 32px;color:#5A5F66}
section{background:#fff;border:1px solid #E3E0DB;padding:22px 24px;
  margin-bottom:20px;max-width:940px;border-radius:3px}
h2{font-size:16px;margin:0 0 4px}
section>p{margin:0 0 18px;color:#5A5F66;font-size:13.5px}
.lab,.sz b,.real b{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.1em;
  text-transform:uppercase;color:#8A8F96}
.row{display:flex;align-items:flex-end;gap:20px;margin-top:8px;flex-wrap:wrap}
.sz{text-align:center}
canvas{display:block;border:1px solid #E3E0DB;image-rendering:pixelated}
.sz b{display:block;margin-top:6px}
.ground{margin-bottom:14px}
.real{margin-top:18px;padding-top:16px;border-top:1px dashed #E3E0DB;
  display:flex;align-items:center;gap:16px}
.rbox{display:flex;align-items:center;justify-content:center;width:160px;
  height:120px;border:1px solid #E3E0DB}
</style></head><body>
<h1>Кольцо на малых размерах</h1>
<p class="sub">Размеры настоящие, увеличено без сглаживания. Смотрите на просвет
внутри кольца: на 24 и 16 пикселях именно он решает, знак это или пятно.</p>
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
p = os.path.join(OUT, 'ring-sizes.html')
io.open(p, 'w', encoding='utf-8').write(page)
print(p)
