import os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
# ---- build_html: keep plate mesh payload
s=open('scripts/build_html.py',encoding='utf8').read()
if "ev=ev,plate=plate" not in s:
    s=s.replace("data=dict(faults=faults,coast=rings,borders=borders,ev=ev)","""pm=json.load(open('data/raw/plate_mesh.json'))
plate=dict(glon=pm['glon'],glat=pm['glat'],PAC=[[None if v is None else round(v,1) for v in r] for r in pm['PAC']],PHS=[[None if v is None else round(v,1) for v in r] for r in pm['PHS']])
data=dict(faults=faults,coast=rings,borders=borders,ev=ev,plate=plate)""")
    open('scripts/build_html.py','w',encoding='utf8').write(s)

t=open('template.html',encoding='utf8').read()
def rep(a,b):
    global t
    assert a in t,a[:80]
    t=t.replace(a,b,1)
# 1. replace drawing block
a=t.index("// ---- fault light");b=t.index("function drawBase(o){")
t=t[:a]+open('scripts/newfault2.js',encoding='utf8').read()+t[b:]
# colours / labels
rep("plate:[140,190,255]","plate:[255,154,60]")
rep("--plate:#8cbeff","--plate:#ff9a3c")
rep('<i></i>プレート(格子)</button>','<i></i>プレート・海溝型震源域</button>')
# frame: shared emphasis
rep("    if(env&&env.fk)k*=env.fk(f);\n    drawFault(f,k,o,S.sel===f,tt);","    let hi=0;\n    if(env&&env.fk){k*=env.fk(f);hi=env.hi(f);}else{const e=liveEmph(f);k*=e.k;hi=e.hi;}\n    drawFault(f,k,o,false,tt,hi);")
# live emphasis state + loop
rep("let anim=null;","let anim=null;\nS.selZone=null;S.selW=0;\nfunction liveEmph(f){const w=S.selW;if(!S.selZone||w<0.005)return {k:1,hi:0};const inF=S.selZone.includes(f)?w:0;return {k:emphK(inF,w),hi:inF};}\nfunction liveMesh(){const w=S.selW;MK.PAC=1;MK.PHS=1;if(!S.selZone||w<0.005)return;const nk=S.selZone.some(f=>f.n.includes('南海トラフ')),jt=S.selZone.some(f=>f.t==='plate'&&!f.n.includes('南海')&&!f.n.includes('相模'));if(nk){MK.PHS=1+0.8*w;MK.PAC=1-0.5*w}else if(jt){MK.PAC=1+0.8*w;MK.PHS=1-0.5*w}else{MK.PAC=1-0.5*w;MK.PHS=1-0.5*w}}")
rep("  const tt=(now-t0)/1000;","  const tt=(now-t0)/1000;\n  const tgt=S.sel?1:0;S.selW+=(tgt-S.selW)*0.18;if(!S.sel&&S.selW<0.01){S.selW=0;S.selZone=null}\n  liveMesh();")
# select
rep("function select(f,fly){S.sel=f;setP(f);document.getElementById('sel').value=f?f.id:'';if(f&&fly)flyTo([f]);}","function groupOf(f){const nm=f.n;const gs=[G.mtl,G.itg,G.noto,G.nank,G.jtr];for(const g of gs)if(g&&g.includes(f))return g;return [f];}\nfunction select(f,fly){S.sel=f;if(f)S.selZone=groupOf(f);setP(f);document.getElementById('sel').value=f?f.id:'';if(f&&fly)flyTo(S.selZone);}")
# hit-test for plates
rep("if(f.P)continue;","if(f.P){for(const p of f.P){const q=proj(p[0],p[1],p[2],S);const d=Math.hypot(q[0]-mx,q[1]-my)+8;if(d<bd){bd=d;best=f;}}continue;}")
# G groups / keys / captions
a=t.index("const G={");b=t.index("const CATA=")
newG='''const G={
  ov:null,
  mtl:grp(f=>f.n.includes('中央構造線')),
  itg:grp(f=>f.n.includes('糸魚川')),
  noto:grp(f=>f.n.includes('能登半島周辺海域')||f.n.includes('能登半島地震')||f.n.includes('邑知潟')),
  nank:grp(f=>f.n.includes('南海トラフ')),
  jtr:grp(f=>/宮城県沖|青森県東方沖|十勝沖|根室沖|千島海溝/.test(f.n))
};
const KEYS=[[0,'ov',-25,55],[4.0,'ov',0,55],[5.2,'mtl',10,52],[8.0,'mtl',20,50],[9.2,'itg',-20,54],[11.9,'itg',-10,52],[13.1,'noto',12,54],[15.8,'noto',22,52],[17.0,'nank',-12,56],[19.6,'nank',4,54],[20.8,'jtr',16,56],[23.4,'jtr',6,54],[25.0,'ov',0,56],[32,'ov',18,58]];
const maxM=g=>Math.max(...g.map(x=>x.M||0));
const maxP=g=>Math.max(...g.map(x=>x.p||0));
const CAPS=[
 {g:'mtl',a:5.0,b:8.4,n:'中央構造線断層帯',m:()=>maxM(G.mtl),p:()=>maxP(G.mtl),note:'(区間別の最大)'},
 {g:'itg',a:9.0,b:12.3,n:'糸魚川―静岡構造線断層帯',m:()=>7.0,p:()=>G.itg.find(f=>f.n.includes('中北部')&&!f.i).p,note:'(中北部)'},
 {g:'noto',a:12.9,b:16.2,n:'能登半島周辺の海域断層',m:()=>maxM(G.noto),p:()=>null,note:''},
 {g:'nank',a:16.8,b:20.0,n:'南海トラフ(想定震源域)',m:()=>maxM(G.nank),p:()=>G.nank[0].p,note:''},
 {g:'jtr',a:20.6,b:23.8,n:'日本海溝・千島海溝(想定震源域)',m:()=>maxM(G.jtr),p:()=>maxP(G.jtr),note:'(根室沖など最大)'}
];
'''
t=t[:a]+newG+t[b:]
rep("const CATA=24.0,CATB=30.8;","const CATA=24.2,CATB=30.8;")
# renderVideo emphasis
rep("    k*=(1+1.1*inF)*(1-0.72*any*(1-inF));\n    k*=1-0.35*catW;\n    return k;}};\n  MK.PAC=1-0.5*any*(1-fw.nank);MK.PHS=(1+0.8*fw.nank)*(1-0.5*(any-fw.nank));","    k*=emphK(inF,any);\n    k*=1-0.35*catW;\n    return k;},\n   hi:f=>{let inF=0;for(const c of CAPS){if(fw[c.g]>0&&G[c.g].includes(f))inF=Math.max(inF,fw[c.g]);}return inF;}};\n  MK.PAC=1-EMPH.dim*0.75*any*(1-Math.max(fw.jtr,0));MK.PHS=1-EMPH.dim*0.75*any*(1-fw.nank);\n  MK.PHS*=1+0.8*fw.nank/(1-EMPH.dim*0.75*any*(1-fw.nank)||1)*0+0;if(fw.jtr>0){MK.PAC=1+0.8*fw.jtr}if(fw.nank>0){MK.PHS=1+0.8*fw.nank}")
# captions in gold with M and probability
a=t.index("    const pv=c.pf?c.pf():null;");b=t.index("  { const cw=sm(29.6")
newcap='''    const pv=c.p(),mv=c.m();
    ctx.globalAlpha=w;ctx.textAlign='left';
    const x=64,y=H-120;
    const gr=ctx.createLinearGradient(0,H-260,0,H);gr.addColorStop(0,'rgba(3,5,10,0)');gr.addColorStop(1,'rgba(3,5,10,.72)');ctx.globalAlpha=w*.9;ctx.fillStyle=gr;ctx.fillRect(0,H-260,W*0.8,260);ctx.globalAlpha=w;
    ctx.fillStyle='#ffd36a';ctx.font='600 52px "Noto Sans JP","Yu Gothic UI",sans-serif';ctx.fillText(c.n,x,y);
    ctx.fillStyle='#ffe4a0';ctx.font='400 32px "Noto Sans JP","Yu Gothic UI",sans-serif';
    ctx.fillText('想定 M'+mv.toFixed(1)+'  /  '+(pv==null?'30年以内の発生確率は未公表':('30年以内 '+fmtP(pv)+c.note)),x,y+50);
    ctx.globalAlpha=1;
  }
'''
t=t[:a]+newcap+t[b:]
rep("/ プレート面: 岩崎ほか(2015) / USGS","/ プレート面: 岩崎ほか(2015)、想定震源域: 内閣府モデル(J-SHIS) / USGS")
rep("プレート面: 岩崎ほか(2015)モデル(東京大学地震研究所)の格子。震源: USGS ComCat。","プレート面の格子: 岩崎ほか(2015)モデル(東京大学地震研究所)。海溝型の想定震源域: 内閣府モデル(J-SHIS)の断層面を5kmごとの等深線と粒で表現(最浅の線が海溝軸の目安)。震源: USGS ComCat。")
open('template.html','w',encoding='utf8').write(t)
print('patched')
