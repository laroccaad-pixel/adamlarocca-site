// Mobile menu
(() => {
  const btn = document.querySelector(".menu-btn"), menu = document.querySelector(".menu");
  if (!btn || !menu) return;
  const close = menu.querySelector("[data-close]");
  const set = open => { menu.classList.toggle("open", open); menu.setAttribute("aria-hidden", !open); btn.setAttribute("aria-expanded", open); document.body.style.overflow = open ? "hidden" : ""; };
  btn.addEventListener("click", () => set(true));
  close.addEventListener("click", () => set(false));
  menu.querySelectorAll("a").forEach(a => a.addEventListener("click", () => set(false)));
  document.addEventListener("keydown", e => { if (e.key === "Escape") set(false); });
})();

// Films: poster first, load the Vimeo/YouTube player only on click
document.querySelectorAll(".film button").forEach(b => b.addEventListener("click", () => {
  const f = b.closest(".film"), src = f.dataset.src;
  const sep = src.includes("?") ? "&" : "?";
  f.innerHTML = `<iframe src="${src}${sep}autoplay=1" title="${f.dataset.title}" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe>`;
  f.classList.add("on");
}));

// Social rail arrows
document.querySelectorAll(".rail-wrap").forEach(w => {
  const r = w.querySelector(".rail");
  w.querySelectorAll("[data-dir]").forEach(b => b.addEventListener("click", () =>
    r.scrollBy({ left: (r.classList.contains("center-rail") ? r.querySelector("figure").offsetWidth + parseFloat(getComputedStyle(r).columnGap || 0) : r.clientWidth * 0.8) * +b.dataset.dir, behavior: "smooth" })));
});

// Centered carousels: open on data-start; phone rails round whatever sits inside the phone
document.querySelectorAll(".center-rail").forEach(r => {
  const frame = r.parentElement.querySelector(".rail-phone"), figs = [...r.querySelectorAll("figure")];
  const mark = () => { if (!frame) return; const f = frame.getBoundingClientRect();
    figs.forEach(g => { const b = g.getBoundingClientRect(); g.classList.toggle("in-phone", b.right > f.left + 1 && b.left < f.right - 1); }); };
  const start = figs[Math.min(+r.dataset.start || 0, figs.length - 1)];
  const center = () => { const rb = r.getBoundingClientRect(), b = start.getBoundingClientRect();
    r.style.scrollSnapType = "none"; r.scrollLeft += (b.left + b.width / 2) - (rb.left + rb.width / 2); r.style.scrollSnapType = ""; mark(); };
  center(); addEventListener("load", center, { once: true });
  let raf; r.addEventListener("scroll", () => { cancelAnimationFrame(raf); raf = requestAnimationFrame(mark); }, { passive: true });
  addEventListener("resize", mark);
});

// Pause background loops that are off screen; respect reduced motion
(() => {
  const vids = document.querySelectorAll("video[data-loop]");
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) { vids.forEach(v => { v.removeAttribute("autoplay"); v.pause(); }); return; }
  const io = new IntersectionObserver(es => es.forEach(e => e.isIntersecting ? e.target.play().catch(() => {}) : e.target.pause()), { threshold: .15 });
  vids.forEach(v => io.observe(v));
})();

// Vimeo covers: pull the default thumbnail from Vimeo's public oEmbed API
document.querySelectorAll("img[data-vimeo]").forEach(async img => {
  const fb = () => { if (img.dataset.fallback) img.src = img.dataset.fallback; else img.remove(); };
  try {
    const r = await fetch(`https://vimeo.com/api/oembed.json?url=https://vimeo.com/${img.dataset.vimeo}&width=1280`);
    if (!r.ok) return fb();
    const d = await r.json();
    img.src = d.thumbnail_url ? d.thumbnail_url.replace(/_\d+x\d+/, "_1280x720") : "";
    img.onerror = () => { img.onerror = null; d.thumbnail_url ? img.src = d.thumbnail_url : fb(); };
  } catch (e) { fb(); }
});
