# Ставит новый знак с именем в шапку палитровых сборок — превью, не часть сборки.
#
# Берёт готовые pt-en-warm.html / pt-en-mint.html и меняет в них только лого:
# исходный коралловый квадрат с волной уходит, на его место встаёт изокуб со швом
# акцентного цвета плюс имя в Archivo Expanded 700.
#
# Акцент берётся из самой палитры: на бумажном тоне шапки — светлая глубина
# (light), на графитовом — плашечная (dark). Те же два значения, что объявляет
# PAL_CSS, поэтому превью не изобретает свой цвет.
#
#   python logo_on_palettes.py
#
# Пишет pt-<палитра>-<имя>.html рядом. Прозаические упоминания PowerTech в тексте
# не трогает: имя ещё не выбрано, и переписывать копирайт рано.
import io
import os
import re

import hero_window

HERE = os.path.dirname(os.path.abspath(__file__))

# --- палитровую механику берём из build.py, чтобы превью не разъехалось со сборкой.
# Исполняем только блок от PALETTES до palette_pass: запускать build.py целиком нельзя,
# он на уровне модуля пишет деплойную пару в репозиторий сайта.
src = io.open(os.path.join(HERE, 'build.py'), encoding='utf-8').read()
block = re.search(r'^PALETTES = \{.*?^(?=mintify = )', src, re.S | re.M).group(0)
ns = {}
exec(block, ns)
PALETTES = ns['PALETTES']
palette_pass = ns['palette_pass']

# У тёплой и мятной готовые сборки уже лежат; синюю получаем тем же пост-проходом
# из терракотовой. palette_pass сам падает, если хоть один терракотовый литерал выжил.
BASES = {'warm': 'pt-en-warm.html', 'mint': 'pt-en-mint.html', 'blue': None}

NAME = 'Gridec'

# Начертание имени, ?wm= . В присланном образце имя набрано округлым геометрическим
# шрифтом со срезанными терминалами — из растра его не опознать, поэтому geo это
# приближение, а не тот самый файл.
# mk — высота куба, gap — просвет до имени. Пропорция куба к прописной держится
# около 1,5, как в присланных локапах; узким прописным нужен и куб крупнее, и
# просвет шире, иначе разрядка съедает воздух между знаком и именем.
WORDMARKS = [
    ('cond', dict(mk='28px', gap='12px',
                  css="font-family:'Archivo','Helvetica Neue',sans-serif;"
                      "font-variation-settings:'wdth' 62;font-weight:700;"
                      "font-size:25px;letter-spacing:.13em;text-transform:uppercase;")),
    # у Big Shoulders прописная — 0,82 от кегля, вдвое выше обычного, поэтому кегль
    # ниже остальных: иначе куб рядом с ней выглядит приставленным
    ('bigsh', dict(mk='33px', gap='13px',
                   css="font-family:'Big Shoulders Display',sans-serif;"
                       "font-variation-settings:normal;font-weight:700;"
                       "font-size:27px;letter-spacing:.17em;text-transform:uppercase;")),
    ('plex', dict(mk='27px', gap='12px',
                  css="font-family:'IBM Plex Sans Condensed',sans-serif;"
                      "font-variation-settings:normal;font-weight:600;"
                      "font-size:24px;letter-spacing:.08em;text-transform:uppercase;")),
    ('geo', dict(mk='26px', gap='10px',
                 css="font-family:'Outfit','Helvetica Neue',sans-serif;"
                     "font-variation-settings:normal;font-weight:500;"
                     "font-size:24px;letter-spacing:.004em;text-transform:none;")),
    ('expand', dict(mk='24px', gap='11px',
                    css="font-family:'Archivo','Helvetica Neue',sans-serif;"
                        "font-variation-settings:'wdth' 125;font-weight:700;"
                        "font-size:21px;letter-spacing:.05em;text-transform:uppercase;")),

    # --- пять новых, каждое в своём регистре ---------------------------------
    # вывесочный узкий гротеск — ближайшее общедоступное к присланной картинке
    ('oswald', dict(mk='27px', gap='12px',
                    css="font-family:'Oswald',sans-serif;"
                        "font-variation-settings:normal;font-weight:600;"
                        "font-size:24px;letter-spacing:.10em;text-transform:uppercase;")),
    # промышленный шильдик: только прописные по рисунку, максимально плотно
    ('bebas', dict(mk='29px', gap='12px',
                   css="font-family:'Bebas Neue',sans-serif;"
                       "font-variation-settings:normal;font-weight:400;"
                       "font-size:27px;letter-spacing:.13em;text-transform:uppercase;")),
    # квадратный технический — регистр приборной панели
    ('square', dict(mk='26px', gap='12px',
                    css="font-family:'Chakra Petch',sans-serif;"
                        "font-variation-settings:normal;font-weight:600;"
                        "font-size:24px;letter-spacing:.07em;text-transform:uppercase;")),
    # моноширинный: шрифт цифр самого сайта, регистр показания прибора
    ('mono', dict(mk='23px', gap='12px',
                  css="font-family:'Martian Mono',monospace;"
                      "font-variation-settings:normal;font-weight:600;"
                      "font-size:18px;letter-spacing:-.01em;text-transform:uppercase;")),
    # брусковый: единственный не-гротеск, регистр норматива и документа
    ('slab', dict(mk='24px', gap='12px',
                  css="font-family:'Zilla Slab',serif;"
                      "font-variation-settings:normal;font-weight:600;"
                      "font-size:24px;letter-spacing:.05em;text-transform:uppercase;")),
    # имя в кривых: тот же Outfit 500, но шрифт не участвует — логотип не мигает
    # на загрузке и не поедет от версии шрифта. Собирается logo_vector.py.
    ('vector', dict(mk='26px', gap='0px', css='')),
]
WM_KEYS = [k for k, _ in WORDMARKS]

