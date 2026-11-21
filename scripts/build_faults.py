import json,math,re,fitz,numpy as np,collections
from shapely.geometry import shape,Point
from shapely.ops import unary_union
from shapely.prepared import prep
R=111.0
codes=json.load(open('data/raw/codes.json',encoding='utf8'))
ne=json.load(open('data/raw/ne_50m_land.geojson',encoding='utf8'))
land=unary_union([shape(f['geometry']) for f in ne['features']]).buffer(0.04)
landp=prep(land)
def on_land(pts):
    return sum(landp.contains(Point(x,y)) for x,y in pts)/len(pts)
feats=[]
def mk(name,typ,length,dip,top,bot,M,p30,last,interp,geom,src,extra=None):
    p=dict(name=name,type=typ,length_km=round(length,1),dip=round(dip),top_km=round(top,1),bottom_km=round(bot,1),
           M=M,p30=p30,last_event=last,interpolated=interp,source=src)
    if extra:p.update(extra)
    feats.append(dict(type='Feature',properties=p,geometry=geom))
def fnum(x,d=None):
    try:return float(x)
    except Exception:return d
def last_ev(n):
    v=fnum(n)
    return None if v is None else "約{:,}年前".format(int(round(v)))
skip=0
for c,v in codes.items():
    d=json.load(open('data/raw/flt/%s.json'%c,encoding='utf8'));m=d['seisact_model'];fs=d['features']
    name=v[0].replace('－','―').replace('−','―')
    if c[0]=='A' and fs[0]['geometry']['type']=='MultiPoint':
        f=max(fs,key=lambda f:len(f['geometry']['coordinates']))
        pts=np.array(f['geometry']['coordinates'])
        key=np.round(pts[:,:2]/0.15).astype(int);_,idx=np.unique(key,axis=0,return_index=True)
        q=pts[np.sort(idx)]
        mu=abs(fnum(m['magu'],0))
        ext=(q[:,0].max()-q[:,0].min())*R*math.cos(math.radians(q[:,1].mean()))
        exn=(q[:,1].max()-q[:,1].min())*R
        mk(name,'plate',max(ext,exn),20,float(q[:,2].min()),float(q[:,2].max()),mu,fnum(m['t30p']),last_ev(m.get('newact')),False,
           dict(type='MultiPoint',coordinates=[[round(a,3),round(b,3),round(c_,1)] for a,b,c_ in q]),'J-SHIS Y2024 '+c+' ('+f['properties']['pattern_code']+')')
        continue
    if c[-1].isalpha() and c[0]!='A' and '同時' in name:
        skip+=1;continue
    polys=[];L=0;dips=[];tops=[];bots=[]
    for f in fs:
        p=f['properties'];co=f['geometry']['coordinates'][0]
        polys.append([[round(x,4),round(y,4),round(z,2)] for x,y,z in co])
        L+=fnum(p['len'],0);dips.append(fnum(p['dip'],60))
        z=[q[2] for q in co];tops.append(min(z));bots.append(max(z))
    top=min(tops);bot=max(bots);dip=float(np.mean([x if x<=90 else 180-x for x in dips]))
    topedge=[(q[0],q[1]) for pl in polys for q in pl if abs(q[2]-top)<0.01]
    typ='land' if on_land(topedge)>=0.5 else 'sea'
    interp=(c[0]=='G' and all(abs(x-90)<0.01 for x in dips))
    extra=None
    if interp:
        extra=dict(jshis_assumed=dict(dip=round(dip),top_km=round(top,1),bottom_km=round(bot,1)))
        wid=13/math.tan(math.radians(60))
        newp=[]
        for pl in polys:
            xs=[q for q in pl if abs(q[2]-top)<0.01];bs=[q for q in pl if abs(q[2]-bot)<0.01]
            A=xs[0];B=xs[1] if len(xs)>1 else xs[0]
            n=0
            if len(bs)>=2:
                shx=((bs[0][0]+bs[1][0])/2-(A[0]+B[0])/2)*R*math.cos(math.radians(A[1]));shy=((bs[0][1]+bs[1][1])/2-(A[1]+B[1])/2)*R
                n=math.hypot(shx,shy)
            if n<0.01:
                ex=(B[0]-A[0])*R*math.cos(math.radians(A[1]));ey=(B[1]-A[1])*R;l=math.hypot(ex,ey) or 1
                shx,shy=ey/l,-ex/l;n=1
            ux,uy=shx/n*wid,shy/n*wid
            dl=lambda q:[round(q[0]+ux/(R*math.cos(math.radians(q[1]))),4),round(q[1]+uy/R,4),15.0]
            newp.append([[A[0],A[1],2.0],[B[0],B[1],2.0],dl(B),dl(A),[A[0],A[1],2.0]])
        polys=newp;top,bot,dip=2.0,15.0,60.0
    mk(name,typ,L,dip,top,bot,abs(fnum(m['magu'],fnum(m['magl'],0))),fnum(m['t30p']),last_ev(m.get('newact')),interp,
       dict(type='MultiPolygon',coordinates=[[pl] for pl in polys]),'J-SHIS Y2024 '+c+(' (その他の活断層: J-SHIS固定仮定値を指示ルールで置換)' if interp else ''),extra)

