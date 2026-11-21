// ---- fault light: smooth traces + depth contours + particle layer
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
function lerp3(a,b,t){return [a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t,a[2]+(b[2]-a[2])*t]}
function surf(q,u,v){return lerp3(lerp3(q[0],q[1],u),lerp3(q[3],q[2],u),v)}
function rng(seed){let s=(seed*2654435761)>>>0||1;return()=>{s^=s<<13;s>>>=0;s^=s>>>17;s^=s<<5;s>>>=0;return s/4294967296}}
F.forEach(f=>{
  if(!f.Q)return;
  const r=rng(f.id+101);
  const top=Math.min(...f.Q.map(q=>q[0][2])),bot=Math.max(...f.Q.map(q=>q[2][2]));
  f.TR=chainSegs(f.Q.filter(q=>q[0][2]<=top+0.01).map(q=>[q[0],q[1]]),0.3);
  f.IS=[];
  const ds=[];for(let d=5;d<bot-0.4;d+=5)if(d>top+0.4)ds.push(d);if(bot>top+0.4)ds.push(bot);
  for(const d of ds){const segs=[];for(const q of f.Q){if(d>q[0][2]-0.01&&d<=q[2][2]+0.01&&q[2][2]>q[0][2]+0.2){const v=(d-q[0][2])/(q[2][2]-q[0][2]);segs.push([surf(q,0,v),surf(q,1,v)])}}
    if(segs.length)f.IS.push({d,ch:chainSegs(segs,0.3)})}
  const dens=0.22*(0.3+f.br*1.3)*(f.i?0.4:1),dir=(f.id%2)?1:-1;
  const PI=[],U0=[],V=[],SP=[],PH=[],FL=[],BA=[];
  f.Q.forEach((q,pi)=>{
    const len=Math.hypot(q[1][0]-q[0][0],q[1][1]-q[0][1]),run=Math.hypot(q[3][0]-q[0][0],q[3][1]-q[0][1]),wid=Math.hypot(run,q[3][2]-q[0][2]);
    let n=Math.round(len*wid*dens);n=Math.max(f.i?2:4,Math.min(900,n));
    for(let k=0;k<n;k++){const v=Math.pow(r(),1.7);PI.push(pi);U0.push(r());V.push(v);SP.push(dir*(0.8+1.6*r())/Math.max(len,4));PH.push(r()*6.283);FL.push(0.5+1.1*r());BA.push((0.5+0.5*f.br)*(1-0.55*v)*(f.i?0.7:1))}
  });
  f.PA={n:PI.length,PI:Uint16Array.from(PI),U0:Float32Array.from(U0),V:Float32Array.from(V),SP:Float32Array.from(SP),PH:Float32Array.from(PH),FL:Float32Array.from(FL),BA:Float32Array.from(BA)};
});
function smoothPath(P){
  ctx.moveTo(P[0][0],P[0][1]);
  if(P.length===2){ctx.lineTo(P[1][0],P[1][1]);return}
  ctx.lineTo((P[0][0]+P[1][0])/2,(P[0][1]+P[1][1])/2);
  for(let i=1;i<P.length-1;i++){ctx.quadraticCurveTo(P[i][0],P[i][1],(P[i][0]+P[i+1][0])/2,(P[i][1]+P[i+1][1])/2)}
  ctx.lineTo(P[P.length-1][0],P[P.length-1][1]);
}
function strokeChains(chs,o){ctx.beginPath();for(const c of chs){smoothPath(c.map(p=>proj(p[0],p[1],p[2],o)))}ctx.stroke()}
function drawFault(f,k,o,sel,tt){
  if(f.P)return;
  const dim=f.i?0.55:1,rgb=COL[f.t].join(',');
  const kb=Math.min(1.6,k*dim),a=Math.min(1,kb*(0.28+0.72*f.br))*(sel?1.5:1);
  ctx.lineCap='round';ctx.lineJoin='round';
  ctx.lineWidth=0.8;ctx.strokeStyle=`rgba(${rgb},${Math.min(1,0.2*a*(f.i?0.7:1))})`;ctx.setLineDash(f.i?[3,5]:[]);
  for(const L of f.IS){strokeChains(L.ch,o)}
  const ca=Math.cos(o.az),sa=Math.sin(o.az),se=Math.sin(o.el),ce=Math.cos(o.el),W2=W/2+o.px,H2=H*0.52+o.py,sc=o.sc,mz=o.mult*ce;
  const s=Math.min(2.6,Math.max(1.1,0.7+sc*1.3)),PA=f.PA,Q=f.Q;
  ctx.fillStyle=`rgb(${rgb})`;
  for(let i=0;i<PA.n;i++){
    let u=(PA.U0[i]+PA.SP[i]*tt)%1;if(u<0)u+=1;
    const fade=Math.sin(3.14159*u);const al=PA.BA[i]*fade*(0.5+0.5*Math.sin(tt*PA.FL[i]+PA.PH[i]))*kb*(sel?1.6:1);
    if(al<0.025)continue;
    const q=Q[PA.PI[i]],v=PA.V[i];
    const tx=q[0][0]+(q[1][0]-q[0][0])*u,ty=q[0][1]+(q[1][1]-q[0][1])*u,tz=q[0][2]+(q[1][2]-q[0][2])*u;
    const bx=q[3][0]+(q[2][0]-q[3][0])*u,by=q[3][1]+(q[2][1]-q[3][1])*u,bz=q[3][2]+(q[2][2]-q[3][2])*u;
    const x=tx+(bx-tx)*v,y=ty+(by-ty)*v,z=tz+(bz-tz)*v;
    const dx=x-o.x,dy=y-o.y,x1=dx*ca+dy*sa,y1=-dx*sa+dy*ca;
    ctx.globalAlpha=al>1?1:al;
    ctx.fillRect(W2+sc*x1-s/2,H2+sc*(-y1*se+z*mz)-s/2,s,s);
  }
  ctx.globalAlpha=1;
  ctx.setLineDash([]);ctx.lineWidth=(VIDEO?5:4)+(sel?3:0);ctx.strokeStyle=`rgba(${rgb},${0.14*a})`;strokeChains(f.TR,o);
  if(f.i)ctx.setLineDash([4,6]);
  ctx.lineWidth=(VIDEO?1.5:1.2)+(sel?1:0);ctx.strokeStyle=`rgba(${rgb},${Math.min(1,0.25+0.85*a)})`;strokeChains(f.TR,o);
  ctx.setLineDash([]);
}
// ---- plate mesh: reused unchanged from the artifact "日本の地震の光" (Iwasaki et al. 2015 PAC/PHS depth grids, 0.5 deg grid, same colors/alpha/width)
function plateSegs(Z){const gl=D.plate.glon,ga=D.plate.glat,out=[];const nl=gl.length,na=ga.length;
 for(let j=0;j<na;j+=2){for(let i=0;i<nl-1;i++){const a=Z[j][i],b=Z[j][i+1];if(a!=null&&b!=null)out.push([gl[i],ga[j],a,gl[i+1],ga[j],b])}}
 for(let i=0;i<nl;i+=2){for(let j=0;j<na-1;j++){const a=Z[j][i],b=Z[j+1][i];if(a!=null&&b!=null)out.push([gl[i],ga[j],a,gl[i],ga[j+1],b])}}
 return out.map(s=>[(s[0]-136)*KX,(s[1]-35)*KY,s[2],(s[3]-136)*KX,(s[4]-35)*KY,s[5]])}
const MESH={};for(const key of ['PAC','PHS']){const bands=[[],[],[],[],[],[]];for(const s of plateSegs(D.plate[key]))bands[Math.min(5,Math.floor((s[2]+s[5])/2/120))].push(s);MESH[key]=bands}
const MK={PAC:1,PHS:1};
function drawMesh(o){
  if(!S.show.plate)return;
  let u=W/1920;if(W<820)u=Math.max(u,.5);
  ctx.lineWidth=Math.max(1.2,1.5*u);ctx.lineCap='butt';ctx.setLineDash([]);
  for(const [key,rgb,al] of [['PAC','140,190,255',.85],['PHS','130,250,225',.85]]){
    MESH[key].forEach((arr,bi)=>{if(!arr.length)return;ctx.beginPath();for(const s of arr){const a=proj(s[0],s[1],s[2],o),b=proj(s[3],s[4],s[5],o);ctx.moveTo(a[0],a[1]);ctx.lineTo(b[0],b[1])}ctx.strokeStyle=`rgba(${rgb},${al*(1-bi*0.09)*MK[key]})`;ctx.stroke()});
  }
}
