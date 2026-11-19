#!/usr/bin/env python3
"""Generates the app icon (design/icon.svg) and every Android launcher PNG.

Run:  python3 tools/make_icons.py
Needs: pip install playwright && playwright install chromium
The icon is a skeuomorphic leather wallet with notes slipping out and a gold
"?" coin  -  "টাকা গেল কই?" (where did the money go?).
"""
import base64
import pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
RES = ROOT / "app/src/main/res"
DESIGN = ROOT / "design"

FONT_B64 = base64.b64encode((ROOT / "web/fonts/hind-siliguri-bengali-700-normal.woff2").read_bytes()).decode()
DEFS = """
<defs>
  <style>@font-face{font-family:HindB;font-weight:700;src:url(data:font/woff2;base64,__FONT__) format("woff2");}</style>
  <radialGradient id="bg" cx="0.32" cy="0.22" r="1.05">
    <stop offset="0" stop-color="#3AA874"/><stop offset="0.55" stop-color="#1A6A45"/><stop offset="1" stop-color="#0D3B27"/>
  </radialGradient>
  <linearGradient id="leather" x1="0" y1="0" x2="0.15" y2="1">
    <stop offset="0" stop-color="#D08C4C"/><stop offset="0.5" stop-color="#9A5527"/><stop offset="1" stop-color="#5B2F14"/>
  </linearGradient>
  <linearGradient id="leatherDark" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#7B3F1B"/><stop offset="1" stop-color="#3F1D0A"/>
  </linearGradient>
  <linearGradient id="gold" x1="0.2" y1="0" x2="0.8" y2="1">
    <stop offset="0" stop-color="#FFE9A0"/><stop offset="0.5" stop-color="#F2B535"/><stop offset="1" stop-color="#B8780F"/>
  </linearGradient>
  <linearGradient id="paper" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="#F7FAEA"/><stop offset="1" stop-color="#C9DDB0"/>
  </linearGradient>
  <linearGradient id="sheen" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff" stop-opacity="0.38"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <filter id="sh" x="-20%" y="-20%" width="140%" height="150%">
    <feDropShadow dx="0" dy="10" stdDeviation="9" flood-color="#000" flood-opacity="0.42"/>
  </filter>
  <filter id="sh2" x="-30%" y="-30%" width="160%" height="170%">
    <feDropShadow dx="0" dy="6" stdDeviation="5" flood-color="#000" flood-opacity="0.38"/>
  </filter>
  <filter id="blur"><feGaussianBlur stdDeviation="9"/></filter>
</defs>
"""

CONTENT = """
<g>
  <ellipse cx="256" cy="430" rx="150" ry="15" fill="#000" opacity="0.32" filter="url(#blur)"/>
  <!-- back of wallet -->
  <rect x="96" y="200" width="320" height="200" rx="34" fill="url(#leatherDark)"/>
  <!-- notes sliding out -->
  <g filter="url(#sh2)">
    <g transform="rotate(-10 230 250)">
      <rect x="132" y="122" width="190" height="130" rx="13" fill="#B8D3A0" stroke="#3C7A52" stroke-width="4"/>
    </g>
    <g transform="rotate(6 250 250)">
      <rect x="160" y="106" width="196" height="140" rx="13" fill="url(#paper)" stroke="#2F6E48" stroke-width="4"/>
      <rect x="172" y="118" width="172" height="116" rx="8" fill="none" stroke="#5E9A74" stroke-width="3"/>
      <circle cx="258" cy="176" r="30" fill="none" stroke="#2F6E48" stroke-width="4"/>
      <text x="258" y="194" text-anchor="middle" font-family="HindB, sans-serif" font-weight="700" font-size="52" fill="#2F6E48">&#2547;</text>
    </g>
  </g>
  <!-- wallet front -->
  <g filter="url(#sh)">
    <rect x="96" y="236" width="320" height="172" rx="34" fill="url(#leather)"/>
  </g>
  <rect x="96" y="236" width="320" height="86" rx="34" fill="url(#sheen)"/>
  <rect x="112" y="252" width="288" height="140" rx="24" fill="none" stroke="#F6DDB0" stroke-opacity="0.8" stroke-width="3.5" stroke-dasharray="9 8"/>
  <!-- clasp tab -->
  <g filter="url(#sh2)">
    <rect x="322" y="292" width="102" height="66" rx="22" fill="url(#leatherDark)"/>
  </g>
  <rect x="330" y="300" width="86" height="50" rx="16" fill="none" stroke="#E3B97E" stroke-opacity="0.6" stroke-width="2.5" stroke-dasharray="7 6"/>
  <circle cx="360" cy="325" r="16" fill="url(#gold)" stroke="#8E5A08" stroke-width="2.5"/>
  <circle cx="355" cy="320" r="5" fill="#fff" opacity="0.65"/>
  <!-- gold coin with question mark -->
  <g filter="url(#sh2)">
    <circle cx="368" cy="146" r="60" fill="url(#gold)" stroke="#A86B0A" stroke-width="5"/>
  </g>
  <circle cx="368" cy="146" r="46" fill="none" stroke="#FFF0B8" stroke-opacity="0.8" stroke-width="3.5"/>
  <text x="368" y="173" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-weight="900" font-size="78" fill="#FFF3C4" opacity="0.7" transform="translate(0,2)">?</text>
  <text x="368" y="171" text-anchor="middle" font-family="Arial, Helvetica, sans-serif" font-weight="900" font-size="78" fill="#6E4105">?</text>
  <path d="M330 118a46 46 0 0 1 38-26" fill="none" stroke="#fff" stroke-opacity="0.7" stroke-width="5" stroke-linecap="round"/>
</g>
"""


