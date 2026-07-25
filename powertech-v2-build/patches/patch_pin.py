# -*- coding: utf-8 -*-
"""Photos on the cards, and the rail paged by vertical scroll while pinned."""
import io

p = 'shell.html'
s = io.open(p, encoding='utf-8').read()

# ---------------------------------------------------------------- CSS
old_css_start = s.index('.railwrap{position:relative;}')
old_css_end = s.index('.railbar{')
new_css = """.railwrap{position:relative;}
/* pinned: the section is tall, the frame sticks, and the rail is paged by scroll */
.suite{position:relative;}
.suite .spin{position:sticky;top:0;min-height:100svh;display:flex;flex-direction:column;justify-content:center;
  padding:clamp(84px,11vh,120px) 0 clamp(28px,4vh,52px);}
.hrail{--per:3.5;display:flex;align-items:flex-start;gap:0;overflow-x:auto;padding:6px 0 26px;
  scrollbar-width:none;-ms-overflow-style:none;overscroll-behavior-x:contain;}
.hrail::-webkit-scrollbar{display:none;}
.suite .hrail{overflow-x:hidden;}                 /* movement comes from the page */
.icard{flex:0 0 calc(100%/var(--per));padding:0 clamp(5px,.7vw,11px);}
.icard:nth-child(7n+1){padding-top:0;}
.icard:nth-child(7n+2){padding-top:clamp(18px,3vw,56px);}
.icard:nth-child(7n+3){padding-top:clamp(8px,1.4vw,26px);}
.icard:nth-child(7n+4){padding-top:clamp(24px,3.8vw,72px);}
.icard:nth-child(7n+5){padding-top:clamp(4px,.8vw,14px);}
.icard:nth-child(7n+6){padding-top:clamp(16px,2.6vw,48px);}
.icard:nth-child(7n+7){padding-top:clamp(10px,1.8vw,32px);}
.ic{position:relative;display:flex;flex-direction:column;min-height:clamp(360px,42vw,520px);
  background:#101218;color:#EFEDEA;border-radius:2px;overflow:hidden;cursor:pointer;
  transition:transform .7s var(--e),box-shadow .7s var(--e);}
.ic:hover{transform:translateY(-5px);box-shadow:0 16px 44px rgba(13,14,19,.18);}
.ic-top{position:absolute;top:0;left:0;right:0;z-index:3;display:flex;align-items:flex-start;
  justify-content:space-between;padding:15px;}
.ic-tag{font-family:'Martian Mono',%%MONOFALL%%;font-size:9.5px;letter-spacing:.16em;
  background:rgba(13,14,19,.55);color:#F4F3F1;padding:6px 9px;border-radius:2px;
  -webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px);}
.ic-go{width:32px;height:32px;border-radius:2px;background:#EFEDEA;color:#101218;
  display:grid;place-items:center;font-size:13px;flex:0 0 auto;
  transition:transform .5s var(--e),background .4s var(--e);}
.ic:hover .ic-go{transform:translate(2px,-2px);background:var(--brand);color:#fff;}
/* the sector photograph, easing in scale so the movement has weight */
.ic-art{position:relative;flex:1 1 auto;min-height:150px;overflow:hidden;}
.ic-art img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;display:block;
  transform:scale(1.04);transform-origin:52% 45%;
  transition:transform 1.15s cubic-bezier(.16,1,.3,1),filter .7s var(--e);
  filter:saturate(.85) contrast(1.03);}
.ic:hover .ic-art img{transform:scale(1.13);filter:saturate(1) contrast(1.05);}
.ic-art::after{content:"";position:absolute;inset:0;pointer-events:none;
  background:linear-gradient(180deg,rgba(13,14,19,.5) 0%,rgba(13,14,19,.05) 42%,rgba(16,18,24,.92) 100%);}
.ic-art svg{position:absolute;inset:0;width:100%;height:100%;overflow:visible;color:rgba(255,251,249,.5);}
.ic-foot{position:relative;z-index:2;padding:0 16px 18px;margin-top:-8px;}
.ic-foot h3{font-size:clamp(19px,1.9vw,26px);margin:0 0 8px;}
.ic-foot p{font-size:13.5px;line-height:1.6;color:rgba(239,237,234,.68);
  display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;}
/* the invitation keeps the brand colour and its drawing */
.ic.is-open-card{background:var(--brand);}
.ic.is-open-card .ic-art::after{background:linear-gradient(180deg,rgba(200,96,61,.1) 0%,rgba(200,96,61,.92) 100%);}
.ic.is-open-card .ic-tag{background:rgba(255,255,255,.18);color:#fff;}
.ic.is-open-card .ic-foot p{color:rgba(255,251,249,.86);}
.ic.is-open-card .ic-go{background:#14161C;color:#fff;}
.rail-dots{display:flex;gap:6px;align-items:center;}
.rail-dots button{width:22px;height:4px;background:var(--hair);border-radius:1px;transition:background .4s var(--e);}
.rail-dots button.on{background:var(--brand);}
.rail-nav{display:flex;gap:6px;}
.rail-nav button{width:38px;height:38px;border-radius:2px;box-shadow:inset 0 0 0 1px var(--hair);
  display:grid;place-items:center;font-size:14px;transition:.3s var(--e);}
.rail-nav button:hover:not(:disabled){background:var(--fg);color:var(--bg);}
.rail-nav button:disabled{opacity:.3;cursor:default;}
.rail-head{display:flex;justify-content:space-between;align-items:flex-end;gap:26px;flex-wrap:wrap;margin-bottom:clamp(20px,2.6vw,34px);}
"""
s = s[:old_css_start] + new_css + s[old_css_end:]

