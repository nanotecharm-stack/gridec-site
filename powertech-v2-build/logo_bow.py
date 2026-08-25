# -*- coding: utf-8 -*-
"""Лук со стрелой: зеркальная G и молния по центру.

Замысел владельца: взять G из имени, отразить её по горизонтали и пустить через
середину молнию. Отражённая G открывается ВЛЕВО, значит дуга выгибается вправо —
это и есть лук: тетива слева, стрела летит вправо сквозь дугу и выходит наружу.
Перекладина G после отражения смотрит внутрь с левой стороны, ровно там, где у
лука лежит древко стрелы, — она и подхватывает молнию.

Одно место требует решения, и оно не косметическое: молния пересекает дугу.
Если ничего не делать, две фигуры сливаются в кляксу, и стрела перестаёт быть
стрелой. Поэтому в дуге вырезается просвет по ходу молнии — маской, а не белой
обводкой: знак остаётся ОДНОГО цвета и ложится на любой грунт.

Веса взяты от стебля самой G, а не назначены на глаз: молния должна быть той же
толщины, что и буква, иначе знак читается как две разные вещи рядом.
"""
import io, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'logo-arrows')

G_D = io.open(os.path.join(OUT, '_g.txt'), encoding='utf-8').read().strip()
# замерено в браузере: габарит глифа в единицах шрифта
GX, GY, GW, GH = 41.0, -10.0, 693.0, 720.0

S = 0.25                      # 720 единиц шрифта → 180 из 200
TX = S * (GX + GW / 2.0)      # отражение: x = tx - S*gx
TY = S * (GY + GH / 2.0)

MIRROR = 'translate(%.3f %.3f) scale(%.4f %.4f)' % (TX, TY, -S, -S)
PLAIN = 'translate(%.3f %.3f) scale(%.4f %.4f)' % (-TX, TY, S, -S)

# Молния: ломаная от тетивы вправо. Излом резкий, без скруглений — разряд, а не
# кардиограмма. Последний отрезок прямой: на нём сидит наконечник.
BOLT = [(-70, 0), (-32, 0), (-15, -35), (6, 33), (27, -21), (46, 0), (70, 0)]
BOLT_W = 28                   # та же толщина, что стебель буквы
HEAD_TIP = 112
HEAD_BASE = 68
HEAD_HALF = 35
GAP = 15                      # на столько просвет шире самой молнии


def poly(pts):
    return 'M' + 'L'.join('%.2f %.2f' % p for p in pts)


def head():
    return ('M%.2f %.2f L%.2f 0 L%.2f %.2f Z'
            % (HEAD_BASE, -HEAD_HALF, HEAD_TIP, HEAD_BASE, HEAD_HALF))


def mark(mirror=True, knockout=True, uid='bw'):
    g_tr = MIRROR if mirror else PLAIN
    parts = []
    if knockout:
        parts.append(
            '<mask id="%s_m" maskUnits="userSpaceOnUse" x="-100" y="-100" '
            'width="200" height="200">'
            '<rect x="-100" y="-100" width="200" height="200" fill="#fff"/>'
            '<path d="%s" fill="none" stroke="#000" stroke-width="%d" '
            'stroke-linejoin="miter" stroke-linecap="butt"/>'
            '<path d="%s" fill="#000" stroke="#000" stroke-width="%d" '
            'stroke-linejoin="miter"/>'
            '</mask>' % (uid, poly(BOLT), BOLT_W + GAP * 2, head(), GAP * 2))
    parts.append('<g%s><path d="%s" transform="%s"/></g>'
                 % (' mask="url(#%s_m)"' % uid if knockout else '', G_D, g_tr))
    parts.append('<path d="%s" fill="none" stroke="currentColor" '
                 'stroke-width="%d" stroke-linejoin="miter" stroke-linecap="butt"/>'
                 % (poly(BOLT), BOLT_W))
    parts.append('<path d="%s"/>' % head())
    return ''.join(parts)


VARIANTS = [
    ('bow', 'Лук со стрелой', True, True,
     'G отражена: дуга выгибается вправо, тетива слева, стрела уходит наружу. '
     'В дуге вырезан просвет по ходу молнии — иначе стрела в неё влипает.'),
    ('bow-nogap', 'То же, без просвета', True, False,
     'Показано, зачем нужен просвет: молния и дуга сливаются.'),
    ('sketch', 'Как на эскизе, без отражения', False, True,
     'G открыта вправо, стрела выходит через её проём. Лук здесь не читается — '
     'дуга смотрит в ту же сторону, куда летит стрела.'),
]

os.makedirs(OUT, exist_ok=True)

PLATE = '#0D2440'
PAPER = '#EFEDEA'


