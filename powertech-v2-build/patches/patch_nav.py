# -*- coding: utf-8 -*-
"""Three header variants for review, switchable on the live page.

Shared decisions, from the brief:
  * the section list never sits in the bar. Variants 2 and 3 move it into an index
    that opens on demand; variant 1 shows only WHERE YOU ARE, the way a drawing's
    titleblock carries the sheet number.
  * the trigger is a counter (03/08), so no new copy is invented in either language.
  * no glass anywhere: the page is flat and drawn, so the bar is either real paper,
    a hairline, or opaque chips.

  0  current           the glass capsule, kept for comparison
  1  titleblock        opaque paper strip, live sheet field, no switching needed
  2  transparent rail  hairline only, tone driven by the section's own tone tag
  3  instrument chips  two opaque chips with hairline frames, nothing between them

?nav=1|2|3 or the chip at the bottom left. The choice is remembered.
"""
import io

s = io.open('shell.html', encoding='utf-8').read()

# ---------------------------------------------------------------- markup
old = """<header id="hdr"><div class="hin">"""
new = """<header id="hdr" data-tone="paper"><div class="hin">"""
assert old in s
s = s.replace(old, new)

old_nav = """  <div class="navr">
    <a class="lang" href="%%LANG_HREF%%">%%LANG_LABEL%%</a>"""
new_nav = """  <div class="navr">
    <button class="ixb" id="ixb" aria-expanded="false" aria-controls="ixp"><b id="ixn">01</b><s>/</s><em id="ixt">08</em></button>
    <a class="lang" href="%%LANG_HREF%%">%%LANG_LABEL%%</a>"""
assert old_nav in s
s = s.replace(old_nav, new_nav)

# the index sheet, and the review switcher
old_close = """</div></header>"""
new_close = """</div>
<div class="ixp" id="ixp" hidden><div class="ixin"><ol id="ixlist"></ol></div></div>
</header>
<div class="navsw" id="navsw" hidden></div>"""
assert old_close in s
s = s.replace(old_close, new_close, 1)

