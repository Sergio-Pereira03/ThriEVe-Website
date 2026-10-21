/* ThriEVe — one-page scroll engine.
   As you scroll: the shifter rows gears, the tach revs, the accent color
   changes per section, and the background parallaxes behind the text. */

(function () {
  "use strict";

  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* Year */
  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = String(new Date().getFullYear());
  });

  /* Contact form (front-end demo) */
  var form = document.querySelector("form[data-thriev-form]");
  if (form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!form.checkValidity()) { form.reportValidity(); return; }
      var btn = form.querySelector("button[type=submit]");
      var status = form.querySelector(".form-status");
      if (btn) { btn.disabled = true; btn.textContent = "Shifting…"; }
      setTimeout(function () {
        form.reset();
        if (btn) { btn.disabled = false; btn.textContent = "Send message"; }
        if (status) { status.hidden = false; status.textContent = "Shifted! We'll get back to you within two business days."; }
      }, 700);
    });
  }

  /* Reveal story beats */
  var reveals = document.querySelectorAll(".reveal");
  if (reveals.length) {
    if (reduce || !("IntersectionObserver" in window)) {
      reveals.forEach(function (el) { el.classList.add("in"); });
    } else {
      var io = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
      }, { threshold: 0.18, rootMargin: "0px 0px -8% 0px" });
      reveals.forEach(function (el) { io.observe(el); });
    }
  }

  /* --- Dashboard + parallax driven by scroll --- */
  var panels = Array.prototype.slice.call(document.querySelectorAll(".panel"));
  var topbar = document.querySelector(".topbar");
  var knob = document.querySelector(".gate .knob");
  var needle = document.querySelector(".tach .needle");
  var gearNo = document.querySelector(".readout .gear-no");
  var gearName = document.querySelector(".readout .gear-name");
  var root = document.documentElement;

  /* H-pattern positions for a 6-speed gate (viewBox 120x90) */
  var gate = { N: [60, 45], "1": [30, 12], "2": [30, 78], "3": [60, 12], "4": [60, 78], "5": [90, 12], "6": [90, 78] };
  var NEEDLE_MIN = -82, NEEDLE_MAX = 82; /* degrees */

  var lastGear = null, ticking = false;

  function render() {
    ticking = false;
    var vh = window.innerHeight;
    var sy = window.pageYOffset;
    var focus = sy + vh * 0.45;

    if (topbar) topbar.classList.toggle("scrolled", sy > 8);

    /* Active panel = last one whose top is above the focus line */
    var active = panels[0];
    for (var i = 0; i < panels.length; i++) {
      if (panels[i].offsetTop <= focus) active = panels[i];
    }
    if (!active) return;

    var g = active.getAttribute("data-gear") || "N";
    var color = active.getAttribute("data-accent") || "#2f9bff";
    var name = active.getAttribute("data-name") || "";

    if (g !== lastGear) {
      lastGear = g;
      root.style.setProperty("--accent", color);
      if (knob) { var p = gate[g] || gate.N; knob.style.transform = "translate(" + p[0] + "px," + p[1] + "px)"; }
      if (gearNo) gearNo.textContent = g;
      if (gearName) gearName.textContent = name;
    }

    /* Tach revs with progress through the active panel */
    if (needle) {
      var top = active.offsetTop, h = active.offsetHeight || vh;
      var prog = (focus - top) / h; if (prog < 0) prog = 0; if (prog > 1) prog = 1;
      var angle = NEEDLE_MIN + prog * (NEEDLE_MAX - NEEDLE_MIN);
      needle.style.transform = "rotate(" + angle.toFixed(1) + "deg)";
    }

    /* Parallax: ghosts drift slower than the text */
    if (!reduce) {
      for (var j = 0; j < panels.length; j++) {
        var ghost = panels[j].querySelector(".ghost");
        if (!ghost) continue;
        var rel = sy - panels[j].offsetTop;
        if (rel > -vh * 1.5 && rel < vh * 1.5) {
          ghost.style.transform = "translate(-50%, -50%) translateY(" + (rel * 0.3).toFixed(1) + "px)";
        }
      }
    }
  }

  function onScroll() {
    if (!ticking) { ticking = true; window.requestAnimationFrame(render); }
  }

  if (panels.length) {
    render();
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    window.addEventListener("load", render);
  }
})();
