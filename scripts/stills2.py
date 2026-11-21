from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1280,'height':720})
    errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('file:///C:/Users/hito1/OneDrive/デスクトップ/claudecode/fault-light/site/index.html?video=1');pg.wait_for_function('window.__lab&&window.__lab.ready')
    print('particles',pg.evaluate('__lab.F.reduce((a,f)=>a+(f.PA?f.PA.n:0),0)'))
    for name,lon,lat,sc,az,el in [('itg3d',138.2,36.2,5.5,0.3,0.7),('mtl3d',134.0,34.0,3.6,0.2,0.75),('noto3d',137.0,37.3,6.0,0.3,0.7),('nank',134,32.8,1.3,0.0,0.9)]:
        pg.evaluate(f'window.__lab.still({lon},{lat},{sc},2,{az},{el})');pg.screenshot(path=f'scratch/s2_{name}.png')
    t0=pg.evaluate('performance.now()')
    for i in range(20): pg.evaluate('window.__lab.render(12.5)')
    print('ms/frame',(pg.evaluate('performance.now()')-t0)/20,errs)
    b.close()
