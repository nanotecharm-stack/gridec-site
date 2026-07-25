# -*- coding: utf-8 -*-
"""Card zone reworked to the brief's mechanics, adapted to this codebase.

The brief targets the live trilingual site (.objects/.sx-card, GSAP, three HTML
files). Here there is one generated page per language and no GSAP, so what is
adopted is the MECHANICS and the NUMBERS, not the file layout:

  focus point            50% of the viewport
  proximity radius       58% of the viewport
  scale                  0.78 -> 1, smoothstep on proximity
  lift                   22px -> 0
  opacity                left at 1 (the brief's own fallback advice)
  exit tail              22vw past the centre for the last card
  travel window          0 - 88% of the pinned range, then a hold
  scroll distance        travel * 1.12 + viewport height * 0.35
  gate                   >=981px, hover:hover, pointer:fine, no reduced-motion

Two structural changes the brief requires:
  * the track is moved with translate3d, not scrollLeft — scrollLeft cannot
    overshoot its content, so the exit tail was impossible before;
  * the scroll-driven transform moves to the SHELL (.icard), leaving .ic to its
    own hover transform, which is exactly the separation the brief asks for.

Everything is computed synchronously from scroll progress: no rAF chase, no
per-frame getBoundingClientRect, no discrete active index.
"""
import io

s = io.open('shell.html', encoding='utf-8').read()

# ---------------------------------------------------------------- CSS
old_rail = """.hrail{--per:3.5;display:flex;align-items:flex-start;gap:0;overflow-x:auto;
  padding:6px var(--inset,56px) 26px;
  scrollbar-width:none;-ms-overflow-style:none;overscroll-behavior-x:contain;}
.hrail::-webkit-scrollbar{display:none;}
.suite .hrail{overflow-x:hidden;}                 /* movement comes from the page */
.icard{flex:0 0 calc((var(--vw,100vw) - var(--inset,0px))/var(--per));padding:0 clamp(5px,.7vw,11px);}"""
new_rail = """/* Horizontal applications scroll — focus-point model.
   The viewport clips, the track carries translate3d, each shell carries its own
   scale/lift from how close its centre is to the focus point. */
.hrail{display:block;overflow:hidden;padding:6px 0 26px;
  scrollbar-width:none;-ms-overflow-style:none;}
.hrail::-webkit-scrollbar{display:none;}
.sx-track{display:flex;align-items:flex-start;gap:clamp(18px,2vw,32px);width:max-content;
  transform:translate3d(0,0,0);will-change:transform;}
.icard{flex:0 0 clamp(270px,28vw,420px);transform-origin:50% 50%;will-change:transform;
  backface-visibility:hidden;}
/* touch and narrow: no pin, no transforms — a native horizontal list instead */
@media (max-width:980px),(hover:none),(pointer:coarse){
  .hrail{overflow-x:auto;scroll-snap-type:x proximity;padding-left:clamp(18px,4vw,56px);}
  .sx-track{transform:none!important;width:max-content;}
  .icard{scroll-snap-align:center;transform:none!important;opacity:1!important;}
}
@media (prefers-reduced-motion:reduce){
  .sx-track{transform:none!important;}
  .icard{transform:none!important;opacity:1!important;}
}"""
assert old_rail in s, 'rail CSS not found'
s = s.replace(old_rail, new_rail)

# the shell owns the scroll-driven transform now, so the card keeps only its hover
old_ic = "  transform:translateY(var(--ty,0px)) scale(var(--s,1));transform-origin:50% 100%;"
new_ic = "  transform:translateY(var(--ty,0px));transform-origin:50% 100%;"
assert old_ic in s
s = s.replace(old_ic, new_ic)

# ---------------------------------------------------------------- JS: the track
old_build = """CARDS.forEach(function(o,i){
  var slide=document.createElement('div');slide.className='icard';"""
new_build = """var sxTrack=document.createElement('div');sxTrack.className='sx-track';
irail.appendChild(sxTrack);
CARDS.forEach(function(o,i){
  var slide=document.createElement('div');slide.className='icard';"""
assert old_build in s
s = s.replace(old_build, new_build)
# cards go into the track, not straight into the viewport
s = s.replace("irail.appendChild(slide);", "sxTrack.appendChild(slide);")

# ---------------------------------------------------------------- JS: geometry + render
start = s.index("var suiteSec=document.querySelector('.suite'),suitePinned=false;")
end = s.index("var navLinks=")
old_block = s[start:end]
assert 'function paintRail' in old_block and 'function suiteUpd' in old_block, 'suite block not matched'

