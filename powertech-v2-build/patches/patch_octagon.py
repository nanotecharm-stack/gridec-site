# -*- coding: utf-8 -*-
"""Keep the strings inside the octagon; move the annotations clear of it.

Containment: every string is a quadratic curve from the centre to a perimeter
anchor, bulging sideways by its own bend. A quadratic curve always lies inside the
triangle of its three points, and the octagon is convex — so it is enough to hold
the CONTROL point inside the shape and the whole curve follows. The same argument
covers the discharge runs, which are polylines: clamp their points and the smoothed
path stays in. No clamping of the drawn curve itself is needed.

Annotations: the shape now keeps a right-hand gutter, and each row measures how
much room it actually has between the octagon's edge at that height and the canvas
edge — the boundary is computed from the polygon's support lines, so it follows the
slow rotation. A row only takes a label that fits its own room, and each row binds
to the anchor nearest its height, so leaders stay short and never cross. The
readout below the canvas is untouched: rows stay above 0.78 of the height.
"""
import io

s = io.open('shell.html', encoding='utf-8').read()

# ---------------------------------------------------------------- geometry + gutter
old = "  CXp=W/2;CYp=H/2;R=Math.min(W,H)*0.42;"
new = ("""  /* the shape sits a little left of centre: the strip on the right belongs to the
     annotations, so no label ever has to sit on top of the drawing */
  CXp=W*0.452;CYp=H/2;R=Math.min(W,H)*0.40;
  OCT_R=R*Math.cos(Math.PI/SIDES);            /* inradius — the flat sides */""")
assert old in s
s = s.replace(old, new)

s = s.replace("var W=0,H=0,dpr=1,tt=0,CXp=0,CYp=0,R=0,rot=0;",
              "var W=0,H=0,dpr=1,tt=0,CXp=0,CYp=0,R=0,OCT_R=0,rot=0;")

# ---------------------------------------------------------------- containment helpers
anchor_fn = "/* soft travelling light: cosine bell over the string */"
assert anchor_fn in s
HELPERS = """/* pull a point back inside the octagon along its own radius. Checking the three
   nearest edge normals is enough: radial scaling shrinks every projection at once. */
function clampIn(x,y,pad){
  var dx=x-CXp,dy=y-CYp,lim=OCT_R-(pad||0);
  var step=Math.PI*2/SIDES,base=step-Math.PI/2+rot;
  var k=Math.round((Math.atan2(dy,dx)-base)/step),worst=0;
  for(var j=k-1;j<=k+1;j++){
    var phi=j*step+base,d=dx*Math.cos(phi)+dy*Math.sin(phi);
    if(d>worst)worst=d;
  }
  if(worst<=lim)return [x,y];
  var sc=lim/worst;
  return [CXp+dx*sc,CYp+dy*sc];
}
/* where the perimeter is at a given height — from the polygon's own support lines,
   so it tracks the rotation instead of assuming a circle */
function octRightAt(yAbs){
  var y=yAbs-CYp,step=Math.PI*2/SIDES,base=step-Math.PI/2+rot,best=1e9;
  for(var k=0;k<SIDES;k++){
    var phi=k*step+base,c=Math.cos(phi),si=Math.sin(phi);
    if(c>1e-3){var lim=(OCT_R-y*si)/c;if(lim<best)best=lim;}
  }
  return CXp+Math.max(0,best);
}
""" + anchor_fn
s = s.replace(anchor_fn, HELPERS, 1)

# the string's control point, held inside
old_q = """    var qx=CXp+dx*0.5+nx*st.bend,qy=CYp+dy*0.5+ny*st.bend;

    /* the string itself */"""
new_q = """    var q=clampIn(CXp+dx*0.5+nx*st.bend,CYp+dy*0.5+ny*st.bend,2);
    var qx=q[0],qy=q[1];

    /* the string itself — the curve cannot leave the shape once its control
       point is inside it, the octagon being convex */"""
assert old_q in s
s = s.replace(old_q, new_q)

# the discharge run, point by point
old_arc = "    pts.push([CXp+dx*u+nx*off,CYp+dy*u+ny*off]);"
new_arc = "    pts.push(clampIn(CXp+dx*u+nx*off,CYp+dy*u+ny*off,1.5));"
assert old_arc in s
s = s.replace(old_arc, new_arc)

