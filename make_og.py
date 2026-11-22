"""Render favicon + social share cards with headless Chrome so type matches the site exactly.
Usage: python3 make_og.py            -> favicons + per-case cards (C)
       python3 make_og.py --preview  -> also homepage options A and B into /tmp/og-preview
"""
import json, sys, pathlib, base64
from playwright.sync_api import sync_playwright
from PIL import Image

ROOT = pathlib.Path(__file__).parent
SITE = ROOT / "site"
FONTS = pathlib.Path("/tmp/gf")

def font_css():
    def ff(fam, path, w):
        b = base64.b64encode(path.read_bytes()).decode()
        return f"@font-face{{font-family:'{fam}';font-weight:{w};src:url(data:font/woff2;base64,{b}) format('woff2')}}"
    bs = FONTS / "fontsource-big-shoulders-display-5.3.0/files"
    ins = FONTS / "fontsource-instrument-sans-5.3.0/files"
    return "".join([ff("BS", bs / "big-shoulders-display-latin-800-normal.woff2", 800),
                    ff("BS", bs / "big-shoulders-display-latin-900-normal.woff2", 900),
                    ff("IS", ins / "instrument-sans-latin-500-normal.woff2", 500),
                    ff("IS", ins / "instrument-sans-latin-600-normal.woff2", 600)])

BASE = """*{margin:0;box-sizing:border-box}html,body{width:%dpx;height:%dpx;overflow:hidden}
body{font-family:IS;-webkit-font-smoothing:antialiased}.d{font-family:BS;font-weight:900;text-transform:uppercase;line-height:.86;letter-spacing:-.005em}"""
NAVY, SUN, PAPER = "#0D1B2A", "#FFC83D", "#F3F5F8"

def img_uri(p):
    return "data:image/webp;base64," + base64.b64encode((SITE / p).read_bytes()).decode()

def favicon_html():
    return f"""<style>{BASE % (512, 512)}body{{background:{SUN};display:grid;place-items:center}}
.d{{color:{NAVY};font-size:400px;line-height:1;transform:translateY(-6px);letter-spacing:-.02em}}</style><div class="d">AL</div>"""

def card_a():
    return f"""<style>{BASE % (1200, 630)}body{{background:{SUN};color:{NAVY};padding:64px 72px}}
.m{{font-family:BS;font-weight:900;font-size:44px}}.d{{font-size:132px;margin-top:62px}}
.f{{position:absolute;left:72px;bottom:56px;font-size:24px;font-weight:600}}.f span{{font-weight:500;opacity:.7;margin-left:14px}}</style>
<div class="m">AL</div><div class="d">Let's make people<br>feel something.</div><div class="f">Adam LaRocca<span>Creative Director</span></div>"""

def card_photo(img, kicker, title, small_title=False, dim=False):
    fs = 120 if not small_title else 96
    return f"""<style>{BASE % (1200, 630)}body{{background:{NAVY} url({img}) center/cover;color:{PAPER};position:relative}}
.s{{position:absolute;inset:0;background:linear-gradient(90deg,rgba(13,27,42,.88) 0%,rgba(13,27,42,.55) 48%,rgba(13,27,42,.05) 85%),linear-gradient(0deg,rgba(13,27,42,.75),rgba(13,27,42,0) 55%){',rgba(13,27,42,.15)' if dim else ''}}}
.m{{position:absolute;left:72px;top:60px;font-family:BS;font-weight:900;font-size:44px;color:{SUN}}}
.b{{position:absolute;left:72px;right:72px;bottom:60px}}.k{{font-size:24px;font-weight:600;color:{SUN};margin-bottom:16px}}
.d{{font-size:{fs}px}}.f{{font-size:22px;font-weight:500;opacity:.8;margin-top:22px}}</style>
<div class="s"></div><div class="m">AL</div><div class="b"><div class="k">{kicker}</div><div class="d">{title}</div><div class="f">Adam LaRocca, Creative Director</div></div>"""

def card_b():
    return f"""<style>{BASE % (1200, 630)}body{{background:{NAVY} url({img_uri('img/glc/poster-hero-1080.webp')}) center/cover;color:{PAPER};position:relative}}
.s{{position:absolute;inset:0;background:linear-gradient(90deg,rgba(13,27,42,.9),rgba(13,27,42,.5) 55%,rgba(13,27,42,.1)),linear-gradient(0deg,rgba(13,27,42,.7),rgba(13,27,42,0) 60%)}}
.m{{position:absolute;left:72px;top:60px;font-family:BS;font-weight:900;font-size:44px;color:{SUN}}}
.b{{position:absolute;left:72px;bottom:60px}}.d{{font-size:150px}}.k{{font-size:28px;font-weight:600;color:{SUN};margin-top:18px}}
.f{{font-size:24px;font-weight:500;opacity:.85;margin-top:8px}}</style>
<div class="s"></div><div class="m">AL</div><div class="b"><div class="d">Adam<br>LaRocca</div><div class="k">Creative Director</div><div class="f">Simple ideas. Just need the feels.</div></div>"""

def shoot(page, html, w, h, out):
    page.set_viewport_size({"width": w, "height": h})
    page.set_content(f"<style>{font_css()}</style>" + html)
    page.evaluate("document.fonts.ready"); page.wait_for_timeout(150)
    page.screenshot(path=str(out), type="jpeg" if str(out).endswith(".jpg") else "png", **({"quality": 88} if str(out).endswith(".jpg") else {}))

def main():
    preview = "--preview" in sys.argv
    (SITE / "img/og").mkdir(parents=True, exist_ok=True)
    projects = json.load(open(ROOT / "projects.json"))
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path="/usr/bin/google-chrome")
        pg = b.new_page()
        shoot(pg, favicon_html(), 512, 512, "/tmp/fav512.png")
        fav = Image.open("/tmp/fav512.png").convert("RGB")
        fav.resize((180, 180), Image.LANCZOS).save(SITE / "apple-touch-icon.png")
        fav.resize((32, 32), Image.LANCZOS).save(SITE / "favicon-32.png")
        fav.save(SITE / "favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])
        for pr in projects:
            cs = json.load(open(ROOT / "content/case" / f"{pr['slug']}.json"))
            hero = cs.get("hero", {})
            src = hero.get("poster") or hero.get("image")
            if not src or src.startswith("http"): continue
            title = cs.get("title") or pr["title"]
            shoot(pg, card_photo(img_uri(src), pr["client"], pr["title"], len(pr["title"]) > 16, hero.get("tint") == "dim"),
                  1200, 630, SITE / "img/og" / f"{pr['slug']}.jpg")
        if preview:
            out = pathlib.Path("/tmp/og-preview"); out.mkdir(exist_ok=True)
            shoot(pg, card_a(), 1200, 630, out / "A.jpg")
            shoot(pg, card_b(), 1200, 630, out / "B.jpg")
        b.close()

if __name__ == "__main__":
    main()
