# -*- coding: utf-8 -*-
"""Почтовая подпись — три НОВЫХ построения.

Прежние три отличались способом раскладки: строка, столбик, без картинки. Эти
три отличаются ЗАМЫСЛОМ — тем, что подпись вообще говорит о человеке:

  строка    — минимум: имя, должность и как связаться. Без знака вовсе.
              Так подписываются европейские инженерные конторы: подпись не
              должна перекрикивать письмо;
  таблица   — набор с подписями полей слева, как в наших же таблицах
              параметров на сайте. Читается как строка приборного отчёта;
  карточка  — знак и имя в ряд, тонкая линия, контакты одной строкой под ней.
              Ближе всего к визитке.

Ограничения почты те же и обсуждению не подлежат: таблицы, стили в тегах,
шрифты, которые есть у всех, знак только картинкой по адресу. Поле подписи в
Gmail узкое, поэтому ни одно построение не шире 460 пикселей и ни в одном нет
двух широких колонок.
"""
import io, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'logo-arrows')

LOGO = 'https://gridec.am/brand/gridec-logo.png'
INK, MUTE, FAINT, LINK, RULE = '#0D0E13', '#5A5F66', '#8A8F96', '#2E5E99', '#D9D5CE'
PLATE = '#0D2440'

PHONE_HREF, PHONE = 'tel:+37441000014', '+374 41 00 00 14'
# Адрес показывается СТРОЧНЫМИ. Точка между «Hrant» и «Melkumyan» терялась:
# она стоит на базовой линии, а справа от неё сразу заглавная M, и основание её
# штриха сливается с точкой в одно пятно. Среди строчных букв точка выступает
# ниже их роста и потому заметна.
# На доставку это не влияет: Google не различает регистр в имени ящика, письмо
# на Hrant.Melkumyan@ и на hrant.melkumyan@ приходит в один и тот же ящик.
MAIL = 'hrant.melkumyan@gridec.am'
MAIL_CAPS = 'Hrant.Melkumyan@gridec.am'

FF_EN = "Arial,Helvetica,sans-serif"
FF_HY = "Arial,'Noto Sans Armenian','Sylfaen',Helvetica,sans-serif"

DATA = {
    'en': dict(ff=FF_EN, name='Hrant Melkumyan', role='Director',
               org='Gridec LLC', what='Power quality monitoring',
               addr='Davtashen 1, 13–25, Yerevan 0058, Armenia',
               l_tel='Tel', l_mail='Mail', l_web='Web', l_addr='Addr'),
    'hy': dict(ff=FF_HY, name='Հրանտ Մելքումյան', role='Տնօրեն',
               org='Գրիդեկ ՍՊԸ', what='Էլեկտրաէներգիայի որակի մոնիթորինգ',
               addr='Դավթաշեն 1, 13-25, Երևան 0058, Հայաստան',
               l_tel='Հեռ.', l_mail='Էլ. փոստ', l_web='Կայք', l_addr='Հասցե'),
}

DOT = '<span style="color:%s">&nbsp;&middot;&nbsp;</span>' % FAINT


def a(href, text, extra=''):
    return ('<a href="%s" style="color:%s;text-decoration:none%s">%s</a>'
            % (href, LINK, extra, text))


# Разрядка в сотую доли кегля. Она раздвигает соседей точки, не трогая сам
# текст: скопированный адрес остаётся посимвольно тем же.
MAIL_STYLE = ';letter-spacing:.02em'


SITE_TXT = 'www.gridec.am'      # по просьбе владельца — с www


def links():
    return (a(PHONE_HREF, PHONE), a('mailto:' + MAIL, MAIL, MAIL_STYLE),
            a('https://gridec.am', SITE_TXT))


# Значки лежат на своём сайте рядом со знаком: вшить их в подпись нельзя, Gmail
# вшитые картинки из подписи выбрасывает. Показываются втрое мельче, чем
# нарисованы, — под экраны с высокой плотностью.
#
# alt здесь несёт нагрузку, а не формальность: если у получателя внешние
# картинки режут — в организациях это обычное дело, — на месте значка встанет
# слово, и строка не останется без подписи поля.
def icon(name, alt):
    return ('<img src="https://gridec.am/brand/ic-%s.png" width="14" height="14" '
            'alt="%s" style="display:block;border:0;outline:none">' % (name, alt))


