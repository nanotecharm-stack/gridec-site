# Герой: тёмная плита справа, а на ней — то самое поле, что было.
#
# Первая версия этого модуля рисовала новую анимацию, и она не подошла: прежняя
# динамика с курсором нравилась. Поэтому здесь не пишется ничего нового — берётся
# существующее поле и меняется ровно три вещи:
#
#   1. форма: SIDES 8 -> 6, то есть шестиугольник, силуэт изокуба из логотипа.
#      Весь код поля параметризован по SIDES (инрадиус, углы вершин, ограничители
#      струн, слоты подписей), поэтому пружины, толчок курсором, бегущий свет,
#      разрядные каналы и события сектора остаются нетронутыми;
#   2. грунт: плита #0D2440 в обрез справа, поле переезжает на неё целиком;
#   3. цвет линий: на тёмном грунте структура становится светлой, а бегущий свет
#      берёт акцент плашечной глубины. Ровно тот же приём, что уже применён для
#      терракотового героя.
#
# Восьмиугольник остаётся доступен: ?sides=8.


def raster(period=8, steps=11, gamma=1.4):
    """Растровый спад вместо плавного: плита рассыпается в вертикальные полосы
    растущей ширины. Плавный градиент на вертикальном крае читается размывкой,
    а полосы — это язык пиксельных полос самого сайта, приём вместо мазка."""
    stops = []
    for i in range(steps):
        duty = ((i + 1) / steps) ** gamma
        w = period * duty
        a, b = i * period, (i + 1) * period
        stops.append('transparent %.1fpx %.1fpx' % (a, b - w))
        stops.append('#000 %.1fpx %.1fpx' % (b - w, b))
    stops.append('#000 %.1fpx' % (steps * period))
    return 'linear-gradient(to right,' + ','.join(stops) + ')'


def cubes_svg(paper):
    """Крупные изометрические кубы вектором — то, что в генерации было растром.
    Каждый куб: три грани в три тона плюс внутренние рёбра из ближнего угла,
    которые продолжаются за силуэт. Кубы больше поля и уходят за его края.
    Вектор, потому что палитра ещё может смениться, а растр не перекрасить."""
    import math
    W, H = 1000, 1340
    # Один куб, а не три: анимированное поле само рисует куб теми же тремя тонами,
    # и четыре фигуры в одном кадре давали шум. Этот стоит вверху справа, далеко
    # от поля, и уходит за обе кромки — он держит глубину, не соревнуясь с ним.
    # cx, cy, R, тона (верх, левая стена, правая стена), альфа рёбер
    CUBES = [(812, 210, 470, (.055, .022, .036), .15)]
    out = []
    for cx, cy, R, tones, edge in CUBES:
        s3 = R * math.cos(math.pi / 6)                    # 0.866R
        T = (cx, cy - R); B = (cx, cy + R); C = (cx, cy)
        UL = (cx - s3, cy - R / 2); UR = (cx + s3, cy - R / 2)
        LL = (cx - s3, cy + R / 2); LR = (cx + s3, cy + R / 2)
        p = lambda *pts: 'M' + 'L'.join('%.1f %.1f' % q for q in pts) + 'Z'
        faces = ((p(T, UR, C, UL), tones[0]),      # верхняя грань светлее
                 (p(UL, C, B, LL), tones[1]),      # левая стена
                 (p(UR, C, B, LR), tones[2]))      # правая стена
        for d, a in faces:
            out.append('<path d="%s" fill="rgba(%s,%.3f)"/>' % (d, paper, a))
        # внутренние рёбра из ближнего угла: вниз, вверх-влево, вверх-вправо,
        # с выносом за силуэт — как на присланном кадре
        for tip in (B, UL, UR):
            ex = C[0] + (tip[0] - C[0]) * 1.34
            ey = C[1] + (tip[1] - C[1]) * 1.34
            out.append('<path d="M%.1f %.1fL%.1f %.1f" stroke="rgba(%s,%.3f)"'
                       ' stroke-width="1.6" fill="none"/>'
                       % (C[0], C[1], ex, ey, paper, edge))
        out.append('<path d="%s" stroke="rgba(%s,%.3f)" stroke-width="1.6"'
                   ' fill="none"/>' % (p(T, UR, LR, B, LL, UL), paper, edge * .8))
    return ('<svg class="hcubes" viewBox="0 0 %d %d" preserveAspectRatio="xMidYMid slice"'
            ' aria-hidden="true">%s</svg>' % (W, H, ''.join(out)))


