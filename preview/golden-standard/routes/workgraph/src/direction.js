/* WorkGraph route enhancement (FS5 Lane B).
 *
 *   1. Context still: one finite editorial settle that starts only when the
 *      Context section enters view. Reduced motion or a missing observer
 *      resolve the still immediately.
 *   2. Source lenses: inspection only. Every record field is visible before a
 *      lens is used; a lens emphasizes, it never reveals or hides. The initial
 *      Meeting state and its status are authored in HTML; script changes them
 *      only after a real pointer, keyboard or touch selection.
 *   3. FS2 scroll-led lifecycle carrier: the active state is a pure function
 *      of scroll position (the last step whose top edge has crossed the 45 %
 *      focus line), so it advances and reverses deterministically. Reduced
 *      motion and a missing IntersectionObserver resolve on Learn. Without
 *      JavaScript the authored resolved state and every label remain.
 */
(function () {
  "use strict";

  var root = document.querySelector("[data-workgraph-page]") || document.querySelector("[data-workgraph]");
  if (!root) return;

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  var hasObserver = typeof window.IntersectionObserver === "function";

  function slice(nodes) {
    return Array.prototype.slice.call(nodes);
  }

  function onMediaChange(query, handler) {
    if (typeof query.addEventListener === "function") {
      query.addEventListener("change", handler);
    } else if (typeof query.addListener === "function") {
      query.addListener(handler);
    }
  }

  /* ------------------------------------------------------------------ *
   * Context still settle                                                 *
   * ------------------------------------------------------------------ */

  var contextSection = root.querySelector('[data-workgraph-section="record"]');
  function settleContext() {
    root.setAttribute("data-workgraph-ready", "");
  }
  if (reduceMotion.matches || !hasObserver || !contextSection) {
    settleContext();
  } else {
    var settle = new window.IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        settle.disconnect();
        window.requestAnimationFrame(function () {
          window.requestAnimationFrame(settleContext);
        });
      });
    }, { threshold: 0.2 });
    settle.observe(contextSection);
  }

  /* ------------------------------------------------------------------ *
   * Source lenses                                                        *
   * ------------------------------------------------------------------ */

  var LENS_STATUS = {
    "meeting": "Meeting source highlights the fields retained from that source",
    "document": "Document source highlights the fields retained from that source",
    "system-state": "System state source highlights operating state and permission"
  };

  var controls = slice(root.querySelectorAll("[data-source-lens]"));
  var fields = slice(root.querySelectorAll("[data-source-field]"));
  var lensStatus = root.querySelector("[data-workgraph-lens-status]");

  function selectLens(lens) {
    controls.forEach(function (control) {
      control.setAttribute("aria-pressed", control.getAttribute("data-source-lens") === lens ? "true" : "false");
    });
    fields.forEach(function (field) {
      var sources = (field.getAttribute("data-source-field") || "").split(/\s+/);
      field.classList.toggle("workgraph-record__field--emphasized", sources.indexOf(lens) !== -1);
    });
    if (lensStatus && LENS_STATUS[lens]) {
      lensStatus.setAttribute("data-copy-state", lens);
      lensStatus.textContent = LENS_STATUS[lens];
    }
  }

  /* Emphasis for the authored Meeting state is applied as a class only; the
     pressed state and status text are already in the document. */
  fields.forEach(function (field) {
    var sources = (field.getAttribute("data-source-field") || "").split(/\s+/);
    field.classList.toggle("workgraph-record__field--emphasized", sources.indexOf("meeting") !== -1);
  });

  controls.forEach(function (control) {
    control.addEventListener("click", function () {
      selectLens(control.getAttribute("data-source-lens"));
    });
  });

  /* ------------------------------------------------------------------ *
   * FS2 scroll-led lifecycle carrier                                     *
   * ------------------------------------------------------------------ */

  var FOCUS_LINE = 0.45;
  var STATE_COPY = {
    connect: "Observed / Connect",
    decide: "Decided / Decide",
    build: "Built / Build",
    learn: "Evidenced / Learn"
  };

  var section = root.querySelector('[data-workgraph-section="lifecycle"]');
  var steps = slice(root.querySelectorAll("[data-workgraph-step]"));
  var marks = slice(root.querySelectorAll("[data-workgraph-state]"));
  var carrier = root.querySelector("[data-workgraph-record-state]");
  var carrierStatus = root.querySelector("[data-workgraph-record-status]");
  if (!section || !carrier || !carrierStatus || steps.length !== 4) return;

  var active = -1;

  function paint(index) {
    if (index === active) return;
    active = index;
    var key = steps[index].getAttribute("data-workgraph-step");
    steps.forEach(function (step, i) {
      step.classList.toggle("is-active", i === index);
      step.classList.toggle("is-done", i < index);
      if (i === index) step.setAttribute("aria-current", "step");
      else step.removeAttribute("aria-current");
    });
    marks.forEach(function (mark, i) {
      mark.classList.toggle("is-active", i === index);
      mark.classList.toggle("is-done", i < index);
    });
    carrier.setAttribute("data-workgraph-active-state", key);
    if (carrierStatus.getAttribute("data-copy-state") !== key) {
      carrierStatus.setAttribute("data-copy-state", key);
      carrierStatus.textContent = STATE_COPY[key];
    }
  }

  function resolve() {
    paint(steps.length - 1);
    carrier.setAttribute("data-workgraph-carrier-mode", "resolved");
  }

  if (reduceMotion.matches || !hasObserver) {
    resolve();
    return;
  }

  carrier.setAttribute("data-workgraph-carrier-mode", "scroll");

  function measure() {
    var line = window.innerHeight * FOCUS_LINE;
    var index = -1;
    steps.forEach(function (step, i) {
      if (step.getBoundingClientRect().top <= line) index = i;
    });
    paint(Math.max(0, index));
  }

  var scheduled = false;
  function onScroll() {
    if (scheduled) return;
    scheduled = true;
    window.requestAnimationFrame(function () {
      scheduled = false;
      measure();
    });
  }

  var listening = false;
  function listen(on) {
    if (on === listening) return;
    listening = on;
    if (on) {
      window.addEventListener("scroll", onScroll, { passive: true });
      window.addEventListener("resize", onScroll);
    } else {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
    }
  }

  /* The scroll listener runs only while the lifecycle section is near the
     viewport. Above the section the carrier reads Observed / Connect; below
     it the state stays at Evidenced / Learn. */
  var observer = new window.IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      listen(entry.isIntersecting);
      measure();
    });
  }, { rootMargin: "25% 0px 25% 0px", threshold: 0 });
  observer.observe(section);
  measure();

  onMediaChange(reduceMotion, function (event) {
    if (!event.matches) return;
    observer.disconnect();
    listen(false);
    resolve();
  });
})();
