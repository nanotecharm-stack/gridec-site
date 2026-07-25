# -*- coding: utf-8 -*-
import io

p = 'shell.html'
s = io.open(p, encoding='utf-8').read()

a = s.index('/* ============ INDUSTRIES')
b = s.index('/* ============ APPROACH ROUTE')

new = r'''/* ============ INDUSTRIES — a stepped rail of card plates ============ */
var irail=document.getElementById('irail'),rbar=document.getElementById('rbar'),
    rprev=document.getElementById('rprev'),rnext=document.getElementById('rnext');

/* Each card carries its own technical drawing: orthogonal runs leaving a core,
   with pads along the way. Deterministic per card, so it never reshuffles. */
function cardArt(seed){
  function rnd(n){seed=(seed*1103515245+12345)&0x7fffffff;return seed%n;}
  var W=100,H=100,parts=[];
  var cw=20+rnd(10),ch=16+rnd(10),cx0=(W-cw)/2,cy0=(H-ch)/2;
  parts.push('<rect x="'+cx0+'" y="'+cy0+'" width="'+cw+'" height="'+ch+'" fill="none" stroke="currentColor" stroke-width=".8"/>');
  var runs=5+rnd(3);
  for(var i=0;i<runs;i++){
    var side=i%4,lane=6+rnd(16),reach=26+rnd(30),pad=rnd(2);
    var d,px,py;
    if(side===0){
      var y0=cy0+2+rnd(Math.max(2,ch-4));
      d='M'+(cx0+cw)+','+y0+' H'+(cx0+cw+lane)+' V'+(y0-reach/2)+' H'+(W+4);
      px=cx0+cw+lane;py=y0-reach/2;
    }else if(side===1){
      var y1=cy0+2+rnd(Math.max(2,ch-4));
      d='M'+cx0+','+y1+' H'+(cx0-lane)+' V'+(y1+reach/2)+' H-4';
      px=cx0-lane;py=y1+reach/2;
    }else if(side===2){
      var x2=cx0+2+rnd(Math.max(2,cw-4));
      d='M'+x2+','+cy0+' V'+(cy0-lane)+' H'+(x2+reach/2)+' V-4';
      px=x2+reach/2;py=cy0-lane;
    }else{
      var x3=cx0+2+rnd(Math.max(2,cw-4));
      d='M'+x3+','+(cy0+ch)+' V'+(cy0+ch+lane)+' H'+(x3-reach/2)+' V'+(H+4);
      px=x3-reach/2;py=cy0+ch+lane;
    }
    parts.push('<path d="'+d+'" fill="none" stroke="currentColor" stroke-width=".8" stroke-opacity=".5"/>');
    if(pad)parts.push('<rect x="'+(px-1.6)+'" y="'+(py-1.6)+'" width="3.2" height="3.2" fill="currentColor" fill-opacity=".55"/>');
  }
  return '<svg viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">'+parts.join('')+'</svg>';
}

var iovl=document.getElementById('iovl');
function openInd(o){
  var img=document.getElementById('im_img'),ph=img.parentElement;
  if(o.img!==undefined&&PT.imgs[o.img]){img.src=PT.imgs[o.img];ph.style.display='';}
  else ph.style.display='none';
  document.getElementById('im_num').textContent=o.num||'';
  document.getElementById('im_tag').textContent=o.num?('CH '+o.num):'';
  document.getElementById('im_t').textContent=o.title;
  document.getElementById('im_p1').textContent=o.p1;
  var fi=document.getElementById('im_fi');fi.innerHTML='';
  var hasF=o.findings&&o.findings.length;
  document.getElementById('im_lb').style.display=hasF?'':'none';
  if(hasF)o.findings.forEach(function(f){
    var d=document.createElement('div');d.className='fi';
    d.innerHTML='<em></em><span></span>';
    d.querySelector('span').textContent=f;fi.appendChild(d);});
  var st=document.getElementById('im_st');
  var txt=o.note||o.statText||'';
  if(o.stat||txt){
    st.style.display='';
    document.getElementById('im_big').textContent=o.stat||'';
    document.getElementById('im_sx').textContent=txt;
    document.getElementById('im_ss').textContent=o.note?'':(o.statSource||'');
  }else st.style.display='none';
  iovl.classList.add('open');document.body.style.overflow='hidden';
}

/* the six sectors, then the open invitation as the seventh plate */
var CARDS=PT.cards.concat([{num:'07',title:PT.otherT,p1:PT.otherP,invite:true}]);
CARDS.forEach(function(o,i){
  var slide=document.createElement('div');slide.className='icard';
  slide.innerHTML='<article class="ic'+(o.invite?' is-open-card':'')+'" tabindex="0">'+
    '<div class="ic-top"><span class="ic-tag"></span><span class="ic-go">&#8599;</span></div>'+
    '<div class="ic-art">'+cardArt(i*97+13)+'</div>'+
    '<div class="ic-foot"><h3></h3><p></p></div></article>';
  slide.querySelector('.ic-tag').textContent='CH '+o.num;
  slide.querySelector('h3').textContent=o.title;
  slide.querySelector('.ic-foot p').textContent=o.p1;
  var card=slide.querySelector('.ic');
  var act=function(){if(dragMoved)return;if(o.invite)openForm();else openInd(o);};
  card.addEventListener('click',act);
  card.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();act();}});
  irail.appendChild(slide);
});

/* drag-to-scroll */
var dragging=false,dragStartX=0,dragStartL=0,dragMoved=false;
irail.addEventListener('pointerdown',function(e){
  dragging=true;dragMoved=false;dragStartX=e.clientX;dragStartL=irail.scrollLeft;
  irail.classList.add('drag');
});
addEventListener('pointermove',function(e){
  if(!dragging)return;
  var d=e.clientX-dragStartX;
  if(Math.abs(d)>4)dragMoved=true;
  irail.scrollLeft=dragStartL-d;
});
addEventListener('pointerup',function(){
  if(!dragging)return;dragging=false;irail.classList.remove('drag');
  railTo(railIndex()*cardStride(),520);
  setTimeout(function(){dragMoved=false;},40);
});
/* one card per press, glided over 800ms — the pace their suite moves at */
var RAIL_MS=800,railTween=0,railIdle=0;
function railEase(t){return 1-Math.pow(1-t,4);}
function railTo(px,ms){
  var from=irail.scrollLeft,max=irail.scrollWidth-irail.clientWidth;
  var to=Math.max(0,Math.min(max,px));
  if(Math.abs(to-from)<1)return;
  if(railTween)cancelAnimationFrame(railTween);
  if(rm){irail.scrollLeft=to;railBar();return;}
  var t0=0,dur=ms||RAIL_MS;
  var step=function(ts){
    if(!t0)t0=ts;
    var k=Math.min(1,(ts-t0)/dur);
    irail.scrollLeft=from+(to-from)*railEase(k);
    railBar();
    if(k<1)railTween=requestAnimationFrame(step);else railTween=0;
  };
  railTween=requestAnimationFrame(step);
}
function cardStride(){var c=irail.querySelector('.icard');return c?c.offsetWidth:280;}
function railIndex(){return Math.round(irail.scrollLeft/Math.max(1,cardStride()));}
function railGo(i){
  i=Math.max(0,Math.min(irail.children.length-1,i));
  railTo(i*cardStride());
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
  var max=irail.scrollWidth-irail.clientWidth;
  var vis=irail.clientWidth/Math.max(1,irail.scrollWidth);
  rbar.style.width=(vis*100).toFixed(2)+'%';
  var p=max>0?irail.scrollLeft/max:0;
  rbar.style.transform='translateX('+(p*(100/Math.max(vis,.0001)-100)).toFixed(2)+'%)';
  rprev.disabled=irail.scrollLeft<4;
  rnext.disabled=irail.scrollLeft>max-4;
  if(rdots){var cur=railIndex();
    for(var i=0;i<rdots.children.length;i++)rdots.children[i].classList.toggle('on',i===cur);}
}
irail.addEventListener('scroll',function(){
  railBar();
  if(railTween||dragging)return;
  clearTimeout(railIdle);
  railIdle=setTimeout(function(){railTo(railIndex()*cardStride(),420);},140);
},{passive:true});
railBar();

'''

