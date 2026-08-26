# -*- coding: utf-8 -*-
"""Страница с выключателями для ленты героя.

Берёт готовую сборку и подменяет ДВЕ строки, которые решают, рисовать ленту
или нет. Производственный исходник при этом не трогается вовсе: пробовать
поведение на живой странице надо, а тащить в неё отладочный код — нет.
"""
import io, os, re, sys

SRC = os.path.join(os.path.dirname(__file__), '..', 'site', 'index.html')
DST = os.path.join(os.path.dirname(__file__), '..', 'site', 'try-band.html')

OLD = ("  var still=!PSMOVE||(ts-PSMOVE)>BAND_HOLD;\n"
       "  var drawNow=canvasOn&&still&&(rm||!frame.d||ts-frame.d>=BAND_MS);")

NEW = """  var __m=window.__BAND||1, __age=PSMOVE?(ts-PSMOVE):1e9, __mv=__age<=90;
  var still, __ms=BAND_MS;
  if(__m===1){ still=!PSMOVE||__age>110; }
  else if(__m===2){ still=!PSMOVE||__age>30; }
  else if(__m===3){ still=true; if(__mv)__ms=100; }
  else { still=true; }
  var drawNow=canvasOn&&still&&(rm||!frame.d||ts-frame.d>=__ms);"""

PANEL = """
<style>
#bandsw{position:fixed;left:14px;bottom:14px;z-index:99999;
  font:13px/1.5 -apple-system,Segoe UI,Roboto,sans-serif;
  background:#0D2440;color:#F6F1E9;padding:12px 14px;border-radius:4px;
  box-shadow:0 10px 30px rgba(0,0,0,.35);max-width:330px;}
#bandsw b{display:block;margin-bottom:6px;font-size:12px;letter-spacing:.08em;
  text-transform:uppercase;opacity:.7;}
#bandsw div{padding:3px 0;cursor:pointer;opacity:.62;}
#bandsw div.on{opacity:1;font-weight:600;}
#bandsw div.on::before{content:"\\2192 ";}
#bandsw i{display:block;margin-top:8px;font-style:normal;font-size:12px;opacity:.6;}
</style>
<div id="bandsw"><b>Лента героя — жмите 1..4</b>
<div data-m="1">1 · как сейчас: стоит, пока страница едет</div>
<div data-m="2">2 · то же, но трогается сразу после остановки</div>
<div data-m="3">3 · идёт медленно, пока страница едет</div>
<div data-m="4">4 · идёт всегда</div>
<i>Прокрутите со второго раздела наверх и обратно. Ищите: где нет дёрганья
и лента не стоит мёртвой.</i></div>
<script>
window.__BAND=1;
(function(){
  var box=document.getElementById('bandsw');
  function paint(){
    var n=box.querySelectorAll('div');
    for(var i=0;i<n.length;i++)n[i].className=(+n[i].dataset.m===window.__BAND)?'on':'';
  }
  box.addEventListener('click',function(e){
    var d=e.target.closest('div[data-m]'); if(!d)return;
    window.__BAND=+d.dataset.m; paint();});
  addEventListener('keydown',function(e){
    if(e.key>='1'&&e.key<='4'){window.__BAND=+e.key;paint();}});
  paint();
})();
</script>
"""

s = io.open(SRC, encoding='utf-8').read()
if s.count(OLD) != 1:
    sys.exit('строка ворот ленты не найдена — сборка изменилась')
s = s.replace(OLD, NEW)
s = s.replace('</body>', PANEL + '</body>') if '</body>' in s else s + PANEL
io.open(DST, 'w', encoding='utf-8').write(s)
print('готово:', DST, len(s) // 1024, 'КБ')
