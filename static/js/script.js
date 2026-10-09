document.addEventListener("DOMContentLoaded", () => {
  initThemeToggle();
  initModalFocus();

  const expMap = document.getElementById("experience-map");
  if (expMap) {
    try {
      renderExperienceMap(expMap);
    } catch (err) {
      console.error("Gagal merender bagian Pengalaman:", err);
    }
  }

  const hobbySlider = document.getElementById("hobby-slider");
  if (hobbySlider) {
    try {
      initHobbySlider(hobbySlider);
    } catch (err) {
      console.error("Gagal merender bagian Hobi:", err);
    }
  }

  const eduStrip = document.getElementById("education-strip");
  if (eduStrip) {
    try {
      renderEducation(eduStrip);
    } catch (err) {
      console.error("Gagal merender bagian Edukasi:", err);
    }
  }

  const expDetail = document.getElementById("experience-detail");
  if (expDetail) {
    try {
      renderExperienceDetail(expDetail);
    } catch (err) {
      console.error("Gagal merender detail Pengalaman:", err);
    }
  }
});

const ICONS = {
  event: `<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M12 4v40"/><path d="M12 8h26l-7 8 7 8H12"/></svg>`,
  hackathon: `<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M18 14 7 24l11 10"/><path d="M30 14l11 10-11 10"/></svg>`,
  web: `<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><circle cx="24" cy="24" r="17"/><path d="M7 24h34"/><path d="M24 7c6.5 5.5 6.5 30.5 0 34"/><path d="M24 7c-6.5 5.5-6.5 30.5 0 34"/></svg>`,
  org: `<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><circle cx="17" cy="17" r="6.5"/><circle cx="32" cy="20" r="5.5"/><path d="M6 41c0-8 5-13 11-13s11 5 11 13"/><path d="M28 41c0-6.5 3.5-10.5 9-10.5s10 4 10 10.5"/></svg>`,
  star: `<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M24 5l6 13 14 1.8-10.5 9.7 2.8 14L24 36.3 11.7 43.5l2.8-14L4 19.8 18 18z"/></svg>`,
  data: `<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M8 40V22"/><path d="M20 40V12"/><path d="M32 40V26"/><path d="M40 40V8"/></svg>`,
  basket: `<svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><circle cx="24" cy="20" r="12"/><path d="M24 8v24"/><path d="M12 20h24"/><path d="M15.5 11.5c4 4 4 13 0 17"/><path d="M32.5 11.5c-4 4-4 13 0 17"/><path d="M14 34l20 8"/></svg>`
};

/* ---------- Experience: satu baris pulau, sejajar horizontal ---------- */
function renderExperienceMap(container) {
  const nodeHtml = (exp) => {
    const hasImage = !!exp.islandImage;
    const islandStyle = hasImage
      ? ` style="background-image:url('${exp.islandImage}');background-size:cover;background-position:center;"`
      : "";
    // Ikon garis hanya ditampilkan kalau tidak ada gambar pulau (islandImage kosong)
    const iconHtml = hasImage ? "" : `<span class="exp-icon" aria-hidden="true">${ICONS[exp.icon] || ICONS.star}</span>`;

    return `
    <div class="exp-node">
      <span class="exp-island"${islandStyle}>${iconHtml}</span>
      <h3>${exp.title}</h3>
    </div>`;
  };

  container.innerHTML = EXPERIENCES.map(nodeHtml).join("");
}

function debounce(fn, wait) {
  let t;
  return (...args) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), wait);
  };
}


/* ---------- Hobby: slider berputar otomatis ---------- */
function initHobbySlider(container) {
  const track = container.querySelector(".slider-track");
  const dotsWrap = container.querySelector(".slider-dots");
  let current = 0;
  let timer = null;
  const AUTOPLAY_MS = 4200;

  track.innerHTML = HOBBIES.map(
    (h) => `
    <figure class="slide">
      <img src="${h.image}" alt="${h.title}" width="${h.width}" height="${h.height}" loading="lazy">
      <figcaption>
        <h3>${h.title}</h3>
        <p>${h.caption}</p>
      </figcaption>
    </figure>`
  ).join("");

  dotsWrap.innerHTML = HOBBIES.map(
    (_, i) => `<button class="dot" data-index="${i}" aria-label="Ke slide ${i + 1}"></button>`
  ).join("");

  const dots = [...dotsWrap.querySelectorAll(".dot")];
  const slideEls = [...track.querySelectorAll(".slide")];

  function goTo(index) {
    current = (index + HOBBIES.length) % HOBBIES.length;
    dots.forEach((d, i) => {
      d.classList.toggle("active", i === current);
      // Penanda slide aktif untuk pembaca layar
      if (i === current) d.setAttribute("aria-current", "true");
      else d.removeAttribute("aria-current");
    });
    slideEls.forEach((s, i) => {
      s.classList.remove("active", "prev", "next");
      if (i === current) s.classList.add("active");
      else if (i < current) s.classList.add("prev");
      else s.classList.add("next");
    });
    centerActiveSlide();
  }

  function centerActiveSlide() {
    const sliderEl = container.querySelector(".slider");
    const activeSlide = slideEls[current];
    if (!sliderEl || !activeSlide) return;
    const sliderWidth = sliderEl.clientWidth;
    const slideLeft = activeSlide.offsetLeft;
    const slideWidth = activeSlide.offsetWidth;
    const offset = slideLeft - (sliderWidth - slideWidth) / 2;
    track.style.transform = `translateX(${-offset}px)`;
  }

  function next() {
    goTo(current + 1);
  }

  function start() {
    stop();
    timer = setInterval(next, AUTOPLAY_MS);
  }

  function stop() {
    if (timer) clearInterval(timer);
  }

  dots.forEach((d) =>
    d.addEventListener("click", () => {
      goTo(parseInt(d.dataset.index, 10));
      // Timer tidak dinyalakan lagi di sini: fokus masih di dalam slider,
      // jadi slide pilihan pengguna tidak langsung tergeser.
    })
  );

  // hormati preferensi "reduce motion" pengguna
  const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  // Slider berhenti saat disorot mouse atau saat fokus keyboard ada di dalamnya,
  // dan baru jalan lagi setelah keduanya sudah keluar dari slider.
  function resume(event) {
    if (prefersReducedMotion) return;
    const focused = event.type === "focusout" ? event.relatedTarget : document.activeElement;
    if (container.contains(focused) || container.matches(":hover")) return;
    start();
  }

  container.addEventListener("mouseenter", stop);
  container.addEventListener("mouseleave", resume);
  container.addEventListener("focusin", stop);
  container.addEventListener("focusout", resume);
  window.addEventListener("resize", debounce(centerActiveSlide, 150));

  goTo(0);
  if (!prefersReducedMotion) start();
}

