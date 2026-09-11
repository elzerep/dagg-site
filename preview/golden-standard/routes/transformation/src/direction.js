/* Dagg golden standard - Transformation enhancement (FS5 Lane A)
 *
 * Progressive only. Without this script the page is complete: the hero is a
 * resolved still, all five outcomes read in order and no inert control exists.
 *
 *  - One finite hero settle, skipped under reduced motion.
 *  - Decision continuum mode, written to data-transformation-mode:
 *      scroll  >= 1180 px, hover-capable fine pointer, motion allowed: five
 *              stations on one rule with one readout; page scroll advances
 *              Preserve -> Retire and back until a direct selection becomes
 *              authoritative for the page view.
 *      manual  everything else, including reduced motion, coarse pointers,
 *              missing :has() support and widths below 1180 px: all five
 *              explanations stay visible in order and the group remains
 *              selectable.
 *  - Reduced motion or a missing capability resolves the route
 *    (data-transformation-resolved) in manual mode.
 * Announcement of a selected outcome belongs to the shared component script.
 */
(function () {
  "use strict";

  var root = document.querySelector("[data-transformation]");
  if (!root) return;

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  var scrollControl = window.matchMedia("(min-width: 1180px) and (hover: hover) and (pointer: fine)");
  var hero = root.querySelector(".transformation-hero");
  var stage = root.querySelector("[data-transformation-stage]");
  var continuum = root.querySelector("[data-transformation-continuum]");

  if (hero) {
    if (reduceMotion.matches || typeof window.requestAnimationFrame !== "function") {
      root.setAttribute("data-transformation-ready", "");
    } else {
      window.requestAnimationFrame(function () {
        window.requestAnimationFrame(function () {
          root.setAttribute("data-transformation-ready", "");
        });
      });
    }
  }

  if (!stage || !continuum || !document.documentElement.classList.contains("cl-enhanced")) return;

  var inputs = Array.prototype.slice.call(continuum.querySelectorAll('input[name="outcome"]'));
  var hasSupport = typeof CSS !== "undefined" && typeof CSS.supports === "function" &&
    CSS.supports("selector(:has(*))");
  var resolved = false;
  var frame = 0;
  var selected = -1;
  var userOwned = false;

  function resolveAll() {
    if (frame) window.cancelAnimationFrame(frame);
    frame = 0;
    resolved = true;
    root.setAttribute("data-transformation-resolved", "");
    root.setAttribute("data-transformation-mode", "manual");
  }

  if (inputs.length !== 5 || typeof window.requestAnimationFrame !== "function" || !hasSupport) {
    resolveAll();
    return;
  }

  function applyMode() {
    if (resolved) return;
    var scroll = scrollControl.matches && !reduceMotion.matches;
    root.setAttribute("data-transformation-mode", scroll ? "scroll" : "manual");
  }

  function choose(index) {
    var next = Math.max(0, Math.min(inputs.length - 1, index));
    if (next === selected) return;
    inputs[next].checked = true;
    selected = next;
  }

  function updateFromScroll() {
    frame = 0;
    if (reduceMotion.matches) {
      resolveAll();
      return;
    }
    if (userOwned || !scrollControl.matches) return;
    var rect = stage.getBoundingClientRect();
    var viewport = Math.max(window.innerHeight || 0, 1);
    var travel = Math.max(stage.offsetHeight - viewport, 1);
    var progress = Math.max(0, Math.min(1, -rect.top / travel));
    choose(Math.min(inputs.length - 1, Math.floor(progress * inputs.length)));
  }

  function queueUpdate() {
    applyMode();
    if (frame || resolved) return;
    frame = window.requestAnimationFrame(updateFromScroll);
  }

  inputs.forEach(function (input, index) {
    input.addEventListener("change", function () {
      userOwned = true;
      selected = index;
    });
  });

  if (reduceMotion.matches) {
    resolveAll();
    return;
  }

  applyMode();
  window.addEventListener("scroll", queueUpdate, { passive: true });
  window.addEventListener("resize", queueUpdate, { passive: true });
  if (typeof reduceMotion.addEventListener === "function") {
    reduceMotion.addEventListener("change", function () {
      if (reduceMotion.matches) resolveAll();
      else queueUpdate();
    });
  }
  if (typeof scrollControl.addEventListener === "function") {
    scrollControl.addEventListener("change", queueUpdate);
  }
  if (scrollControl.matches) queueUpdate();
})();
