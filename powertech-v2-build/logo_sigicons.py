# -*- coding: utf-8 -*-
"""Три значка для почтовой подписи: телефон, конверт, глобус.

Рисуются втрое крупнее, чем показываются: 42 пикселя против 14. Почту читают и
с телефонов, у которых на точку экрана приходится две-три точки растра, и
значок в свой размер там был бы мутным.

Обводка, а не заливка: на 14 пикселях залитая фигура превращается в кляксу, а
контур сохраняет, что это за предмет. Толщина 3 из 42 — это ровно один пиксель
на показе, тоньше делать нечего.

У каждого значка есть alt: если почтовая программа получателя режет внешние
картинки — а в организациях это обычное дело, — на месте значка встанет слово.
Подпись не останется без подписей полей.
"""
import io, os
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'brand')
S = 42
COL = (90, 95, 102, 255)      # #5A5F66 — тон подписей полей
W = 3


def canvas():
    img = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    return img, ImageDraw.Draw(img)


def phone():
    """Телефон-трубка узнаётся хуже плоского аппарата — рисуем аппарат."""
    img, d = canvas()
    d.rounded_rectangle([12, 3, 30, 39], radius=4, outline=COL, width=W)
    d.rounded_rectangle([18, 33, 24, 35], radius=1, fill=COL)
    return img


def mail():
    img, d = canvas()
    d.rectangle([4, 10, 38, 32], outline=COL, width=W)
    d.line([(5, 11), (21, 24), (37, 11)], fill=COL, width=W, joint='curve')
    return img


def web():
    img, d = canvas()
    d.ellipse([4, 4, 38, 38], outline=COL, width=W)
    d.ellipse([14, 4, 28, 38], outline=COL, width=W)
    d.line([(5, 21), (37, 21)], fill=COL, width=W)
    return img


os.makedirs(OUT, exist_ok=True)
for name, fn in (('ic-tel', phone), ('ic-mail', mail), ('ic-web', web)):
    p = os.path.join(OUT, name + '.png')
    fn().save(p)
    print(name, os.path.getsize(p), 'bytes')
