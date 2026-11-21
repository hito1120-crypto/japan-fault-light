import json,urllib.request,csv
rows=[]
for y in range(1998,2027):
    for h in ((f"{y}-01-01",f"{y}-07-01"),(f"{y}-07-01",f"{y+1}-01-01")):
        u=f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&starttime={h[0]}&endtime={h[1]}&minmagnitude=4.5&minlatitude=24&maxlatitude=46&minlongitude=122&maxlongitude=148&orderby=time-asc"
        t=urllib.request.urlopen(u,timeout=90).read().decode()
        r=list(csv.DictReader(t.splitlines()))
        rows+= [(x['time'],float(x['latitude']),float(x['longitude']),float(x['depth'] or 0),float(x['mag'])) for x in r]
rows.sort()
json.dump(rows,open('data/raw/usgs_m45.json','w'))
print(len(rows))
