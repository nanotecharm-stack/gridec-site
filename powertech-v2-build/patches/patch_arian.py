# -*- coding: utf-8 -*-
"""Armenian type: Arian AMU for headings and body, Arian AMU Serif for the label
role that Martian Mono fills in English. Noto drops out of the HY build entirely."""
import io, re

b = io.open('build.py', encoding='utf-8').read()

# weights may now be ranges ('600 900') — Arian ships only Regular and Bold, and a
# range keeps 500/600 on a real face instead of letting the browser fake a bold.
b = b.replace("font-weight:%d;font-display:swap;", "font-weight:%s;font-display:swap;")
assert "font-weight:%d" not in b, 'a %d weight slot survived'

def swap_list(src, name, faces):
    i = src.index(name + " = '")
    j = src.index('])', i) + 2
    return src[:i] + name + " = '\\n'.join([\n" + faces + "\n])" + src[j:]

FACES_B64 = """    font_face('Arian AMU', '400 500', 'arian-amu-400.woff2'),
    font_face('Arian AMU', '600 900', 'arian-amu-700.woff2'),
    font_face('Arian AMU Serif', '400 500', 'arian-amu-serif-400.woff2'),
    font_face('Arian AMU Serif', '600 900', 'arian-amu-serif-700.woff2'),"""
FACES_URL = FACES_B64.replace('font_face(', 'font_face_url(')

b = swap_list(b, 'FF_HY_D', FACES_URL)   # the longer name first
b = swap_list(b, 'FF_HY', FACES_B64)

b = b.replace(""" 'BODYFONT': "'Noto Sans Armenian','Helvetica Neue',sans-serif",
 'HEADFONT': "'PT HY Display','Noto Sans Armenian',sans-serif",
 'MONOFALL': "'Noto Sans Armenian',monospace",""",
""" 'BODYFONT': "'Arian AMU','Helvetica Neue',sans-serif",
 'HEADFONT': "'Arian AMU',sans-serif",
 'MONOFONT': "'Arian AMU Serif',Georgia,serif",""")
b = b.replace(""" 'MONOFALL': 'monospace',""", """ 'MONOFONT': "'Martian Mono',monospace",""")

io.open('build.py', 'w', encoding='utf-8').write(b)

print('MONOFONT tokens :', b.count("'MONOFONT'"))
print('MONOFALL left   :', b.count('MONOFALL'))
print('arian faces     :', b.count('arian-amu'))
print('noto in HY list :', 'noto-sans-armenian' in b[b.index('FF_HY ='):b.index('IMG_FILES')])
print('weight ranges   :', b.count("'600 900'"))
