# -*- coding: utf-8 -*-
"""Premium scroll: wheel input decoupled from the viewport and eased toward a target.

The reference site does this with Lenis at lerp 0.1. No library here — the brief
rules out extra dependencies — but the same principle, and deliberately the same
mechanism Lenis uses by default: the page is moved with window.scrollTo on every
frame rather than by transforming a wrapper. A transformed wrapper would break
position:sticky, and both pinned sections (the event chain and the card zone)
depend on it.

Kept native: touch (iOS momentum is already right, and hijacking it is what broke
Chrome-on-iOS before), reduced-motion, narrow viewports, and anything with its own
scroller — the modals and the horizontal card rail.
"""
import io

s = io.open('shell.html', encoding='utf-8').read()

anchor = """/* capture-phase on document catches wrapper scrolling too; paint synchronously — no frame lag */"""
assert anchor in s

SMOOTH = r"""/* ============ PREMIUM SCROLL — eased wheel, native everywhere else ============ */
/* Lenis-style: accumulate wheel delta into a target, ease the real scroll toward it
   with scrollTo (NOT a transformed wrapper — that would kill position:sticky, and
   the pinned chain and card zone both rely on it). */
var PS={t:0,c:0,raf:0,last:0,self:false,lerp:0.1};
function psActive(){
  return !rm && matchMedia('(pointer:fine)').matches && innerWidth>=900
      && !matchMedia('(hover:none)').matches;
}
function psMax(){return Math.max(0,document.documentElement.scrollHeight-innerHeight);}
/* an ancestor that can take the vertical delta itself keeps it */
function psInner(el){
  for(var n=el;n&&n!==document.body&&n!==document.documentElement;n=n.parentElement){
    if(n.nodeType!==1)continue;
    var o=getComputedStyle(n).overflowY;
    if((o==='auto'||o==='scroll')&&n.scrollHeight>n.clientHeight+2)return true;
  }
  return false;
}
function psFrame(ts){
  var dt=PS.last?Math.min(.05,(ts-PS.last)/1000):.016;PS.last=ts;
  var k=1-Math.pow(1-PS.lerp,dt*60);                 /* frame-rate independent */
  PS.t=Math.max(0,Math.min(psMax(),PS.t));
  PS.c+=(PS.t-PS.c)*k;
  if(Math.abs(PS.t-PS.c)<0.35){PS.c=PS.t;PS.raf=0;PS.last=0;}
  else PS.raf=requestAnimationFrame(psFrame);
  PS.self=true;window.scrollTo(0,PS.c);PS.self=false;
}
function psPush(dy){
  PS.t=Math.max(0,Math.min(psMax(),PS.t+dy));
  if(!PS.raf){PS.last=0;PS.raf=requestAnimationFrame(psFrame);}
}
function psTo(y){
  PS.t=Math.max(0,Math.min(psMax(),y));
  if(!PS.raf){PS.last=0;PS.raf=requestAnimationFrame(psFrame);}
}
function psStart(){
  if(!psActive())return;
  document.documentElement.style.scrollBehavior='auto';   /* we do the easing now */
  PS.t=PS.c=window.pageYOffset;
  addEventListener('wheel',function(e){
    if(e.ctrlKey||e.defaultPrevented)return;              /* pinch-zoom stays native */
    if(psInner(e.target))return;                          /* modals keep their own scroll */
    e.preventDefault();
    var dy=e.deltaMode===1?e.deltaY*16:e.deltaMode===2?e.deltaY*innerHeight:e.deltaY;
    psPush(dy);
  },{passive:false});
  /* keyboard, scrollbar drags and hash jumps move the page without us — resync */
  addEventListener('scroll',function(){
    if(PS.self||PS.raf)return;
    PS.t=PS.c=window.pageYOffset;
  },{passive:true});
  /* in-page links ride the same easing instead of the browser's smooth jump */
  document.addEventListener('click',function(e){
    var a=e.target.closest&&e.target.closest('a[href^="#"]');
    if(!a)return;
    var id=a.getAttribute('href').slice(1);
    if(!id){e.preventDefault();psTo(0);return;}
    var el=document.getElementById(id);if(!el)return;
    e.preventDefault();
    psTo(el.getBoundingClientRect().top+window.pageYOffset-(id==='top'?0:26));
    history.replaceState(null,'','#'+id);
  });
  addEventListener('resize',function(){PS.t=PS.c=window.pageYOffset;});
}
psStart();
"""

s = s.replace(anchor, SMOOTH + anchor, 1)
io.open('shell.html', 'w', encoding='utf-8').write(s)

print('smooth block  :', s.count('PREMIUM SCROLL'))
print('uses scrollTo :', 'PS.self=true;window.scrollTo' in s)
print('no wrapper transform:', 'translate3d(0,-' not in SMOOTH)
print('guards        :', all(g in s for g in ['psActive','psInner','pointer:fine','hover:none']))