def tail_svg(ink, ink2, ink5, paper):
    """Границу секции пересекает фигура, а не градиент.

    Прежний хвост гас вертикальным градиентом и читался серой мутью — то же самое,
    что уже дважды не получилось на левом крае. Здесь вниз уходит нижняя половина
    крупного куба: у границы её цвет совпадает с низом плиты, поэтому стыка нет, а
    ниже она сама сходится к вершине и кончается — глаз следит за формой и шва не
    замечает. Ни одного градиента."""
    import math
    W, H = 1000, 460
    cx, cy, R = 690, -150, 560
    s3 = R * math.cos(math.pi / 6)
    T = (cx, cy - R); B = (cx, cy + R); C = (cx, cy)
    UL = (cx - s3, cy - R / 2); UR = (cx + s3, cy - R / 2)
    LL = (cx - s3, cy + R / 2); LR = (cx + s3, cy + R / 2)
    p = lambda *pts: 'M' + 'L'.join('%.1f %.1f' % q for q in pts) + 'Z'
    out = ['<path d="%s" fill="%s"/>' % (p(UL, C, B, LL), ink5),
           '<path d="%s" fill="%s"/>' % (p(UR, C, B, LR), ink2),
           '<path d="%s" fill="%s"/>' % (p(T, UR, C, UL), ink)]
    # ребро вниз из ближнего угла — та же деталь, что у кубов на плите
    out.append('<path d="M%.1f %.1fL%.1f %.1f" stroke="rgba(%s,.10)"'
               ' stroke-width="1.6" fill="none"/>' % (C[0], C[1], B[0], B[1], paper))
    return ('<svg class="htail" viewBox="0 0 %d %d" preserveAspectRatio="xMidYMin slice"'
            ' aria-hidden="true">%s</svg>' % (W, H, ''.join(out)))


MARKUP = ('\n<div class="hplate" aria-hidden="true">%(cubes)s'
          '<i class="hveil"></i></div>\n')
TAIL = '\n<div class="hplate-tail" aria-hidden="true">%(tail)s</div>\n'

CSS = """
/* ==================== герой: тёмная плита под полем ====================
   Растровый спад по левому краю снят: в деле он читался штрих-кодом, а хвост
   ниже — гребёнкой. Вертикальный край теперь честно резкий, с одним хайрлайном:
   резкая граница — это решение, а смягчение вертикали любым способом выглядит
   недоделкой. Тёмное держат крупные формы внутри плиты, а не обработка кромки.
   Стык снизу по-прежнему снят хвостом: колонка переходит границу секции. */
.hplate{position:absolute;right:0;top:0;bottom:0;z-index:1;display:none;
  width:clamp(340px,42vw,580px);overflow:hidden;
  background:linear-gradient(176deg,%(ink)s 0%%,%(ink2)s 62%%,%(ink5)s 100%%);
  box-shadow:inset 1px 0 0 rgba(%(darkrgb)s,.22);}
.hplate-tail{position:absolute;right:0;top:0;z-index:0;display:none;
  pointer-events:none;overflow:hidden;
  width:clamp(340px,42vw,580px);height:clamp(160px,22vh,260px);}
.htail{position:absolute;inset:0;width:100%%;height:100%%;display:block;}

/* Крупные изометрические кубы: вектор, три грани в три тона, рёбра с выносом.
   Ни одного фильтра и ни одного блюра — только тон. */
.hcubes{position:absolute;inset:0;width:100%%;height:100%%;display:block;}
/* Затемнение к левому краю: самая тёмная точка плиты приходится на стык с
   бумагой, поэтому граница читается как контраст, а не как размывка. */
.hveil{position:absolute;inset:0;display:block;pointer-events:none;
  background:linear-gradient(90deg,rgba(%(shadowrgb)s,.72) 0%%,
    rgba(%(shadowrgb)s,.28) 34%%,rgba(%(shadowrgb)s,0) 62%%);}

@media(min-width:1100px){
  html[data-hero2="1"] .hplate,
  html[data-hero2="1"] .hplate-tail{display:block;}
  html[data-hero2="1"] #why{position:relative;}
  /* поле занимает плиту целиком: та же разметка, другой бокс */
  html[data-hero2="1"] .stage{left:auto;right:0;top:0;bottom:0;
    width:clamp(340px,42vw,580px);height:auto;aspect-ratio:auto;transform:none;}
  /* на тёмном структура светлая, свет — акцент плашечной глубины */
  html[data-hero2="1"] .stage{--wv-line:%(paperrgb)s;--wv-glow:%(darkrgb)s;}
  /* показания переезжают внутрь плиты */
  html[data-hero2="1"] .rd{left:clamp(20px,2.4vw,34px);
    bottom:clamp(22px,3.4vh,40px);color:rgba(%(paperrgb)s,.60);}
  html[data-hero2="1"] .rd b{color:rgba(%(paperrgb)s,.94);}
  html[data-hero2="1"] .rd .st{color:%(dark)s;}
  /* радиальная подсветка героя не нужна: она тонировала бы плиту */
  html[data-hero2="1"] .hero::after{display:none;}
}
"""

