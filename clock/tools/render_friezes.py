#!/usr/bin/env python3
"""Render the nine friezes from the simulator's own pattern code (clock/index.html, PAT) as images
for the watch face: white on transparent, 480 x 480 (the Galaxy Watch Ultra's screen).

  frieze_<key>.png       what the face shows (pattern strength 0.7, as in the simulator); tinted on the watch
  frieze_<key>_mask.png  the same ornament at full strength: the mask that the seconds glow lights up

Needs Playwright with Chrome, and the repository served over HTTP:
  python3 -m http.server 8765   (from the repository root)
  python3 clock/tools/render_friezes.py
Run it again whenever a frieze changes in the simulator, then rebuild the watch face.
"""
import asyncio
import os
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'watchface', 'watchface', 'src', 'main', 'res', 'drawable-nodpi')
URL = 'http://localhost:8765/clock/index.html'
KEYS = ['laurel', 'meander', 'tesserae', 'knotwork', 'tracery', 'starchart', 'gears', 'blueprint', 'orbits']
FI, FO = 172, 186           # frieze inner and outer radius (simulator defaults)


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=os.environ.get('CHROME', '/usr/bin/google-chrome'))
        pg = await b.new_page()
        await pg.goto(URL)
        await pg.wait_for_timeout(1500)
        data = await pg.evaluate(
            "([keys,fi,fo])=>{const o={};for(const k of keys){const P=PAT[k](fi,fo);o[k]={ring:P.ring,field:k==='orbits'?P.field:''};}return o;}",
            [KEYS, FI, FO])
        p2 = await b.new_page(viewport={'width': 480, 'height': 480})
        os.makedirs(OUT, exist_ok=True)
        for k in KEYS:
            for mode in ('show', 'mask'):
                inner = data[k]['ring'] + (data[k]['field'] if mode == 'show' else '')
                style = '' if mode == 'show' else '<style>*{stroke-opacity:1!important;fill-opacity:1!important}</style>'
                op = '0.7' if mode == 'show' else '1'
                html = (f'<html><body style="margin:0;background:transparent">{style}'
                        f'<svg width="480" height="480" viewBox="0 0 450 450" style="color:#fff;display:block">'
                        f'<g opacity="{op}">{inner}</g></svg></body></html>')
                await p2.set_content(html)
                await p2.wait_for_timeout(100)
                name = f'frieze_{k}{"_mask" if mode == "mask" else ""}.png'
                await p2.screenshot(path=os.path.join(OUT, name), omit_background=True)
                print('wrote', name)
        await b.close()

asyncio.run(main())
