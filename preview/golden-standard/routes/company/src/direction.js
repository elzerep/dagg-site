(function () {
  "use strict";
  var root = document.querySelector("[data-company]");
  if (!root) return;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    root.setAttribute("data-company-ready", "");
    return;
  }
  window.requestAnimationFrame(function () {
    window.requestAnimationFrame(function () {
      root.setAttribute("data-company-ready", "");
    });
  });
})();
