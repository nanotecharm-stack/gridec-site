# -*- coding: utf-8 -*-
"""Почтовая подпись Gmail — три построения, два языка.

Почтовая программа — не браузер: своих шрифтов у неё нет, внешние стили она
выбрасывает, современную вёрстку ломает. Поэтому всё собрано так, как собирают
письма: таблицей, со стилями прямо в тегах, на шрифтах, которые есть у всех.

Три построения решают разные затруднения, а не «выглядят по-разному»:

  строка   — узкая, в две колонки. Занимает мало места под письмом, но поле
             подписи в Gmail само по себе узкое, и широкую таблицу оно жмёт;
  столбик  — колонок нет вообще, только строки друг под другом. Ничему не во
             что упираться, поэтому в поле Gmail ведёт себя спокойнее всего;
  без картинки — знак нарисован ЯЧЕЙКОЙ таблицы: тёмная заливка и слово
             набором. Ни одного изображения, значит ничего не может не
             загрузиться. Многие почтовые системы в организациях режут внешние
             картинки, и подпись с картинкой приходит к ним с пустым
             прямоугольником. Здесь такого не бывает.

За это построение платят точностью: пиксельного шрифта у получателя нет, слово
набирается обычным, и знак ПОХОЖ на сайтовый, но не равен ему.

Тексты взяты с живого сайта слово в слово, не переведены заново.
"""
import io, os

HERE = os.path.dirname(os.path.abspath(__file__))
# Подписи кладём НЕ в brand/: оттуда сборка выкладывает всё на сайт, и страница
# с личными данными директора оказалась бы по адресу gridec.am/brand/.
OUT = os.path.join(HERE, 'logo-arrows')

LOGO = 'https://gridec.am/brand/gridec-logo.png'
INK, MUTE, FAINT, LINK, RULE = '#0D0E13', '#5A5F66', '#8A8F96', '#2E5E99', '#D9D5CE'
PLATE, PLATE_FG = '#0D2440', '#F6F1E9'

PHONE_HREF, PHONE = 'tel:+37441000014', '+374 41 00 00 14'
MAIL = 'Hrant.Melkumyan@gridec.am'

FF_EN = "Arial,Helvetica,sans-serif"
FF_HY = "Arial,'Noto Sans Armenian','Sylfaen',Helvetica,sans-serif"

DATA = {
    'en': dict(ff=FF_EN, name='Hrant Melkumyan', role='Director',
               org='Gridec LLC', what='Power quality monitoring',
               addr='Davtashen 1, 13–25, Yerevan 0058, Armenia'),
    'hy': dict(ff=FF_HY, name='Հրանտ Մելքումյան', role='Տնօրեն',
               org='Գրիդեկ ՍՊԸ', what='Էլեկտրաէներգիայի որակի մոնիթորինգ',
               addr='Դավթաշեն 1, 13-25, Երևան 0058, Հայաստան'),
}


def a(href, text, color=LINK):
    return ('<a href="%s" style="color:%s;text-decoration:none">%s</a>'
            % (href, color, text))


def links(d):
    return (a(PHONE_HREF, PHONE), a('mailto:' + MAIL, MAIL),
            a('https://gridec.am', 'gridec.am'))


def img(w=121, h=46):
    return ('<img src="%s" width="%d" height="%d" alt="Gridec" '
            'style="display:block;border:0;outline:none;text-decoration:none">'
            % (LOGO, w, h))


# ------------------------------------------------------------------ строка
def v_row(d):
    tel, mail, site = links(d)
    return (
        '<table cellpadding="0" cellspacing="0" border="0" style="border-collapse:'
        'collapse;font-family:%(ff)s;color:%(ink)s;font-size:13px;line-height:19px">'
        '<tr><td style="padding:0 14px 0 0;vertical-align:middle">%(img)s</td>'
        '<td style="border-left:1px solid %(rule)s;padding:0 0 0 14px;'
        'vertical-align:middle">'
        '<div><b style="font-size:14px">%(name)s</b>'
        '<span style="color:%(mute)s">&nbsp;&middot;&nbsp;%(role)s</span></div>'
        '<div style="color:%(mute)s">%(org)s</div>'
        '<div style="padding-top:4px">%(tel)s<span style="color:%(faint)s">'
        '&nbsp;&middot;&nbsp;</span>%(mail)s<span style="color:%(faint)s">'
        '&nbsp;&middot;&nbsp;</span>%(site)s</div>'
        '</td></tr></table>'
        % dict(d, ink=INK, mute=MUTE, faint=FAINT, rule=RULE, img=img(),
               tel=tel, mail=mail, site=site))