# строка HERO в чипе ревью
ROW = ("html+='</div><div class=\"row\"><span>HERO</span>';"
       "var HV=['0','1'],HL=['as built','window'];"
       "for(var q=0;q<HV.length;q++)"
       "html+='<button data-h2=\"'+HV[q]+'\">'+HV[q]+' '+HL[q]+'</button>';")

BOOT = """<script>
function hero2Set(v){
  document.documentElement.setAttribute('data-hero2',v);
  var b=document.querySelectorAll('#navsw button[data-h2]');
  for(var i=0;i<b.length;i++)b[i].classList.toggle('on',b[i].dataset.h2===v);
  /* поле читает свои цвета и размеры в size(), а тот висит на resize */
  try{dispatchEvent(new Event('resize'));}catch(e){}
}
(function(){
  var m=(location.search.match(/[?&]hero2=([01])/)||[])[1]||'0';
  hero2Set(m);
  document.addEventListener('DOMContentLoaded',function(){
    hero2Set(document.documentElement.getAttribute('data-hero2'));});
})();
</script>"""

# Поза куба вместо медленного вращения. Угол вершины считается как
# (k/SIDES)*2pi + pi/SIDES - pi/2 + rot, то есть при rot=0 и шести сторонах сверху
# оказывается плоская сторона. Сдвиг на -pi/SIDES ставит вершину вверх, и тогда швы
# к вершинам 0, 2, 4 дают ровно ту букву Y, что в знаке. Вращение снято: крутящийся
# куб не может держать позу логотипа, а «двигается свет, не геометрия» — то, из чего
# премиальность и складывается.
ROT_SRC = 'R=0,OCT_R=0,rot=0;'
ROT_NEW = 'R=0,OCT_R=0,rot=(SIDES===6?-Math.PI/SIDES:0);'
SPIN_SRC = 'tt+=dt;rot+=dt*0.032;'
SPIN_NEW = 'tt+=dt;if(SIDES!==6)rot+=dt*0.032;'

SIDES_SRC = 'var SIDES=8,PER_EDGE=11,N=SIDES*PER_EDGE;'
SIDES_NEW = ('var SIDES=/[?&]sides=6/.test(location.search)?6:8,'
             'PER_EDGE=SIDES===8?11:14,N=SIDES*PER_EDGE;')

# Второй, тихий контур снаружи фигуры логотипу не принадлежит — гасим.
RING_SRC = "cx.strokeStyle='rgba('+MILK+',.11)';cx.lineWidth=1;cx.stroke();"
RING_NEW = "cx.strokeStyle='rgba('+MILK+',0)';cx.lineWidth=1;cx.stroke();"

