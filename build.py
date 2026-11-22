import os
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

SITE_URL = "https://adamlarocca-site.larocca-ad.workers.dev"  # swap to https://adamlarocca.com at launch

def head(title, pre, desc, noindex=False, og_img=None, path=""):
    robots = '<meta name="robots" content="noindex,nofollow">\n' if noindex else ''
    desc = desc.replace("\n", " ")
    icons = (f'<link rel="icon" href="{pre}favicon.ico" sizes="any"><link rel="icon" type="image/png" href="{pre}favicon-32.png">'
             f'<link rel="apple-touch-icon" href="{pre}apple-touch-icon.png">\n')
    og = (f'<meta property="og:type" content="website"><meta property="og:title" content="{E(title)}">'
          f'<meta property="og:description" content="{E(desc)}"><meta property="og:url" content="{SITE_URL}/{path}">'
          + (f'<meta property="og:image" content="{SITE_URL}/{og_img}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
             f'<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{SITE_URL}/{og_img}">' if og_img else "")
          + "\n")
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
{robots}{icons}{og}{FONTS}
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
  <h2 class="display">Let's make people<br>feel something.</h2>
  <div class="foot-row">
    <a href="mailto:larocca.ad@gmail.com">larocca.ad@gmail.com</a><a href="https://www.linkedin.com/in/alarocca/" target="_blank" rel="noopener">LinkedIn</a><a href="{pre}LaRoccaResume.pdf" target="_blank" rel="noopener">Resumé (PDF)</a>
  </div>
  <small>© 2026 Adam LaRocca</small>