# mobile: no pinning, a plain swipeable rail
s = s.replace("  .hrail{--per:2.2;}", "  .hrail{--per:2.2;}")
s = s.replace("@media (max-width:991px){.hrail{--per:2.2;}}",
              "@media (max-width:991px){.hrail{--per:2.2;}\n"
              "  .suite{height:auto!important;}\n"
              "  .suite .spin{position:static;min-height:0;padding:0;}\n"
              "  .suite .hrail{overflow-x:auto;}}")

# ---------------------------------------------------------------- markup
s = s.replace('<section class="sec" id="applications" data-rail><div class="wrap">',
              '<section class="sec suite" id="applications" data-rail><div class="spin"><div class="wrap">')
s = s.replace("""  <div class="railwrap">
    <div class="hrail" id="irail"></div>
    <div class="railbar"><i id="rbar"></i></div>
  </div>
</div></section>""",
"""  <div class="railwrap">
    <div class="hrail" id="irail"></div>
    <div class="railbar"><i id="rbar"></i></div>
  </div>
</div></div></section>""")

# ---------------------------------------------------------------- JS
old = """  slide.innerHTML='<article class="ic'+(o.invite?' is-open-card':'')+'" tabindex="0">'+
    '<div class="ic-top"><span class="ic-tag"></span><span class="ic-go">&#8599;</span></div>'+
    '<div class="ic-art">'+cardArt(i*97+13)+'</div>'+
    '<div class="ic-foot"><h3></h3><p></p></div></article>';"""
new = """  var visual=(o.img!==undefined&&PT.imgs[o.img])
    ? '<img alt="" src="'+PT.imgs[o.img]+'">'
    : cardArt(i*97+13);
  slide.innerHTML='<article class="ic'+(o.invite?' is-open-card':'')+'" tabindex="0">'+
    '<div class="ic-top"><span class="ic-tag"></span><span class="ic-go">&#8599;</span></div>'+
    '<div class="ic-art">'+visual+'</div>'+
    '<div class="ic-foot"><h3></h3><p></p></div></article>';"""
assert old in s
s = s.replace(old, new)

# drag is replaced by the page: dragging would fight the scroll mapping
old_drag_start = s.index("/* drag-to-scroll */")
old_drag_end = s.index("/* one card per press, glided over 800ms")
s = s[:old_drag_start] + "var dragMoved=false;\n" + s[old_drag_end:]