LOCKUP = os.path.join(HERE, 'gridec-lockup.frag')
LOCK = io.open(LOCKUP, encoding='utf-8').read() if os.path.exists(LOCKUP) else ''

# Выбор заказчика 2026-08-03: синяя палитра, знак с акцентной гранью, имя округлым
# геометрическим. Эти три значения и есть состояние страницы по умолчанию.
PICK_WM = 'vector'   # WORD 10 — кривые, тот же рисунок что geo, но без шрифта
PICK_LOGO = '3'      # LOGO 3 face
PICK_BAR = '3'       # BAR 3 chips

# Изокуб: три грани по 120°. В знаке три состояния, переключаются ?mark=
#
#   solid  зазор 12 единиц, зазор = фон. Основное состояние для бара: в шапке
#          знак живёт на 34 px, где 12 единиц дают 2 px молочного просвета —
#          светлое против графита читается, цветной шов на этом размере нет.
#   face   одна грань акцентом. Единственный способ удержать цвет в баре:
#          площадь большая, и контраст считается с фоном (4,79:1 тёплый,
#          6,68:1 мятный), а не с соседней гранью.
#   seam   шов акцентом, 18 единиц. Приём крупного размера — оставлен для
#          сравнения, чтобы было видно, почему он в шапке не работает.
# Грани при зазоре 12 единиц (d=6) и при 18 (d=9)
WALL_L6 = 'M-86.603 -50 L-6 -96.536 L-6 -3.464 L-86.603 43.072 Z'
WALL_R6 = 'M86.603 -50 L6 -96.536 L6 -3.464 L86.603 43.072 Z'
DIAMOND6 = 'M-86.603 56.928 L0 6.928 L86.603 56.928 L0 100 Z'
HEX = 'M0 -100 L86.603 -50 L86.603 50 L0 100 L-86.603 50 L-86.603 -50 Z'