new_block = r"""var suiteSec=document.querySelector('.suite'),suitePinned=false;
/* ---- focus-point card zone -------------------------------------------------
   Measured once per layout: the shells' local centres, where the track starts so
   the first card sits on the focus point, and where it ends so the last card has
   passed it by the exit tail. Nothing here is read again during scrolling. */
var SX={centres:[],startX:0,endX:0,travel:0,dist:0,railLeft:0,focus:0,
        radius:0,scaleMin:0.78,lift:22,tail:0.22,window:0.88};
function sxShells(){return [].slice.call(sxTrack.children);}
function sxCanPin(){
  return innerWidth>=981 && matchMedia('(hover:hover)').matches
      && matchMedia('(pointer:fine)').matches && !rm;
}
function sxMeasure(){
  var shells=sxShells();if(!shells.length)return;
  sxTrack.style.transform='translate3d(0,0,0)';          /* measure unshifted */
  SX.centres=shells.map(function(el){return el.offsetLeft+el.offsetWidth/2;});
  SX.railLeft=irail.getBoundingClientRect().left;
  SX.focus=innerWidth*0.5;
  SX.radius=innerWidth*0.58;
  var first=SX.centres[0],last=SX.centres[SX.centres.length-1];
  SX.startX=SX.focus-SX.railLeft-first;
  SX.endX=SX.focus-SX.railLeft-last-innerWidth*SX.tail;
  SX.travel=Math.abs(SX.endX-SX.startX);
  SX.dist=SX.travel*1.12+innerHeight*0.35;
}
function layoutSuite(){
  if(!suiteSec)return;
  suitePinned=sxCanPin();
  if(!suitePinned){
    suiteSec.style.height='';sxTrack.style.transform='';
    sxShells().forEach(function(el){el.style.transform='';});
    railBar();return;
  }
  /* the card has to fit the pinned frame — measure once, then correct against it */
  var head=suiteSec.querySelector('.rail-head'),spin=suiteSec.querySelector('.spin');
  var hs=getComputedStyle(head),spins=getComputedStyle(spin);
  var chrome=head.offsetHeight+parseFloat(hs.marginBottom||0)
            +parseFloat(spins.paddingTop||0)+parseFloat(spins.paddingBottom||0)
            +(document.querySelector('.railbar')?document.querySelector('.railbar').offsetHeight+18:0)+32;
  var est=Math.max(260,Math.min(520,Math.round(innerHeight-chrome)));
  irail.style.setProperty('--cardh',est+'px');
  var over=spin.offsetHeight-innerHeight;
  if(over>0)irail.style.setProperty('--cardh',Math.max(260,est-over)+'px');
  sxMeasure();
  suiteSec.style.height=(innerHeight+SX.dist)+'px';
  suiteUpd();
}
function suiteProgress(){
  var r=suiteSec.getBoundingClientRect();
  var span=suiteSec.offsetHeight-innerHeight;
  if(span<=0)return 0;
  return Math.max(0,Math.min(1,-r.top/span));
}
/* smoothstep — the card grows long before the centre and never snaps */
function sxEase(t){return t*t*(3-2*t);}
function sxRender(x){
  var shells=sxShells();
  for(var i=0;i<shells.length;i++){
    var centre=SX.railLeft+x+SX.centres[i];
    var d=Math.abs(centre-SX.focus);
    var prox=1-d/SX.radius; prox=prox<0?0:prox>1?1:prox;
    var e=sxEase(prox);
    var sc=SX.scaleMin+(1-SX.scaleMin)*e;
    var y=SX.lift-SX.lift*e;
    shells[i].style.transform='translate3d(0,'+y.toFixed(2)+'px,0) scale('+sc.toFixed(4)+')';
    var im=shells[i].querySelector('.ic-art img');
    if(im){var rel=(centre-SX.focus)/SX.focus;
      im.style.transform='scale(1.06) translate3d('+(-rel*12).toFixed(2)+'px,0,0)';}
  }
}
function suiteUpd(){
  if(!suiteSec||!suitePinned)return;
  var p=suiteProgress();
  var tp=p/SX.window; tp=tp<0?0:tp>1?1:tp;      /* the last stretch is the hold */
  var x=SX.startX+(SX.endX-SX.startX)*tp;
  sxTrack.style.transform='translate3d('+x.toFixed(2)+'px,0,0)';
  sxRender(x);
  railBar(tp);
}
function railBar(tp){
  var bar=document.getElementById('rbar');if(!bar)return;
  if(tp===undefined)tp=0;
  bar.style.transform='scaleX('+Math.max(0.02,Math.min(1,tp)).toFixed(4)+')';
}
"""
s = s[:start] + new_block + s[end:]

# nothing chases any more
s = s.replace("irail.addEventListener('scroll',railBar,{passive:true});\n", "")

io.open('shell.html', 'w', encoding='utf-8').write(s)

import re
print('track element     :', "className='sx-track'" in s)
print('cards into track  :', s.count('sxTrack.appendChild(slide)'))
print('translate3d track :', "sxTrack.style.transform='translate3d(" in s)
print('scrollLeft gone   :', 'irail.scrollLeft' not in s)
print('railChase gone    :', 'railChase' not in s)
print('shell owns scale  :', 'shells[i].style.transform=' in s)
print('.ic keeps hover   :', 'transform:translateY(var(--ty,0px));' in s)
print('numbers           : scaleMin 0.78, lift 22, tail .22vw, window .88, dist travel*1.12+vh*.35')
print('dupes             :', [n for n in ['layoutSuite','suiteUpd','railBar','suiteProgress','sxMeasure']
                              if len(re.findall(r'function\s+'+n+r'\s*\(', s))!=1])
