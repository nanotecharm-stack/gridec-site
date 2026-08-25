# -*- coding: utf-8 -*-
"""Три стрелки — как отличить фазы от осей координат.

Замечание владельца: три луча из точки через 120° — это ровно то, как рисуют
изометрические оси X-Y-Z. Он прав. На чертеже эти две вещи различают ПОДПИСИ:
«A B C» у фаз, «X Y Z» у осей. В знаке подписей нет.

Различие, которое подписи не требует: оси стоят, фазы ИДУТ ПО КРУГУ. Всё, что
вносит в знак ход по кругу, снимает прочтение «оси координат».

Три способа внести его:
  1. поставить стрелки в треугольник — они пойдут одна за другой (и это заодно
     соединение треугольником, ещё одна вещь из трёхфазных схем);
  2. оставить звезду, но замкнуть её кольцом с одной стрелкой — вектор
     вращается;
  3. развернуть стрелки по касательной — вертушка.

Вес линии считается по прошлому проходу: древко толще трёх физических пикселей
на 24, просветы шире двух, мелких деталей нет.
"""
import io, os, math

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'logo-arrows')

INK = '#0D2440'
PAPER = '#EFEDEA'


def poly(pts):
    return 'M' + 'L'.join('%.2f %.2f' % p for p in pts) + 'Z'


def arrow_between(a, b, t0, t1, tip_t, half, head):
    """Стрелка ВДОЛЬ отрезка a→b, заданная долями его длины."""
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    px, py = -uy, ux
    def P(t, across):
        return (a[0] + ux * L * t + px * across, a[1] + uy * L * t + py * across)
    return poly([P(t0, -half), P(t1, -half), P(t1, -head), P(tip_t, 0),
                 P(t1, head), P(t1, half), P(t0, half)])


def ray(cx, cy, ang, r0, r1, tip, half, head):
    a = math.radians(ang)
    ux, uy = math.cos(a), -math.sin(a)
    px, py = -uy, ux
    def P(al, ac):
        return (cx + ux * al + px * ac, cy + uy * al + py * ac)
    return poly([P(r0, -half), P(r1, -half), P(r1, -head), P(tip, 0),
                 P(r1, head), P(r1, half), P(r0, half)])


def vert(cx, cy, r, ang):
    a = math.radians(ang)
    return (cx + r * math.cos(a), cy - r * math.sin(a))


# ------------------------------------------------------------------ знаки
def delta(cx=50, cy=50, R=46):
    """Три стрелки, поставленные в треугольник: идут одна за другой."""
    V = [vert(cx, cy, R, a) for a in (90, 330, 210)]     # по часовой
    d = []
    for i in range(3):
        d.append(arrow_between(V[i], V[(i + 1) % 3], 0.06, 0.60, 0.94, 7.5, 18))
    return ' '.join(d)


def star_ring(cx=50, cy=50):
    """Звезда плюс кольцо с одной стрелкой — вектор вращается."""
    rays = ' '.join(ray(cx, cy, a, 0, 20, 34, 7, 16) for a in (90, 210, 330))
    # кольцо: толстая дуга с разрывом, в разрыв встаёт голова
    r, w = 43, 9
    a0, a1 = math.radians(118), math.radians(56)
    def arc(rr, s, e, sweep):
        p0 = (cx + rr * math.cos(s), cy - rr * math.sin(s))
        p1 = (cx + rr * math.cos(e), cy - rr * math.sin(e))
        return p0, p1
    o0, o1 = arc(r + w / 2, a0, a1 - 2 * math.pi, 0)
    i0, i1 = arc(r - w / 2, a0, a1 - 2 * math.pi, 0)
    ring = ('M%.2f %.2f A%.2f %.2f 0 1 0 %.2f %.2f L%.2f %.2f '
            'A%.2f %.2f 0 1 1 %.2f %.2f Z'
            % (o0[0], o0[1], r + w / 2, r + w / 2, o1[0], o1[1],
               i1[0], i1[1], r - w / 2, r - w / 2, i0[0], i0[1]))
    # голова на конце дуги, поперёк неё
    ah = math.radians(56)
    tx, ty = cx + r * math.cos(ah), cy - r * math.sin(ah)
    ux, uy = -math.sin(ah), -math.cos(ah)          # по касательной, по часовой
    px, py = -uy, ux
    head = poly([(tx + px * 15, ty + py * 15), (tx - px * 15, ty - py * 15),
                 (tx + ux * 26, ty + uy * 26)])
    return rays + ' ' + ring + ' ' + head