def faces(extra_r='', extra_d=''):
    return ('<path d="%s"/><path%s d="%s"/><path%s d="%s"/>'
            % (WALL_L6, extra_r, WALL_R6, extra_d, DIAMOND6))

# Шесть состояний знака, строка LOGO переключателя ставит html[data-logo].
#
# 0 solid    как в присланном знаке: ромб внизу, зазор = фон
# 1 flip     то же, повёрнуто на 180° — ромб сверху. Присланный знак читается как
#            куб, увиденный СНИЗУ, а глаз ждёт вид сверху; отсюда, вероятно,
#            «непонятно какая фигура»
# 2 shade    flip плюс одна стена в 55% тона — светотень, то есть то, как куб
#            рисуют вообще всегда. Всё ещё один цвет, только его тон
# 3 face      одна грань акцентом: цвет на площади, контраст с фоном
# 4 seam      акцент в шве: приём крупного размера, в баре не работает
# 5 contour   ромб контуром — объём вместо плоского шестиугольника
MARK = (
    '<svg class="mk" viewBox="-86.603 -100 173.205 200" aria-hidden="true">'
    '<g class="m0">' + faces() + '</g>'
    '<g class="m1" transform="scale(1,-1)">' + faces() + '</g>'
    '<g class="m2" transform="scale(1,-1)">'
    + faces(extra_r=' opacity=".55"') + '</g>'
    '<g class="m3">' + faces(extra_r=' class="acc"') + '</g>'
    '<g class="m4">'
    '<path class="seam" d="' + HEX + '"/>'
    '<path d="M-86.603 -50 L-9 -94.804 L-9 -5.196 L-86.603 39.608 Z"/>'
    '<path d="M86.603 -50 L9 -94.804 L9 -5.196 L86.603 39.608 Z"/>'
    '<path d="M-86.603 60.392 L0 10.392 L86.603 60.392 L0 100 Z"/>'
    '</g>'
    '<g class="m5">'
    + faces(extra_d=' fill="none" stroke="currentColor" stroke-width="9"') + '</g>'
    '</svg>'
)

LOGO_LABELS = "var LOGOV=['0','1','2','3','4','5']," \
              "logoLabels=['solid','flip','shade','face','seam','contour'];"

# Инлайновая Archivo в сборке — статические 400 и 600: ни 700, ни оси ширины в ней
# нет, поэтому вариативную тянем из Google. Семейство то же, начертание совпадает,
# на текст страницы это не влияет.
FONT_LINK = (
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@62..125,400..700'
    '&family=Outfit:wght@400..700&family=IBM+Plex+Sans+Condensed:wght@600'
    '&family=Big+Shoulders+Display:wght@700'
    '&family=Oswald:wght@600&family=Bebas+Neue&family=Chakra+Petch:wght@600'
    '&family=Zilla+Slab:wght@600&display=swap" rel="stylesheet">'
)
# Martian Mono в сборку уже вшита base64, её тянуть не нужно

# Строка WORD переключателя. wmSet объявлен глобально ещё в голове документа,
# поэтому обработчик чипа, который собирается ниже по странице, его уже видит.
WM_JS = """<script>
var WMV=%(keys)s;
function wmSet(v){
  document.documentElement.setAttribute('data-wm',v);
  var b=document.querySelectorAll('#navsw button[data-w]');
  for(var i=0;i<b.length;i++)b[i].classList.toggle('on',b[i].dataset.w===v);
}
(function(){
  var m=(location.search.match(/[?&]wm=(%(alt)s)/)||[])[1]||'%(first)s';
  wmSet(m);
  /* написание имени: в присланных логотипах Gridec, в переписке возникло Gritec */
  var n=(location.search.match(/[?&]name=(gridec|gritec)/)||[])[1];
  document.addEventListener('DOMContentLoaded',function(){
    wmSet(document.documentElement.getAttribute('data-wm'));
    if(n){var w=document.querySelector('#hdr .brand .wm');
      if(w)w.textContent=n.charAt(0).toUpperCase()+n.slice(1);}});
})();
</script>"""

