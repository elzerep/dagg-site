/* Trust route enhancement (FS5 Lane B).
 *
 * The control-path band performs one finite settle in semantic order and then
 * holds. The settle starts only when the band enters view, so it cannot finish
 * invisibly during page load. Reduced motion or a missing IntersectionObserver
 * resolve immediately; without JavaScript the CSS already shows the resolved
 * band. The sole state string is authored in HTML and never rewritten here.
 */
(function () {
  "use strict";

  var root = document.querySelector("[data-trust]");
  if (!root) return;
  var band = root.querySelector("[data-trust-control]");

  function settle() {
    root.setAttribute("data-trust-ready", "");
  }

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  if (reduceMotion.matches || typeof window.IntersectionObserver !== "function" || !band) {
    settle();
    return;
  }

  var observer = new window.IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      observer.disconnect();
      window.requestAnimationFrame(function () {
        window.requestAnimationFrame(settle);
      });
    });
  }, { threshold: 0.25 });
  observer.observe(band);

  if (typeof reduceMotion.addEventListener === "function") {
    reduceMotion.addEventListener("change", function (event) {
      if (!event.matches) return;
      observer.disconnect();
      settle();
    });
  }
})();
