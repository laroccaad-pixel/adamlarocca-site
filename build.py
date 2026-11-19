#!/usr/bin/env python3
"""Builds the static site from content/.
   content/projects.json  -> homepage list (visible + order control what shows)
   content/case/<slug>.json -> site/work/<slug>.html
Run: python3 build.py
"""
import json, html, os
ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, "site")
E = html.escape

projects = json.load(open(os.path.join(ROOT, "projects.json")))
cards = json.load(open(os.path.join(ROOT, "content", "cards.json")))
live = sorted([p for p in projects if p.get("visible")], key=lambda p: p["order"])
has_case = lambda slug: os.path.exists(os.path.join(ROOT, "content", "case", slug + ".json"))

FONTS = '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Big+Shoulders+Display:wght@500;800;900&family=Instrument+Sans:wght@400;500;600&display=swap" rel="stylesheet">'

def head(title, pre, desc):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
{FONTS}
<link rel="stylesheet" href="{pre}css/site.css">
</head>
<body>'''

def nav(pre, current=""):
    home = pre + "index.html"
    cur = lambda k: ' aria-current="page"' if k == current else ""
    return f'''<nav class="nav" aria-label="Main">
  <a class="mark" href="{home}" aria-label="Adam LaRocca, home">AL</a>
  <ul><li><a href="{home}#work"{cur("work")}>Work</a></li><li><a href="{home}#about">About</a></li><li><a href="#contact">Contact</a></li></ul>
  <button class="menu-btn" aria-expanded="false" aria-controls="menu">Menu</button>
</nav>
<div class="menu" id="menu" aria-hidden="true">
  <div class="menu-top"><a class="mark" href="{home}" aria-label="Adam LaRocca, home">AL</a><button data-close>Close</button></div>
  <ul><li><a href="{home}#work">Work</a></li><li><a href="{home}#about">About</a></li><li><a href="#contact">Contact</a></li></ul>
  <p>Creative Director. Tallahassee, FL.</p>
</div>'''

def footer(pre):
    return f'''<footer class="foot" id="contact">
  <h2 class="display">Let's make<br>something.</h2>
  <div class="foot-row">
    <a href="mailto:larocca.ad@gmail.com">larocca.ad@gmail.com</a><a href="https://www.linkedin.com/in/alarocca/" target="_blank" rel="noopener">LinkedIn</a><a href="{pre}LaRoccaResume.pdf" target="_blank" rel="noopener">Résumé (PDF)</a><span>Tallahassee, FL. Working everywhere.</span>
  </div>
  <small>© 2026 Adam LaRocca</small>
</footer>
<script src="{pre}js/site.js"></script>
</body>
</html>'''

# ---------------- homepage ----------------
def frame(p, i, pre=""):
    c = cards[p["slug"]]
    href = f'{pre}work/{p["slug"]}.html' if has_case(p["slug"]) else "#"
    return f'''<a class="frame" href="{href}">
  <img src="{pre}img/{c["img"]}.webp" alt="{E(p["client"])}, {E(p["title"])}" loading="{"eager" if i < 3 else "lazy"}">
  <span class="watch">View project</span>
  <div class="frame-copy"><p class="kicker">{E(c.get("client", p["client"]))}</p><h3 class="display">{E(p["title"])}</h3></div>
  <p class="frame-meta">{E(c["role"])}<br>{E(c["agency"])}</p></a>'''

def build_home():
    # rhythm: 1 = wide frame, 2 = side-by-side pair
    pattern = [1, 2, 2, 1, 2, 1, 1, 2, 2, 1, 2]
    out, i = [], 0
    for n in pattern:
        if i >= len(live): break
        if n == 1 or i + 1 >= len(live):
            out.append(frame(live[i], i)); i += 1
        else:
            out.append('<div class="split">' + frame(live[i], i) + frame(live[i+1], i+1) + '</div>'); i += 2
    while i < len(live): out.append(frame(live[i], i)); i += 1
    about = open(os.path.join(ROOT, "about.txt")).read().strip().split("\n\n")
    page = head("Adam LaRocca, Creative Director", "", "Creative Director. Simple ideas that spark emotion and forge connection.") + nav("", "") + f'''