DEFS = DEFS.replace("__FONT__", FONT_B64)


def svg(size, kind):
    """kind: legacy | round | store | fg | bg"""
    head = f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 512 512">{DEFS}'
    gloss = '<path d="M0 0H512V170Q256 230 0 150Z" fill="#fff" opacity="0.07"/>'
    if kind == "bg":
        return head + f'<rect width="512" height="512" fill="url(#bg)"/>{gloss}</svg>'
    if kind == "fg":
        return head + CONTENT + "</svg>"
    scale = 1.28 if kind in ("legacy", "round") else 1.12
    body = f'<g transform="translate(256 256) scale({scale}) translate(-256 -256)">{CONTENT}</g>'
    if kind == "legacy":
        shape = '<rect width="512" height="512" rx="112" fill="url(#bg)"/>'
        clip = '<clipPath id="c"><rect width="512" height="512" rx="112"/></clipPath>'
    elif kind == "round":
        shape = '<circle cx="256" cy="256" r="256" fill="url(#bg)"/>'
        clip = '<clipPath id="c"><circle cx="256" cy="256" r="256"/></clipPath>'
    else:  # store: full bleed square
        shape = '<rect width="512" height="512" fill="url(#bg)"/>'
        clip = '<clipPath id="c"><rect width="512" height="512"/></clipPath>'
    return head + clip + shape + f'<g clip-path="url(#c)">{gloss}</g>' + body + "</svg>"


def render(page, markup, size, out, transparent=True):
    out.parent.mkdir(parents=True, exist_ok=True)
    page.set_viewport_size({"width": size, "height": size})
    page.set_content(f'<html><body style="margin:0;background:transparent">{markup}</body></html>')
    page.screenshot(path=str(out), omit_background=transparent, clip={"x": 0, "y": 0, "width": size, "height": size})


def main():
    DESIGN.mkdir(exist_ok=True)
    (DESIGN / "icon.svg").write_text(svg(512, "legacy"), encoding="utf-8")
    (DESIGN / "icon-foreground.svg").write_text(svg(512, "fg"), encoding="utf-8")
    legacy = {"mdpi": 48, "hdpi": 72, "xhdpi": 96, "xxhdpi": 144, "xxxhdpi": 192}
    adaptive = {"mdpi": 108, "hdpi": 162, "xhdpi": 216, "xxhdpi": 324, "xxxhdpi": 432}
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page()
        for d, px in legacy.items():
            render(page, svg(px, "legacy"), px, RES / f"mipmap-{d}/ic_launcher.png")
            render(page, svg(px, "round"), px, RES / f"mipmap-{d}/ic_launcher_round.png")
        for d, px in adaptive.items():
            render(page, svg(px, "fg"), px, RES / f"mipmap-{d}/ic_launcher_foreground.png")
            render(page, svg(px, "bg"), px, RES / f"mipmap-{d}/ic_launcher_background.png", transparent=False)
        render(page, svg(512, "store"), 512, DESIGN / "play-store-icon-512.png", transparent=False)
        render(page, svg(512, "legacy"), 512, DESIGN / "icon-512.png")
        b.close()
    print("icons done")


if __name__ == "__main__":
    main()