# ---------------------------------------------------------------- CSS
anchor = "/* right group — language, then the enquiry button */"
assert anchor in s
CSS = """/* ============ HEADER VARIANTS (under review) ============================
   0 = the glass capsule as built, 1 = titleblock, 2 = hairline rail, 3 = chips.
   The section list is out of the bar in every variant; it lives in the index. */
.ixb{display:inline-flex;align-items:baseline;gap:3px;font-family:%%MONOFONT%%;font-size:12px;
  letter-spacing:.1em;padding:9px 11px;border-radius:2px;color:rgba(13,14,19,.82);
  box-shadow:inset 0 0 0 1px rgba(13,14,19,.12);background:rgba(252,251,250,.9);
  transition:color .35s var(--e),box-shadow .35s var(--e),background .35s var(--e);}
.ixb s{text-decoration:none;opacity:.45;}
.ixb em{font-style:normal;opacity:.55;}
.ixb b{font-weight:600;}
.ixb:hover{box-shadow:inset 0 0 0 1px rgba(13,14,19,.3);}
/* the index sheet: numbered rows, nothing decorative */
.ixp{position:absolute;left:0;right:0;top:100%;background:var(--bg);
  box-shadow:0 1px 0 var(--hair);pointer-events:auto;overflow:hidden;}
.ixp[hidden]{display:none;}
.ixin{padding:clamp(14px,2vh,26px) clamp(14px,2.1vw,30px) clamp(20px,3vh,34px);}
.ixp ol{list-style:none;margin:0 auto;padding:0;max-width:1400px;
  display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:0 clamp(24px,4vw,64px);}
@media (max-width:760px){.ixp ol{grid-template-columns:1fr;}}
.ixp li{border-top:1px solid var(--hair2);}
.ixp a{display:grid;grid-template-columns:34px 1fr;gap:14px;align-items:baseline;
  padding:13px 0;color:var(--fg);}
.ixp a .no{font-family:%%MONOFONT%%;font-size:11px;letter-spacing:.14em;color:var(--brand-ink);}
.ixp a .tl{font-size:16px;line-height:1.35;}
.ixp a:hover .tl{color:var(--brand-ink);}
.ixp a.here .no{font-weight:600;}
/* motion: a sheet sliding out from under the bar, nothing bouncing */
.ixp{max-height:0;transition:max-height .34s var(--e);}
.ixp.on{max-height:70svh;overflow-y:auto;}
@media (prefers-reduced-motion:reduce){.ixp{transition:none;}}

/* ---- 1 titleblock: the bar is a real strip of paper -------------------- */
html[data-nav="1"] header{background:var(--bg);box-shadow:0 1px 0 var(--hair);pointer-events:auto;}
html[data-nav="1"] .hin{height:58px;grid-template-columns:auto 1fr auto;}
html[data-nav="1"] nav{display:none;}
html[data-nav="1"] .brand .mark{width:28px;height:28px;}
html[data-nav="1"] .brand .wm{font-size:18px;}
html[data-nav="1"] .ixb{justify-self:start;background:none;box-shadow:none;padding:9px 0 9px 22px;
  position:relative;color:var(--fg-mid);}
html[data-nav="1"] .ixb::before{content:"";position:absolute;left:0;top:50%;width:11px;height:1px;
  background:var(--hair);}
html[data-nav="1"] .ixb .sheet{margin-left:10px;text-transform:uppercase;letter-spacing:.16em;
  font-size:10px;color:var(--fg);}
html[data-nav="1"] .lang{background:none;box-shadow:none;padding:9px 6px;}
html[data-nav="1"] .btn{padding:10px 15px;font-size:13px;}
html[data-nav="1"] .btn i{width:19px;height:19px;}
html[data-nav="1"] .ixp{box-shadow:0 1px 0 var(--hair),0 24px 40px -30px rgba(13,14,19,.3);}

/* ---- 2 hairline rail: no plate at all, tone follows the section -------- */
html[data-nav="2"] .hin{height:66px;grid-template-columns:auto 1fr auto;
  box-shadow:inset 0 -1px 0 rgba(13,14,19,.12);transition:box-shadow .45s var(--e);}
html[data-nav="2"] nav{display:none;}
html[data-nav="2"] .ixb,html[data-nav="2"] .lang{background:none;box-shadow:none;padding:9px 8px;}
html[data-nav="2"] .ixb{justify-self:end;}
html[data-nav="2"] .btn{background:none;color:var(--fg);box-shadow:inset 0 0 0 1px rgba(13,14,19,.22);
  padding:11px 16px;font-size:13px;}
html[data-nav="2"] .btn::before{background:var(--fg);}
html[data-nav="2"] .btn:hover span{color:var(--bg);}
html[data-nav="2"] .btn i{background:rgba(13,14,19,.09);}
/* over an ink section the whole rail inverts, hairline included */
html[data-nav="2"] header[data-tone="ink"] .hin{box-shadow:inset 0 -1px 0 rgba(239,237,234,.22);}
html[data-nav="2"] header[data-tone="ink"] .brand,
html[data-nav="2"] header[data-tone="ink"] .ixb,
html[data-nav="2"] header[data-tone="ink"] .lang{color:#EFEDEA;}
html[data-nav="2"] header[data-tone="ink"] .btn{color:#EFEDEA;box-shadow:inset 0 0 0 1px rgba(239,237,234,.34);}
html[data-nav="2"] header[data-tone="ink"] .btn::before{background:#EFEDEA;}
html[data-nav="2"] header[data-tone="ink"] .btn:hover span{color:#0D0E13;}
html[data-nav="2"] header[data-tone="ink"] .btn i{background:rgba(239,237,234,.18);}
html[data-nav="2"] .brand,html[data-nav="2"] .ixb,html[data-nav="2"] .lang,html[data-nav="2"] .btn{
  transition:color .45s var(--e),box-shadow .45s var(--e);}

/* ---- 3 instrument chips: two opaque plates, nothing between ------------ */
html[data-nav="3"] .hin{height:76px;grid-template-columns:auto 1fr auto;align-items:start;
  padding-top:12px;}
html[data-nav="3"] nav{display:none;}
html[data-nav="3"] .brand{padding:8px 13px 8px 10px;background:var(--bg);
  box-shadow:inset 0 0 0 1px rgba(13,14,19,.14);border-radius:2px;}
html[data-nav="3"] .navr{gap:0;background:var(--bg);border-radius:2px;padding:5px;
  box-shadow:inset 0 0 0 1px rgba(13,14,19,.14);}
html[data-nav="3"] .ixb,html[data-nav="3"] .lang{background:none;box-shadow:none;}
html[data-nav="3"] .lang{position:relative;}
html[data-nav="3"] .lang::before{content:"";position:absolute;left:0;top:6px;bottom:6px;width:1px;
  background:var(--hair2);}
html[data-nav="3"] .btn{padding:10px 15px;font-size:13px;margin-left:5px;}
html[data-nav="3"] .btn i{width:19px;height:19px;}
html[data-nav="3"] .ixp{margin-top:12px;box-shadow:inset 0 0 0 1px rgba(13,14,19,.14);}

/* narrow: every variant lands on the same compact bar */
@media (max-width:900px){
  html[data-nav] .hin{grid-template-columns:auto 1fr auto;height:62px;}
  html[data-nav] .ixb .sheet{display:none;}
  html[data-nav="3"] .brand{box-shadow:none;background:none;padding:0;}
}

/* the review switcher, removed once a variant is chosen */
.navsw{position:fixed;left:14px;bottom:14px;z-index:9000;display:flex;gap:6px;padding:7px;
  background:rgba(13,14,19,.92);border-radius:3px;font:400 11px/1 ui-sans-serif,system-ui,sans-serif;}
.navsw[hidden]{display:none;}
.navsw button{color:rgba(239,237,234,.8);background:rgba(239,237,234,.08);border:none;
  border-radius:2px;padding:6px 9px;cursor:pointer;font:inherit;}
.navsw button.on{background:var(--brand);color:#fff;}
.navsw span{color:rgba(239,237,234,.45);align-self:center;padding:0 4px;letter-spacing:.1em;}

"""
s = s.replace(anchor, CSS + anchor, 1)