<header class="hero" id="top">
  <video src="video/hero-home.mp4" poster="img/hero-home-poster.webp" autoplay muted loop playsinline data-loop aria-hidden="true"></video>
  <p class="playing"><i></i>Now playing: Belize, Grab Life</p>
  <div class="hero-copy">
    <h1 class="display">Adam<br>LaRocca</h1>
    <div class="hero-side">
      <p>Make it simple yet significant.</p>
      <p>Ideas teams rally around and audiences remember.</p>
    </div>
  </div>
</header>
<main>
<section class="reel" id="work" aria-labelledby="work-h">
  <div class="reel-head"><h2 id="work-h">Selected work</h2><span>{len(live)} projects</span></div>
  {"".join(out)}
</section>
<section class="about" id="about">
  <img src="img/headshot.webp" alt="Adam LaRocca" loading="lazy">
  <div>
    <h2 class="display">Simple ideas. Real feeling.</h2>
    {"".join(f"<p>{E(p)}</p>" for p in about[1:])}
    <p><a href="LaRoccaResume.pdf" target="_blank" rel="noopener" style="color:var(--sun);border-bottom:1px solid var(--sun)">Download résumé (PDF)</a></p>
    <div class="chips"><span>Cannes Lions</span><span>The One Show</span><span>Effie</span><span>Clio</span><span>Webby</span></div>
  </div>
</section>
</main>
''' + footer("")
    open(os.path.join(SITE, "index.html"), "w").write(page)

# ---------------- case studies ----------------
def fig(item, pre, eager=False):
    cap = f'<figcaption>{E(item["caption"])}</figcaption>' if item.get("caption") else ""
    return f'<figure><img src="{pre}{item["src"]}" alt="{E(item.get("alt",""))}" loading="{"eager" if eager else "lazy"}">{cap}</figure>'

def film_tile(m, pre, small=False):
    """Default cover = the platform's own thumbnail. A local poster is used only when "lock": true."""
    title = m.get("title", "")
    src = m["src"]
    local = (pre + m["poster"]) if m.get("poster") else ""
    if m.get("lock") and local:
        img = f'<img src="{local}" alt="" loading="lazy">'
    elif "youtube" in src:
        vid = src.split("/embed/")[1].split("?")[0]
        img = (f'<img src="https://i.ytimg.com/vi/{vid}/maxresdefault.jpg" alt="" loading="lazy" '
               f'onerror="this.onerror=null;this.src=\'https://i.ytimg.com/vi/{vid}/hqdefault.jpg\'">')
    elif "vimeo" in src:
        vid = src.split("/video/")[1].split("?")[0]
        img = f'<img data-vimeo="{vid}" data-fallback="{local}" alt="" loading="lazy">'
    else:
        img = f'<img src="{local}" alt="" loading="lazy">' if local else ""
    label = f'<span><b>{E(title)}</b><span>Play film</span></span>' if title else ""
    return f'''<div class="film{' small' if small else ''}" data-src="{E(src)}" data-title="{E(title or "Film")}"><button aria-label="Play {E(title or "film")}">
  {img}<span class="play"><i></i>{label}</span></button></div>'''

def module(m, pre):
    t = m["type"]
    if t == "section":
        credit = f'<p class="cs-credit-line">{E(m["credit"])}</p>' if m.get("credit") else ""
        body = f'<div><p>{E(m["body"])}</p>{credit}</div>' if m.get("body") else f"<div>{credit}</div>"
        return f'<div class="cs-section-head"><h2 class="display">{E(m["title"]).replace("-", "\u2011")}</h2>{body}</div>'
    if t == "videos":
        tiles = "".join(film_tile(i, pre, small=True) for i in m["items"])
        return f'<div class="vgrid cols-{m.get("cols",3)}">{tiles}</div>'
    if t == "loops":
        vids = "".join(f'<figure><video src="{pre}{v}" autoplay muted loop playsinline data-loop aria-hidden="true"></video></figure>' for v in m["items"])
        return f'<div class="media m-loops cols-{m.get("cols",4)}" style="--ar:{m.get("aspect","9/16")}">{vids}</div>'
    if t == "film":
        return film_tile(m, pre)
    if t == "loop":
        poster = f' poster="{pre}{m["poster"]}"' if m.get("poster") else ""
        return f'<div class="media m-{m["layout"]}"><figure><video src="{pre}{m["src"]}"{poster} autoplay muted loop playsinline data-loop aria-label="{E(m.get("alt",""))}"></video></figure></div>'
    if t == "images":
        return f'<div class="media m-{m["layout"]}">' + "".join(fig(i, pre) for i in m["items"]) + "</div>"
    if t == "rail":
        def rf(i):
            if i.get("video"): return f'<figure><video src="{pre}{i["video"]}" autoplay muted loop playsinline data-loop aria-hidden="true"></video></figure>'
            return f'<figure><img src="{pre}{i["src"]}" alt="{E(m.get("alt",""))}" loading="lazy"></figure>'
        figs = "".join(rf(i) for i in m["items"])
        noun = m.get("noun", "posts")
        return f'''<div class="rail-wrap"><div class="rail{' tall' if m.get('tall') else ''}" tabindex="0" aria-label="{E(m.get("alt","Gallery"))}">{figs}</div>
  <div class="rail-controls"><span>{len(m["items"])} {noun}. Swipe or use the arrows.</span><div><button data-dir="-1" aria-label="Previous">&#8592;</button><button data-dir="1" aria-label="Next">&#8594;</button></div></div></div>'''
    raise ValueError(t)

