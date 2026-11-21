// ---- fault light v3: continuous bright trace + depth contours + large distinct particles; gold highlight for the featured fault
const GOLD=[255,190,56];
// emphasis settings shared by the video scenes and the panel selection (single source of truth)
const EMPH={dim:0.67,boost:1.1};
const emphK=(inF,any)=>(1+EMPH.boost*inF)*(1-EMPH.dim*any*(1-inF));
function d2xy(a,b){const x=a[0]-b[0],y=a[1]-b[1];return x*x+y*y}
function chainSegs(segs,tol){
  const used=new Array(segs.length).fill(false),out=[];
  for(let i=0;i<segs.length;i++){
    if(used[i])continue;used[i]=true;const pts=[segs[i][0],segs[i][1]];
    let ext=true;
    while(ext){ext=false;
      for(let j=0;j<segs.length;j++){if(used[j])continue;const a=segs[j][0],b=segs[j][1],e=pts[pts.length-1],s0=pts[0];
        if(d2xy(e,a)<tol){pts.push(b);used[j]=true;ext=true}
        else if(d2xy(e,b)<tol){pts.push(a);used[j]=true;ext=true}
        else if(d2xy(s0,b)<tol){pts.unshift(a);used[j]=true;ext=true}
        else if(d2xy(s0,a)<tol){pts.unshift(b);used[j]=true;ext=true}}}
    out.push(pts);}
  return out;
}
// join chains whose end points are closer than maxGap km, so each fault reads as one continuous streak
function mergeChains(ch,maxGap){
  const g2=maxGap*maxGap;ch=ch.map(c=>c.slice());
  let again=true;
  while(again&&ch.length>1){again=false;let best=null;
    for(let i=0;i<ch.length;i++)for(let j=i+1;j<ch.length;j++){
      const A=ch[i],B=ch[j];
      for(const [ea,eb] of [[0,0],[0,1],[1,0],[1,1]]){
        const pa=ea?A[A.length-1]:A[0],pb=eb?B[B.length-1]:B[0],d=d2xy(pa,pb);
        if(d<g2&&(!best||d<best.d))best={i,j,ea,eb,d};}}
    if(best){const A=ch[best.i].slice(),B=ch[best.j].slice();
      if(!best.ea)A.reverse();if(best.eb)B.reverse();
      ch[best.i]=A.concat(B);ch.splice(best.j,1);again=true;}}
  return ch;
}
function lerp3(a,b,t){return [a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,a[2]+(b[2]-a[2])*t]}
function surf(q,u,v){return lerp3(lerp3(q[0],q[1],u),lerp3(q[3],q[2],u),v)}
function rng(seed){let s=(seed*2654435761)>>>0||1;return()=>{s^=s<<13;s>>>=0;s^=s>>>17;s^=s<<5;s>>>=0;return s/4294967296}}
F.forEach(f=>{
  const r=rng(f.id+101);
  const dens=0.10*(0.3+f.br*1.3)*(f.i?0.4:1);
  if(f.Q){
    const top=Math.min(...f.Q.map(q=>q[0][2])),bot=Math.max(...f.Q.map(q=>q[2][2]));
    f.TR=mergeChains(chainSegs(f.Q.filter(q=>q[0][2]<=top+0.01).map(q=>[q[0],q[1]]),0.3),12);
    f.IS=[];
    const ds=[];for(let d=5;d<bot-0.4;d+=5)if(d>top+0.4)ds.push(d);if(bot>top+0.4)ds.push(bot);
    for(const d of ds){const segs=[];for(const q of f.Q){if(d>q[0][2]-0.01&&d<=q[2][2]+0.01&&q[2][2]>q[0][2]+0.2){const v=(d-q[0][2])/(q[2][2]-q[0][2]);segs.push([surf(q,0,v),surf(q,1,v)])}}
      if(segs.length)f.IS.push({d,ch:chainSegs(segs,0.3)})}
    const dir=(f.id%2)?1:-1;
    const PI=[],U0=[],V=[],SP=[],PH=[],FL=[],BA=[],RK=[];
    f.Q.forEach((q,pi)=>{
      const len=Math.hypot(q[1][0]-q[0][0],q[1][1]-q[0][1]),run=Math.hypot(q[3][0]-q[0][0],q[3][1]-q[0][1]),wid=Math.hypot(run,q[3][2]-q[0][2]);
      let n=Math.round(len*wid*dens);n=Math.max(f.i?2:5,Math.min(700,n));
      for(let k=0;k<n;k++){const v=Math.pow(r(),2.0);PI.push(pi);U0.push(r());V.push(v);SP.push(dir*(0.8+1.6*r())/Math.max(len,4));PH.push(r()*6.283);FL.push(0.5+1.1*r());BA.push((0.6+0.4*f.br)*(1-0.5*v)*(f.i?0.7:1));RK.push(k/n)}
    });
    f.PA={n:PI.length,PI:Uint16Array.from(PI),U0:Float32Array.from(U0),V:Float32Array.from(V),SP:Float32Array.from(SP),PH:Float32Array.from(PH),FL:Float32Array.from(FL),BA:Float32Array.from(BA),RK:Float32Array.from(RK)};
  }else if(f.ct){
    // assumed source zone on the plate interface (Cabinet Office model via J-SHIS): depth contours + particles on the cells;
    // the shallowest contour is drawn on the surface (z=0) as the trench-axis line
    const km=ch=>ch.map(c=>c.map(p=>[(p[0]-136)*KX,(p[1]-35)*KY]));
    f.IS=[];f.TR=[];
    f.ct.forEach((L,k)=>{const ch=km(L.ch);
      if(k===0)f.TR=mergeChains(ch.map(c=>c.map(p=>[p[0],p[1],0])),12);
      else f.IS.push({d:L.d,ch:ch.map(c=>c.map(p=>[p[0],p[1],L.d]))});});
    const PX=[],PY=[],PZ=[],PH=[],FL=[],BA=[],RK=[];
    const pc=Math.max(1,Math.round(1.6*(0.3+f.br*1.3)));
    f.P.forEach(p=>{for(let k=0;k<pc;k++){PX.push(p[0]+(r()-0.5)*16);PY.push(p[1]+(r()-0.5)*14);PZ.push(p[2]);PH.push(r()*6.283);FL.push(0.5+1.1*r());BA.push((0.6+0.4*f.br)*(1-Math.min(0.5,p[2]/110)));RK.push(r())}});
    f.PL={n:PX.length,X:Float32Array.from(PX),Y:Float32Array.from(PY),Z:Float32Array.from(PZ),PH:Float32Array.from(PH),FL:Float32Array.from(FL),BA:Float32Array.from(BA),RK:Float32Array.from(RK)};
  }
});
function smoothPath(P){
  ctx.moveTo(P[0][0],P[0][1]);
  if(P.length===2){ctx.lineTo(P[1][0],P[1][1]);return}
  ctx.lineTo((P[0][0]+P[1][0])/2,(P[0][1]+P[1][1])/2);
  for(let i=1;i<P.length-1;i++){ctx.quadraticCurveTo(P[i][0],P[i][1],(P[i][0]+P[i+1][0])/2,(P[i][1]+P[i+1][1])/2)}
  ctx.lineTo(P[P.length-1][0],P[P.length-1][1]);
}
function strokeChains(chs,o){ctx.beginPath();for(const c of chs){if(c.length<2)continue;smoothPath(c.map(p=>proj(p[0],p[1],p[2],o)))}ctx.stroke()}
function drawFault(f,k,o,sel,tt,hi){
  hi=Math.max(hi||0,sel?1:0);
  const dim=f.i?0.55:1;
  const base=COL[f.t];
  const rgb=[0,1,2].map(i=>Math.round(base[i]+(GOLD[i]-base[i])*hi)).join(',');
  const kb=Math.min(1.8,k*dim);
  const a=Math.min(1,Math.max(kb*(0.3+0.7*f.br),0.95*hi));
  const lw=(VIDEO?4.2:3.4)*(1+0.55*hi);
  ctx.lineCap='round';ctx.lineJoin='round';
  if(f.IS&&f.IS.length){ctx.lineWidth=1.0+0.6*hi;ctx.strokeStyle=`rgba(${rgb},${Math.min(1,0.26*a*(f.i?0.7:1)*(1+hi))})`;ctx.setLineDash(f.i?[4,6]:[]);for(const L of f.IS)strokeChains(L.ch,o);}
  const s=Math.min(4.6,Math.max(2.6,2.3+o.sc*0.9))*(1+0.3*hi);
  const frac=0.42+0.58*hi;
  ctx.fillStyle=`rgb(${rgb})`;
  const ca=Math.cos(o.az),sa=Math.sin(o.az),se=Math.sin(o.el),ce=Math.cos(o.el),W2=W/2+o.px,H2=H*0.52+o.py,sc=o.sc,mz=o.mult*ce;
  if(f.PA){
    const PA=f.PA,Q=f.Q;
    for(let i=0;i<PA.n;i++){
      if(PA.RK[i]>frac)continue;
      let u=(PA.U0[i]+PA.SP[i]*tt)%1;if(u<0)u+=1;
      const fade=Math.sin(3.14159*u);const al=PA.BA[i]*(0.35+0.65*fade)*(0.6+0.4*Math.sin(tt*PA.FL[i]+PA.PH[i]))*Math.min(1.2,kb)*(1+0.6*hi);
      if(al<0.07)continue;
      const q=Q[PA.PI[i]],v=PA.V[i];
      const tx=q[0][0]+(q[1][0]-q[0][0])*u,ty=q[0][1]+(q[1][1]-q[0][1])*u,tz=q[0][2]+(q[1][2]-q[0][2])*u;
      const bx=q[3][0]+(q[2][0]-q[3][0])*u,by=q[3][1]+(q[2][1]-q[3][1])*u,bz=q[3][2]+(q[2][2]-q[3][2])*u;
      const x=tx+(bx-tx)*v,y=ty+(by-ty)*v,z=tz+(bz-tz)*v;
      const dx=x-o.x,dy=y-o.y,x1=dx*ca+dy*sa,y1=-dx*sa+dy*ca;
      ctx.globalAlpha=al>1?1:al;
      ctx.fillRect(W2+sc*x1-s/2,H2+sc*(-y1*se+z*mz)-s/2,s,s);
    }
  }else if(f.PL){
    const PL=f.PL;
    for(let i=0;i<PL.n;i++){
      if(PL.RK[i]>frac)continue;
      const al=PL.BA[i]*(0.55+0.45*Math.sin(tt*PL.FL[i]+PL.PH[i]))*Math.min(1.2,kb)*(1+0.6*hi);
      if(al<0.07)continue;
      const dx=PL.X[i]-o.x,dy=PL.Y[i]-o.y,x1=dx*ca+dy*sa,y1=-dx*sa+dy*ca;
      ctx.globalAlpha=al>1?1:al;
      ctx.fillRect(W2+sc*x1-s/2,H2+sc*(-y1*se+PL.Z[i]*mz)-s/2,s,s);
    }
  }
  ctx.globalAlpha=1;
  ctx.setLineDash([]);
  const dk=Math.min(1,kb),gl=1-0.55*hi;
  ctx.lineWidth=lw*3.2;ctx.strokeStyle=`rgba(${rgb},${Math.min(0.5,0.12*a*(1+1.2*hi))*dk*gl})`;strokeChains(f.TR,o);
  ctx.lineWidth=lw*1.7;ctx.strokeStyle=`rgba(${rgb},${Math.min(0.7,0.2*a*(1+hi))*dk*gl})`;strokeChains(f.TR,o);
  if(f.i)ctx.setLineDash([10,9]);
  ctx.lineWidth=lw;ctx.strokeStyle=`rgba(${rgb},${Math.min(hi>0?0.88:1,0.35+0.75*a)*dk})`;strokeChains(f.TR,o);
  ctx.setLineDash([]);
}
// ---- plate mesh: reused unchanged from the artifact "日本の地震の光" (Iwasaki et al. 2015 PAC/PHS depth grids, 0.5 deg grid, same colors/alpha/width)
function plateSegs(Z){const gl=D.plate.glon,ga=D.plate.glat,out=[];const nl=gl.length,na=ga.length;
 for(let j=0;j<na;j+=2){for(let i=0;i<nl-1;i++){const a=Z[j][i],b=Z[j][i+1];if(a!=null&&b!=null)out.push([gl[i],ga[j],a,gl[i+1],ga[j],b])}}
 for(let i=0;i<nl;i+=2){for(let j=0;j<na-1;j++){const a=Z[j][i],b=Z[j+1][i];if(a!=null&&b!=null)out.push([gl[i],ga[j],a,gl[i],ga[j+1],b])}}
 return out.map(s=>[(s[0]-136)*KX,(s[1]-35)*KY,s[2],(s[3]-136)*KX,(s[4]-35)*KY,s[5]])}
