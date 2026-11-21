import json,urllib.request,concurrent.futures as cf,os
codes=json.load(open('data/raw/codes.json',encoding='utf8'))
os.makedirs('data/raw/flt',exist_ok=True)
def get(c):
    p=f'data/raw/flt/{c}.json'
    if os.path.exists(p): return c,True
    for _ in range(3):
        try:
            t=urllib.request.urlopen(f"https://www.j-shis.bosai.go.jp/map/api/pshm/Y2024/AVR/{c}/fltinfo.geojson?epsg=4326",timeout=40).read()
            open(p,'wb').write(t);return c,True
        except Exception as e: pass
    return c,False
with cf.ThreadPoolExecutor(8) as ex: res=list(ex.map(get,codes))
print(sum(1 for _,o in res if o),len(res),[c for c,o in res if not o])
