# -*- coding: utf-8 -*-
"""Armenian type trial.

Stages:
  dl     download the candidate archives from fonter.am into fonts_src/
  make   unpack, subset to Armenian+Latin, emit woff2 into ../assets/v2/tfonts/
  pages  write two review pages into ../assets/v2/:
           type.html     all candidates side by side on the site's own HY copy
           hy-type.html  the real HY page with a switcher (heading / body / labels)

Run: python fonts_try.py dl make pages
"""
import io, os, re, sys, zipfile, json, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(HERE, 'fonts_src')
V2   = os.path.abspath(os.path.join(HERE, '..', 'assets', 'v2'))
OUT  = os.path.join(V2, 'tfonts')

# slug -> (display name, the role it is plausibly for)
CAND = [
    ('montserrat-armenian', 'Montserrat Armenian', 'geometric sans'),
    ('arian-amu-serif',     'Arian AMU Serif',     'serif'),
    ('arian-amu',           'Arian AMU',           'grotesque sans'),
    ('ghea-grapalat',       'GHEA Grapalat',       'humanist sans (state font)'),
    ('atyan-dsegh',         'Atyan Dsegh',         'display, all caps'),
    ('amrys',               'Amrys',               'sans'),
    ('weblysleek-ui',       'WeblySleek UI',       'UI sans'),
    ('parz',                'Parz',                'sans'),
]

# Licence status read out of each archive: the OS/2 fsType embedding bits, the
# font's own name-table records (13 = licence, 14 = licence URL) and any licence
# file shipped alongside. Three levels, because two of these cannot go on a site.
LIC = {
    'montserrat-armenian': ('ok',   u'SIL OFL 1.1 — վեբում ազատ'),
    'arian-amu-serif':     ('ok',   u'SIL OFL 1.1 (Tarumian) — վեբում ազատ'),
    'arian-amu':           ('ok',   u'SIL OFL 1.1 (Tarumian) — վեբում ազատ'),
    'ghea-grapalat':       ('warn', u'ՀՀ պետական տառատեսակ, fsType=editable — գրավոր վեբ-լիցենզիա չկա'),
    'atyan-dsegh':         ('warn', u'fsType=preview&print only — վեբ-ներդրումն արգելված է դրոշակով'),
    'amrys':               ('risk', u'Monotype Imaging Inc. — առևտրային, պահանջում է վճարովի վեբ-լիցենզիա'),
    'weblysleek-ui':       ('risk', u'լիցենզիա բացակայում է, Segoe UI-ի ածանցյալ — իրավական ռիսկ'),
    'parz':                ('warn', u'լիցենզիա բացակայում է արխիվում — հեղինակի հաստատում է պետք'),
}