def img(w=121, h=46):
    return ('<img src="%s" width="%d" height="%d" alt="Gridec" '
            'style="display:block;border:0;outline:none;text-decoration:none">'
            % (LOGO, w, h))


# ------------------------------------------------------------------ строка
def v_line(d):
    tel, mail, site = links()
    return (
        '<table cellpadding="0" cellspacing="0" border="0" style="border-collapse:'
        'collapse"><tr><td style="border-top:2px solid %(plate)s;padding:9px 0 0;'
        'font-family:%(ff)s;font-size:13px;line-height:20px;color:%(ink)s">'
        '<b>%(name)s</b><span style="color:%(mute)s">%(dot)s%(role)s%(dot)s'
        '%(org)s</span><br>%(tel)s%(dot)s%(mail)s%(dot)s%(site)s'
        '</td></tr></table>'
        % dict(d, ink=INK, mute=MUTE, plate=PLATE, dot=DOT,
               tel=tel, mail=mail, site=site))


# ----------------------------------------------------------------- таблица
def v_table(d):
    tel, mail, site = links()
    # Значок стоит в первой колонке вместо слова. Колонка узкая и одинаковая на
    # всех строках, поэтому значения выстраиваются в столбец сами.
    # Отступ сверху в 3 пикселя сажает значок на среднюю линию строки: он 14
    # пикселей при межстрочном 20, и без поправки висел бы у верхнего края.
    def row(label, value, pad=4):
        return ('<tr><td style="padding:3px 12px %dpx 0;vertical-align:top;'
                'width:14px;color:%s">%s</td>'
                '<td style="padding:0 0 %dpx;vertical-align:top;font-size:13px;'
                'line-height:20px">%s</td></tr>' % (pad, FAINT, label, pad, value))
    # Знак ВНИЗУ, под контактами. Наверху он первым перехватывал взгляд, а в
    # письме первым должен читаться человек: имя, должность, как связаться.
    # Знак закрывает подпись — так же, как печатный бланк закрывает страницу
    # маркой внизу, а не над текстом.
    return (
        '<table cellpadding="0" cellspacing="0" border="0" style="border-collapse:'
        'collapse;font-family:%(ff)s;color:%(ink)s">'
        '<tr><td colspan="2" style="padding:0 0 2px;font-size:15px;'
        'font-weight:bold">%(name)s</td></tr>'
        '<tr><td colspan="2" style="padding:0 0 14px;font-size:13px;'
        'line-height:20px;color:%(mute)s">%(role)s%(dot)s%(org)s</td></tr>'
        '%(rows)s'
        '<tr><td colspan="2" style="padding:16px 0 0">'
        '<table cellpadding="0" cellspacing="0" border="0" style="border-collapse:'
        'collapse"><tr><td style="border-top:1px solid %(rule)s;padding:14px 0 0">'
        '%(img)s</td></tr></table></td></tr></table>'
        % dict(d, ink=INK, mute=MUTE, rule=RULE, dot=DOT, img=img(),
               rows=(row(icon('tel', d['l_tel']), tel)
                     + row(icon('mail', d['l_mail']), mail)
                     + row(icon('web', d['l_web']), site, pad=0))))


def v_table_side(d):
    """То же, но знак стоит СБОКУ от имени, а не над ним."""
    tel, mail, site = links()
    def row(label, value, pad=4):
        return ('<tr><td style="padding:3px 12px %dpx 0;vertical-align:top;'
                'width:14px;color:%s">%s</td>'
                '<td style="padding:0 0 %dpx;vertical-align:top;font-size:13px;'
                'line-height:20px">%s</td></tr>' % (pad, FAINT, label, pad, value))
    return (
        '<table cellpadding="0" cellspacing="0" border="0" style="border-collapse:'
        'collapse;font-family:%(ff)s;color:%(ink)s">'
        '<tr><td style="padding:0 20px 16px 0;vertical-align:middle">'
        '<div style="font-size:15px;font-weight:bold">%(name)s</div>'
        '<div style="font-size:13px;line-height:20px;color:%(mute)s">'
        '%(role)s%(dot)s%(org)s</div></td>'
        '<td style="padding:0 0 16px;vertical-align:middle" align="right">'
        '%(img)s</td></tr>'
        '<tr><td colspan="2" style="padding:0">'
        '<table cellpadding="0" cellspacing="0" border="0" style="border-collapse:'
        'collapse;font-family:%(ff)s">%(rows)s</table></td></tr></table>'
        % dict(d, ink=INK, mute=MUTE, dot=DOT, img=img(),
               rows=(row(icon('tel', d['l_tel']), tel)
                     + row(icon('mail', d['l_mail']), mail)
                     + row(icon('web', d['l_web']), site, pad=0))))


