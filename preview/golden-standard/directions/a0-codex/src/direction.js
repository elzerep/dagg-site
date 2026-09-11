/* Direction A0 Codex — one finite editorial resolution and local no-JS-safe controls. */
(function () {
  "use strict";

  function init() {
    var hero = document.querySelector("[data-a-hero-motion]");
    var surfaceControls = document.querySelector("[data-a-surface-controls]");
    var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

    if (surfaceControls) {
      surfaceControls.hidden = false;
    }

    if (!hero) {
      return;
    }

    if (reduceMotion.matches) {
      hero.classList.add("a-motion-resolved");
      return;
    }

    hero.classList.add("a-motion-armed");
    window.requestAnimationFrame(function () {
      window.requestAnimationFrame(function () {
        hero.classList.add("a-motion-resolved");
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