# Куб поверх готового кадра: три грани заливаются разным тоном (объём одним
# цветом, как в знаке), обводятся, и по трём швам из центра пробиваются
# прозрачные каналы. Пробивка идёт destination-out, то есть сквозь неё видно
# градиент самой плиты, а не подложенная краска. Швы следуют за vertex(), поэтому
# держатся фигуры при её медленном повороте. Струны, пружины, курсор и разряды
# не тронуты — это дорисовка после них.
CUBE_SRC = '  requestAnimationFrame(frame);\n}'
CUBE_NEW = """  cubeFaces();
  requestAnimationFrame(frame);
}
/* три грани знака поверх поля: тон, обводка, швы */
function cubeFaces(){
  if(SIDES!==6||!/[?&]cube=1/.test(location.search))return;
  /* три разных тона одной краски = светотень куба; грань без тона читалась бы
     дырой, поэтому ни одна не нулевая */
  var k,i,f,C=[CXp,CYp],SH=[.026,.046,.072];
  for(k=0;k<3;k++){
    f=[vertex(2*k,R),vertex(2*k+1,R),vertex(2*k+2,R),C];
    cx.beginPath();cx.moveTo(f[0][0],f[0][1]);
    for(i=1;i<4;i++)cx.lineTo(f[i][0],f[i][1]);
    cx.closePath();
    if(SH[k]){cx.fillStyle='rgba('+MILK+','+SH[k]+')';cx.fill();}
    cx.strokeStyle='rgba('+MILK+',.34)';cx.lineWidth=1;cx.stroke();
  }
  /* швы: три канала из центра к вершинам 0, 2, 4 — схема «звезда» */
  var GAP=Math.max(5,R*0.055);
  /* при destination-out стирает альфа источника, а не его цвет: кисть обязана
     быть непрозрачной, иначе от заливки грани останется 5% и шов не пробьётся */
  cx.save();cx.globalCompositeOperation='destination-out';cx.fillStyle='#000';
  for(k=0;k<3;k++){
    var v=vertex(2*k,R*1.02),dx=v[0]-CXp,dy=v[1]-CYp;
    var L=Math.hypot(dx,dy)||1,nx=-dy/L*GAP/2,ny=dx/L*GAP/2;
    cx.beginPath();
    cx.moveTo(CXp+nx,CYp+ny);cx.lineTo(v[0]+nx,v[1]+ny);
    cx.lineTo(v[0]-nx,v[1]-ny);cx.lineTo(CXp-nx,CYp-ny);
    cx.closePath();cx.fill();
  }
  cx.restore();
}
try{window.__field={frame:frame,faces:cubeFaces,
  geom:function(){return{CXp:CXp,CYp:CYp,R:R,SIDES:SIDES,N:N,rot:rot};}};}catch(e){}"""


def patch(html, pal, rgb):
    subs = dict(ink=pal['ink'], ink2=pal['ink2'], ink5=pal['ink5'], dark=pal['dark'],
                darkrgb=rgb(pal['dark']), paperrgb=rgb(pal['paper']),
                ink5rgb=rgb(pal['ink5']), shadowrgb=rgb(pal['shadow']))

    anchor = '<section class="hero" id="top">'
    if html.count(anchor) != 1:
        raise SystemExit('секция героя не найдена')
    html = html.replace(anchor, anchor + MARKUP % dict(
        cubes=cubes_svg(rgb(pal['paper']))), 1)

    tail_at = '<section class="sec thesis" id="why" data-rail>'
    if html.count(tail_at) != 1:
        raise SystemExit('секция #why не найдена')
    html = html.replace(tail_at, tail_at + TAIL % dict(
        tail=tail_svg(pal['ink'], pal['ink2'], pal['ink5'],
                      rgb(pal['paper']))), 1)

    for src, new, what in ((SIDES_SRC, SIDES_NEW, 'объявление SIDES'),
                           (ROT_SRC, ROT_NEW, 'начальный угол'),
                           (SPIN_SRC, SPIN_NEW, 'приращение поворота'),
                           (CUBE_SRC, CUBE_NEW, 'конец кадра поля')):
        if html.count(src) != 1:
            raise SystemExit('%s: не найдено однозначно' % what)
        html = html.replace(src, new, 1)

    j = html.rindex('</style>')
    html = html[:j] + (CSS % subs) + html[j:]

    tail = "sw.innerHTML=html+'</div>';"
    if html.count(tail) != 1:
        raise SystemExit('сборка чипа не найдена')
    html = html.replace(tail, ROW + tail, 1)
    html = html.replace("if(w)wmSet(w.dataset.w);});",
                        "if(w){wmSet(w.dataset.w);return;}"
                        "var h2=e.target.closest('button[data-h2]');"
                        "if(h2)hero2Set(h2.dataset.h2);});", 1)

    k = html.rindex('</body>') if '</body>' in html else len(html)
    return html[:k] + BOOT + html[k:]