# ---------------------------------------------------------------- JS
js_anchor = "/* ============ PREMIUM SCROLL"
assert js_anchor in s
JS = """/* ============ HEADER VARIANTS + SECTION INDEX ============ */
var ixb=document.getElementById('ixb'),ixp=document.getElementById('ixp'),
    ixlist=document.getElementById('ixlist'),ixn=document.getElementById('ixn'),
    ixt=document.getElementById('ixt');
/* the index is read off the page itself, so the copy and the language always match
   and nothing new has to be written for either */
var ixItems=[].slice.call(document.querySelectorAll('section')).map(function(sec){
  var cnt=sec.querySelector('.cnt'),h2=sec.querySelector('h2');
  if(!cnt||!h2||!sec.id)return null;
  return {id:sec.id,no:cnt.textContent.trim(),
          title:h2.textContent.replace(/\\s+/g,' ').trim(),sec:sec};
}).filter(Boolean);
if(ixt)ixt.textContent=ixItems.length<10?('0'+ixItems.length):String(ixItems.length);
ixItems.forEach(function(it){
  var li=document.createElement('li');
  li.innerHTML='<a href="#'+it.id+'"><span class="no"></span><span class="tl"></span></a>';
  li.querySelector('.no').textContent=it.no;
  li.querySelector('.tl').textContent=it.title;
  ixlist.appendChild(li);
});
/* variant 1 shows the sheet you are on, right in the bar */
var sheet=document.createElement('span');sheet.className='sheet';ixb.appendChild(sheet);
function ixOpen(on){
  if(on){ixp.hidden=false;requestAnimationFrame(function(){ixp.classList.add('on');});}
  else{ixp.classList.remove('on');setTimeout(function(){if(!ixp.classList.contains('on'))ixp.hidden=true;},360);}
  ixb.setAttribute('aria-expanded',on?'true':'false');
}
ixb.addEventListener('click',function(){ixOpen(ixp.hidden||!ixp.classList.contains('on'));});
ixp.addEventListener('click',function(e){if(e.target.closest('a'))ixOpen(false);});
document.addEventListener('keydown',function(e){if(e.key==='Escape'&&!ixp.hidden)ixOpen(false);});
document.addEventListener('click',function(e){
  if(ixp.hidden)return;
  if(e.target.closest('#ixp')||e.target.closest('#ixb'))return;
  ixOpen(false);
});
/* which sheet are we on, and what tone is under the bar */
function ixSpy(){
  var probe=innerHeight*0.34,cur=null;
  for(var i=0;i<ixItems.length;i++){
    var r=ixItems[i].sec.getBoundingClientRect();
    if(r.top<=probe&&r.bottom>probe)cur=ixItems[i];
  }
  if(cur){ixn.textContent=cur.no;sheet.textContent=cur.title;}
  else{ixn.textContent=ixItems.length?ixItems[0].no:'01';sheet.textContent='';}
  var links=ixlist.querySelectorAll('a');
  for(var k=0;k<links.length;k++)
    links[k].classList.toggle('here',!!cur&&links[k].getAttribute('href')==='#'+cur.id);
}
/* tone is tagged on the sections themselves rather than guessed from a list */
[].slice.call(document.querySelectorAll('.plate,.plate2')).forEach(function(sec){
  sec.dataset.tone='ink';
});
function toneUnderBar(){
  var y=38,tone='paper';
  var secs=document.querySelectorAll('section[data-tone]');
  for(var i=0;i<secs.length;i++){
    var r=secs[i].getBoundingClientRect();
    if(r.top<=y&&r.bottom>=y){tone=secs[i].dataset.tone;break;}
  }
  if(!ixp.hidden)tone='paper';            /* the index is paper, keep the bar readable on it */
  hdr.setAttribute('data-tone',tone);
  hdr.classList.toggle('on-dark',tone==='ink');
}
/* the variant switch, for review only */
var NAVV=['0','1','2','3'],navLabels=['glass','titleblock','rail','chips'];
function navSet(v){
  if(v==='0')document.documentElement.removeAttribute('data-nav');
  else document.documentElement.setAttribute('data-nav',v);
  try{localStorage.setItem('pt-nav',v);}catch(e){}
  var b=document.querySelectorAll('#navsw button');
  for(var i=0;i<b.length;i++)b[i].classList.toggle('on',b[i].dataset.v===v);
  layoutSuite&&layoutSuite();
}
(function(){
  var m=/[?&]nav=([0-3])/.exec(location.search),stored=null;
  try{stored=localStorage.getItem('pt-nav');}catch(e){}
  var v=m?m[1]:(stored||'0');
  var sw=document.getElementById('navsw');
  if(m||stored){
    sw.hidden=false;
    var html='<span>HEADER</span>';
    for(var i=0;i<NAVV.length;i++)
      html+='<button data-v="'+NAVV[i]+'">'+NAVV[i]+' '+navLabels[i]+'</button>';
    sw.innerHTML=html;
    sw.addEventListener('click',function(e){
      var b=e.target.closest('button[data-v]');if(b)navSet(b.dataset.v);});
  }
  navSet(v);
})();
"""
s = s.replace(js_anchor, JS + js_anchor, 1)

# keep the spy and the tone in the scroll pass
s = s.replace("headerTheme();\n},{passive:true,capture:true});",
              "headerTheme();toneUnderBar();ixSpy();\n},{passive:true,capture:true});")
s = s.replace("headerTheme();\n/* capture-phase on document",
              "headerTheme();toneUnderBar();ixSpy();\n/* capture-phase on document")

io.open('shell.html', 'w', encoding='utf-8').write(s)

print('trigger markup   :', 'id="ixb"' in s)
print('index sheet      :', 'id="ixp"' in s and 'id="ixlist"' in s)
print('switcher         :', 'id="navsw"' in s)
print('variant css      :', all(('html[data-nav="%s"]' % v) in s for v in '123'))
print('tone tagging     :', "sec.dataset.tone='ink'" in s)
print('spy wired        :', s.count('toneUnderBar();ixSpy();'))
print('nav pill hidden  :', s.count('nav{display:none;}'))