</footer>
<script src="{pre}js/site.js"></script>
<!-- Cloudflare Web Analytics --><script type='module' src='https://static.cloudflareinsights.com/beacon.min.js' data-cf-beacon='{{"token": "65a49ff2afe44cc1abe7a54dd15e1950"}}'></script><!-- End Cloudflare Web Analytics -->
</body>
</html>'''

# ---------------- homepage ----------------
def frame(p, i, pre=""):
    c = cards[p["slug"]]
    href = f'{pre}work/{p["slug"]}.html' if has_case(p["slug"]) else "#"
    tint = f' tint-{c["tint"]}' if c.get("tint") else ""
    ttl = "<br>".join(E(x) for x in c["title"].split("\n")) if c.get("title") else E(p["title"])
    return f'''<a class="frame{tint}" href="{href}">
  <img src="{c.get("imgUrl") or pre + "img/" + c["img"] + ".webp"}" alt="{E(p["client"])}, {E(p["title"])}" loading="{"eager" if i < 3 else "lazy"}">
  <span class="watch">View project</span>
  <div class="frame-copy"><p class="kicker">{E(c.get("client", p["client"]))}</p><h3 class="display">{ttl}</h3></div>
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
    page = head("Adam LaRocca, Creative Director", "", "Creative Director. Simple ideas that spark emotion and forge connection.", og_img="img/og/home.jpg") + nav("", "") + f'''
<header class="hero" id="top">
  <video src="video/glc-hero-1080.mp4" poster="img/glc/poster-hero-1080.webp" autoplay muted loop playsinline data-loop aria-hidden="true"></video>
  <p class="playing"><i></i>Now playing: Belize, Grab Life</p>
  <div class="hero-copy">
    <h1 class="display">Adam<br>LaRocca</h1>
    <div class="hero-side">
      <p>Make it simple yet significant.</p>
      <p>Ideas teams rally around and<br class="br-desk"> audiences remember.</p>
    </div>
  </div>
</header>
<main>
<section class="reel" id="work" aria-labelledby="work-h">
  <div class="reel-head"><h2 id="work-h">Selected work</h2><span>{len(live)} projects</span></div>
  {"".join(out)}
</section>
<section class="about" id="about">
  <figure class="portrait"><img src="img/headshot.webp" alt="Adam LaRocca" loading="lazy"></figure>
  <div>
    <h2 class="display">Simple ideas. Just need the feels.</h2>
    {"".join(f"<p>{E(p)}</p>" for p in about[1:])}
    <p><a href="LaRoccaResume.pdf" target="_blank" rel="noopener" style="color:var(--sun);border-bottom:1px solid var(--sun)">Download Resumé (PDF)</a></p>
    <div class="chips"><span>Cannes Lions</span><span>The One Show</span><span>Effies</span><span>Clios</span><span>Webbys</span><span>Graphis</span></div>
    <div class="chips chips-sub"><span>B2B ACE Awards</span><span>Adrian Awards</span><span>Magellan Awards</span><span>Flagler Awards</span></div>
  </div>
  <figure class="logo-grid"><img src="img/logo-grid.webp" alt="Brands Adam has worked with, including Gatorade, Hertz, T-Mobile, McDonald's, Marriott, Toyota and Lincoln Financial" loading="lazy" width="1840" height="1300"></figure>
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
    src = m["src"] if m["src"].startswith("http") else pre + m["src"]
    local = (pre + m["poster"]) if m.get("poster") else ""
    if m.get("lock") and local:
        img = f'<img src="{local}" alt="" loading="lazy">'
    elif "youtube" in src:
        vid = src.split("/embed/")[1].split("?")[0]
        step = "this.src=this.src.replace(/maxresdefault|sddefault/,m=>m==='maxresdefault'?'sddefault':'hqdefault')"
        img = (f'<img src="https://i.ytimg.com/vi/{vid}/maxresdefault.jpg" alt="" loading="lazy" '
               f'onload="if(this.naturalWidth<=120&&!/hqdefault/.test(this.src)){step}" '
               f'onerror="if(!/hqdefault/.test(this.src)){step}">')
    elif "vimeo" in src:
        vid = src.split("/video/")[1].split("?")[0]
        img = f'<img data-vimeo="{vid}" data-fallback="{local}" alt="" loading="lazy">'
    else:
        img = f'<img src="{local}" alt="" loading="lazy">' if local else ""
    label = f'<span><b>{E(title)}</b><span>Play film</span></span>' if title else ""
    return f'''<div class="film{' small' if small else ''}{' dark-label' if m.get('darkLabel') else ''}" data-src="{E(src)}" data-title="{E(title or "Film")}"><button aria-label="Play {E(title or "film")}">
  {img}<span class="play"><i></i>{label}</span></button></div>'''

def phones(items, pre):
    """9:16 films shown full-screen inside iPhone frames."""
    out = []
    for i in items:
        tile = film_tile({**i, "title": ""}, pre)
        cap = f'<figcaption>{E(i["title"])}</figcaption>' if i.get("title") else ""
        out.append(f'<figure class="phone-wrap"><div class="phone">{tile}</div>{cap}</figure>')
    return f'<div class="phones n-{len(items)}">' + "".join(out) + "</div>"

def module(m, pre):
    t = m["type"]
    if t == "section":
        credit = f'<p class="cs-credit-line">{E(m["credit"])}</p>' if m.get("credit") else ""
        body = f'<div><p>{E(m["body"])}</p>{credit}</div>' if m.get("body") else f"<div>{credit}</div>"
        return f'<div class="cs-section-head"><h2 class="display{' long' if max(len(w) for w in m['title'].split()) > 13 else ''}">{E(m["title"]).replace("-", "\u2011")}</h2>{body}</div>'
    if t == "videos" and m.get("phone"):
        return phones(m["items"], pre)
    if t == "videos":
        tiles = "".join(film_tile(i, pre, small=True) for i in m["items"])
        return f'<div class="vgrid cols-{m.get("cols",3)}">{tiles}</div>'
    if t == "loops" and m.get("phone"):
        vids = "".join(f'<figure class="phone-top"><div class="screen"><video src="{pre}{v}" autoplay muted loop playsinline data-loop aria-hidden="true"></video></div></figure>' for v in m["items"])
        return f'<div class="phone-tops" style="--n:{len(m["items"])}">{vids}</div>'
    if t == "loops":
        vids = "".join(f'<figure><video src="{pre}{v}" autoplay muted loop playsinline data-loop aria-hidden="true"></video></figure>' for v in m["items"])
        return f'<div class="media m-loops cols-{m.get("cols",4)}{' narrow' if m.get('narrow') else ''}{' skinny' if m.get('skinny') else ''}" style="--ar:{m.get("aspect","9/16")}">{vids}</div>'
    if t == "film" and m.get("phone"):
        return phones([m], pre)
    if t == "film":
        return film_tile(m, pre)
    if t == "phone3":
        a = E(m.get("alt", ""))
        return (f'<div class="media phone3" style="--pt:{m.get("post_top",0.33)}">'
                f'<img class="p3-side" src="{pre}{m["left"]}" alt="{a}" loading="lazy">'
                f'<div class="p3-phone"><img src="{pre}{m["screen"]}" alt="{a}" loading="lazy"></div>'
                f'<img class="p3-side" src="{pre}{m["right"]}" alt="{a}" loading="lazy"></div>')
    if t == "split":
        def cell(i):
            if i.get("video"):
                pst = f' poster="{pre}{i["poster"]}"' if i.get("poster") else ""
                return f'<figure><video src="{pre}{i["video"]}"{pst} autoplay muted loop playsinline data-loop aria-hidden="true"></video></figure>'
            return f'<figure><img src="{pre}{i["src"]}" alt="{E(i.get("alt",""))}" loading="lazy"></figure>'
        return f'<div class="media m-split">{cell(m["left"])}<div class="split-col">' + "".join(cell(i) for i in m["right"]) + "</div></div>"
    if t == "loop":
        poster = f' poster="{pre}{m["poster"]}"' if m.get("poster") else ""
        return f'<div class="media m-{m["layout"]}"><figure><video src="{pre}{m["src"]}"{poster} autoplay muted loop playsinline data-loop aria-label="{E(m.get("alt",""))}"></video></figure></div>'
    if t == "images":
        anchor = f' anchor-{m["anchor"]}' if m.get("anchor") else ""
        if m.get("inset"): anchor += " inset"
        if m.get("pad") == "top": anchor += " padded-top"
        elif m.get("pad"): anchor += " padded"
        if m.get("contain"): anchor += " contain"
        if m.get("tall"): anchor += " tall"
        ar = f' style="--ar:{m["ar"]}"' if m.get("ar") else ""
        return f'<div class="media m-{m["layout"]}{anchor}"{ar}>' + "".join(fig(i, pre) for i in m["items"]) + "</div>"
    if t == "adpage":
        v = lambda f, w, h: f'<video src="{pre}{f}" width="{w}" height="{h}" autoplay muted loop playsinline data-loop aria-hidden="true"></video>'
        sk = lambda n, cls="": "".join(f'<i class="sk{cls}" style="width:{w}%"></i>' for w in n)
        return f'''<div class="adpage" role="img" aria-label="{E(m.get("alt","Banner ads in a web page"))}"><div class="ap-bar"></div><div class="ap-body">
  <div class="ap-nav"><i class="sk logo"></i><span>{sk([9,7,8,6])}</span></div>
  <div class="ap-ad lb">{v(m["top"],728,90)}</div>
  <div class="ap-cols"><div class="ap-main"><i class="sk h"></i><i class="sk h" style="width:62%"></i><div class="ap-hero"></div>{sk([100,96,98,91,64])}<div class="ap-ad lb">{v(m["mid"],728,90)}</div>{sk([100,94,97,88,99,72])}</div>
  <aside class="ap-rail"><div class="ap-ad mr">{v(m["rail"],300,250)}</div>{sk([90,100,80])}<div class="ap-card"></div>{sk([100,70])}</aside></div>