# ---------------------------------------------------------------- карточка
def v_card(d):
    tel, mail, site = links()
    return (
        '<table cellpadding="0" cellspacing="0" border="0" style="border-collapse:'
        'collapse;font-family:%(ff)s;color:%(ink)s">'
        '<tr><td style="padding:0 16px 0 0;vertical-align:middle">%(img)s</td>'
        '<td style="vertical-align:middle;font-size:13px;line-height:19px">'
        '<div style="font-size:15px;font-weight:bold">%(name)s</div>'
        '<div style="color:%(mute)s">%(role)s%(dot)s%(org)s</div></td></tr>'
        '<tr><td colspan="2" style="padding:12px 0 0">'
        '<table cellpadding="0" cellspacing="0" border="0" style="border-collapse:'
        'collapse;width:100%%"><tr><td style="border-top:1px solid %(rule)s;'
        'padding:10px 0 0;font-size:13px;line-height:19px;font-family:%(ff)s">'
        '%(tel)s%(dot)s%(mail)s%(dot)s%(site)s</td></tr></table>'
        '</td></tr></table>'
        % dict(d, ink=INK, mute=MUTE, rule=RULE, dot=DOT, img=img(),
               tel=tel, mail=mail, site=site))


VARIANTS = [
    ('line', 'Строка', v_line,
     'Ни знака, ни адреса — имя, должность и как связаться. Две строки под '
     'тонкой чертой. Подпись не перекрикивает письмо; в переписке из двадцати '
     'ответов это чувствуется.'),
    ('table', 'Таблица · знак внизу', v_table,
     'Знак закрывает подпись, а не открывает её: первым читается человек, '
     'последним — марка. Так устроен печатный бланк.'),
    ('tside', 'Таблица · знак сбоку', v_table_side,
     'Знак стоит в одну строку с именем, у правого края. Подпись на строку '
     'ниже и держится плотнее.'),
    ('card', 'Карточка', v_card,
     'Знак и имя в ряд, тонкая черта, контакты одной строкой под ней. Ближе '
     'всего к визитке; занимает три строки вместо шести.'),
]

os.makedirs(OUT, exist_ok=True)
sections = []
for key, title, fn, note in VARIANTS:
    sections.append(
        '<section><h2>%s</h2><p class="note">%s</p><div class="pair">'
        '<div class="col"><span class="lab">English</span>'
        '<div class="sig" id="%s-en">%s</div>'
        '<button data-copy="%s-en">Скопировать</button></div>'
        '<div class="col"><span class="lab">Հայերեն</span>'
        '<div class="sig" id="%s-hy">%s</div>'
        '<button data-copy="%s-hy">Скопировать</button></div>'
        '</div></section>'
        % (title, note, key, fn(DATA['en']), key, key, fn(DATA['hy']), key))
    for lang in ('en', 'hy'):
        io.open(os.path.join(OUT, 'sig2-%s-%s.html' % (key, lang)), 'w',
                encoding='utf-8').write(
            '<!doctype html><meta charset="utf-8">' + fn(DATA[lang]))

