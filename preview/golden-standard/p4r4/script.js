(function () {
  "use strict";

  var root = document.documentElement;
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  var desktop = window.matchMedia("(min-width: 940px)");

  root.classList.add("is-enhanced");

  function ready(callback) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", callback, { once: true });
    } else {
      callback();
    }
  }

  function initHero() {
    var art = document.querySelector("[data-hero-art]");
    if (!art || reduceMotion.matches) {
      return;
    }
    requestAnimationFrame(function () {
      art.classList.add("is-resolving");
    });
    art.addEventListener(
      "animationend",
      function () {
        art.classList.remove("is-resolving");
        art.classList.add("is-resolved");
      },
      { once: true }
    );
  }

  function initBuildFlyout() {
    var flyout = document.querySelector("[data-build-flyout]");
    if (!flyout) {
      return;
    }
    var trigger = flyout.querySelector("summary");
    var openTimer = 0;
    var closeTimer = 0;

    function sync() {
      trigger.setAttribute("aria-expanded", flyout.open ? "true" : "false");
    }

    function openWithIntent() {
      if (!desktop.matches) {
        return;
      }
      window.clearTimeout(closeTimer);
      window.clearTimeout(openTimer);
      openTimer = window.setTimeout(function () {
        flyout.open = true;
        sync();
      }, 80);
    }

    function closeWithGrace() {
      if (!desktop.matches) {
        return;
      }
      window.clearTimeout(openTimer);
      window.clearTimeout(closeTimer);
      closeTimer = window.setTimeout(function () {
        flyout.open = false;
        sync();
      }, 210);
    }

    flyout.addEventListener("toggle", sync);
    flyout.addEventListener("mouseenter", openWithIntent);
    flyout.addEventListener("mouseleave", closeWithGrace);
    flyout.addEventListener("focusin", function () {
      window.clearTimeout(closeTimer);
      if (desktop.matches) {
        flyout.open = true;
        sync();
      }
    });
    flyout.addEventListener("focusout", function (event) {
      if (!flyout.contains(event.relatedTarget)) {
        closeWithGrace();
      }
    });
    flyout.addEventListener("keydown", function (event) {
      if (event.key === "Escape" && flyout.open) {
        event.preventDefault();
        flyout.open = false;
        sync();
        trigger.focus();
      }
    });
    desktop.addEventListener("change", function () {
      flyout.open = false;
      sync();
    });
    sync();
  }

  function initDecisionContinuum() {
    var decisions = Array.prototype.slice.call(
      document.querySelectorAll(".decision-continuum .decision")
    );
    decisions.forEach(function (decision) {
      decision.addEventListener("toggle", function () {
        if (!decision.open) {
          return;
        }
        decisions.forEach(function (other) {
          if (other !== decision) {
            other.open = false;
          }
        });
      });
    });
  }

  function initStateSelector(options) {
    var scope = document.querySelector(options.scope);
    if (!scope) {
      return;
    }
    var buttons = Array.prototype.slice.call(
      scope.querySelectorAll(options.button)
    );
    var states = Array.prototype.slice.call(scope.querySelectorAll(options.state));
    if (!buttons.length || !states.length) {
      return;
    }

    function select(key, focus) {
      buttons.forEach(function (button) {
        var selected = button.getAttribute(options.buttonKey) === key;
        button.setAttribute("aria-pressed", selected ? "true" : "false");
        button.tabIndex = selected ? 0 : -1;
        if (selected && focus) {
          button.focus();
        }
      });
      states.forEach(function (state) {
        state.hidden = state.getAttribute(options.stateKey) !== key;
      });
    }

    buttons.forEach(function (button, index) {
      button.addEventListener("click", function () {
        select(button.getAttribute(options.buttonKey), false);
      });
      button.addEventListener("keydown", function (event) {
        var next = null;
        if (event.key === "ArrowRight" || event.key === "ArrowDown") {
          next = (index + 1) % buttons.length;
        } else if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
          next = (index - 1 + buttons.length) % buttons.length;
        } else if (event.key === "Home") {
          next = 0;
        } else if (event.key === "End") {
          next = buttons.length - 1;
        }
        if (next !== null) {
          event.preventDefault();
          select(buttons[next].getAttribute(options.buttonKey), true);
        }
      });
    });
    select(buttons[0].getAttribute(options.buttonKey), false);
  }

  function initFactory() {
    var factory = document.querySelector("[data-factory]");
    if (!factory) {
      return;
    }
    var stages = Array.prototype.slice.call(
      factory.querySelectorAll("[data-factory-stage]")
    );
    var resolved = factory.querySelector("[data-factory-resolved]");
    var resolvedLabels = [
      "Requirement linked to company context",
      "Operating decision and human boundary explicit",
      "Sources, tools and permissions bounded",
      "Working path recorded for evaluation",
      "Evidence quality and exceptions evaluated",
      "Verified release held for accountable review",
    ];
    var hasRun = false;

    function select(index) {
      stages.forEach(function (stage, stageIndex) {
        stage.open = stageIndex === index;
      });
      if (resolved) {
        resolved.textContent = resolvedLabels[index];
      }
    }

    stages.forEach(function (stage, index) {
      stage.addEventListener("toggle", function () {
        if (!stage.open) {
          return;
        }
        stages.forEach(function (other) {
          if (other !== stage) {
            other.open = false;
          }
        });
        if (resolved) {
          resolved.textContent = resolvedLabels[index];
        }
      });
    });

    function run() {
      if (hasRun) {
        return;
      }
      hasRun = true;
      if (reduceMotion.matches) {
        select(stages.length - 1);
        return;
      }
      stages.forEach(function (_, index) {
        window.setTimeout(function () {
          select(index);
        }, index * 520);
      });
    }

    if ("IntersectionObserver" in window) {
      var observer = new IntersectionObserver(
        function (entries) {
          entries.forEach(function (entry) {
            if (entry.isIntersecting) {
              observer.disconnect();
              run();
            }
          });
        },
        { threshold: 0.42 }
      );
      observer.observe(factory);
    } else {
      run();
    }
  }

  ready(function () {
    initHero();
    initBuildFlyout();
    initDecisionContinuum();
    initStateSelector({
      scope: "[data-source-instrument]",
      button: "[data-source-button]",
      buttonKey: "data-source-button",
      state: "[data-source-record]",
      stateKey: "data-source-record",
    });
    initFactory();
    initStateSelector({
      scope: "[data-impact]",
      button: "[data-impact-button]",
      buttonKey: "data-impact-button",
      state: "[data-impact-state]",
      stateKey: "data-impact-state",
    });
  });
})();