def pinwheel(cx=50, cy=50):
    """Стрелки по касательной — вертушка: ход по кругу без всякой рамки."""
    d = []
    for a in (90, 210, 330):
        ar = math.radians(a)
        # начало на радиусе 14, направление — под 60° к радиусу
        sx, sy = cx + 14 * math.cos(ar), cy - 14 * math.sin(ar)
        dirang = ar + math.radians(58)
        ux, uy = math.cos(dirang), -math.sin(dirang)
        px, py = -uy, ux
        def P(al, ac, sx=sx, sy=sy, ux=ux, uy=uy, px=px, py=py):
            return (sx + ux * al + px * ac, sy + uy * al + py * ac)
        d.append(poly([P(0, -7.5), P(26, -7.5), P(26, -18), P(46, 0),
                       P(26, 18), P(26, 7.5), P(0, 7.5)]))
    return ' '.join(d)


def wye(cx=50, cy=50):
    """Прошлый выбор — сплошной Y. Оставлен для сравнения: он и есть «оси»."""
    return ' '.join(ray(cx, cy, a, 0, 28, 48, 7.8, 18) for a in (90, 210, 330))


CAND = [
    ('wye', 'Сплошной Y — для сравнения', wye(),
     'Тот самый знак, про который вы и спросили. Читается и как фазы, и как оси.'),
    ('delta', 'Стрелки в треугольник', delta(),
     'Три стрелки идут одна за другой — ход по кругу виден сразу. Треугольник '
     'вдобавок сам по себе из трёхфазных схем: соединение треугольником.'),
    ('pinwheel', 'Вертушка', pinwheel(),
     'Те же три стрелки, но развёрнуты по касательной. Вращение без рамки. '
     'Риск: похоже на значок переработки — смотрите сами.'),
    ('star-ring', 'Звезда в кольце вращения', star_ring(),
     'Звезда остаётся, кольцо со стрелкой добавляет ход. Деталей больше всех — '
     'проверяйте на 24 и 16.'),
]

SIZES = [(16, 12), (24, 8), (32, 6), (48, 4)]


def svg_src(d, color):
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'
            '<path d="%s" fill="%s" fill-rule="nonzero"/></svg>' % (d, color))


os.makedirs(OUT, exist_ok=True)
for key, _, d, _ in CAND:
    io.open(os.path.join(OUT, key + '.svg'), 'w', encoding='utf-8').write(
        svg_src(d, INK))

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
    big = ('<div class="real"><div class="rbox" style="background:%s">'
           '<svg viewBox="0 0 100 100" width="112" height="112">'
           '<path d="%s" fill="%s"/></svg></div>'
           '<b>крупно: визитка, бланк, вывеска</b></div>' % (PAPER, d, INK))
    rows.append('<section id="%s"><h2>%s</h2><p>%s</p>%s%s</section>'
                % (key, title, note, ''.join(grounds), big))

page = u"""<!doctype html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Gridec — фазы, а не оси</title>
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
.rbox{display:flex;align-items:center;justify-content:center;width:140px;
  height:140px;border:1px solid #E3E0DB}
</style></head><body>
<h1>Фазы, а не оси координат</h1>
<p class="sub">Оси стоят, фазы идут по кругу. Каждый знак ниже вносит этот ход
своим способом. Размеры настоящие, увеличены без сглаживания — видны те самые
пиксели, что видит экран.</p>
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
</script>
</body></html>""" % ''.join(rows)

path = os.path.join(OUT, 'phase.html')
io.open(path, 'w', encoding='utf-8').write(page)
print(path)