s = s[:a] + new + s[b:]

old_form = ("document.querySelectorAll('[data-open-form]').forEach(function(b){b.addEventListener('click',function(){\n"
            "  document.getElementById('f_main').style.display='';document.getElementById('f_done').style.display='none';\n"
            "  fovl.classList.add('open');document.body.style.overflow='hidden';});});")
new_form = ("function openForm(){\n"
            "  document.getElementById('f_main').style.display='';document.getElementById('f_done').style.display='none';\n"
            "  fovl.classList.add('open');document.body.style.overflow='hidden';\n"
            "}\n"
            "document.querySelectorAll('[data-open-form]').forEach(function(b){b.addEventListener('click',openForm);});")
assert old_form in s, 'form opener not found'
s = s.replace(old_form, new_form)

s = s.replace("function closeAll(){fovl.classList.remove('open');document.body.style.overflow='';}",
              "function closeAll(){fovl.classList.remove('open');iovl.classList.remove('open');document.body.style.overflow='';}")
s = s.replace("fovl.addEventListener('click',function(e){if(e.target===fovl)closeAll();});",
              "fovl.addEventListener('click',function(e){if(e.target===fovl)closeAll();});\n"
              "iovl.addEventListener('click',function(e){if(e.target===iovl)closeAll();});")

# the art inherits a quiet milk on the ink plates, brighter on the brand plate
s = s.replace('.ic-art svg{position:absolute;inset:0;width:100%;height:100%;overflow:visible;}',
              '.ic-art svg{position:absolute;inset:0;width:100%;height:100%;overflow:visible;color:rgba(239,237,234,.42);}\n'
              '.ic.is-open-card .ic-art svg{color:rgba(255,251,249,.5);}')

io.open(p, 'w', encoding='utf-8').write(s)
print('cardArt:', 'function cardArt' in s)
print('openInd:', 'function openInd' in s)
print('seventh card:', "num:'07'" in s)
print('openForm:', 'function openForm' in s)
