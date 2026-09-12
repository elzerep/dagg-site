/* Build route enhancement (FS5 Lane B).
 *
 *   1. Plan inspection: two pressed-button selectors reveal one plan detail at
 *      a time. A reader-selected plan is never reset by the pass.
 *   2. Finite Factory pass (FS2 carrier, retained): one pass starts when the
 *      sentinel enters the upper 60 percent of the viewport, advances
 *      Intervention -> Specification -> Architecture -> Build -> Evaluation ->
 *      Governed review, holds visibly at judgment and verification, stops on
 *      Governed review and never restarts by itself. Temporary interruptions
 *      (offscreen, hidden document, non-touch hover over the stages, focus on
 *      an interactive descendant) suspend the timer and clear only themselves;
 *      explicit Pause is authoritative until explicit Resume.
 *   3. Pause, Resume, Replay and Inspect are static controls; this file only
 *      toggles their visibility and exact copy state. Reduced motion and a
 *      missing IntersectionObserver resolve to Governed review immediately and
 *      offer Inspect instead of playback. Without JavaScript the authored
 *      resolved status and all six stages are already in the document.
 */
(function () {
  "use strict";

  var root = document.querySelector("[data-build]");
  if (!root) return;

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  var narrow = window.matchMedia("(max-width: 939.98px)");
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

  function setCopy(element, state, text) {
    if (element.getAttribute("data-copy-state") !== state) {
      element.setAttribute("data-copy-state", state);
    }
    if (element.textContent !== text) {
      element.textContent = text;
    }
  }

  /* ------------------------------------------------------------------ *
   * Plan inspection                                                      *
   * ------------------------------------------------------------------ */

  var selectors = slice(root.querySelectorAll("[data-build-plan-select]"));
  var summaries = slice(root.querySelectorAll("[data-build-plan-summary]"));
  var plans = slice(root.querySelectorAll("[data-build-plan]"));

  function selectPlan(name) {
    selectors.forEach(function (button) {
      button.setAttribute("aria-pressed", button.getAttribute("data-build-plan-select") === name ? "true" : "false");
    });
    summaries.forEach(function (summary) {
      summary.classList.toggle("build-plan-summary--selected", summary.getAttribute("data-build-plan-summary") === name);
    });
    plans.forEach(function (plan) {
      var selected = plan.getAttribute("data-build-plan") === name;
      plan.classList.toggle("build-plan--selected", selected);
      if (selected) plan.removeAttribute("aria-hidden");
      else plan.setAttribute("aria-hidden", "true");
    });
  }

  selectors.forEach(function (button) {
    button.addEventListener("click", function () {
      selectPlan(button.getAttribute("data-build-plan-select"));
    });
  });
  if (selectors.length) selectPlan("automate");

  /* ------------------------------------------------------------------ *
   * Finite Factory pass                                                  *
   * ------------------------------------------------------------------ */

  var STEP_WIDE_MS = 880;
  var HOLD_WIDE_MS = 950;
  var STEP_NARROW_MS = 580;
  var HOLD_NARROW_MS = 650;
  var HOLD_STAGES = { intervention: true, evaluation: true };
  var STATUS_COPY = {
    initial: "",
    intervention: "Judgment hold",
    specification: "Specification",
    architecture: "Architecture",
    build: "Build",
    evaluation: "Verification hold",
    paused: "Factory pass paused",
    resolved: "Governed review complete"
  };
  var PAUSE_COPY = { pause: "Pause sequence", resume: "Resume sequence" };
  var INTERACTIVE = "a[href],button,input,select,textarea,summary,[tabindex]";

  var progress = root.querySelector("[data-build-factory-progress]");
  var sentinel = root.querySelector("[data-build-factory-sentinel]");
  var stageList = root.querySelector("[data-build-factory-stages]");
  var stages = slice(root.querySelectorAll("[data-build-stage]"));
  var pauseButton = root.querySelector("[data-build-pause]");
  var replayButton = root.querySelector("[data-build-replay]");
  var inspectButton = root.querySelector("[data-build-inspect]");
  var status = root.querySelector("[data-build-status]");
  if (!progress || !sentinel || !stageList || stages.length !== 6 ||
      !pauseButton || !replayButton || !inspectButton || !status) {
    return;
  }

  var LAST = stages.length - 1;
  var phase = "idle";          /* idle | running | complete */
  var index = -1;
  var timer = null;
  var userPaused = false;
  var suspended = { offscreen: false, hover: false, focus: false, hidden: false };

  progress.setAttribute("tabindex", "-1");

  function isSuspended() {
    return suspended.offscreen || suspended.hover || suspended.focus || suspended.hidden;
  }

  function clearTimer() {
    if (timer !== null) {
      window.clearTimeout(timer);
      timer = null;
    }
  }

  function stageKey(i) {
    return stages[i].getAttribute("data-build-stage");
  }

  function paintStage(nextIndex) {
    index = nextIndex;
    stages.forEach(function (stage, i) {
      var isActive = i === index;
      stage.classList.toggle("build-stage--active", isActive);
      stage.classList.toggle("build-stage--done", i < index || (index === LAST && i === LAST));
      if (isActive) stage.setAttribute("aria-current", "step");
      else stage.removeAttribute("aria-current");
    });
    progress.setAttribute("data-build-signal-stage", stageKey(index));
    var key = index === LAST ? "resolved" : stageKey(index);
    setCopy(status, key, STATUS_COPY[key]);
  }

  function setControls() {
    var resolvedByPreference = reduceMotion.matches || !hasObserver;
    pauseButton.hidden = phase !== "running";
    replayButton.hidden = !(phase === "complete" && !resolvedByPreference);
    inspectButton.hidden = !resolvedByPreference;
    var pauseState = userPaused ? "resume" : "pause";
    setCopy(pauseButton, pauseState, PAUSE_COPY[pauseState]);
    pauseButton.setAttribute("aria-pressed", userPaused ? "true" : "false");
    progress.setAttribute("data-build-pass", userPaused ? "paused" : phase);
  }

  function complete() {
    clearTimer();
    phase = "complete";
    userPaused = false;
    status.setAttribute("aria-live", "polite");
    paintStage(LAST);
    setControls();
  }

  function schedule() {
    if (phase !== "running" || userPaused || isSuspended() || timer !== null) return;
    var hold = HOLD_STAGES[stageKey(index)] === true;
    var delay = narrow.matches
      ? (hold ? HOLD_NARROW_MS : STEP_NARROW_MS)
      : (hold ? HOLD_WIDE_MS : STEP_WIDE_MS);
    timer = window.setTimeout(advance, delay);
  }

  function advance() {
    timer = null;
    if (phase !== "running") return;
    if (index >= LAST - 1) {
      complete();
      return;
    }
    paintStage(index + 1);
    schedule();
  }

  function start() {
    if (phase === "running") return;
    clearTimer();
    phase = "running";
    userPaused = false;
    status.setAttribute("aria-live", "off");
    stages.forEach(function (stage) {
      stage.classList.remove("build-stage--active", "build-stage--done");
      stage.removeAttribute("aria-current");
    });
    paintStage(0);
    setControls();
    schedule();
  }

  /* Temporary interruptions suspend; their end resumes unless the reader
     explicitly paused. Each source clears only itself. */
  function suspend(key, on) {
    if (suspended[key] === on) return;
    suspended[key] = on;
    if (on) clearTimer();
    else schedule();
  }

  pauseButton.addEventListener("click", function () {
    if (phase !== "running") return;
    userPaused = !userPaused;
    if (userPaused) {
      clearTimer();
      status.setAttribute("aria-live", "polite");
      setCopy(status, "paused", STATUS_COPY.paused);
    } else {
      /* Explicit Resume is reader intent: the pointer or focus that is
         necessarily on this control must not immediately re-suspend. */
      suspended.hover = false;
      suspended.focus = false;
      status.setAttribute("aria-live", "off");
      paintStage(index);
      schedule();
    }
    setControls();
  });

  replayButton.addEventListener("click", function () {
    if (phase !== "complete") return;
    phase = "idle";
    start();
  });

  inspectButton.addEventListener("click", function () {
    complete();
    progress.focus({ preventScroll: false });
  });

  /* Hover and focus on the moving part of the carrier suspend it. The stage
     list is the moving part; the controls are excluded so Pause and Resume
     remain operable under the pointer. */
  stageList.addEventListener("pointerenter", function (event) {
    if (event.pointerType === "touch") return;
    suspend("hover", true);
  });
  stageList.addEventListener("pointerleave", function (event) {
    if (event.pointerType === "touch") return;
    suspend("hover", false);
  });
  progress.addEventListener("focusin", function (event) {
    var target = event.target;
    if (!target || typeof target.closest !== "function") return;
    var control = target.closest(INTERACTIVE);
    if (!control || !progress.contains(control)) return;
    if (pauseButton.contains(control) || replayButton.contains(control) || inspectButton.contains(control)) return;
    suspend("focus", true);
  });
  progress.addEventListener("focusout", function (event) {
    if (event.relatedTarget && progress.contains(event.relatedTarget)) return;
    suspend("focus", false);
  });
  document.addEventListener("visibilitychange", function () {
    suspend("hidden", document.hidden === true);
  });

  onMediaChange(reduceMotion, function (event) {
    if (!event.matches) return;
    clearTimer();
    complete();
  });

  if (reduceMotion.matches || !hasObserver) {
    complete();
    return;
  }

  /* Enhanced idle state: the pass has not started, so the status is empty. */
  progress.setAttribute("data-build-signal-stage", "");
  setControls();
  status.setAttribute("aria-live", "off");
  setCopy(status, "initial", STATUS_COPY.initial);
  stages.forEach(function (stage) {
    stage.classList.remove("build-stage--active", "build-stage--done");
    stage.removeAttribute("aria-current");
  });

  /* Offscreen suspension: any visible part of the progression counts as on
     screen; leaving entirely suspends the pass. */
  var visibility = new window.IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      suspend("offscreen", !entry.isIntersecting);
    });
  }, { threshold: 0 });
  visibility.observe(progress);

  /* The sentinel is a 1 px marker at the head of the progression. The pass
     begins once, when it enters the upper 60 percent of the viewport. */
  var trigger = new window.IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting) return;
      trigger.disconnect();
      if (phase === "idle") start();
    });
  }, { rootMargin: "0px 0px -40% 0px", threshold: 0 });
  trigger.observe(sentinel);
})();
