import sys,os,multiprocessing as mp
from playwright.sync_api import sync_playwright
ROOT='C:/Users/hito1/OneDrive/デスクトップ/claudecode/fault-light'
FPS=30;N=32*FPS
os.makedirs(ROOT+'/frames',exist_ok=True)
def work(ids):
    with sync_playwright() as p:
        b=p.chromium.launch();pg=b.new_page(viewport={'width':1920,'height':1080})
        pg.goto('file:///'+ROOT+'/site/index.html?video=1');pg.wait_for_function('window.__lab&&window.__lab.ready')
        for i in ids:
            pg.evaluate('t=>window.__lab.render(t)',i/FPS)
            pg.screenshot(path=f'{ROOT}/frames/f{i:04d}.jpg',type='jpeg',quality=92)
        b.close()
if __name__=='__main__':
    ids=list(range(int(sys.argv[1]) if len(sys.argv)>1 else 0,N))
    with mp.Pool(4) as pool: pool.map(work,[ids[k::4] for k in range(4)])
    print('done',len(os.listdir(ROOT+'/frames')))