# ---------------------------------------------------------------- annotations
old_lab = """/* pick a label no other row is showing */
function nextLabel(row){
  var used=lrows.map(function(r){return r===row?-1:r.idx;});
  for(var tries=0;tries<40;tries++){
    var c=Math.floor(Math.random()*labelSlots.length);
    if(used.indexOf(c)<0&&c!==row.idx)return c;
  }
  return (row.idx+1)%labelSlots.length;
}"""
new_lab = """/* pick a label no other row is showing AND one that fits this row's own room */
function rowY(lr){return Math.round(H*(0.20+lr*0.29));}
function rowRoom(lr){return (W-10)-(octRightAt(rowY(lr))+16);}
function nextLabel(row,lr){
  var used=lrows.map(function(r){return r===row?-1:r.idx;});
  var room=rowRoom(lr===undefined?lrows.indexOf(row):lr);
  cx.font='600 '+(W>520?11:10)+'px '+PT.canvasFont;
  var fits=[];
  for(var c=0;c<labelSlots.length;c++){
    if(used.indexOf(c)>=0||c===row.idx)continue;
    if(cx.measureText(labelSlots[c].lab).width<=room)fits.push(c);
  }
  if(fits.length)return fits[Math.floor(Math.random()*fits.length)];
  /* nothing fits this row — hold the shortest one there */
  var best=-1,bw=1e9;
  for(var c2=0;c2<labelSlots.length;c2++){
    if(used.indexOf(c2)>=0)continue;
    var w=cx.measureText(labelSlots[c2].lab).width;
    if(w<bw){bw=w;best=c2;}
  }
  return best<0?(row.idx+1)%labelSlots.length:best;
}"""
assert old_lab in s
s = s.replace(old_lab, new_lab)

s = s.replace("      if(row.vis<=0){row.vis=0;row.idx=nextLabel(row);row.mode='in';}",
              "      if(row.vis<=0){row.vis=0;row.idx=nextLabel(row,k);row.mode='in';}")

# the row start: each row binds to the anchor nearest its own height, and the text
# begins clear of the perimeter
old_draw = """    var stl=strings[item.i],Al=anchor(stl,R);
    var rowY=Math.round(H*(0.24+lr*0.26));      /* three fixed heights */
    var ex=W-10,tw=cx.measureText(item.lab).width;
    cx.beginPath();
    cx.moveTo(Al[0]+4,Al[1]);
    cx.lineTo(ex-tw-8,rowY);"""
new_draw = """    var ry=rowY(lr),ex=W-10,tw=cx.measureText(item.lab).width;
    /* tie the row to the perimeter point nearest its height: short leaders that
       cannot cross another row's */
    var Al=null,bd=1e9;
    for(var ai=0;ai<N;ai++){
      var ap=anchor(strings[ai],R);
      if(ap[0]<CXp)continue;
      var d2=Math.abs(ap[1]-ry);
      if(d2<bd){bd=d2;Al=ap;}
    }
    if(!Al)Al=anchor(strings[item.i],R);
    var tx=Math.max(octRightAt(ry)+16,ex-tw);    /* never over the drawing */
    cx.beginPath();
    cx.moveTo(Al[0]+4,Al[1]);
    cx.lineTo(tx-8,ry);"""
assert old_draw in s
s = s.replace(old_draw, new_draw)
s = s.replace("""    cx.fillStyle='rgba('+MILK+','+(row.vis*.92).toFixed(3)+')';
    cx.fillText(item.lab,ex,rowY+3.5);""",
              """    cx.fillStyle='rgba('+MILK+','+(row.vis*.92).toFixed(3)+')';
    cx.fillText(item.lab,Math.max(tx+tw,ex),ry+3.5);""")

io.open('shell.html', 'w', encoding='utf-8').write(s)

print('gutter + smaller R :', 'CXp=W*0.452;CYp=H/2;R=Math.min(W,H)*0.40' in s)
print('inradius cached    :', 'OCT_R=R*Math.cos' in s)
print('clampIn on control :', 'var q=clampIn(' in s)
print('clampIn on arcs    :', 'pts.push(clampIn(' in s)
print('rows 0.20/0.49/0.78:', 'H*(0.20+lr*0.29)' in s)
print('width-aware labels :', 'rowRoom' in s and 'measureText(labelSlots[c].lab)' in s)
print('nearest anchor     :', 'cannot cross another' in s)