def svg(key, mirror, knock, color, size=None):
    wh = ('width="%d" height="%d" ' % (size, size)) if size else ''
    return ('<svg xmlns="http://www.w3.org/2000/svg" %sviewBox="-100 -100 200 200" '
            'fill="%s" style="color:%s">%s</svg>'
            % (wh, color, color, mark(mirror, knock, uid=key)))


for key, _, mirror, knock, _ in VARIANTS:
    io.open(os.path.join(OUT, 'bow-%s.svg' % key), 'w', encoding='utf-8').write(
        svg(key, mirror, knock, PLATE))

# ------------------------------------------------ знак в шапке настоящего сайта
# Знак квадратный 200×200, куб был 173×193 — ставим по той же середине плашки.
LOCK_SCALE = 0.30
CUBE = re.compile(
    r'<g transform="translate\(56\.0 61\.7\) scale\(0\.3168\)".*?</g>'
    r'<g transform="translate\(56\.0 57\.9\) scale\(0\.3168\)".*?</g>'
    r'<g transform="translate\(56\.0 56\.0\) scale\(0\.3168\)".*?</g>', re.S)
src = io.open(os.path.join(HERE, 'pt-en.html'), encoding='utf-8').read()
for key, _, mirror, knock, _ in VARIANTS:
    body = mark(mirror, knock, uid='lk' + key.replace('-', ''))
    new = ('<g transform="translate(56.0 56.0) scale(%.4f)" fill="#FFFFFF" '
           'style="color:#FFFFFF">%s</g>' % (LOCK_SCALE, body))
    page, n = CUBE.subn(new, src)
    assert n == 1
    io.open(os.path.join(OUT, 'bow-site-%s.html' % key), 'w',
            encoding='utf-8').write(page)
    print('bow-site-%s.html' % key, n)

# ------------------------------------------------------- размеры и страница
SIZES = [(16, 12), (24, 8), (32, 6), (48, 4), (96, 2)]
rows = []
for key, title, mirror, knock, note in VARIANTS:
    grounds = []
    for bg, fg, lab in ((PAPER, PLATE, 'на бумаге'), (PLATE, PAPER, 'на плашке')):
        cells = ''.join(
            '<div class="sz"><canvas data-src="%s" data-size="%d" data-zoom="%d" '
            'style="background:%s"></canvas><b>%dpx</b></div>'
            % (svg(key + str(s), mirror, knock, fg).replace('"', '&quot;'),
               s, z, bg, s)
            for s, z in SIZES)
        grounds.append('<div class="ground"><span class="lab">%s</span>'
                       '<div class="row">%s</div></div>' % (lab, cells))
    big = ('<div class="real"><div class="rbox" style="background:%s">%s</div>'
           '<b>крупно: визитка, бланк</b></div>'
           % (PAPER, svg(key + 'big', mirror, knock, PLATE, size=132)))
    rows.append('<section><h2>%s</h2><p>%s</p>%s%s</section>'
                % (title, note, ''.join(grounds), big))

page = u"""<!doctype html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Лук со стрелой</title><style>
*{box-sizing:border-box}
body{margin:0;padding:40px 28px 60px;background:#F6F5F3;color:#0D0E13;
  font:15px/1.6 -apple-system,Segoe UI,Roboto,sans-serif}
h1{font-size:22px;margin:0 0 6px}
.sub{max-width:64ch;margin:0 0 32px;color:#5A5F66}
section{background:#fff;border:1px solid #E3E0DB;padding:22px 24px;
  margin-bottom:20px;max-width:980px;border-radius:3px}
h2{font-size:16px;margin:0 0 4px}
section>p{margin:0 0 18px;color:#5A5F66;font-size:13.5px;max-width:62ch}
.lab,.sz b,.real b{font:11px/1.4 ui-monospace,Menlo,monospace;letter-spacing:.1em;
  text-transform:uppercase;color:#8A8F96}
.row{display:flex;align-items:flex-end;gap:18px;margin-top:8px;flex-wrap:wrap}
.sz{text-align:center}
canvas{display:block;border:1px solid #E3E0DB;image-rendering:pixelated}
.sz b{display:block;margin-top:6px}
.ground{margin-bottom:14px}
.real{margin-top:18px;padding-top:16px;border-top:1px dashed #E3E0DB;
  display:flex;align-items:center;gap:16px}
.rbox{display:flex;align-items:center;justify-content:center;width:164px;
  height:164px;border:1px solid #E3E0DB}
</style></head><body>
<h1>Лук со стрелой</h1>
<p class="sub">G из имени, отражённая по горизонтали, и молния через середину.
Размеры настоящие, увеличены без сглаживания.</p>
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
p = os.path.join(OUT, 'bow.html')
io.open(p, 'w', encoding='utf-8').write(page)
print(p)