/* ---------- Education: foto SD / SMP / SMA ---------- */
function renderEducation(container) {
  container.innerHTML = EDUCATION.map(
    (ed) => `
    <figure class="edu-frame">
      <img src="${ed.photo}" alt="Foto masa ${ed.level}: ${ed.note}" width="${ed.width}" height="${ed.height}" loading="lazy">
      <figcaption>
        <span class="edu-level">${ed.level}</span>
        <span class="edu-name">${ed.fullName}</span>
        <span class="edu-years">${ed.years}</span>
      </figcaption>
    </figure>`
  ).join("");
}

/* ---------- Halaman detail pengalaman ---------- */
function renderExperienceDetail(container) {
  const params = new URLSearchParams(window.location.search);
  const id = params.get("id");
  const exp = EXPERIENCES.find((e) => e.id === id) || EXPERIENCES[0];

  document.title = `${exp.title} — Pengalaman`;
  document.body.setAttribute("data-theme", exp.theme || "");

  container.innerHTML = `
    <div class="theme-banner" aria-hidden="true"></div>
    <h1>${exp.title}</h1>
    <p class="exp-meta">${exp.org} · ${exp.year}</p>
    <img class="exp-detail-img" src="${exp.image}" alt="${exp.title}">
    <p class="exp-summary">${exp.summary}</p>
    <div class="exp-detail-body">
      ${exp.detail.map((p) => `<p>${p}</p>`).join("")}
    </div>
    <ul class="exp-tags">
      ${exp.tags.map((t) => `<li>${t}</li>`).join("")}
    </ul>
  `;
}

/* ---------- Mode gelap/terang ---------- */
// Tema awal sudah dipasang oleh skrip kecil di <head> (base.html).
// Di sini tombolnya dihubungkan dan pilihan pengguna disimpan ke localStorage.
function initThemeToggle() {
  const toggle = document.getElementById("theme-toggle");
  if (!toggle) return;
  const root = document.documentElement;
  const systemDark = window.matchMedia("(prefers-color-scheme: dark)");

  function storedTheme() {
    try {
      return localStorage.getItem("theme");
    } catch (err) {
      return null;
    }
  }

  function applyTheme(mode) {
    root.dataset.mode = mode;
    toggle.setAttribute("aria-pressed", String(mode === "dark"));
  }

  applyTheme(root.dataset.mode === "dark" ? "dark" : "light");

  toggle.addEventListener("click", () => {
    const mode = root.dataset.mode === "dark" ? "light" : "dark";
    applyTheme(mode);
    try {
      localStorage.setItem("theme", mode);
    } catch (err) {
      // localStorage bisa diblokir; tema tetap berganti untuk halaman ini
    }
  });

  // Selama pengguna belum memilih sendiri, ikuti perubahan tema sistem
  systemDark.addEventListener("change", (event) => {
    if (!storedTheme()) applyTheme(event.matches ? "dark" : "light");
  });
}

/* ---------- Modal (popover): fokus keyboard ---------- */
// Saat modal dibuka, fokus pindah ke kolom pertama dan Tab berputar di dalam modal.
// Saat ditutup (termasuk dengan Escape), browser mengembalikan fokus ke tombol pembuka.
function initModalFocus() {
  const FOCUSABLE = 'a[href], button:not([disabled]), input:not([disabled]):not([type="hidden"]), select:not([disabled]), textarea:not([disabled])';

  document.querySelectorAll(".project-form-modal[popover]").forEach((modal) => {
    const focusableItems = () =>
      [...modal.querySelectorAll(FOCUSABLE)].filter((el) => el.tabIndex !== -1);

    modal.addEventListener("toggle", (event) => {
      if (event.newState !== "open") return;
      const firstField = modal.querySelector("input:not([type='hidden']), select, textarea");
      if (firstField) firstField.focus();
    });

    modal.addEventListener("keydown", (event) => {
      if (event.key !== "Tab") return;
      const items = focusableItems();
      if (items.length === 0) return;
      const first = items[0];
      const last = items[items.length - 1];

      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus();
      }
    });
  });
}
