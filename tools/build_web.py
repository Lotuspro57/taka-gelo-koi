#!/usr/bin/env python3
"""Bundles web/index.html + fonts + logo into ONE self-contained file:
   app/src/main/assets/index.html   (this is what the Android app loads, and
   also the file you pick in  Settings -> "আপডেট ফাইল বেছে নিন"  to update a phone
   without rebuilding the APK).

Run:  python3 tools/build_web.py
"""
import base64, pathlib, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
WEB = ROOT / "web"
OUT = ROOT / "app/src/main/assets/index.html"


def b64(path, mime):
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


html = (WEB / "index.html").read_text(encoding="utf-8")
html = re.sub(r"url\((fonts/[^)]+\.woff2)\)", lambda m: "url(" + b64(WEB / m.group(1), "font/woff2") + ")", html)
html = html.replace('src="logo.png"', 'src="' + b64(WEB / "logo.png", "image/png") + '"')
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(html, encoding="utf-8")
print(f"built {OUT.relative_to(ROOT)}  ({OUT.stat().st_size/1024:.0f} KB)")