# ----------------------------------------------------------------- столбик
def v_stack(d):
    tel, mail, site = links(d)
    return (
        '<div style="font-family:%(ff)s;color:%(ink)s;font-size:13px;'
        'line-height:20px">'
        '%(img)s'
        '<div style="height:12px;line-height:12px">&nbsp;</div>'
        '<div style="font-size:15px;font-weight:bold">%(name)s</div>'
        '<div style="color:%(mute)s">%(role)s</div>'
        '<div style="color:%(mute)s">%(org)s &middot; %(what)s</div>'
        '<div style="height:8px;line-height:8px">&nbsp;</div>'
        '<div>%(tel)s</div><div>%(mail)s</div><div>%(site)s</div>'
        '<div style="color:%(faint)s;font-size:12px;padding-top:6px">%(addr)s</div>'
        '</div>'
        % dict(d, ink=INK, mute=MUTE, faint=FAINT, img=img(),
               tel=tel, mail=mail, site=site))


# ------------------------------------------------------------ без картинки
def v_plain(d):
    tel, mail, site = links(d)
    return (
        '<table cellpadding="0" cellspacing="0" border="0" style="border-collapse:'
        'collapse;font-family:%(ff)s;color:%(ink)s;font-size:13px;line-height:20px">'
        '<tr><td bgcolor="%(plate)s" style="background-color:%(plate)s;'
        'padding:11px 14px;border-radius:2px">'
        '<span style="color:%(pfg)s;font-size:17px;font-weight:bold;'
        'letter-spacing:4px;line-height:17px">GRIDEC</span></td></tr>'
        '<tr><td style="height:12px;line-height:12px">&nbsp;</td></tr>'
        '<tr><td>'
        '<div style="font-size:15px;font-weight:bold">%(name)s</div>'
        '<div style="color:%(mute)s">%(role)s</div>'
        '<div style="color:%(mute)s">%(org)s &middot; %(what)s</div>'
        '<div style="height:8px;line-height:8px">&nbsp;</div>'
        '<div>%(tel)s</div><div>%(mail)s</div><div>%(site)s</div>'
        '<div style="color:%(faint)s;font-size:12px;padding-top:6px">%(addr)s</div>'
        '</td></tr></table>'
        % dict(d, ink=INK, mute=MUTE, faint=FAINT, plate=PLATE, pfg=PLATE_FG,
               tel=tel, mail=mail, site=site))


VARIANTS = [
    ('row', 'Строка', v_row,
     'Узкая и низкая — меньше всего места под письмом. Знак картинкой. '
     'Две колонки: в узком поле Gmail может сжаться.'),
    ('stack', 'Столбик', v_stack,
     'Колонок нет вообще. Ведёт себя в поле Gmail спокойнее всех. '
     'Знак картинкой.'),
    ('plain', 'Без картинки', v_plain,
     'Ни одного изображения: знак нарисован тёмной ячейкой и набором. '
     'Доходит везде, даже там, где внешние картинки режут. '
     'Слово набрано обычным шрифтом — знак похож на сайтовый, но не равен ему.'),
]

