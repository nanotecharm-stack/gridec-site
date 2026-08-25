# Иконки под выбранный локап: та же плашка, тот же свет.
#
# Два чертежа, а не один. Крупный несёт тень, блик и уклон плашки. Мелкий (16 и
# 32 пикселя) их теряет — там тень занимает полпикселя и превращается в грязь,
# поэтому для мелких кадров рисуется упрощённый: ровные грани, без тени и блика.
#
#   python icons_plate.py
#
# Пишет favicon.svg, favicon.ico, apple-touch-icon.png в корень репозитория
# и рабочие файлы в logo-v8/final/icons/.
import io
import os
import subprocess
import sys

from PIL import Image

from logo_lib import HX, MARK_H, faces

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..'))
WORK = os.path.join(HERE, 'logo-v8', 'final', 'icons')
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'

def edges(d):
    a, b = round(0.57735 * d, 3), round(1.1547 * d, 3)
    return ('M-%s -50 L-%s -%s' % (HX, d, round(100 - a, 3)),
            'M%s -%s L%s -50' % (d, round(100 - a, 3), HX),
            'M-%s %s L0 %s L%s %s' % (HX, round(50 + b, 3), b, HX, round(50 + b, 3)))
VECS = ((0, 0, 1, 0.4), (1, 0, 0, 0.4), (0.5, 0, 0.5, 1))
RAMPS = (('#C6C6C6', '#9A9A9A'), ('#F6F6F6', '#D2D2D2'), ('#FFFFFF', '#E4E4E4'))
FLAT = ('#AEAEAE', '#E0E0E0', '#F7F7F7')      # средний тон каждой грани
PLATE = ('#162E52', '#0D2440')      # ink3 -> ink синей палитры сайта
ALT = ('#414141', '#141414')        # запасной графитовый грунт


def icon(size=100, rx=0.21, plate=PLATE, detail=True, mark=0.66, seam=12.0):
    FACES = faces(seam)
    mh = size * mark
    k = mh / MARK_H
    c = size / 2
    r = round(size * rx, 2)
    rect = 'width="%s" height="%s" rx="%s"' % (size, size, r)
    defs = ['<linearGradient id="bg" x1="0" y1="0" x2="0.55" y2="1">'
            '<stop offset="0" stop-color="%s"/><stop offset="1" stop-color="%s"/>'
            '</linearGradient>' % plate]
    body = ['<rect %s fill="url(#bg)"/>' % rect]
    if detail:
        defs += ['<linearGradient id="f%d" x1="%s" y1="%s" x2="%s" y2="%s">'
                 '<stop offset="0" stop-color="%s"/>'
                 '<stop offset="1" stop-color="%s"/></linearGradient>'
                 % ((i,) + tuple(v) + (a, b))
                 for i, ((a, b), v) in enumerate(zip(RAMPS, VECS))]
        defs += ['<linearGradient id="sn" x1="0" y1="0" x2="0" y2="1">'
                 '<stop offset="0" stop-color="#FFFFFF" stop-opacity="0.16"/>'
                 '<stop offset="0.5" stop-color="#FFFFFF" stop-opacity="0"/>'
                 '<stop offset="1" stop-color="#000000" stop-opacity="0.20"/>'
                 '</linearGradient>',
                 '<radialGradient id="vg" cx="0.28" cy="0.22" r="0.95">'
                 '<stop offset="0" stop-color="#FFFFFF" stop-opacity="0.07"/>'
                 '<stop offset="0.55" stop-color="#000000" stop-opacity="0"/>'
                 '<stop offset="1" stop-color="#000000" stop-opacity="0.22"/>'
                 '</radialGradient>']
        drop = ''.join('<path d="%s"/>' % d for d in FACES)
        for i, (dev, dy, op) in enumerate(((0.13, 0.09, 0.38), (0.035, 0.03, 0.45))):
            defs.append('<filter id="s%d" x="-50%%" y="-50%%" width="200%%" '
                        'height="200%%"><feGaussianBlur stdDeviation="%s"/></filter>'
                        % (i, round(mh * dev, 3)))
            body.append('<g transform="translate(%s %s) scale(%s)" fill-opacity="%s" '
                        'filter="url(#s%d)">%s</g>'
                        % (c, round(c + mh * dy, 3), round(k, 6), op, i, drop))
        face_ps = ''.join('<path fill="url(#f%d)" d="%s"/>' % (i, d)
                          for i, d in enumerate(FACES))
        face_ps += ''.join('<path d="%s" fill="none" stroke="#FFFFFF" '
                         'stroke-opacity="0.55" stroke-width="2.6" '
                         'stroke-linecap="round" stroke-linejoin="round"/>' % d
                         for d in edges(seam))
    else:
        face_ps = ''.join('<path fill="%s" d="%s"/>' % (col, d)
                          for col, d in zip(FLAT, FACES))
    body.append('<g transform="translate(%s %s) scale(%s)">%s</g>'
                % (c, c, round(k, 6), face_ps))
    if detail:
        body.append('<rect %s fill="url(#sn)"/>' % rect)
        body.append('<rect %s fill="url(#vg)"/>' % rect)
    return ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %s %s" role="img" '
            'aria-label="Gridec"><defs>%s</defs>%s</svg>'
            % (size, size, ''.join(defs), ''.join(body)))


def shoot(svg_path, png_path, px):
    subprocess.run([CHROME, '--headless', '--disable-gpu', '--hide-scrollbars',
                    '--default-background-color=00000000',
                    '--force-device-scale-factor=1',
                    '--screenshot=' + png_path, '--window-size=%d,%d' % (px, px),
                    'file:///' + svg_path.replace('\\', '/')],
                   check=True, capture_output=True)


os.makedirs(WORK, exist_ok=True)
# Чем мельче кадр, тем крупнее куб и тем меньше скругление: на 16 пикселях знак
# в 56 % плашки занимает девять точек и читается пятном.
plans = [('icon-full', 48, dict()),
         ('icon-full', 64, dict()),
         ('icon-16', 16, dict(detail=False, mark=0.74, rx=0.18, seam=18.0)),
         ('icon-32', 32, dict(detail=False, mark=0.68, rx=0.20, seam=15.0)),
         ('icon-graphite', None, dict(plate=ALT))]
pngs = {}
for name, px, kw in plans:
    p = os.path.join(WORK, '%s.svg' % name)
    io.open(p, 'w', encoding='utf-8').write(icon(**kw))
    if px is None:
        continue
    out = os.path.join(WORK, '%s-%d.png' % (name, px))
    shoot(p, out, px)
    pngs[px] = out
    print('%-16s %3d px' % (name, px))

# apple-touch — квадрат без скруглений: iOS кладёт свою маску поверх, и наш
# радиус под ней даёт двойной кант.
p = os.path.join(WORK, 'icon-apple.svg')
io.open(p, 'w', encoding='utf-8').write(icon(rx=0, mark=0.50))
shoot(p, os.path.join(WORK, 'apple-180.png'), 180)

ico = os.path.join(ROOT, 'favicon.ico')
frames = [Image.open(pngs[px]).convert('RGBA') for px in (16, 32, 48, 64)]
frames[0].save(ico, format='ICO',
               sizes=[(16, 16), (32, 32), (48, 48), (64, 64)],
               append_images=frames[1:])
io.open(os.path.join(ROOT, 'favicon.svg'), 'w', encoding='utf-8').write(icon())
Image.open(os.path.join(WORK, 'apple-180.png')).convert('RGB').save(
    os.path.join(ROOT, 'apple-touch-icon.png'))
print('favicon.svg / favicon.ico / apple-touch-icon.png -> %s' % ROOT)
