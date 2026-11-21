import json,math,datetime,os
from shapely.geometry import shape,box
from shapely.ops import unary_union
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
F=json.load(open('data/faults.geojson',encoding='utf8'))['features']
ne=json.load(open('data/raw/ne_50m_land.geojson',encoding='utf8'))
bb=box(118,22,156,52)
rings=[]
for f in ne['features']:
    g=shape(f['geometry'])
    gs=g.geoms if hasattr(g,'geoms') else [g]
    for p in gs:
        if not p.intersects(bb): continue
        p=p.simplify(0.01 if p.area<50 else 0.08)
        rings.append([[round(x,2),round(y,2)] for x,y in p.exterior.coords])
faults=[]
for f in F:
    p=f['properties'];g=f['geometry']
    o=dict(n=p['name'],t=p['type'],L=p['length_km'],d=p['dip'],a=p['top_km'],b=p['bottom_km'],M=p['M'],p=p['p30'],e=p['last_event'],i=1 if p['interpolated'] else 0,s=p['source'])
    if p.get('note'):o['no']=p['note']
    if p.get('jshis_assumed'):o['ja']=p['jshis_assumed']
    if g['type']=='MultiPoint':
        o['pts']=[[round(a,2),round(b,2),round(c,0)] for a,b,c in g['coordinates']]
    else:
        o['q']=[[[round(x,2),round(y,2),round(z,0)] for x,y,z in poly[0][:4]] for poly in g['coordinates']]
    faults.append(o)
cat=json.load(open('data/raw/usgs_m45.json'))
t0=datetime.datetime(1998,1,1)
ev=[]
for t,la,lo,de,m in cat:
    if lo<126 or de>100 or lo>148.5 or la<30: continue
    d=datetime.datetime.strptime(t[:19],'%Y-%m-%dT%H:%M:%S')
    ev.append([round((d-t0).total_seconds()/86400),round(lo*100),round(la*100),round(de),round(m*10)])
ev.sort()
data=dict(faults=faults,coast=rings,ev=ev)
js=json.dumps(data,ensure_ascii=False,separators=(',',':'))
tpl=open('template.html',encoding='utf8').read()
os.makedirs('site',exist_ok=True)
open('site/index.html','w',encoding='utf8').write(tpl.replace('/*__DATA__*/null',js))
print(len(js)//1024,'KB data',len(faults),'faults',len(ev),'events',len(rings),'coast rings')