CSS = """
/* ==================== превью логотипа (%(pal)s / %(name)s) ====================
   Знак наследует цвет шапки, шов держит акцент палитры на своей глубине. */
/* в строке WORD теперь десять кнопок — чипу нужен перенос, иначе он уезжает за край */
#navsw .row{flex-wrap:wrap;max-width:min(92vw,900px);}
#hdr .brand{gap:var(--gap,12px);}
/* Высота куба и просвет едут вместе со шрифтом имени: у прописных в разрядку своя
   оптика, одна пара значений на все начертания не работает. */
#hdr .brand .mk{height:var(--mkh,28px);width:auto;aspect-ratio:173.205/200;
  display:block;flex:0 0 auto;fill:currentColor;}
/* строка LOGO переключателя ставит html[data-logo] — на нём и держим состояния;
   старые правила data-logo целились в .mark и .glyph, которых больше нет */
#hdr .brand .mk g{display:none;}
#hdr .brand .mk .m0{display:block;}
html[data-logo="1"] #hdr .brand .mk .m0,
html[data-logo="2"] #hdr .brand .mk .m0,
html[data-logo="3"] #hdr .brand .mk .m0,
html[data-logo="4"] #hdr .brand .mk .m0,
html[data-logo="5"] #hdr .brand .mk .m0{display:none;}
html[data-logo="1"] #hdr .brand .mk .m1,
html[data-logo="2"] #hdr .brand .mk .m2,
html[data-logo="3"] #hdr .brand .mk .m3,
html[data-logo="4"] #hdr .brand .mk .m4,
html[data-logo="5"] #hdr .brand .mk .m5{display:block;}
/* .on-dark — тот же класс, которым страница перекрашивает сам логотип в молочный,
   поэтому грани и акцент переключаются одновременно, а не по разным условиям. */
#hdr .brand .mk .seam,#hdr .brand .mk .acc{fill:%(light)s;}
#hdr.on-dark .brand .mk .seam,#hdr.on-dark .brand .mk .acc{fill:%(dark)s;}
#hdr .brand .wm{line-height:1;}
#hdr .brand .wm i{color:inherit;}
/* локап в кривых: одна фигура вместо знака и текста, у него свой viewBox,
   поэтому ширина считается сама. --acc отдаёт акцент внутрь вектора. */
#hdr .brand{--acc:%(light)s;}
#hdr.on-dark .brand{--acc:%(dark)s;}
#hdr .brand .lock{display:none;height:26px;width:auto;flex:0 0 auto;fill:currentColor;}
html[data-wm="vector"] #hdr .brand .lock{display:block;}
html[data-wm="vector"] #hdr .brand .mk,
html[data-wm="vector"] #hdr .brand .wm{display:none;}
%(wm_rules)s"""

BRAND_RE = re.compile(r'<a class="brand" href="#top">.*?</a>', re.S)


