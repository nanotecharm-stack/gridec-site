# Рисует слово GRIDEC шрифтом Departure Mono — так же, как в шапке сайта:
# кегль кратен 11 (сетка шрифта), трекинг = 3/22 кегля, лишний просвет
# после последней буквы снимается.
from PIL import Image, ImageDraw, ImageFont

FONT = 'departure-mono.ttf'
WORD = 'GRIDEC'


def draw(scale, rgb, out):
    size = 22 * scale
    track = 3 * scale
    f = ImageFont.truetype(FONT, size)
    adv = [f.getlength(c) for c in WORD]
    w = int(round(sum(adv) + track * (len(WORD) - 1)))
    h = size * 2
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = 0.0
    for i, c in enumerate(WORD):
        d.text((x, size // 2), c, font=f, fill=rgb + (255,))
        x += adv[i] + track
    bb = im.getbbox()
    im = im.crop(bb)
    im.save(out)
    print(out, im.size)


PAPER = (246, 241, 233)
INK = (13, 36, 64)
draw(8, PAPER, 'wm_paper.png')
draw(8, INK, 'wm_ink.png')
draw(3, PAPER, 'wm_paper_sm.png')
draw(3, INK, 'wm_ink_sm.png')