const MESH={};for(const key of ['PAC','PHS']){const bands=[[],[],[],[],[],[]];for(const s of plateSegs(D.plate[key]))bands[Math.min(5,Math.floor((s[2]+s[5])/2/120))].push(s);MESH[key]=bands}
const MK={PAC:1,PHS:1};
// Izu-Ogasawara trench side: seaward edge of the Iwasaki PAC grid (no J-SHIS source zone there), drawn on the surface
const IZU=(()=>{const gl=D.plate.glon,ga=D.plate.glat,pts=[];for(let j=0;j<ga.length;j++){if(ga[j]>34.5||ga[j]<29.5)continue;const row=D.plate.PAC[j];let e=-1;for(let i=0;i<gl.length;i++)if(row[i]!=null&&row[i]<40&&gl[i]>=139.5)e=i;if(e>=0)pts.push([(gl[e]-136)*KX,(ga[j]-35)*KY,0])}return pts})();
function drawMesh(o){
  if(!S.show.plate)return;
  let u=W/1920;if(W<820)u=Math.max(u,.5);
  ctx.lineWidth=Math.max(1.2,1.5*u);ctx.lineCap='butt';ctx.setLineDash([]);
  for(const [key,rgb,al] of [['PAC','140,190,255',.85],['PHS','130,250,225',.85]]){
    MESH[key].forEach((arr,bi)=>{if(!arr.length)return;ctx.beginPath();for(const s of arr){const a=proj(s[0],s[1],s[2],o),b=proj(s[3],s[4],s[5],o);ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1])}ctx.strokeStyle=`rgba(${rgb},${al*(1-bi*0.09)*MK[key]})`;ctx.stroke()});
  }
  if(IZU.length>1){ctx.lineCap='round';ctx.lineJoin='round';ctx.lineWidth=2.6;ctx.strokeStyle=`rgba(255,240,200,${0.9*MK.PAC})`;strokeChains([IZU],o);}
}
