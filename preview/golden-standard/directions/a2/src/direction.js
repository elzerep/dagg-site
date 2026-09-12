(function () {
  "use strict";

  var instrument = document.querySelector("[data-a2-instrument]");
  var proof = document.querySelector("[data-a2-proof]");
  var replay = document.querySelector("[data-a2-replay]");
  var label = document.querySelector("[data-a2-control-label]");
  var icon = document.querySelector("[data-a2-control-icon]");
  var status = document.querySelector("[data-a2-status]");
  if (!instrument || !proof || !replay) return;

  var steps = Array.prototype.slice.call(proof.querySelectorAll("[data-a2-step]"));
  var timers = [];
  var hasPlayed = false;
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  var replayIcon = "/assets/vendor/lucide-dagg/icons/rotate-ccw.svg";

  function clearTimers() {
    timers.forEach(window.clearTimeout);
    timers = [];
  }

  function setControlResolved() {
    if (label) label.textContent = "Replay the pass";
    if (icon) icon.src = replayIcon;
  }

  function setActiveStep(activeIndex) {
    steps.forEach(function (step, index) {
      step.classList.toggle("is-active", index === activeIndex);
    });
  }

  function resolveImmediately() {
    clearTimers();
    setActiveStep(steps.length - 1);
    hasPlayed = true;
    setControlResolved();
    if (status) status.textContent = "Resolved state: draft withheld for Finance review.";
  }

  function playPass() {
    clearTimers();

    if (reduceMotion.matches) {
      resolveImmediately();
      return;
    }

    steps.forEach(function (step) { step.classList.remove("is-active"); });
    if (status) status.textContent = "Following the decision into a verified state.";

    steps.forEach(function (step, index) {
      timers.push(window.setTimeout(function () {
        setActiveStep(index);
        if (index === steps.length - 1) {
          hasPlayed = true;
          setControlResolved();
          if (status) status.textContent = "Resolved state: draft withheld for Finance review.";
        }
      }, index * 220));
    });
  }

  replay.addEventListener("click", playPass);
  reduceMotion.addEventListener("change", function (event) {
    if (event.matches) resolveImmediately();
  });

  if (reduceMotion.matches) {
    resolveImmediately();
  } else if ("IntersectionObserver" in window) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting && !hasPlayed) {
          observer.disconnect();
          playPass();
        }
      });
    }, { threshold: 0.4 });
    observer.observe(instrument);
  }
}());
