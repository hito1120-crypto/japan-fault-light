import sys,asyncio
from playwright.sync_api import sync_playwright
mode=sys.argv[1]; out=sys.argv[2]
with sync_playwright() as p:
    b=p.chromium.launch()
    if mode=='video':
        pg=b.new_page(viewport={'width':1920,'height':1080})
        errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('console',lambda m:errs.append(m.text) if m.type=='error' else None)
        pg.goto('file:///'+sys.argv[3]+'?video=1');pg.wait_for_function('window.__lab&&window.__lab.ready')
        for t in sys.argv[4:]:
            pg.evaluate('t=>window.__lab.render(t)',float(t));pg.screenshot(path=f'{out}_{t}.png')
        print(errs)
    else:
        w,h=(390,780) if mode=='mobile' else (1280,800)
        pg=b.new_page(viewport={'width':w,'height':h},device_scale_factor=1)
        errs=[];pg.on('pageerror',lambda e:errs.append(str(e)));pg.on('console',lambda m:errs.append(m.text) if m.type=='error' else None)
        pg.goto('file:///'+sys.argv[3]);pg.wait_for_timeout(7000);pg.screenshot(path=out+'.png');print(errs)
    b.close()
