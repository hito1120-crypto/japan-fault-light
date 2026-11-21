import sys
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b=p.chromium.launch();pg=b.new_page(viewport={'width':1280,'height':720})
    pg.goto('file:///C:/Users/hito1/OneDrive/デスクトップ/claudecode/fault-light/site/index.html?video=1');pg.wait_for_function('window.__lab&&window.__lab.ready')
    for name,lon,lat,sc in [('noto',137.0,37.2,2.8),('mtl',134.0,34.0,1.7),('itg',138.2,36.2,2.6),('nank',134,32.8,1.2)]:
        pg.evaluate(f'window.__lab.still({lon},{lat},{sc},1)');pg.screenshot(path=f'scratch/top_{name}.png')
    b.close()
