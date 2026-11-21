import os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..'))
s=open('scripts/build_html.py',encoding='utf8').read()
old="""    if g['type']=='MultiPoint':
        o['pts']=[[round(a,2),round(b,2),round(c,0)] for a,b,c in g['coordinates']]"""
new="""    if g['type']=='MultiPoint':
        code=p['source'].split()[2]
        cells,cont=plate_grid(code)
        o['pts']=cells;o['ct']=cont"""
assert old in s
s=s.replace(old,new)
helper='''
import numpy as np,contourpy
def plate_grid(code,st=0.15):
    # Cabinet Office (via J-SHIS) assumed-source-zone interface points -> 0.15deg depth grid -> depth contours (no interpolation outside data)
    d=json.load(open('data/raw/flt/%s.json'%code,encoding='utf8'))
    pts=np.vstack([np.array(f['geometry']['coordinates']) for f in d['features']])
    x0,y0=pts[:,0].min(),pts[:,1].min()
    ix=np.floor((pts[:,0]-x0)/st).astype(int);iy=np.floor((pts[:,1]-y0)/st).astype(int)
    nx,ny=ix.max()+1,iy.max()+1
    S=np.zeros((ny,nx));N=np.zeros((ny,nx));np.add.at(S,(iy,ix),pts[:,2]);np.add.at(N,(iy,ix),1)
    Z=np.where(N>0,S/np.maximum(N,1),np.nan)
    xs=x0+(np.arange(nx)+0.5)*st;ys=y0+(np.arange(ny)+0.5)*st
    cells=[[round(float(xs[i]),3),round(float(ys[j]),3),round(float(Z[j,i]),1)] for j in range(ny) for i in range(nx) if N[j,i]>0]
    zm=np.ma.masked_invalid(Z);gen=contourpy.contour_generator(xs,ys,zm)
    cont=[]
    lo,hi=np.nanmin(Z),np.nanmax(Z)
    for lev in range(5,int(hi)+1,5):
        if lev<=lo:continue
        ls=gen.lines(lev)
        ch=[[[round(float(a),3),round(float(b),3)] for a,b in l] for l in ls if len(l)>=3]
        if ch:cont.append(dict(d=lev,ch=ch))
    return cells,cont
'''
s=s.replace("faults=[]\nfor f in F:",helper+"faults=[]\nfor f in F:",1)
# drop the plate-mesh payload from the page
s=s.replace("data=dict(faults=faults,coast=rings,borders=borders,ev=ev,plate=plate)","data=dict(faults=faults,coast=rings,borders=borders,ev=ev)")
open('scripts/build_html.py','w',encoding='utf8').write(s)
print('ok')