</div></div>'''
    if t == "collage":
        W, H = m["w"], m["h"]
        def tile(i):
            x, y, w, h = i["box"]
            return (f'<figure style="left:{x/W*100:.3f}%;top:{y/H*100:.3f}%;width:{w/W*100:.3f}%;height:{h/H*100:.3f}%">'
                    f'<img src="{pre}{i["src"]}" alt="{E(m.get("alt",""))}" loading="lazy"></figure>')
        return f'<div class="media m-collage" style="aspect-ratio:{W}/{H}">' + "".join(tile(i) for i in m["items"]) + "</div>"
    if t == "rail":
        def rf(i):
            if i.get("video") and i.get("browser"): return f'<figure class="rail-browser"><div class="bw"><video src="{pre}{i["video"]}" autoplay muted loop playsinline data-loop aria-hidden="true"></video></div></figure>'
            if i.get("video"): return f'<figure><video src="{pre}{i["video"]}" autoplay muted loop playsinline data-loop aria-hidden="true"></video></figure>'
            return f'<figure><img src="{pre}{i["src"]}" alt="{E(m.get("alt",""))}" loading="lazy"></figure>'
        figs = "".join(rf(i) for i in m["items"])
        noun = m.get("noun", "posts")
        cls = ' tall' if m.get('tall') else ''
        if m.get("phone"): cls += ' phone-rail center-rail'
        elif m.get("center"): cls += ' center-rail'
        attrs = f' data-start="{m.get("start", 2 if m.get("phone") else 0)}"'
        sty = (f'--pw:min({m["size"]}px,86vw);' if m.get("size") else '') + (f'--rar:{m["aspect"]};' if m.get("aspect") else '')
        if sty: attrs += f' style="{sty}"'
        frame = '<div class="rail-phone" aria-hidden="true"></div>' if m.get("phone") else ''
        return f'''<div class="rail-wrap{' has-phone' if m.get('phone') else ''}"><div class="rail-stage">{frame}<div class="rail{cls}"{attrs} tabindex="0" aria-label="{E(m.get("alt","Gallery"))}">{figs}</div></div>
  <div class="rail-controls"><span>{len(m["items"])} {noun}. Swipe or use the arrows.</span><div><button data-dir="-1" aria-label="Previous">&#8592;</button><button data-dir="1" aria-label="Next">&#8594;</button></div></div></div>'''
    raise ValueError(t)