def build_case(p, nxt):
    pre = "../"
    cs = json.load(open(os.path.join(ROOT, "content", "case", p["slug"] + ".json")))
    c = cards[p["slug"]]
    awards = p.get("awards") or []
    meta = [("Role", p["role"]), ("Agency", p["agency"]), ("Recognition", ", ".join(awards) if awards else p["category"])]
    meta_label = "Recognition" if awards else "Category"
    meta[2] = (meta_label, meta[2][1])
    groups = [[]]
    for m in cs["modules"]:
        if m["type"] == "section" and groups[-1]: groups.append([])
        groups[-1].append(m)
    mods = "".join('<section class="cs-section">' + "".join(module(m, pre) for m in g) + "</section>" for g in groups)
    credits = "".join(f'<li class="{"me" if "Adam LaRocca" in cr else ""}"><b>{E(cr.split(":")[0])}</b>{E(cr.split(":",1)[1].strip())}</li>' for cr in p["credits"])
    award_chips = "".join(f"<span>{E(a)}</span>" for a in awards)
    nc = cards[nxt["slug"]]
    nhref = f'{nxt["slug"]}.html' if has_case(nxt["slug"]) else "../index.html#work"
    hero = cs["hero"]
    hero_media = (f'<video src="{pre}{hero["video"]}" poster="{pre}{hero["poster"]}" autoplay muted loop playsinline data-loop aria-hidden="true"></video>'
                  if hero.get("video") else f'<img src="{pre}{hero["image"]}" alt="" fetchpriority="high">')
    page = head(f'{p["client"]}: {p["title"]}. Adam LaRocca', pre, cs["lead"]) + nav(pre, "work") + f'''
<header class="cs-hero">
  {hero_media}
  <div class="cs-hero-copy">
    <p class="kicker">{E(p["client"])}</p>
    <h1 class="display">{E(p["title"])}</h1>
    <dl class="cs-meta">{"".join(f"<div><dt>{k}</dt><dd>{E(v)}</dd></div>" for k, v in meta)}</dl>
  </div>
</header>
<main>
<section class="cs-intro"><p class="lead{' long' if len(cs['lead']) > 70 else ''}">{E(cs["lead"])}</p><div class="body">{"".join(f"<p>{E(b)}</p>" for b in cs["body"])}</div></section>
{mods}
<section class="cs-credits">
  <div><h2 class="display">Credits</h2><p class="prod">{E(cs.get("productionCredit",""))}</p><div class="cs-awards">{award_chips}</div></div>
  <ul>{credits}<li><b>Agency</b>{E(p["agency"])}</li></ul>
</section>
<a class="next" href="{nhref}"><img src="{pre}img/{nc["img"]}.webp" alt="" loading="lazy"><div><p class="kicker">Next project</p><h2 class="display">{E(nxt["title"])}</h2><p class="kicker">{E(nxt["client"])}</p></div></a>
</main>
''' + footer(pre)
    open(os.path.join(SITE, "work", p["slug"] + ".html"), "w").write(page)

if __name__ == "__main__":
    os.makedirs(os.path.join(SITE, "work"), exist_ok=True)
    build_home()
    for i, p in enumerate(live):
        if has_case(p["slug"]):
            build_case(p, live[(i + 1) % len(live)])
            print("built", p["slug"])
    print("home:", len(live), "projects")
