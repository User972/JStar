/* ============================================================================
   J Star Technologies — interactive behaviors (vanilla JS, no framework)

   Replaces the design prototype's React/Babel runtime so the site ships as
   plain static files. Powers four behaviors; each initializer is a no-op when
   its markup isn't on the page, so this one script serves every page.

     1. scroll-reveal     — transform-only entrance (content is never hidden)
     2. persona toggle    — Home "who we work with" switcher
     3. tech-stack filter  — Home filterable technology grid
     4. pipeline           — Zero-to-Ten auto-advancing interactive pipeline
============================================================================ */
(function () {
  'use strict';

  var slice = function (nl) { return Array.prototype.slice.call(nl); };

  /* ---- 1. scroll reveal --------------------------------------------------
     Mirrors the prototype's useReveal: reveal anything already in view on
     load, animate genuine scroll entrances via IntersectionObserver, with a
     scroll-listener + timeout backstop so content can never stay hidden. */
  function initReveal() {
    var els = slice(document.querySelectorAll('.reveal'));
    if (!els.length) return;
    var reveal = function (e) { e.classList.add('in'); };
    var inView = function (e) {
      var r = e.getBoundingClientRect();
      var vh = window.innerHeight || document.documentElement.clientHeight;
      return r.top < vh * 0.9 && r.bottom > 0;
    };
    var sweep = function () {
      var remaining = false;
      els.forEach(function (e) {
        if (e.classList.contains('in')) return;
        if (inView(e)) reveal(e); else remaining = true;
      });
      return remaining;
    };
    sweep(); // immediate — covers everything in the initial viewport

    if (!('IntersectionObserver' in window)) { els.forEach(reveal); return; }
    var io = new IntersectionObserver(function (ents) {
      ents.forEach(function (x) {
        if (x.isIntersecting) { reveal(x.target); io.unobserve(x.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
    els.forEach(function (e) { if (!e.classList.contains('in')) io.observe(e); });

    var onScroll = function () { if (!sweep()) window.removeEventListener('scroll', onScroll); };
    window.addEventListener('scroll', onScroll, { passive: true });
    setTimeout(function () { els.forEach(reveal); }, 2500); // last-resort safety net
  }

  /* ---- 2. persona toggle (Home) ----------------------------------------- */
  function initPersona() {
    var toggle = document.querySelector('.persona-toggle');
    var panel = document.querySelector('.persona-panel');
    if (!toggle || !panel) return;
    var btns = slice(toggle.querySelectorAll('.persona-btn'));

    function select(btn) {
      btns.forEach(function (b) { b.classList.toggle('on', b === btn); });
      // Rebuilding innerHTML mounts a fresh .persona-fade, restarting its fade.
      panel.innerHTML =
        '<div class="persona-fade">' +
          '<div class="pline"></div>' +
          '<p class="pbody"></p>' +
          '<div class="pproof"><span class="star-glyph">★</span> <span class="pproof-t"></span></div>' +
        '</div>';
      panel.querySelector('.pline').textContent = btn.getAttribute('data-line');
      panel.querySelector('.pbody').textContent = btn.getAttribute('data-body');
      panel.querySelector('.pproof-t').textContent = btn.getAttribute('data-proof');
    }
    btns.forEach(function (b) {
      b.addEventListener('click', function () { select(b); });
    });
  }

  /* ---- 3. tech-stack filter (Home) -------------------------------------- */
  function initTechFilter() {
    var filters = document.querySelector('.stack-filters');
    var grid = document.querySelector('.stack-grid');
    if (!filters || !grid) return;
    var chips = slice(filters.querySelectorAll('.fchip'));
    var tiles = slice(grid.querySelectorAll('.tech'));

    chips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        var cat = chip.getAttribute('data-cat'); // null/'' on the ALL chip
        chips.forEach(function (c) { c.classList.toggle('on', c === chip); });
        tiles.forEach(function (t) {
          t.classList.toggle('dim', !!cat && t.getAttribute('data-cat') !== cat);
        });
      });
    });
  }

  /* ---- 4. Zero-to-Ten pipeline ------------------------------------------ */
  function initPipeline() {
    var pipe = document.querySelector('.pipeline');
    if (!pipe) return;
    var nodes = slice(pipe.querySelectorAll('.pipe-node'));
    var details = slice(pipe.querySelectorAll('.pipe-detail'));
    var fill = pipe.querySelector('.pipe-line i');
    var stage = pipe.querySelector('.pipe-stage');
    var playBtn = pipe.querySelector('.pipe-play');
    var n = nodes.length;
    if (!n) return;

    var active = 0, playing = true, seen = false, timer = null;

    function paint() {
      nodes.forEach(function (nd, i) {
        nd.classList.toggle('on', i === active);
        nd.classList.toggle('done', i < active);
      });
      if (fill) fill.style.width = (active / (n - 1)) * 100 + '%';
      details.forEach(function (d, i) { d.style.display = (i === active) ? '' : 'none'; });
      if (stage) stage.textContent = 'STAGE ' + (active + 1) + ' / ' + n;
      if (playBtn) playBtn.textContent = playing ? '❚❚ Pause' : '▶ Play';
    }
    function fade() { // restart the active panel's entrance animation
      var d = details[active];
      if (!d) return;
      d.classList.remove('pipe-fade');
      void d.offsetWidth; // force reflow
      d.classList.add('pipe-fade');
    }
    function schedule() {
      clearTimeout(timer);
      if (!playing || !seen) return;
      timer = setTimeout(function () {
        active = (active + 1) % n;
        paint(); fade(); schedule();
      }, 4200);
    }
    function go(i, stop) { // jump to a stage (active changes → fade)
      active = i;
      if (stop) playing = false;
      paint(); fade(); schedule();
    }

    nodes.forEach(function (nd, i) {
      nd.addEventListener('click', function () { go(i, true); });
    });
    if (playBtn) playBtn.addEventListener('click', function () {
      playing = !playing; paint(); schedule();
    });
    pipe.addEventListener('mouseenter', function () { playing = false; clearTimeout(timer); paint(); });
    pipe.addEventListener('mouseleave', function () { playing = true; paint(); schedule(); });

    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (e) {
        if (e[0].isIntersecting) { seen = true; schedule(); io.disconnect(); }
      }, { threshold: 0.3 });
      io.observe(pipe);
    } else { seen = true; schedule(); }

    paint();
  }

  function init() {
    initReveal();
    initPersona();
    initTechFilter();
    initPipeline();
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