# ---- MLIT japan sea tsunami fault models (F01-F60)
d=fitz.open('data/raw/mlit_Data_02.pdf')
cols=dict(mw=123,lat=149,lon=181,top=220,bot=248,st=277,dip=307,rk=334,len=363,wid=393,tot=427)
rows=[];labels=[];tot_vals={}
for pi in (22,23):
    W=d[pi].get_text('words')
    lat=[w for w in W if 140<w[0]<160 and re.fullmatch(r'\d\d\.\d{4}',w[4])]
    for w in sorted(lat,key=lambda w:w[1]):
        r={}
        for x in W:
            if abs(x[1]-w[1])<1.5:
                k=min([(abs(x[0]-cx),k) for k,cx in cols.items()])[1]
                r[k]=x[4]
        r['y']=w[1];r['page']=pi
        rows.append(r)
    for x in W:
        if re.fullmatch(r'F\d\d',x[4]) and x[0]<118: labels.append((pi,x[1],x[4]))
    tot_vals[pi]=[(x[1],x[4]) for x in W if 420<x[0]<435 and re.fullmatch(r'\d+',x[4])]
labels.sort()
def totfor(grp):
    pg=grp[0]['page'];ys=[g['y'] for g in grp]
    return [v for y,v in tot_vals[pg] if min(ys)-4<=y<=max(ys)+4]
groups=[];i=0
while i<len(rows):
    j=i;grp=[]
    while j<len(rows):
        grp.append(rows[j]);j+=1
        t=totfor(grp)
        if t and abs(sum(float(g['len']) for g in grp)-float(t[0]))<=1.0:break
    layers=[grp];n=len(grp)
    while j+n<=len(rows) and rows[j]['page']==grp[0]['page'] and all(abs(float(rows[j+k]['len'])-float(grp[k]['len']))<0.05 for k in range(n)) and not any(lp==rows[j]['page'] and rows[j]['y']-1.5<=ly<=rows[j+n-1]['y']+1.5 for lp,ly,_ in labels):
        layers.append(rows[j:j+n]);j+=n
    groups.append(layers);i=j
print('mlit groups',len(groups),'labels',len(labels))
for layers,lab in zip(groups,labels):
    pg=layers[0][0]['page'];W=d[pg].get_text('words')
    allys=[r['y'] for l in layers for r in l]
    mw=[float(a) for a in [x[4] for x in W if abs(x[0]-123)<8 and min(allys)-3<=x[1]<=max(allys)+3] if re.fullmatch(r'\d\.\d\d',a)]
    polys=[];L=sum(float(r['len']) for r in layers[0]);dips=[];tops=[];bots=[]
    for li,g in enumerate(layers):
        ys=[r['y'] for r in g]
        pk=lambda cx:[float(x[4]) for x in W if abs(x[0]-cx)<8 and min(ys)-3<=x[1]<=max(ys)+3]
        top=pk(220);bot=pk(248)
        top=top[0] if top else 2.0;bot=bot[0] if bot else 15.0
        tops.append(top);bots.append(bot)
        for r in g:
            la,lo=float(r['lat']),float(r['lon']);st=math.radians(float(r['st']));dp=float(r['dip']);ln=float(r['len'])
            cl=math.cos(math.radians(la))
            la2=la+math.cos(st)*ln/R;lo2=lo+math.sin(st)*ln/(R*cl)
            run=(bot-top)/math.tan(math.radians(dp))
            dx,dy=math.sin(st+math.pi/2)*run,math.cos(st+math.pi/2)*run
            dl=lambda a_,b_:[round(b_+dx/(R*cl),4),round(a_+dy/R,4),bot]
            polys.append([[[round(lo,4),round(la,4),top],[round(lo2,4),round(la2,4),top],dl(la2,lo2),dl(la,lo),[round(lo,4),round(la,4),top]]])
            if li==0:dips.append(dp)
    la0,lo0=float(layers[0][0]['lat']),float(layers[0][0]['lon'])
    region='能登半島周辺海域' if (36.8<la0<38.2 and 136.3<lo0<138.2) else '日本海'
    mk('%s 海域断層 %s'%(region,lab[2]),'sea',L,float(np.mean(dips)),min(tops),max(bots),mw[0] if mw else None,None,None,False,
       dict(type='MultiPolygon',coordinates=[[p] if False else p for p in polys]),'国土交通省 日本海における大規模地震に関する調査検討会 データ集② 表3.3/3.4 (矩形断層モデルのパラメータから幾何を再構成)',dict(note='発生確率は公表されていない'))
json.dump(dict(type='FeatureCollection',features=feats),open('data/faults.geojson','w',encoding='utf8'),ensure_ascii=False,separators=(',',':'))
print(len(feats),collections.Counter(f['properties']['type'] for f in feats),'skipped combined',skip,'interp',sum(f['properties']['interpolated'] for f in feats))
