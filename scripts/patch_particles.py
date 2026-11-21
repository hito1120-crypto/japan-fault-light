import os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
s=open('scripts/build_html.py',encoding='utf8').read()
if 'plate_mesh.json' not in s:
    s=s.replace("data=dict(faults=faults,coast=rings,borders=borders,ev=ev)","""pm=json.load(open('data/raw/plate_mesh.json'))
plate=dict(glon=pm['glon'],glat=pm['glat'],PAC=[[None if v is None else round(v,1) for v in r] for r in pm['PAC']],PHS=[[None if v is None else round(v,1) for v in r] for r in pm['PHS']])
data=dict(faults=faults,coast=rings,borders=borders,ev=ev,plate=plate)""")
    open('scripts/build_html.py','w',encoding='utf8').write(s)

t=open('template.html',encoding='utf8').read()
def rep(a,b):
    global t
    assert a in t,a[:70]
    t=t.replace(a,b,1)
rep("--plate:#ff9a3c","--plate:#8cbeff")
rep("plate:[255,154,60]","plate:[140,190,255]")
rep('<i></i>プレート境界</button>','<i></i>プレート(格子)</button>')
rep("function frame(o,tt,env){\n  drawBase(o);","function frame(o,tt,env){\n  ctx.setTransform(DPR,0,0,DPR,0,0);\n  drawBase(o);")
a=t.index("function drawFault(f,k,o,sel){");b=t.index("function drawBase(o){")
t=t[:a]+open('scripts/newfault.js',encoding='utf8').read()+t[b:]
rep("  path(coast);ctx.strokeStyle='rgba(222,234,252,.88)'","  drawMesh(o);\n  path(coast);ctx.strokeStyle='rgba(222,234,252,.88)'")
rep("drawFault(f,k,o,S.sel===f);","drawFault(f,k,o,S.sel===f,tt);")
rep("if(f.P){for(const p of f.P){const q=proj(p[0],p[1],p[2],S);const d=Math.hypot(q[0]-mx,q[1]-my)+8;if(d<bd){bd=d;best=f;}}continue;}","if(f.P)continue;")
rep("想定の中で最も大きいパターンの断層面を点で表示しています(上端・下端は面の最も浅い/深い点)。","プレート境界は、日本の地震の光と同じ格子(岩崎ほか2015)で表示しています。ここでは想定地震の規模・確率だけを示します(上端・下端は想定断層面の最も浅い/深い点)。")
rep("  frame(cam,t,env);","  MK.PAC=1-0.5*any*(1-fw.nank);MK.PHS=(1+0.8*fw.nank)*(1-0.5*(any-fw.nank));\n  frame(cam,t,env);")
rep("震源: USGS ComCat。海岸線: Natural Earth。","プレート面: 岩崎ほか(2015)モデル(東京大学地震研究所)の格子。震源: USGS ComCat。海岸線・県境: Natural Earth。")
open('template.html','w',encoding='utf8').write(t)
print('patched')
