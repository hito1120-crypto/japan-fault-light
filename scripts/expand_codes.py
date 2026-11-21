import json,urllib.request,urllib.error,concurrent.futures as cf,os,itertools
codes=json.load(open('data/raw/codes.json',encoding='utf8'))
have=set(codes)
cand=set()
for c in have:
    if c[0] not in 'FG' or len(c)!=7: continue
    for d in '0123456789ABCDEF': cand.add(c[:-1]+d)
    for dd in range(1,20): cand.add(c[:-2]+'%02d'%dd)
cand-=have
print(len(cand),'candidates')
os.makedirs('data/raw/flt',exist_ok=True)
def get(c):
    for _ in range(2):
        try:
            t=urllib.request.urlopen("https://www.j-shis.bosai.go.jp/map/api/pshm/Y2024/AVR/%s/fltinfo.geojson?epsg=4326"%c,timeout=30).read()
            d=json.loads(t)
            if d.get('status')=='Success' and d.get('features'):
                return c,t,d
            return c,None,None
        except urllib.error.HTTPError: return c,None,None
        except Exception: pass
    return c,None,None
new={}
with cf.ThreadPoolExecutor(16) as ex:
    for c,t,d in ex.map(get,sorted(cand)):
        if t:
            open('data/raw/flt/%s.json'%c,'wb').write(t)
            m=d['seisact_model'];new[c]=[m['ltename'],'3',m.get('magu'),m.get('t30p')]
print(len(new),'new codes')
for c,v in new.items(): print(c,v[0])
codes.update(new)
json.dump(codes,open('data/raw/codes.json','w',encoding='utf8'),ensure_ascii=False)