def build_case(p, nxt, hidden=False):
    pre = "../"
    cs = json.load(open(os.path.join(ROOT, "content", "case", p["slug"] + ".json")))
    c = cards[p["slug"]]
    awards = p.get("awards") or []
    meta = [("Role", p["role"]), ("Agency", p["agency"]), ("Recognition", "\n".join(awards) if awards else p["category"])]
    meta_label = "Recognition" if awards else "Category"
    meta[2] = (meta_label, meta[2][1])
    groups = [[]]
    for m in cs["modules"]:
        if m["type"] == "section" and groups[-1]: groups.append([])
        groups[-1].append(m)
    mods = "".join(('<section class="cs-section divided">' if g[0].get("divider") else '<section class="cs-section">') + "".join(module(m, pre) for m in g) + "</section>" for g in groups)
    credits = "".join(f'<li class="{"me" if "Adam LaRocca" in cr else ""}"><b>{E(cr.split(":")[0])}</b>{E(cr.split(":",1)[1].strip())}</li>' for cr in p["credits"])
    award_chips = "".join(f"<span>{E(a)}</span>" for a in awards)
    nc = cards[nxt["slug"]]
    nhref = f'{nxt["slug"]}.html' if has_case(nxt["slug"]) else "../index.html#work"
    hero = cs["hero"]
    pc = cs.get("productionCredit", "")
    prod_html = "".join((f'<p class="prod">{E(x)}</p>' if x else '<p class="prod sp" aria-hidden="true"></p>') for x in (pc if isinstance(pc, list) else ([pc] if pc else [])))
    hero_media = (f'<video src="{pre}{hero["video"]}" poster="{pre}{hero["poster"]}" autoplay muted loop playsinline data-loop aria-hidden="true"></video>'
                  if hero.get("video") else f'<img src="{"" if hero["image"].startswith("http") else pre}{hero["image"]}" alt="" fetchpriority="high">')
    page = head(f'{p["client"]}: {p["title"]}. Adam LaRocca', pre, cs["lead"], noindex=hidden,
                og_img=(f'img/og/{p["slug"]}.jpg' if os.path.exists(f'site/img/og/{p["slug"]}.jpg') else None), path=f'work/{p["slug"]}') + nav(pre, "work") + f'''
<header class="cs-hero{(' tint-' + cs['hero']['tint']) if cs.get('hero',{}).get('tint') else ''}">
  {hero_media}
  <div class="cs-hero-copy">
    <p class="kicker">{E(p["client"])}</p>
    <h1 class="display">{E(p["title"])}</h1>
    <dl class="cs-meta">{"".join(f"<div><dt>{k}</dt><dd>{E(v).replace(chr(10), "<br>")}</dd></div>" for k, v in meta)}</dl>
  </div>
</header>
<main>
<section class="cs-intro"><p class="lead{' long' if len(cs['lead']) > 70 else ''}">{E(cs["lead"]).replace(chr(10), "<br>")}</p><div class="body">{"".join(f"<p>{E(b)}</p>" for b in cs["body"])}</div></section>
{mods}
<section class="cs-credits">
  <div><h2 class="display">Credits</h2>{prod_html}<div class="cs-awards">{award_chips}</div></div>
  <ul>{credits}<li><b>Agency</b>{E(p["agency"])}</li></ul>
</section>
<a class="next" href="{nhref}"><img src="{nc.get("imgUrl") or pre + "img/" + nc["img"] + ".webp"}" alt="" loading="lazy"><div><p class="kicker">Next project</p><h2 class="display">{E(nxt["title"])}</h2><p class="kicker">{E(nxt["client"])}</p></div></a>
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
    # hidden projects: still built as unlisted preview pages (noindex), reachable by URL only
    hidden = sorted([p for p in projects if not p.get("visible")], key=lambda p: p["order"])
    for p in hidden:
        if has_case(p["slug"]):
            build_case(p, live[0], hidden=True)
    with open(os.path.join(SITE, "preview.html"), "w") as f:
        f.write('<!doctype html><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><title>Hidden previews</title>'
                '<style>body{font:16px system-ui;background:#0D1B2A;color:#F3F5F8;padding:40px}a{color:#FFC83D;display:block;margin:8px 0}</style>'
                '<h1>Hidden case studies</h1>' + "".join(f'<a href="work/{p["slug"]}.html">{E(p["client"])}: {E(p["title"])}</a>' for p in hidden))
    print("home:", len(live), "projects;", len(hidden), "hidden previews")