os.makedirs(OUT, exist_ok=True)
sections = []
for key, title, fn, note in VARIANTS:
    for lang, label in (('en', 'English'), ('hy', 'Հայերեն')):
        pass
    sections.append(
        '<section><h2>%s</h2><p class="note">%s</p>'
        '<div class="pair">'
        '<div class="col"><span class="lab">English</span>'
        '<div class="sig" id="%s-en">%s</div>'
        '<button data-copy="%s-en">Скопировать</button></div>'
        '<div class="col"><span class="lab">Հայերեն</span>'
        '<div class="sig" id="%s-hy">%s</div>'
        '<button data-copy="%s-hy">Скопировать</button></div>'
        '</div></section>'
        % (title, note, key, fn(DATA['en']), key, key, fn(DATA['hy']), key))
    for lang in ('en', 'hy'):
        io.open(os.path.join(OUT, 'sig-%s-%s.html' % (key, lang)), 'w',
                encoding='utf-8').write(
            '<!doctype html><meta charset="utf-8">' + fn(DATA[lang]))

page = u"""<!doctype html><html lang="ru"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Подпись Gmail — три варианта</title><style>
*{box-sizing:border-box}
body{margin:0;padding:36px 26px 70px;background:#F6F5F3;color:#0D0E13;
  font:15px/1.6 -apple-system,Segoe UI,Roboto,sans-serif}
h1{font-size:22px;margin:0 0 6px}
.sub{max-width:66ch;margin:0 0 22px;color:#5A5F66}
section{background:#fff;border:1px solid #E3E0DB;border-radius:3px;
  padding:20px 22px 22px;margin-bottom:18px;max-width:1000px}
h2{font-size:15px;margin:0 0 4px}
.note{margin:0 0 16px;color:#5A5F66;font-size:13.5px;max-width:70ch}
.pair{display:flex;gap:18px;flex-wrap:wrap}
.col{flex:1 1 380px;min-width:0}
.lab{display:block;margin-bottom:8px;font:11px/1 ui-monospace,Menlo,monospace;
  letter-spacing:.12em;text-transform:uppercase;color:#8A8F96}
.sig{padding:16px;border:1px dashed #E3E0DB;border-radius:2px;overflow-x:auto}
button{margin-top:12px;font:13px/1 inherit;padding:10px 16px;border:0;
  border-radius:2px;background:#0D2440;color:#F6F1E9;cursor:pointer}
button:active{transform:translateY(1px)}
ol{max-width:70ch;padding-left:20px}li{margin-bottom:6px}
.warn{background:#FFF8E8;border:1px solid #E8D9B0;padding:14px 16px;
  border-radius:2px;max-width:1000px;margin-bottom:18px}
code{font:13px ui-monospace,Menlo,monospace;background:#F1EFEC;padding:1px 5px}
</style></head><body>
<h1>Почтовая подпись — три построения</h1>
<p class="sub">Отличаются не видом, а тем, какое затруднение решают. Нажмите
кнопку под нужной — блок копируется целиком, вместе со ссылками.</p>

<div class="warn"><b>Проверьте до того, как ставить.</b><br>
Написание имени по-армянски — <b>Հրանտ Մելքումյան</b> — моя транслитерация,
а не ваше написание из паспорта. Должность: <b>Director</b> / <b>Տնօրեն</b>.</div>

%s

<section><h2>Как поставить в Gmail</h2>
<ol>
<li>Gmail → шестерёнка → <b>Смотреть все настройки</b>.</li>
<li>Вкладка <b>Общие</b>, прокрутите вниз до раздела <b>Подпись</b>.</li>
<li><b>Создать новую</b>, назовите <code>EN</code>.</li>
<li>Щёлкните в поле подписи и вставьте: <b>Ctrl+V</b>.</li>
<li>Ещё раз <b>Создать новую</b>, назовите <code>HY</code>, вставьте армянскую.</li>
<li>Ниже выберите, какая идёт в новых письмах и какая в ответах.</li>
<li>В самом низу страницы — <b>Сохранить изменения</b>.</li>
</ol>
<p style="color:#5A5F66;max-width:70ch">Если после вставки подпись «поехала» —
возьмите построение <b>Столбик</b>: в нём нет колонок, и сжимать в поле нечего.
Переключать язык в готовом письме можно значком пера внизу окна.</p>
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

io.open(os.path.join(OUT, 'signature.html'), 'w', encoding='utf-8').write(page)
print(os.path.join(OUT, 'signature.html'))