page = u"""<!doctype html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Подпись Gmail — ещё три</title><style>
*{box-sizing:border-box}
body{margin:0;padding:36px 26px 70px;background:#F6F5F3;color:#0D0E13;
  font:15px/1.6 -apple-system,Segoe UI,Roboto,sans-serif}
h1{font-size:22px;margin:0 0 6px}
.sub{max-width:68ch;margin:0 0 22px;color:#5A5F66}
section{background:#fff;border:1px solid #E3E0DB;border-radius:3px;
  padding:20px 22px 22px;margin-bottom:18px;max-width:1040px}
h2{font-size:15px;margin:0 0 4px}
.note{margin:0 0 16px;color:#5A5F66;font-size:13.5px;max-width:72ch}
.pair{display:flex;gap:18px;flex-wrap:wrap}
.col{flex:1 1 400px;min-width:0}
.lab{display:block;margin-bottom:8px;font:11px/1 ui-monospace,Menlo,monospace;
  letter-spacing:.12em;text-transform:uppercase;color:#8A8F96}
.sig{padding:16px;border:1px dashed #E3E0DB;border-radius:2px;overflow-x:auto}
button{margin-top:12px;font:13px/1 inherit;padding:10px 16px;border:0;
  border-radius:2px;background:#0D2440;color:#F6F1E9;cursor:pointer}
button:active{transform:translateY(1px)}
ol{max-width:70ch;padding-left:20px}li{margin-bottom:6px}
.warn{background:#FFF8E8;border:1px solid #E8D9B0;padding:14px 16px;
  border-radius:2px;max-width:1040px;margin-bottom:18px}
code{font:13px ui-monospace,Menlo,monospace;background:#F1EFEC;padding:1px 5px}
.cmp{border-collapse:collapse}
.cmp td{padding:10px 22px 10px 0;vertical-align:middle;border-top:1px solid #EFEDEA}
.cmp tr:first-child td{border-top:0}
.cmp td:first-child{font:12px/1.5 ui-monospace,Menlo,monospace;color:#8A8F96;
  white-space:nowrap}
</style></head><body>
<h1>Ещё три подписи</h1>
<p class="sub">Прежние три отличались раскладкой. Эти — замыслом: сколько подпись
о вас говорит. Нажмите кнопку под нужной, она копируется целиком.</p>

<div class="warn"><b>Проверьте перед тем, как ставить.</b><br>
Написание имени по-армянски — <b>Հրանտ Մելքումյան</b> — моя транслитерация.
В «Таблице» подписи полей заменены значками; словами они появятся только у тех
получателей, у кого картинки не грузятся — <b>Հեռ. / Էլ. փոստ / Կայք</b>.</div>

<section><h2>Точка в адресе — три написания</h2>
<p class="note">Точка стоит на базовой линии, и справа от неё сразу заглавная M:
основание её штриха сливается с точкой в одно пятно. Среди строчных букв точка
выступает ниже их роста и потому видна. На доставку регистр не влияет — Google
не различает его в имени ящика.</p>
<table class="cmp">
<tr><td>как было</td><td style="font:13px/20px Arial,Helvetica,sans-serif;color:#2E5E99">Hrant.Melkumyan@gridec.am</td></tr>
<tr><td>строчными</td><td style="font:13px/20px Arial,Helvetica,sans-serif;color:#2E5E99">hrant.melkumyan@gridec.am</td></tr>
<tr><td>строчными + разрядка<br><b>сейчас в подписях</b></td><td style="font:13px/20px Arial,Helvetica,sans-serif;color:#2E5E99;letter-spacing:.02em">hrant.melkumyan@gridec.am</td></tr>
</table></section>

%s

<section><h2>Как поставить</h2>
<ol>
<li>Gmail → шестерёнка → <b>Смотреть все настройки</b> → вкладка <b>Общие</b>.</li>
<li>Раздел <b>Подпись</b> → <b>Создать новую</b>, назовите <code>EN</code>.</li>
<li>Щёлкните в поле и вставьте: <b>Ctrl+V</b>.</li>
<li>Ещё одна, <code>HY</code>, — вставьте армянскую.</li>
<li>Внизу страницы — <b>Сохранить изменения</b>.</li>
</ol>
</section>
<script>
document.querySelectorAll('button[data-copy]').forEach(function(b){
  b.addEventListener('click',function(){
    var el=document.getElementById(b.dataset.copy);
    var r=document.createRange();r.selectNodeContents(el);
    var s=getSelection();s.removeAllRanges();s.addRange(r);
    var ok=document.execCommand('copy');s.removeAllRanges();
    var t=b.textContent;b.textContent=ok?'Скопировано':'Выделите руками';
    setTimeout(function(){b.textContent=t;},1700);
  });
});
</script>
</body></html>""" % ''.join(sections)

io.open(os.path.join(OUT, 'signature2.html'), 'w', encoding='utf-8').write(page)
print(os.path.join(OUT, 'signature2.html'))
