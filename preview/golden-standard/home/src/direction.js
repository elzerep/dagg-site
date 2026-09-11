/* Dagg golden standard - Home execution instrument (FS5 Lane A)
 *
 * Progressive enhancement only. The static document already carries the
 * identity, the Request, all four states in source order and the resolved
 * status `Human decision recorded. Release remains withheld.`; Pause, Resume
 * and Replay exist as static controls hidden while inert. This script only
 * animates the finite sequence and exposes its state.
 *
 * Runtime state (FS5 §4 motion repair):
 *   phase        ready | running | paused | complete   -> data-home-sequence
 *   index        0..3                                  -> data-home-state-index
 *   userPaused   explicit Pause; authoritative until explicit Resume
 *   suspended    {viewport, visibility, hover, focus}; each source clears
 *                only itself; explicit Resume also clears hover and focus.
 * A timer runs only while phase is running, userPaused is false and the
 * suspension set is empty. Holding preserves the remaining interval so the
 * exact 1.6 s + 2.2 s + 2.2 s cadence is not restarted by a hover.
 * Reduced motion and a missing IntersectionObserver resolve immediately and
 * hide Replay (R8). Status copy uses only the four manifest states.
 */
(function () {
  "use strict";

  var root = document.querySelector("[data-home]");
  if (!root) return;
  var carrier = root.querySelector("[data-home-execution]");
  if (!carrier) return;

  var list = carrier.querySelector("[data-home-execution-states]");
  var states = Array.prototype.slice.call(
    carrier.querySelectorAll("[data-home-execution-state]")
  );
  var status = carrier.querySelector("[data-home-execution-status]");
  var controls = carrier.querySelector("[data-home-execution-controls]");
  var pauseButton = carrier.querySelector("[data-home-pause]");
  var replayButton = carrier.querySelector("[data-home-replay]");
  if (states.length !== 4 || !list || !status || !controls || !pauseButton || !replayButton) {
    return;
  }

  var STATUS = {
    initial: "Ready to inspect the operating change",
    running: "Operating change in progress",
    paused: "Operating change paused",
    resolved: "Human decision recorded. Release remains withheld."
  };
  var INTERVALS = [1600, 2200, 2200];
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  var phase = "ready";
  var index = -1;
  var timer = 0;
  var stepStarted = 0;
  var remaining = 0;
  var userPaused = false;
  var suspended = { viewport: false, visibility: false, hover: false, focus: false };
  var resolvedForReduce = false;

  carrier.setAttribute("data-home-enhanced", "");

  function now() {
    return window.performance && typeof window.performance.now === "function"
      ? window.performance.now()
      : Date.now();
  }

  function setStatus(id) {
    status.textContent = STATUS[id];
    status.setAttribute("data-copy-state", id);
  }

  function setPauseLabel(resume) {
    pauseButton.textContent = resume ? "Resume sequence" : "Pause sequence";
    pauseButton.setAttribute("data-copy-state", resume ? "resume" : "pause");
  }

  function setPhase(next) {
    phase = next;
    carrier.setAttribute("data-home-sequence", next);
  }

  function paint(current, complete) {
    carrier.setAttribute("data-home-state-index", String(current));
    states.forEach(function (state, i) {
      var value = complete ? "done" : (i < current ? "done" : (i === current ? "current" : "pending"));
      if (complete && i === current) value = "current";
      state.setAttribute("data-home-phase", value);
    });
  }

  function heldBySource() {
    return suspended.viewport || suspended.visibility || suspended.hover || suspended.focus;
  }

  function hold() {
    if (!timer) return;
    window.clearTimeout(timer);
    timer = 0;
    remaining = Math.max(0, remaining - (now() - stepStarted));
  }

  function schedule() {
    if (timer || phase === "complete" || phase === "ready") return;
    if (userPaused || heldBySource()) return;
    stepStarted = now();
    timer = window.setTimeout(advance, remaining);
  }

  function reflect() {
    if (phase === "ready" || phase === "complete") return;
    if (userPaused || heldBySource()) {
      hold();
      if (phase !== "paused") {
        setPhase("paused");
        setStatus("paused");
      }
      return;
    }
    if (phase !== "running") {
      setPhase("running");
      setStatus("running");
    }
    schedule();
  }

  function advance() {
    timer = 0;
    index += 1;
    if (index >= states.length - 1) {
      complete();
      return;
    }
    paint(index, false);
    remaining = INTERVALS[index];
    schedule();
  }

  function complete() {
    hold();
    index = states.length - 1;
    paint(index, true);
    setPhase("complete");
    status.setAttribute("aria-live", "polite");
    setStatus("resolved");
    pauseButton.hidden = true;
    setPauseLabel(false);
    replayButton.hidden = resolvedForReduce;
    controls.hidden = resolvedForReduce;
  }

  function start() {
    hold();
    userPaused = false;
    suspended.hover = false;
    suspended.focus = false;
    index = 0;
    remaining = INTERVALS[0];
    status.setAttribute("aria-live", "off");
    paint(index, false);
    controls.hidden = false;
    pauseButton.hidden = false;
    replayButton.hidden = true;
    setPauseLabel(false);
    setPhase("running");
    setStatus("running");
    reflect();
  }

  function resolveImmediately() {
    resolvedForReduce = true;
    hold();
    complete();
  }

  /* Initial enhanced state: ready, status initial, controls inert and hidden. */
  setPhase("ready");
  carrier.removeAttribute("data-home-state-index");
  states.forEach(function (state) { state.setAttribute("data-home-phase", "pending"); });
  status.setAttribute("aria-live", "off");
  setStatus("initial");
  setPauseLabel(false);
  pauseButton.hidden = true;
  replayButton.hidden = true;
  controls.hidden = true;

  pauseButton.addEventListener("click", function () {
    if (phase === "complete" || phase === "ready") return;
    if (userPaused) {
      userPaused = false;
      suspended.hover = false;
      suspended.focus = false;
      setPauseLabel(false);
    } else {
      userPaused = true;
      setPauseLabel(true);
    }
    reflect();
  });

  replayButton.addEventListener("click", function () {
    if (phase !== "complete" || resolvedForReduce) return;
    start();
  });

  /* Pointer hover over the moving state list suspends; touch never does.
     Pause and Replay live outside the list, so they are excluded by geometry. */
  list.addEventListener("pointerenter", function (event) {
    if (event.pointerType === "touch") return;
    suspended.hover = true;
    reflect();
  });
  list.addEventListener("pointerleave", function (event) {
    if (event.pointerType === "touch") return;
    suspended.hover = false;
    reflect();
  });

  /* Focus suspension applies only to an already-interactive descendant of the
     moving carrier. The state rows themselves are never made focusable. */
  list.addEventListener("focusin", function () {
    suspended.focus = true;
    reflect();
  });
  list.addEventListener("focusout", function (event) {
    if (event.relatedTarget && list.contains(event.relatedTarget)) return;
    suspended.focus = false;
    reflect();
  });

  document.addEventListener("visibilitychange", function () {
    suspended.visibility = document.visibilityState === "hidden";
    reflect();
  });

  function onReduceChange() {
    if (reduceMotion.matches) resolveImmediately();
  }
  if (typeof reduceMotion.addEventListener === "function") {
    reduceMotion.addEventListener("change", onReduceChange);
  } else if (typeof reduceMotion.addListener === "function") {
    reduceMotion.addListener(onReduceChange);
  }

  if (reduceMotion.matches || typeof window.IntersectionObserver !== "function") {
    resolveImmediately();
    return;
  }

  var observer = new window.IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (phase === "ready") {
        if (entry.isIntersecting && entry.intersectionRatio >= 0.35) {
          suspended.viewport = false;
          start();
        }
        return;
      }
      if (phase === "complete") return;
      suspended.viewport = !entry.isIntersecting;
      reflect();
    });
  }, { threshold: [0, 0.35] });

  observer.observe(carrier);
})();
