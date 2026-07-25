# -*- coding: utf-8 -*-
"""Full-bleed card zone + inertial rail (the physics Lenis gives their page)."""
import io

p = 'shell.html'
s = io.open(p, encoding='utf-8').read()

# ---------------------------------------------------------------- markup: rail leaves the content column
old = """  <div class="railwrap">
    <div class="hrail" id="irail"></div>
    <div class="railbar"><i id="rbar"></i></div>
  </div>
</div></div></section>"""
new = """</div>
  <div class="railwrap">
    <div class="hrail" id="irail"></div>
  </div>
  <div class="wrap"><div class="railbar"><i id="rbar"></i></div></div>
</div></section>"""
assert old in s, 'rail markup not found'
s = s.replace(old, new)

# ---------------------------------------------------------------- CSS
s = s.replace(".railwrap{position:relative;}",
              ".railwrap{position:relative;width:100%;}")
s = s.replace(""".hrail{--per:3.5;display:flex;align-items:flex-start;gap:0;overflow-x:auto;padding:6px 0 26px;
  scrollbar-width:none;-ms-overflow-style:none;overscroll-behavior-x:contain;}""",
"""/* the zone runs the full width: the first card lines up with the heading above,
   the rest carry on past the right edge */
.hrail{--per:3.5;display:flex;align-items:flex-start;gap:0;overflow-x:auto;
  padding:6px clamp(18px,4vw,56px) 26px;
  scrollbar-width:none;-ms-overflow-style:none;overscroll-behavior-x:contain;}""")
s = s.replace(".rail-head{display:flex;", ".suite .spin>.wrap{width:100%;}\n.rail-head{display:flex;")

# ---------------------------------------------------------------- JS: inertia instead of a hard mapping
old_js = """function suiteUpd(){
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
}"""
new_js = """/* Their page scrolls through Lenis at lerp 0.1, which is why anything tied to
   scroll feels soft there. Mapping scroll straight onto the rail felt stepped,
   so the rail now chases its target with the same easing, frame-rate normalised. */
var railTarget=0,railCur=0,railRAF=0,railLast=0;
function railChase(ts){
  var dt=railLast?Math.min(.05,(ts-railLast)/1000):.016;railLast=ts;
  var k=1-Math.pow(1-0.1,dt*60);              /* lerp 0.1 per 60fps frame */
  railCur+=(railTarget-railCur)*k;
  if(Math.abs(railTarget-railCur)<0.4){railCur=railTarget;railRAF=0;railLast=0;}
  else railRAF=requestAnimationFrame(railChase);
  paintRail();
}
function paintRail(){
  irail.scrollLeft=railCur;
  railBar();
  /* each photo drifts against its card — weight, not decoration */
  var mid=irail.clientWidth/2;
  for(var i=0;i<irail.children.length;i++){
    var im=irail.children[i].querySelector('.ic-art img');
    if(!im)continue;
    var c=irail.children[i],cx0=c.offsetLeft-railCur+c.offsetWidth/2;
    var d=(cx0-mid)/mid;
    im.style.transform='scale(1.06) translate3d('+(-d*12).toFixed(2)+'px,0,0)';
  }
}
function suiteUpd(){
  if(!suiteSec||!suitePinned)return;
  railTarget=suiteProgress()*suiteTravel();
  if(rm){railCur=railTarget;paintRail();return;}
  if(!railRAF){railLast=0;railRAF=requestAnimationFrame(railChase);}
}"""
assert old_js in s, 'suiteUpd not found'
s = s.replace(old_js, new_js)

s = s.replace("""  if(!suitePinned){suiteSec.style.height='';irail.scrollLeft=0;railBar();return;}""",
              """  if(!suitePinned){suiteSec.style.height='';railCur=0;railTarget=0;irail.scrollLeft=0;railBar();return;}""")

io.open(p, 'w', encoding='utf-8').write(s)
print('full-bleed rail:', 'padding:6px clamp(18px,4vw,56px) 26px' in s)
print('inertia:', 'function railChase' in s)
print('paintRail:', s.count('function paintRail'))
print('suiteUpd:', s.count('function suiteUpd'))
