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
    r.scrollBy({ left: r.clientWidth * 0.8 * +b.dataset.dir, behavior: "smooth" })));
});

// Pause background loops that are off screen; respect reduced motion
(() => {
  const vids = document.querySelectorAll("video[data-loop]");
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) { vids.forEach(v => { v.removeAttribute("autoplay"); v.pause(); }); return; }
  const io = new IntersectionObserver(es => es.forEach(e => e.isIntersecting ? e.target.play().catch(() => {}) : e.target.pause()), { threshold: .15 });
  vids.forEach(v => io.observe(v));
})();