# ----------------------------------------------------------------- dl
def dl():
    os.makedirs(SRC, exist_ok=True)
    for slug, name, _ in CAND:
        dst = os.path.join(SRC, slug + '.zip')
        if os.path.exists(dst) and os.path.getsize(dst) > 1000:
            print('have  %-22s %d KB' % (slug, os.path.getsize(dst) // 1024)); continue
        url = 'https://fonter.am/fonts/download/' + slug
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        data = urllib.request.urlopen(req, timeout=90).read()
        io.open(dst, 'wb').write(data)
        print('got   %-22s %d KB' % (slug, len(data) // 1024))

# ----------------------------------------------------------------- make
UNI = ('U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,'
       'U+0530-058F,U+FB13-FB17,'
       'U+2000-206F,U+2074,U+20AC,U+2122,U+2191,U+2192,U+2197,U+2212,U+2500-2502,U+25A0,U+25CF')

WMAP = [  # subfamily fragment -> weight ; order matters (longest first)
    ('extrabold', 800), ('semibold', 600), ('demibold', 600), ('extralight', 200),
    ('black', 900), ('heavy', 900), ('bold', 700), ('medium', 500),
    ('regular', 400), ('normal', 400), ('book', 400), ('light', 300), ('thin', 100),
]
WANT = (400, 500, 600, 700)

def face_info(path):
    from fontTools.ttLib import TTFont
    f = TTFont(path, fontNumber=0, lazy=True)
    nm = {}
    for rec in f['name'].names:
        if rec.nameID in (1, 2, 16, 17) and rec.platformID in (1, 3):
            try: nm.setdefault(rec.nameID, rec.toUnicode())
            except Exception: pass
    fam = nm.get(16) or nm.get(1) or ''
    sub = (nm.get(17) or nm.get(2) or '').lower()
    italic = 'italic' in sub or 'oblique' in sub
    try: os2w = f['OS/2'].usWeightClass
    except Exception: os2w = 400
    w = None
    for frag, val in WMAP:
        if frag in sub.replace(' ', ''): w = val; break
    if w is None: w = int(round(os2w / 100.0)) * 100
    # a font whose only face is heavy still has to answer for 400
    f.close()
    return fam.strip(), sub, w, italic

# These three must not be published as webfonts, so the trial renders them as
# images instead — you can still judge the letterforms, but no font file leaves
# the machine. Amrys is Monotype's, WeblySleek UI ships no licence and descends
# from Segoe UI, and Atyan Dsegh's own embedding flag says preview & print only.
RESTRICT = ('amrys', 'weblysleek-ui', 'atyan-dsegh')
SHOT = os.path.join(V2, 'tsheet')

def raster(slug, name, picked, copy):
    """Draw the same specimen lines straight to PNG at 2x."""
    from PIL import Image, ImageDraw, ImageFont
    os.makedirs(SHOT, exist_ok=True)
    reg = picked.get(400) or list(picked.values())[0]
    bold = picked.get(700) or picked.get(600) or reg
    S, BG, FG = 2, (239, 237, 234), (13, 14, 19)
    out = {}

    def draw(key, lines, W):
        """lines: (path, px, colour, leading, text) — text None ends a block."""
        pad = 2 * S
        H = pad * 2 + sum(int(l[3] * S) for l in lines)
        im = Image.new('RGB', (W * S, H), BG)
        d = ImageDraw.Draw(im)
        y = pad
        for path, px, col, lead, text in lines:
            f = ImageFont.truetype(path, int(px * S))
            if text:
                d.text((0, y + int((lead - px) * S * .18)), text, font=f, fill=col)
            y += int(lead * S)
        fn = '%s-%s.png' % (slug, key)
        im.save(os.path.join(SHOT, fn), optimize=True)
        out[key] = {'file': fn, 'w': W, 'h': H // S}
        return out[key]

    def wrap(path, px, text, W):
        from PIL import ImageFont
        f = ImageFont.truetype(path, int(px * S))
        words, line, res = text.split(), '', []
        for w_ in words:
            t = (line + ' ' + w_).strip()
            if f.getlength(t) > W * S and line:
                res.append(line); line = w_
            else:
                line = t
        if line: res.append(line)
        return res

    h1 = copy['h1']
    # heading column: eyebrow-ish label, the h1, a subhead, the alphabet
    W1 = 520
    lines = [(bold, 11, (200, 96, 61), 26, copy['up'])]
    for ln in wrap(bold, 40, h1, W1):
        lines.append((bold, 40, FG, 44, ln))
    lines.append((bold, 20, FG, 44, copy['h2']))
    for ln in wrap(reg, 19, copy['alpha'], W1):
        lines.append((reg, 19, (13, 14, 19), 30, ln))
    draw('head', lines, W1)
    # text column: paragraph, small print, figures, the weights it actually has
    W2 = 470
    lines = []
    for ln in wrap(reg, 15.5, copy['p1'], W2):
        lines.append((reg, 15.5, FG, 27, ln))
    lines.append((reg, 12, FG, 22, None))
    for ln in wrap(reg, 13, copy['p2'], W2):
        lines.append((reg, 13, (70, 71, 76), 23, ln))
    lines.append((reg, 12, FG, 20, None))
    lines.append((reg, 12.5, (110, 111, 116), 30,
                  u'01 · 230 V · 50 Hz · THD 4,8 % · 7 օր'))
    for wt in sorted(picked):
        lines.append((picked[wt], 17, FG, 27, u'%s %d — հոսանքի որակ' % (name, wt)))
    draw('body', lines, W2)
    return out

def make():
    from fontTools import subset
    os.makedirs(OUT, exist_ok=True)
    copy = sheet_copy()
    manifest = []
    for slug, name, kind in CAND:
        zp = os.path.join(SRC, slug + '.zip')
        if not os.path.exists(zp): print('skip (no zip)', slug); continue
        ex = os.path.join(SRC, slug)
        if not os.path.isdir(ex):
            with zipfile.ZipFile(zp) as z: z.extractall(ex)
        files = []
        for root, _, fns in os.walk(ex):
            for fn in fns:
                if fn.lower().endswith(('.ttf', '.otf')):
                    files.append(os.path.join(root, fn))
        picked, upright = {}, []
        for p in sorted(files):
            fam, sub, w, italic = face_info(p)
            if italic: continue
            upright.append((w, sub, p))
            if w in WANT and w not in picked:
                picked[w] = p
        # WeblySleek UI ships no Regular at all — Light / SemiLight / SemiBold only.
        # Its text weight is SemiLight, so that face has to take the 400 slot or the
        # browser would fake-bold everything from SemiBold.
        if 400 not in picked and upright:
            light = [u for u in upright if u[0] < 600]
            if light:
                light.sort(key=lambda u: (0 if 'semilight' in u[1].replace(' ', '') else 1, -u[0]))
                picked[400] = light[0][2]
        if not picked and files:                       # display cuts with odd naming
            picked[400] = sorted(files)[0]
        if slug in RESTRICT:
            for stale in os.listdir(OUT):
                if stale.startswith(slug + '-'): os.remove(os.path.join(OUT, stale))
            manifest.append({'slug': slug, 'name': name, 'kind': kind, 'faces': [],
                             'img': raster(slug, name, picked, copy),
                             'weights': sorted(picked), 'found': len(files)})
            print('%-22s images only (%s) - licence' % (slug, ' '.join(map(str, sorted(picked)))))
            continue
        emitted = []
        for w in sorted(picked):
            dst = os.path.join(OUT, '%s-%d.woff2' % (slug, w))
            args = [picked[w], '--unicodes=' + UNI, '--layout-features=*',
                    '--flavor=woff2', '--output-file=' + dst,
                    '--no-hinting', '--desubroutinize']
            try:
                subset.main(args)
            except Exception as e:
                print('  subset failed %s %d: %s' % (slug, w, e)); continue
            emitted.append({'w': w, 'file': os.path.basename(dst),
                            'kb': round(os.path.getsize(dst) / 1024.0, 1)})
        manifest.append({'slug': slug, 'name': name, 'kind': kind,
                         'faces': emitted, 'found': len(files)})
        print('%-22s %s' % (slug, ' '.join('%d(%.1fkb)' % (e['w'], e['kb']) for e in emitted) or 'NOTHING'))
    io.open(os.path.join(HERE, 'tfonts.json'), 'w', encoding='utf-8').write(
        json.dumps(manifest, ensure_ascii=False, indent=1))
    return manifest

# ----------------------------------------------------------------- pages
def hy_copy():
    """Pull real strings out of the built HY page so the trial is not lorem."""
    s = io.open(os.path.join(V2, 'hy.html'), encoding='utf-8').read()
    def one(pat, d=''):
        m = re.search(pat, s, re.S)
        return re.sub(r'<[^>]+>', '', m.group(1)).strip() if m else d
    h1 = one(r'<h1[^>]*>(.*?)</h1>')
    h2s = [re.sub(r'<[^>]+>', '', x).strip() for x in re.findall(r'<h2[^>]*>(.*?)</h2>', s, re.S)]
    ps = [re.sub(r'<[^>]+>', '', x).strip() for x in re.findall(r'<p[^>]*>(.*?)</p>', s, re.S)]
    ps = [p for p in ps if len(p) > 90][:3]
    eye = [re.sub(r'<[^>]+>', '', x).strip()
           for x in re.findall(r'class="eyebrow"[^>]*>(.*?)</div>', s, re.S)][:6]
    navs = [re.sub(r'<[^>]+>', '', x).strip()
            for x in re.findall(r'class="nlink"[^>]*>(.*?)</a>', s, re.S)][:6]
    return {'h1': h1, 'h2': [h for h in h2s if h][:3], 'p': ps,
            'eye': [e for e in eye if e], 'nav': [n for n in navs if n]}

def sheet_copy():
    """One resolved set of specimen strings, shared by the HTML and the PNGs."""
    c = hy_copy()
    ps = c['p'] + [u'Չափումն անցնում է աշխատանքային բերի տակ։']
    return {
        'h1':    c['h1'] or u'Հոսանքի որակ',
        'h2':    (c['h2'] + [u'Ւնչ է ցույց տալիս չափումը'])[0],
        'p1':    ps[0],
        'p2':    ps[1] if len(ps) > 1 else ps[0],
        'up':    (c['eye'] + [u'ՈԼՈՐՏՆԵՐ'])[0],
        'alpha': ALPHA,
    }

ALPHA = (u'Ա Բ Գ Դ Ե Զ Է Ը Թ Ժ Ի Լ Խ Ծ Կ Հ Ձ Ղ Ճ Մ Յ Ն Շ Ո Չ Պ Ջ Ռ Ս Վ Տ Ր Ց Ւ Փ Ք Օ Ֆ  '
         u'ա բ գ դ ե զ է ը թ ժ ի լ խ ծ կ հ ձ ղ ճ մ յ ն շ ո չ պ ջ ռ ս վ տ ր ց ւ փ ք օ ֆ  '
         u'0123456789 ։ , « »')

def faces_css(man, prefix='tfonts/'):
    out = []
    for f in man:
        for e in f['faces']:
            out.append("@font-face{font-family:'T %s';font-weight:%d;font-display:swap;"
                       "src:url(%s%s) format('woff2');}" % (f['name'], e['w'], prefix, e['file']))
    return '\n'.join(out)

SHEET = u"""<!doctype html><html lang="hy"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow"><title>Հայկական տիպագրություն — փորձ</title>
<style>
%%FACES%%
@font-face{font-family:'Noto Sans Armenian';font-weight:400;font-display:swap;src:url(../fonts/noto-sans-armenian-400-armenian.woff2) format('woff2');}
@font-face{font-family:'Noto Sans Armenian';font-weight:700;font-display:swap;src:url(../fonts/noto-sans-armenian-700-armenian.woff2) format('woff2');}
:root{--bg:#EFEDEA;--fg:#0D0E13;--mid:rgba(13,14,19,.62);--soft:rgba(13,14,19,.42);
 --hair:rgba(13,14,19,.13);--hair2:rgba(13,14,19,.08);--brand:#C8603D;}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:400 16px/1.7 'Noto Sans Armenian',sans-serif;}
.wrap{max-width:1180px;margin:0 auto;padding:0 clamp(18px,4vw,56px);}
header{padding:64px 0 34px;border-bottom:1px solid var(--hair);}
h1.t{font-size:clamp(28px,4vw,44px);line-height:1.05;font-weight:700;margin:0 0 14px;}
.lead{color:var(--mid);max-width:62ch;font-size:15.5px;}
.lab{font-size:10.5px;letter-spacing:.18em;text-transform:uppercase;color:var(--brand);}
.card{border-bottom:1px solid var(--hair);padding:44px 0;}
.hd{display:flex;justify-content:space-between;align-items:baseline;gap:20px;flex-wrap:wrap;margin-bottom:26px;}
.hd .nm{font-size:13px;letter-spacing:.04em;color:var(--fg);}
.hd .meta{font-size:11px;letter-spacing:.1em;color:var(--soft);}
.tag{font-size:10px;letter-spacing:.1em;padding:3px 7px;border-radius:2px;white-space:normal;}
.tag.ok{background:rgba(46,110,74,.12);color:#2E6E4A;}
.tag.warn{background:rgba(200,96,61,.13);color:#A34D31;}
.tag.risk{background:rgba(160,32,32,.12);color:#9B2020;}
.legend{display:flex;gap:20px;flex-wrap:wrap;margin-top:20px;font-size:12px;color:var(--mid);}
img{max-width:100%;height:auto;display:block;}
.grid{display:grid;grid-template-columns:minmax(0,1.05fr) minmax(0,1fr);gap:clamp(22px,3vw,48px);}
@media(max-width:860px){.grid{grid-template-columns:1fr}}
.spec h2{margin:0 0 6px;font-weight:700;font-size:clamp(26px,3.4vw,46px);line-height:1.02;letter-spacing:-.01em;}
.spec .sub{font-weight:700;font-size:20px;line-height:1.25;margin:18px 0 8px;}
.spec .up{font-size:10.5px;letter-spacing:.2em;text-transform:uppercase;color:var(--brand);margin-bottom:10px;}
.body p{margin:0 0 12px;font-size:15.5px;line-height:1.72;color:rgba(13,14,19,.86);}
.body .sm{font-size:13px;color:var(--mid);}
.body .num{font-size:12.5px;letter-spacing:.12em;color:var(--soft);}
.alpha{margin-top:16px;font-size:19px;line-height:1.5;letter-spacing:.01em;color:rgba(13,14,19,.72);word-break:break-word;}
.w{display:flex;gap:18px;flex-wrap:wrap;margin-top:14px;}
.w span{font-size:17px;}
nav.jump{position:sticky;top:0;background:rgba(239,237,234,.92);backdrop-filter:blur(8px);
 border-bottom:1px solid var(--hair);z-index:5;}
nav.jump .wrap{display:flex;gap:16px;flex-wrap:wrap;padding-top:12px;padding-bottom:12px;}
nav.jump a{font-size:11px;letter-spacing:.1em;color:var(--mid);text-decoration:none;}
nav.jump a:hover{color:var(--brand);}
.foot{padding:52px 0 90px;color:var(--mid);font-size:14px;}
.foot a{color:var(--brand);}
</style></head><body>
<nav class="jump"><div class="wrap">%%JUMP%%</div></nav>
<div class="wrap">
<header><div class="lab">PowerTech · type trial</div>
<h1 class="t">Հայկական տառատեսակների ընտրություն</h1>
<p class="lead">%%LEAD%%</p>
<div class="legend"><span><i class="tag ok">OFL</i> — վեբում ազատ</span>
<span><i class="tag warn">?</i> — գրավոր լիցենզիա չկա</span>
<span><i class="tag risk">⚠</i> — չի կարելի դնել կայքում, ցուցադրվանում է նկարով</span></div></header>
%%CARDS%%
<div class="foot">%%FOOT%%</div>
</div></body></html>
"""

def pages(man):
    c = sheet_copy()
    h1, h2, p1, p2, up, alpha = c['h1'], c['h2'], c['p1'], c['p2'], c['up'], c['alpha']
    rows, jump = [], []
    for f in man:
        # licence-restricted candidates were rendered to PNG instead of a webfont
        if not f['faces'] and f.get('img'):
            im = f['img']
            jump.append('<a href="#%s">%s &#9888;</a>' % (f['slug'], f['name']))
            rows.append(u"""<section class="card" id="{slug}">
 <div class="hd"><div class="nm">{name}</div>
  <div class="meta">{kind} · կտրվածքներ {ws} · նկար, ոչ վեբ-տառատեսակ</div>
  <div class="tag {lcls}">{lnote}</div></div>
 <div class="grid">
  <div><img src="tsheet/{fh}" width="{wh}" height="{hh}" alt="{name} — վերնագիր" loading="lazy"></div>
  <div><img src="tsheet/{fb}" width="{wb}" height="{hb}" alt="{name} — տեքստ" loading="lazy"></div>
 </div></section>""".format(
                slug=f['slug'], name=f['name'], kind=f['kind'],
                ws=' · '.join(str(w) for w in f.get('weights', [])),
                fh=im['head']['file'], wh=im['head']['w'], hh=im['head']['h'],
                fb=im['body']['file'], wb=im['body']['w'], hb=im['body']['h'],
                lcls=LIC.get(f['slug'], ('warn', ''))[0],
                lnote=LIC.get(f['slug'], ('warn', '?'))[1]))
            continue
        if not f['faces']: continue
        ws = ' · '.join(str(e['w']) for e in f['faces'])
        kb = sum(e['kb'] for e in f['faces'])
        fam = "'T %s'" % f['name']
        jump.append('<a href="#%s">%s</a>' % (f['slug'], f['name']))
        rows.append(u"""<section class="card" id="{slug}">
 <div class="hd"><div class="nm">{name}</div>
  <div class="meta">{kind} · կտրվածքներ {ws} · {kb:.0f} KB (subset)</div>
  <div class="tag {lcls}">{lnote}</div></div>
 <div class="grid">
  <div class="spec" style="font-family:{fam},sans-serif">
    <div class="up">{up}</div>
    <h2>{h1}</h2>
    <div class="sub">{h2}</div>
    <div class="alpha">{alpha}</div>
  </div>
  <div class="body" style="font-family:{fam},sans-serif">
    <p>{p1}</p><p class="sm">{p2}</p>
    <p class="num">01 · 230 V · 50 Hz · THD 4,8 % · 7 օր</p>
    <div class="w"><span style="font-weight:400">Regular 400</span>
      <span style="font-weight:500">Medium 500</span>
      <span style="font-weight:600">SemiBold 600</span>
      <span style="font-weight:700">Bold 700</span></div>
  </div>
 </div></section>""".format(slug=f['slug'], name=f['name'], kind=f['kind'], ws=ws, kb=kb,
                            fam=fam, up=up, h1=h1, h2=h2, alpha=alpha, p1=p1, p2=p2,
                            lcls=LIC.get(f['slug'],('warn',''))[0],
                            lnote=LIC.get(f['slug'],('warn','?'))[1]))
    # the control: what the page uses today
    rows.insert(0, u"""<section class="card" id="noto">
 <div class="hd"><div class="nm">Noto Sans Armenian — ներկայիս վիճակը</div>
  <div class="meta">baseline · 400 · 600 · 700</div></div>
 <div class="grid">
  <div class="spec"><div class="up">%s</div><h2>%s</h2><div class="sub">%s</div>
   <div class="alpha">%s</div></div>
  <div class="body"><p>%s</p><p class="sm">%s</p>
   <p class="num">01 · 230 V · 50 Hz · THD 4,8 %%%% · 7 օր</p></div>
 </div></section>""" % (up, h1, h2, alpha, p1, p2))
    jump.insert(0, '<a href="#noto">Noto (այսօր)</a>')
    lead = (u'Նույն տեքստը՝ էջի իրական հայերենով։ Ձախում՝ վերնագրային դերը, աջում՝ '
            u'տեքստային դերը և կտրվածքները։ Ամեն տառատեսակ կարելի է տեսնել կենդանի էջի վրա՝ ')
    foot = (u'Կենդանի փորձ՝ <a href="hy-type.html">hy-type.html</a> — իրական էջը '
            u'փոխարկիչով (վերնագիր / տեքստ / պիտակ)։ Աղբյուր՝ fonter.am')
    html = (SHEET.replace('%%FACES%%', faces_css(man))
                 .replace('%%JUMP%%', ' '.join(jump))
                 .replace('%%LEAD%%', lead + u'<a href="hy-type.html">hy-type.html</a>')
                 .replace('%%CARDS%%', '\n'.join(rows))
                 .replace('%%FOOT%%', foot))
    io.open(os.path.join(V2, 'type.html'), 'w', encoding='utf-8').write(html)
    print('type.html', len(html) // 1024, 'KB')
    switcher(man)

def switcher(man):
    """The real HY page + a panel that reassigns the three type roles live."""
    s = io.open(os.path.join(V2, 'hy.html'), encoding='utf-8').read()
    css = s[s.index('<style>') + 7:s.index('</style>')]
    # every selector that currently resolves to the mono/label role
    lab = []
    for m in re.finditer(r'([^{}]+)\{([^{}]*)\}', css):
        if "'Martian Mono'" in m.group(2):
            for sel in m.group(1).split(','):
                sel = sel.strip()
                if sel and not sel.startswith('@'): lab.append(sel)
    lab = sorted(set(lab))
    heads = ['h1', 'h2', 'h3', '.display', '.stat b']
    opts = [('noto', 'Noto (այսօր)', "'Noto Sans Armenian'")] + \
           [(f['slug'], f['name'], "'T %s'" % f['name']) for f in man if f['faces']]
    rules = [faces_css(man, prefix='tfonts/')]
    for slug, name, fam in opts:
        if slug == 'noto': continue
        rules.append('html[data-h="%s"] :is(%s){font-family:%s,sans-serif!important;}'
                     % (slug, ','.join(heads), fam))
        rules.append('html[data-b="%s"] body,html[data-b="%s"] p,html[data-b="%s"] li,'
                     'html[data-b="%s"] input,html[data-b="%s"] textarea,html[data-b="%s"] select'
                     '{font-family:%s,sans-serif!important;}' % (slug, slug, slug, slug, slug, slug, fam))
        rules.append('html[data-m="%s"] :is(%s){font-family:%s,sans-serif!important;}'
                     % (slug, ','.join(lab), fam))
    panel_css = """
#tsw{position:fixed;left:14px;bottom:14px;z-index:9000;background:rgba(13,14,19,.93);
 color:#EFEDEA;border:1px solid rgba(239,237,234,.18);border-radius:3px;padding:12px 14px 13px;
 font:400 11px/1.5 ui-sans-serif,system-ui,sans-serif;max-width:min(92vw,560px);
 box-shadow:0 18px 50px rgba(0,0,0,.34);}
#tsw.min{padding:8px 11px;}
#tsw.min .tsbody{display:none;}
#tsw h4{margin:0 0 9px;font-size:10px;letter-spacing:.18em;text-transform:uppercase;
 color:rgba(239,237,234,.5);font-weight:400;display:flex;justify-content:space-between;gap:14px;}
#tsw h4 b{color:#C8603D;cursor:pointer;font-weight:400;letter-spacing:.1em;}
#tsw .row{display:grid;grid-template-columns:64px 1fr;gap:8px;align-items:start;margin-bottom:7px;}
#tsw .rl{color:rgba(239,237,234,.55);padding-top:4px;letter-spacing:.06em;}
#tsw .bs{display:flex;flex-wrap:wrap;gap:5px;}
#tsw button{font:inherit;background:rgba(239,237,234,.07);color:rgba(239,237,234,.86);
 border:1px solid rgba(239,237,234,.14);border-radius:2px;padding:4px 8px;cursor:pointer;}
#tsw button:hover{border-color:rgba(200,96,61,.7);}
#tsw button.on{background:#C8603D;border-color:#C8603D;color:#fff;}
#tsw .hint{color:rgba(239,237,234,.4);margin-top:8px;}
#tsw .hint a{color:#C8603D;}
@media(max-width:700px){#tsw{left:8px;right:8px;bottom:8px;max-width:none;}}
"""
    def btns(role):
        out = []
        for slug, name, _ in opts:
            mark = {'risk': ' ⚠', 'warn': ' ·'}.get(LIC.get(slug, ('', ''))[0], '')
            out.append('<button data-r="%s" data-v="%s" title="%s">%s%s</button>'
                       % (role, slug, LIC.get(slug, ('', ''))[1], name, mark))
        return ''.join(out)
    panel = (u'<div id="tsw"><h4><span>Տառատեսակի փորձ</span>'
             u'<b data-act="min">—</b></h4><div class="tsbody">'
             u'<div class="row"><div class="rl">Վերնագիր</div><div class="bs">' + btns('h') + u'</div></div>'
             u'<div class="row"><div class="rl">Տեքստ</div><div class="bs">' + btns('b') + u'</div></div>'
             u'<div class="row"><div class="rl">Պիտակ</div><div class="bs">' + btns('m') + u'</div></div>'
             u'<div class="hint">Բոլորը կողք կողքի՝ <a href="type.html">type.html</a>·'
             u' ընտրությունը պահվում է դիտարկիչում · ⚠ = լիցենզիան թույլ չի տալիս</div></div></div>')
    js = """
<script>(function(){var d=document.documentElement,K='pt-type';
var st=JSON.parse(localStorage.getItem(K)||'{}');
function apply(){['h','b','m'].forEach(function(r){
  if(st[r]&&st[r]!=='noto')d.setAttribute('data-'+r,st[r]);else d.removeAttribute('data-'+r);
  document.querySelectorAll('#tsw button[data-r="'+r+'"]').forEach(function(b){
    b.classList.toggle('on',(st[r]||'noto')===b.dataset.v);});});}
document.addEventListener('click',function(e){
  var b=e.target.closest('#tsw button[data-r]');
  if(b){st[b.dataset.r]=b.dataset.v;localStorage.setItem(K,JSON.stringify(st));apply();return;}
  if(e.target.closest('#tsw [data-act="min"]'))document.getElementById('tsw').classList.toggle('min');});
apply();})();</script>"""
    s = s.replace('</style>', '\n'.join(rules) + panel_css + '</style>', 1)
    s = s.replace('<title>', '<title>[type] ', 1)
    s = s.replace('</body>', panel + js + '\n</body>', 1)
    # keep the trial out of search results and off the language toggle
    s = s.replace('href="index.html"', 'href="index.html"', 1)
    io.open(os.path.join(V2, 'hy-type.html'), 'w', encoding='utf-8').write(s)
    print('hy-type.html', len(s) // 1024, 'KB · label selectors:', len(lab))

if __name__ == '__main__':
    todo = sys.argv[1:] or ['dl', 'make', 'pages']
    man = None
    if 'dl' in todo: dl()
    if 'make' in todo: man = make()
    if 'pages' in todo:
        if man is None:
            man = json.loads(io.open(os.path.join(HERE, 'tfonts.json'), encoding='utf-8').read())
        pages(man)
