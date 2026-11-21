import json, urllib.request, concurrent.futures as cf, itertools, sys
B="https://www.j-shis.bosai.go.jp/map/api/fltsearch?position=%s,%s&epsg=4326&mode=%s&version=Y2024&case=AVR&period=P_T30&format=json"
pts=[(round(lo,2),round(la,2)) for lo in [128+0.3*i for i in range(0,62)] for la in [30+0.3*j for j in range(0,54)]]
codes={}
def get(a):
    lo,la,m=a
    for _ in range(3):
        try:
            d=json.load(urllib.request.urlopen(B%(lo,la,m),timeout=30));return d
        except Exception as e: err=e
    return None
def walk(f,out):
    out[f['ltecode']]=f['ltename']
    for p in f.get('Pattern',[]) or []: pass
jobs=[(lo,la,m) for lo,la in pts for m in ('C','S')]
ok=0
with cf.ThreadPoolExecutor(12) as ex:
    for d in ex.map(get,jobs):
        if not d: continue
        ok+=1
        for f in d.get('Fault',[]):
            codes[f['ltecode']]=(f['ltename'],f.get('eqcategory'),f.get('magnitude'),f.get('probability'))
print(ok,len(jobs),len(codes))
json.dump(codes,open('data/raw/codes.json','w'),ensure_ascii=False,indent=0)