def patch(html, pal):
    p = PALETTES[pal]

    brand = ('<a class="brand" href="#top" aria-label="%s">%s%s<span class="wm">%s</span></a>'
             % (NAME, LOCK, MARK, NAME))
    html, hit = BRAND_RE.subn(brand, html, count=1)
    if hit != 1:
        raise SystemExit('%s: шапка не найдена' % pal)

    wm_js = WM_JS % dict(keys=str(WM_KEYS).replace("'", "'"),
                         alt='|'.join(WM_KEYS), first=PICK_WM)
    i = html.index('<style')
    html = html[:i] + FONT_LINK + wm_js + html[i:]

    # третья строка переключателя: начертание имени
    row = ("html+='</div><div class=\"row\"><span>WORD</span>';"
           "for(var k=0;k<WMV.length;k++)"
           "html+='<button data-w=\"'+WMV[k]+'\">'+k+' '+WMV[k]+'</button>';"
           "sw.innerHTML=html+'</div>';")
    if html.count("sw.innerHTML=html+'</div>';") != 1:
        raise SystemExit('%s: сборка чипа не найдена' % pal)
    html = html.replace("sw.innerHTML=html+'</div>';", row, 1)

    handler = ("var l=e.target.closest('button[data-l]');if(l)logoSet(l.dataset.l);});")
    if html.count(handler) != 1:
        raise SystemExit('%s: обработчик чипа не найден' % pal)
    html = html.replace(handler,
                        "var l=e.target.closest('button[data-l]');"
                        "if(l){logoSet(l.dataset.l);return;}"
                        "var w=e.target.closest('button[data-w]');"
                        "if(w)wmSet(w.dataset.w);});", 1)

    # строка LOGO: старые ярлыки целились в удалённую плитку, переводим на новый знак
    old = re.search(r"var LOGOV=\[[^;]*;", html)
    if not old:
        raise SystemExit('%s: массив LOGOV не найден' % pal)
    html = html.replace(old.group(0), LOGO_LABELS, 1)
    # состояние по умолчанию — выбранное заказчиком, а не прежнее contour;
    # адресный параметр ?logo= должен доставать до шестого состояния
    html = html.replace("logoSet(lm?lm[1]:'1');",
                        "logoSet(lm?lm[1]:'%s');" % PICK_LOGO, 1)
    html = html.replace("/[?&]logo=([0-3])/", "/[?&]logo=([0-5])/", 1)
    # и вид шапки: было 0 glass, выбрано 3 chips
    if html.count("var v=m?m[1]:(stored||'0');") != 1:
        raise SystemExit('%s: инициализация BAR не найдена' % pal)
    html = html.replace("var v=m?m[1]:(stored||'0');",
                        "var v=m?m[1]:'%s';" % PICK_BAR, 1)

    wm_rules = '\n'.join(
        'html[data-wm="%s"] #hdr .brand{--mkh:%s;--gap:%s;}\n'
        'html[data-wm="%s"] #hdr .brand .wm{%s}' % (k, v['mk'], v['gap'], k, v['css'])
        for k, v in WORDMARKS)
    css = CSS % dict(pal=pal, name=NAME, light=p['light'], dark=p['dark'],
                     wm_rules=wm_rules)
    j = html.rindex('</style>')
    html = html[:j] + css + html[j:]

    # Переключатель языка: армянская подпись падала в системную подмену, потому что
    # в EN-сборку вшита только латинская подрезка Martian Mono. В build.py уже
    # исправлено, здесь — чтобы правка была видна в готовой сборке без пересборки.
    lang_old, lang_new = '>ՀԱՅ</a>', '>HY</a>'
    if html.count(lang_old) != 1:
        raise SystemExit('%s: подпись переключателя языка не найдена' % pal)
    html = html.replace(lang_old, lang_new, 1)

    html = hero_window.patch(html, p, ns['_rgb'])

    # имя решено, поэтому меняем его и в тексте. Адрес почты и домен не трогаем:
    # powertech.am ещё живой, а новый домен не выбран.
    html = html.replace('powertech.am', '\x00DOMAIN\x00')
    html = html.replace('PowerTech', NAME).replace('powertech', NAME.lower())
    html = html.replace('\x00DOMAIN\x00', 'powertech.am')
    return html


for pal in ('warm', 'mint', 'blue'):
    if BASES[pal]:
        base = io.open(os.path.join(HERE, BASES[pal]), encoding='utf-8').read()
    else:
        terra = io.open(os.path.join(HERE, 'pt-en.html'), encoding='utf-8').read()
        base = palette_pass(pal)(terra)
    out = 'pt-%s-gridec.html' % pal
    io.open(os.path.join(HERE, out), 'w', encoding='utf-8').write(patch(base, pal))
    print('%-24s %s акцент %s / %s' % (out, pal, PALETTES[pal]['light'],
                                       PALETTES[pal]['dark']))