old_tween_start = s.index("/* one card per press, glided over 800ms")
old_tween_end = s.index("/* ============ APPROACH ROUTE")
new_tween = """/* The rail is paged by the page itself: the section is tall, its frame sticks,
   and vertical progress maps onto horizontal travel — so every card is stepped
   through on the way past. Arrows and dots move the page, not the rail. */
var suiteSec=document.querySelector('.suite'),suitePinned=false;
function suiteTravel(){return Math.max(0,irail.scrollWidth-irail.clientWidth);}
function layoutSuite(){
  if(!suiteSec)return;
  suitePinned=innerWidth>991;
  if(!suitePinned){suiteSec.style.height='';irail.scrollLeft=0;railBar();return;}
  /* a little more page than rail, so the pass feels unhurried */
  suiteSec.style.height=(innerHeight+suiteTravel()*1.15)+'px';
  suiteUpd();
}
function suiteProgress(){
  var r=suiteSec.getBoundingClientRect();
  var total=suiteSec.offsetHeight-innerHeight;
  if(total<=0)return 0;
  var p=-r.top/total;
  return p<0?0:(p>1?1:p);
}
function suiteUpd(){
  if(!suiteSec||!suitePinned)return;
  var p=suiteProgress();
  irail.scrollLeft=p*suiteTravel();
  railBar();
  /* each photo drifts a little against its card — weight, not decoration */
  var mid=irail.clientWidth/2;
  for(var i=0;i<irail.children.length;i++){
    var im=irail.children[i].querySelector('.ic-art img');
    if(!im)continue;
    var c=irail.children[i],cx0=c.offsetLeft-irail.scrollLeft+c.offsetWidth/2;
    var d=(cx0-mid)/mid;
    im.style.transform='scale(1.06) translate3d('+(-d*10).toFixed(2)+'px,0,0)';
  }
}
function cardStride(){var c=irail.querySelector('.icard');return c?c.offsetWidth:280;}
function railIndex(){return Math.round(irail.scrollLeft/Math.max(1,cardStride()));}
function railGo(i){
  var n=irail.children.length;
  i=Math.max(0,Math.min(n-1,i));
  if(!suitePinned){irail.scrollTo({left:i*cardStride(),behavior:'smooth'});return;}
  var travel=suiteTravel();
  if(travel<=0)return;
  var target=Math.min(1,(i*cardStride())/travel);
  var top=suiteSec.getBoundingClientRect().top+scrollY;
  scrollTo({top:top+target*(suiteSec.offsetHeight-innerHeight),behavior:'smooth'});
}
function railStep(dir){railGo(railIndex()+dir);}
rprev.addEventListener('click',function(){railStep(-1);});
rnext.addEventListener('click',function(){railStep(1);});
var rdots=document.getElementById('rdots');
if(rdots){
  for(var di=0;di<irail.children.length;di++){
    (function(k){var b=document.createElement('button');
      b.setAttribute('aria-label','card '+(k+1));
      b.addEventListener('click',function(){railGo(k);});
      rdots.appendChild(b);})(di);
  }
}
function railBar(){
  var max=suiteTravel();
  var vis=irail.clientWidth/Math.max(1,irail.scrollWidth);
  rbar.style.width=(vis*100).toFixed(2)+'%';
  var p=max>0?irail.scrollLeft/max:0;
  rbar.style.transform='translateX('+(p*(100/Math.max(vis,.0001)-100)).toFixed(2)+'%)';
  rprev.disabled=irail.scrollLeft<4;
  rnext.disabled=irail.scrollLeft>max-4;
  if(rdots){var cur=railIndex();
    for(var i=0;i<rdots.children.length;i++)rdots.children[i].classList.toggle('on',i===cur);}
}
irail.addEventListener('scroll',railBar,{passive:true});
layoutSuite();

"""
s = s[:old_tween_start] + new_tween + s[old_tween_end:]

# wire into the scroll and resize passes
s = s.replace("  seqUpd();paintJoints();paintRails();paintCoFlow();paintDither();navSpy();revealPass();",
              "  seqUpd();suiteUpd();paintJoints();paintRails();paintCoFlow();paintDither();navSpy();revealPass();")
s = s.replace("size();buildJoints();buildWipe();buildRails();buildCoFlow();buildDither();",
              "size();buildJoints();buildWipe();buildRails();buildCoFlow();buildDither();layoutSuite();")
s = s.replace("addEventListener('load',function(){buildRails();buildCoFlow();});",
              "addEventListener('load',function(){buildRails();buildCoFlow();layoutSuite();});")

io.open(p, 'w', encoding='utf-8').write(s)
print('photos on cards:', "PT.imgs[o.img]+'\">'" in s)
print('pinned rail:', 'function layoutSuite' in s)
print('parallax:', 'translate3d(' in s)
print('drag removed:', 'pointerdown' not in s.split('INDUSTRIES')[1][:6000])
