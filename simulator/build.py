"""Wrap the simulator page (body content, as published to the claude.ai artifact) into an
installable page for GitHub Pages. Usage: python3 build.py <artifact_page.html> <version label>"""
import sys, datetime
src = open(sys.argv[1], encoding='utf-8').read()
label = sys.argv[2] if len(sys.argv) > 2 else datetime.date.today().isoformat()
if '<body' in src:  # a saved copy of the published artifact: keep only the body
    src = src[src.index('<body'):]; src = src[src.index('>') + 1:]
    src = src[:src.rindex('</body>')] if '</body>' in src else src
head = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<meta name="theme-color" content="#07080d">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Trip Sim">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" href="icon-192.png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<meta name="sim-version" content="{label}">
<style>html,body{{margin:0;background:#07080d}}*,*::before,*::after{{box-sizing:border-box}}</style>
</head>
<body>
"""
tail = f"""
<p style="max-width:1100px;margin:0 auto;padding:0 16px 32px;font:12px 'Space Mono',monospace;color:#8d93a8">Build {label}</p>
<script>if('serviceWorker' in navigator)addEventListener('load',()=>navigator.serviceWorker.register('sw.js'));</script>
</body>
</html>
"""
open('index.html', 'w', encoding='utf-8').write(head + src + tail)
print('index.html built,', label)
