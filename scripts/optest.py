import json
from playwright.sync_api import sync_playwright
U='https://hito1120-crypto.github.io/japan-fault-light/'
FN="(lon,lat)=>{const S=__lab.S,KX=111*Math.cos(35*Math.PI/180),KY=111;const x=(lon-136)*KX,y=(lat-35)*KY,dx=x-S.x,dy=y-S.y,c=Math.cos(S.az),s=Math.sin(S.az);const x1=dx*c+dy*s,y1=-dx*s+dy*c;return [innerWidth/2+S.px+S.sc*x1,innerHeight*0.52+S.py+S.sc*(-y1*Math.sin(S.el))]}"
def pos(pg,lon,lat): return pg.evaluate(f"({FN})({lon},{lat})")
def st(pg): return pg.evaluate("({az:__lab.S.az,el:__lab.S.el,px:__lab.S.px,py:__lab.S.py,sc:__lab.S.sc,view:__lab.S.view})")
with sync_playwright() as p:
    b=p.chromium.launch()
    # ---- PC
    pg=b.new_page(viewport={'width':1280,'height':800});errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto(U);pg.wait_for_timeout(5000)
    s0=st(pg);south=pos(pg,131,32);north=pos(pg,141,43)
    pg.mouse.move(640,400);pg.mouse.down();pg.mouse.move(740,400,steps=8);pg.mouse.up();pg.wait_for_timeout(200)
    s1=st(pg);south1=pos(pg,131,32);north1=pos(pg,141,43)
    print('PC rotate: drag right 100px -> south pt dx',round(south1[0]-south[0]),'north pt dx',round(north1[0]-north[0]),'az',round(s0['az'],3),'->',round(s1['az'],3))
    e0=s1['el'];pg.mouse.move(640,400);pg.mouse.down();pg.mouse.move(640,460,steps=6);pg.mouse.up();s2=st(pg)
    print('PC vertical: drag down 60px -> el',round(e0,3),'->',round(s2['el'],3))
    pg.mouse.move(640,400);pg.mouse.down(button='right');pg.mouse.move(540,350,steps=6);pg.mouse.up(button='right');s3=st(pg)
    print('PC right-drag pan: px,py',round(s2['px']),round(s2['py']),'->',round(s3['px']),round(s3['py']))
    pg.keyboard.down('Shift');pg.mouse.move(640,400);pg.mouse.down();pg.mouse.move(700,430,steps=6);pg.mouse.up();pg.keyboard.up('Shift');s4=st(pg)
    print('PC shift-drag pan: px,py ->',round(s4['px']),round(s4['py']),'az unchanged',round(s4['az'],3)==round(s3['az'],3))
    pg.mouse.move(640,400);pg.mouse.wheel(0,-400);pg.wait_for_timeout(200);s5=st(pg);print('PC wheel zoom in: sc',round(s4['sc'],3),'->',round(s5['sc'],3))
    pg.click('#reset');pg.wait_for_timeout(300);s6=st(pg);print('PC reset:',{k:round(v,3) if isinstance(v,float) else v for k,v in s6.items()},'initial',{k:round(v,3) if isinstance(v,float) else v for k,v in s0.items()})
    pg.screenshot(path='scratch/op_pc.png');print('PC errs',errs)
    # ---- mobile
    ctx=b.new_context(viewport={'width':390,'height':780},is_mobile=True,has_touch=True);m=ctx.new_page();errs=[];m.on('pageerror',lambda e:errs.append(str(e)))
    m.goto(U);m.wait_for_timeout(5000);cdp=ctx.new_cdp_session(m)
    def touch(typ,pts): cdp.send('Input.dispatchTouchEvent',{'type':typ,'touchPoints':[{'x':x,'y':y,'id':i} for i,(x,y) in enumerate(pts)]})
    m0=st(m);ms=pos(m,131,32)
    touch('touchStart',[(150,400)]);
    for k in range(1,9): touch('touchMove',[(150+k*12,400)])
    touch('touchEnd',[]);m.wait_for_timeout(200);m1=st(m);ms1=pos(m,131,32)
    print('mobile rotate: drag right ~96px -> south pt dx',round(ms1[0]-ms[0]),'az',round(m0['az'],3),'->',round(m1['az'],3))
    touch('touchStart',[(150,400),(250,400)])
    for k in range(1,9): touch('touchMove',[(150-k*8,400+k*6),(250-k*8,400+k*6)])
    touch('touchEnd',[]);m.wait_for_timeout(200);m2=st(m)
    print('mobile 2-finger pan: px,py',round(m1['px']),round(m1['py']),'->',round(m2['px']),round(m2['py']),'sc',round(m1['sc'],3),'->',round(m2['sc'],3),'az same',round(m2['az'],3)==round(m1['az'],3))
    touch('touchStart',[(150,400),(250,400)])
    for k in range(1,9): touch('touchMove',[(150-k*8,400),(250+k*8,400)])
    touch('touchEnd',[]);m.wait_for_timeout(200);m3=st(m);print('mobile pinch out: sc',round(m2['sc'],3),'->',round(m3['sc'],3))
    m.click('#reset');m.wait_for_timeout(300);m4=st(m);print('mobile reset sc',round(m4['sc'],3),'initial',round(m0['sc'],3),'px,py',round(m4['px']),round(m4['py']))
    m.screenshot(path='scratch/op_mob.png');print('mobile errs',errs)
    b.close()
