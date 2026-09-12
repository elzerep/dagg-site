/* Dagg golden standard — P4 selected-direction vertical slice
 *
 * Contract: design/golden-standard/packages/P4-DIRECTION-SLICE.md, sections
 * 8, 10 and 11.
 *
 * This file only enhances a page that is already complete without it. The
 * flag below is set synchronously, before <body> is parsed, so the enhanced
 * composition never flashes through the no-JavaScript one. If this script
 * is blocked, absent or fails to parse, the flag is never set and every
 * mechanism renders its full record: all five WorkGraph stages, both
 * Factory modes, all six operating-record states and every lifecycle step
 * in its resolved condition.
 *
 * Motion is one-pass and meaning-bearing. Nothing loops and there is no
 * ornamental signal rail; every transition changes context, decision,
 * permission, state or evidence.
 */
(function () {
  "use strict";

  document.documentElement.setAttribute("data-enhanced", "true");

  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  var finePointer = window.matchMedia("(hover: hover) and (pointer: fine)");
  var desktop = window.matchMedia("(min-width: 940px)");

  /* Adaptive-flyout timings, from the accepted interaction contract:
     open on 70-100ms hover intent, close 180-240ms after leaving both. */
  var FLYOUT_OPEN_MS = 80;
  var FLYOUT_CLOSE_MS = 200;

  /* Motion grammar: a human intervention resolves in 320-480ms, a material
     alignment in 480-800ms, a full state reveal in 800-1200ms. */
  var LIFECYCLE_STEP_MS = 720;
  var LEDGER_STATE_MS = 1400;

  function ready(fn) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", fn, { once: true });
    } else {
      fn();
    }
  }

  /* ------------------------------------------------------------------ *
   * A tab set built on real in-page links.                              *
   *                                                                     *
   * Without this script the controls are anchors that navigate to their  *
   * panel and every panel is visible. With it they become an APG tab      *
   * list: roving tabindex, arrow keys, Home and End.                     *
   * ------------------------------------------------------------------ */

  function TabSet(options) {
    this.tabs = options.tabs;
    this.panels = options.panels;
    this.orientation = options.orientation || "horizontal";
    this.onSelect = options.onSelect || function () {};
    this.index = -1;

    options.list.setAttribute("role", "tablist");
    if (options.labelledBy) {
      options.list.setAttribute("aria-labelledby", options.labelledBy);
    }
    options.list.setAttribute("aria-orientation", this.orientation);

    var set = this;
    this.tabs.forEach(function (tab, i) {
      var panel = set.panels[i];
      tab.setAttribute("role", "tab");
      tab.setAttribute("aria-controls", panel.id);
      panel.setAttribute("role", "tabpanel");
      panel.setAttribute("aria-labelledby", tab.id);
      panel.setAttribute("tabindex", "0");
      tab.addEventListener("click", function (event) {
        event.preventDefault();
        set.select(i, true);
      });
      tab.addEventListener("keydown", function (event) {
        set.onKeydown(event, i);
      });
    });
    this.select(0, false);
  }

  TabSet.prototype.select = function (index, moveFocus) {
    if (index === this.index) {
      return;
    }
    this.index = index;
    var set = this;
    this.tabs.forEach(function (tab, i) {
      var selected = i === index;
      tab.setAttribute("aria-selected", selected ? "true" : "false");
      tab.setAttribute("tabindex", selected ? "0" : "-1");
      set.panels[i].hidden = !selected;
    });
    if (moveFocus) {
      this.tabs[index].focus();
    }
    this.onSelect(index, this.tabs[index]);
  };

  TabSet.prototype.onKeydown = function (event, index) {
    var previous = this.orientation === "vertical" ? "ArrowUp" : "ArrowLeft";
    var next = this.orientation === "vertical" ? "ArrowDown" : "ArrowRight";
    var target = null;
    if (event.key === previous) {
      target = (index - 1 + this.tabs.length) % this.tabs.length;
    } else if (event.key === next) {
      target = (index + 1) % this.tabs.length;
    } else if (event.key === "Home") {
      target = 0;
    } else if (event.key === "End") {
      target = this.tabs.length - 1;
    }
    if (target === null) {
      return;
    }
    event.preventDefault();
    this.select(target, true);
  };

  /* ------------------------------------------------------------------ *
   * One-pass state runner, with the pause and replay the copy names.    *
   * ------------------------------------------------------------------ */

  function StateRun(options) {
    this.length = options.length;
    this.apply = options.apply;
    this.interval = options.interval;
    this.index = 0;
    this.timer = null;
    this.playing = false;
    this.controls = options.controls || null;

    var run = this;
    if (this.controls) {
      this.controls.hidden = false;
      this.pauseButton = this.controls.querySelector("[data-motion-pause]");
      this.replayButton = this.controls.querySelector("[data-motion-replay]");
      if (this.pauseButton) {
        this.pauseButton.addEventListener("click", function () {
          if (run.playing) {
            run.pause();
          } else {
            run.play();
          }
        });
      }
      if (this.replayButton) {
        this.replayButton.addEventListener("click", function () {
          run.replay();
        });
      }
    }
  }

  StateRun.prototype.setPressed = function (pressed) {
    if (this.pauseButton) {
      this.pauseButton.setAttribute("aria-pressed", pressed ? "true" : "false");
    }
  };

  StateRun.prototype.go = function (index) {
    this.index = index;
    this.apply(index);
  };

  /* Reduced motion is not "no state": it is the resolved end state, shown
     at once, with the whole record still beside it. */
  StateRun.prototype.resolve = function () {
    this.pause();
    this.go(this.length - 1);
  };

  StateRun.prototype.play = function () {
    if (reduceMotion.matches) {
      this.resolve();
      return;
    }
    this.pause();
    this.playing = true;
    this.setPressed(false);
    var run = this;
    var tick = function () {
      if (run.index >= run.length - 1) {
        run.playing = false;
        run.setPressed(false);
        return;
      }
      run.go(run.index + 1);
      run.timer = window.setTimeout(tick, run.interval);
    };
    this.timer = window.setTimeout(tick, this.interval);
  };

  StateRun.prototype.pause = function () {
    window.clearTimeout(this.timer);
    this.timer = null;
    if (this.playing) {
      this.playing = false;
      this.setPressed(true);
    }
  };

  StateRun.prototype.replay = function () {
    this.pause();
    if (reduceMotion.matches) {
      this.resolve();
      return;
    }
    this.go(0);
    this.play();
  };

  /* Starts the one pass the first time the mechanism is actually on
     screen, so a record below the fold does not silently finish unseen. */
  function whenVisible(node, fn) {
    if (!("IntersectionObserver" in window)) {
      fn();
      return;
    }
    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            observer.disconnect();
            fn();
          }
        });
      },
      { threshold: 0.35 }
    );
    observer.observe(node);
  }

  /* ------------------------------------------------------------------ *
   * Act 1 — the hero record's one-pass lifecycle                        *
   * ------------------------------------------------------------------ */

  function initLifecycle() {
    var artifact = document.querySelector("[data-lifecycle]");
    if (!artifact) {
      return;
    }
    var steps = [].slice.call(
      artifact.querySelectorAll("[data-lifecycle-track] .lifecycle__step")
    );
    if (!steps.length) {
      return;
    }
    var controls = artifact.querySelector("[data-motion-controls]");

    var run = new StateRun({
      length: steps.length,
      interval: LIFECYCLE_STEP_MS,
      controls: controls,
      apply: function (index) {
        steps.forEach(function (step, i) {
          if (i <= index) {
            step.setAttribute("data-resolved", "");
          } else {
            step.removeAttribute("data-resolved");
          }
          if (i === index) {
            step.setAttribute("data-active", "");
          } else {
            step.removeAttribute("data-active");
          }
        });
      },
    });

    if (reduceMotion.matches) {
      run.resolve();
      return;
    }
    run.go(0);
    run.play();
  }

  /* ------------------------------------------------------------------ *
   * Act 3 — the decision continuum                                      *
   *                                                                     *
   * The exclusive accordion is native (`name` on <details>). The only    *
   * thing script adds is that the open path cannot be closed onto        *
   * nothing, so one outcome is always readable.                          *
   * ------------------------------------------------------------------ */

  function initContinuum() {
    var continuum = document.querySelector("[data-continuum]");
    if (!continuum) {
      return;
    }
    [].forEach.call(continuum.querySelectorAll(".outcome"), function (outcome) {
      var summary = outcome.querySelector(".outcome__summary");
      summary.addEventListener("click", function (event) {
        if (outcome.open) {
          event.preventDefault();
        }
      });
      summary.addEventListener("keydown", function (event) {
        if ((event.key === "Enter" || event.key === " ") && outcome.open) {
          event.preventDefault();
        }
      });
    });
  }

  /* ------------------------------------------------------------------ *
   * Act 4 — WorkGraph                                                   *
   *                                                                     *
   * Five stages, one invariant record. The record never changes its      *
   * source, owner, boundary, decision, permission or provenance; the     *
   * stage only changes which of those fields the reader is being asked   *
   * to look at. Semantic field emphasis makes the new context, decision  *
   * or boundary resolve in place.                                       *
   * ------------------------------------------------------------------ */

  var WORKGRAPH_EMPHASIS = {
    map: { machine: ["source", "captured", "system", "work-item"] },
    decide: {
      decision: ["decision", "owner"],
      machine: ["exception"],
    },
    build: { machine: ["source", "provenance"], boundary: ["permission"] },
    govern: { boundary: ["permission", "owner"] },
    operate: {
      boundary: ["exception"],
      decision: ["decision"],
      machine: ["provenance"],
    },
  };

  function initWorkGraph() {
    var root = document.querySelector("[data-workgraph]");
    if (!root) {
      return;
    }
    var list = root.querySelector("[data-wg-rail]");
    var tabs = [].slice.call(root.querySelectorAll("[data-wg-tab]"));
    var panels = [].slice.call(root.querySelectorAll("[data-wg-panel]"));
    var rows = [].slice.call(root.querySelectorAll(".record__row"));

    new TabSet({
      list: list,
      tabs: tabs,
      panels: panels,
      orientation: desktop.matches ? "vertical" : "horizontal",
      labelledBy: "workgraph-title",
      onSelect: function (index, tab) {
        var stage = tab.getAttribute("data-stage");
        var map = WORKGRAPH_EMPHASIS[stage] || {};
        rows.forEach(function (row) {
          var field = row.getAttribute("data-field");
          var tone = null;
          Object.keys(map).forEach(function (key) {
            if (map[key].indexOf(field) !== -1) {
              tone = key;
            }
          });
          if (tone) {
            row.setAttribute("data-emphasis", tone);
          } else {
            row.removeAttribute("data-emphasis");
          }
        });
      },
    });

    desktop.addEventListener("change", function (query) {
      list.setAttribute(
        "aria-orientation",
        query.matches ? "vertical" : "horizontal"
      );
    });
  }

  /* ------------------------------------------------------------------ *
   * Act 5 — Factory                                                     *
   *                                                                     *
   * Two modes over one provenance. Switching mode re-runs the build      *
   * states, which is the only place velocity is shown: the same context  *
   * reaches governed review faster the second time.                      *
   * ------------------------------------------------------------------ */

  function initFactory() {
    var root = document.querySelector("[data-factory]");
    if (!root) {
      return;
    }
    var list = root.querySelector("[data-factory-modes]");
    var tabs = [].slice.call(root.querySelectorAll("[data-factory-tab]"));
    var panels = [].slice.call(root.querySelectorAll("[data-factory-panel]"));
    var states = [].slice.call(root.querySelectorAll(".buildstate"));
    var timer = null;

    function runBuildStates() {
      window.clearTimeout(timer);
      if (reduceMotion.matches) {
        states.forEach(function (state) {
          state.setAttribute("data-reached", "");
        });
        return;
      }
      states.forEach(function (state) {
        state.removeAttribute("data-reached");
      });
      var index = 0;
      var step = function () {
        states[index].setAttribute("data-reached", "");
        index += 1;
        if (index < states.length) {
          timer = window.setTimeout(step, 260);
        }
      };
      step();
    }

    new TabSet({
      list: list,
      tabs: tabs,
      panels: panels,
      orientation: "horizontal",
      labelledBy: "factory-title",
      onSelect: function () {
        runBuildStates();
      },
    });
  }

  /* ------------------------------------------------------------------ *
   * Act 6 — the operating record                                        *
   *                                                                     *
   * Six states in one ledger. Every state stays readable at all times;   *
   * motion only moves which one is currently accountable. While motion   *
   * is paused, each state remains directly inspectable by pointer,       *
   * touch or keyboard.                                                  *
   * ------------------------------------------------------------------ */

  function initOperatingRecord() {
    var root = document.querySelector("[data-operating]");
    if (!root) {
      return;
    }
    var states = [].slice.call(root.querySelectorAll(".state"));
    var controls = root.querySelector("[data-motion-controls]");

    var run = new StateRun({
      length: states.length,
      interval: LEDGER_STATE_MS,
      controls: controls,
      apply: function (index) {
        states.forEach(function (state, i) {
          if (i === index) {
            state.setAttribute("data-current", "");
          } else {
            state.removeAttribute("data-current");
          }
        });
      },
    });

    states.forEach(function (state, i) {
      var button = state.querySelector("[data-state-button]");
      if (!button) {
        return;
      }
      button.addEventListener("click", function () {
        run.pause();
        run.go(i);
      });
    });

    if (reduceMotion.matches) {
      run.resolve();
      return;
    }
    run.go(0);
    whenVisible(root, function () {
      run.play();
    });
  }

  /* ------------------------------------------------------------------ *
   * The one justified flyout — Build                                    *
   *                                                                     *
   * A native <details> is the disclosure at every width, so the four     *
   * destinations are reachable with no script at all. Script adds the    *
   * adaptive behavior the interaction contract asks for: hover intent,   *
   * a close grace period, Escape with focus return, outside click and    *
   * an explicit expanded state.                                          *
   * ------------------------------------------------------------------ */

  function initFlyout() {
    var item = document.querySelector("[data-flyout-item]");
    if (!item) {
      return;
    }
    var flyout = item.querySelector("[data-flyout]");
    var summary = item.querySelector("[data-flyout-summary]");
    var panel = item.querySelector("[data-flyout-panel]");
    if (!flyout || !summary || !panel) {
      return;
    }
    var openTimer = null;
    var closeTimer = null;

    function sync() {
      summary.setAttribute("aria-expanded", flyout.open ? "true" : "false");
    }

    flyout.addEventListener("toggle", sync);
    sync();

    function open() {
      window.clearTimeout(closeTimer);
      if (!flyout.open) {
        flyout.open = true;
      }
    }

    function close(restoreFocus) {
      window.clearTimeout(openTimer);
      if (!flyout.open) {
        return;
      }
      flyout.open = false;
      if (restoreFocus) {
        summary.focus();
      }
    }

    /* Hover intent applies only to a genuine fine pointer. A coarse
       pointer gets the plain disclosure, with no hover dependency. */
    item.addEventListener("pointerenter", function (event) {
      if (event.pointerType !== "mouse" || !finePointer.matches || !desktop.matches) {
        return;
      }
      window.clearTimeout(closeTimer);
      openTimer = window.setTimeout(open, FLYOUT_OPEN_MS);
    });

    item.addEventListener("pointerleave", function (event) {
      if (event.pointerType !== "mouse" || !finePointer.matches || !desktop.matches) {
        return;
      }
      window.clearTimeout(openTimer);
      closeTimer = window.setTimeout(function () {
        close(false);
      }, FLYOUT_CLOSE_MS);
    });

    item.addEventListener("focusin", function () {
      window.clearTimeout(closeTimer);
    });

    item.addEventListener("focusout", function (event) {
      if (item.contains(event.relatedTarget)) {
        return;
      }
      if (desktop.matches) {
        close(false);
      }
    });

    document.addEventListener("keydown", function (event) {
      if (event.key !== "Escape" || !flyout.open) {
        return;
      }
      event.preventDefault();
      event.stopPropagation();
      close(true);
    });

    document.addEventListener("click", function (event) {
      if (flyout.open && !item.contains(event.target)) {
        close(false);
      }
    });

    desktop.addEventListener("change", function () {
      close(false);
    });
  }

  ready(function () {
    initFlyout();
    initLifecycle();
    initContinuum();
    initWorkGraph();
    initFactory();
    initOperatingRecord();
  });
})();
