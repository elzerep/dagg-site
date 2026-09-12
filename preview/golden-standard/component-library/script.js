/* Dagg golden standard — P4R5 Component and Interaction Specimen
 *
 * Package: design/golden-standard/packages/P4R5-COMPONENT-INTERACTION-SPECIMEN.md
 *
 * Progressive enhancement only. Everything this file adds is additive:
 *
 *   - the Build flyout works as a native <details> disclosure without it;
 *   - the strategic continuum is a native radiogroup with CSS-only
 *     selection, so it needs no script at all;
 *   - the WorkGraph tablist and the Factory motion controls are *created*
 *     here, so no inert control is ever present in the no-JavaScript DOM;
 *   - the two-surface mode group falls back to both surfaces rendered in
 *     reading order.
 *
 * Timings are the approved ones (Dagg-Design-System-Foundations.pdf p.12
 * and p.13; Dagg-Image-Language-System.pdf p.08). No spring, no overshoot,
 * no ambient loop, no unbounded autoplay.
 */
(function () {
  "use strict";

  var HOVER_INTENT_MS = 85;      /* Foundations p.12: open intent 70–100 ms  */
  var CLOSE_GRACE_MS = 210;      /* Foundations p.12: close grace 180–240 ms */
  var PREVIEW_MORPH_MS = 200;    /* Foundations p.12: panel morph 180–240 ms */
  var SIGNAL_PASS_MS = 900;      /* under 1 s, so no replay control          */
  var FACTORY_STEP_MS = 900;     /* six stages + two holds = 7.2 s total     */
  var FACTORY_HOLD_MS = 900;     /* ILS p.08: hold at judgment and at        */
                                 /* verification, then stop                  */

  var ICON_DIR = "/assets/vendor/lucide-dagg/icons/";

  var root = document.documentElement;
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  var desktop = window.matchMedia("(min-width: 940px)");

  root.classList.add("cl-enhanced");
  /* Enhancement decides several initial states — the coarse Machine Signal
     geometry, the first proof-inset state, the Factory's first stage. None
     of them is a transition the reader asked for, so transitions are
     suppressed for the first frame and armed immediately afterwards. This
     is why the specimen never animates itself on load. */
  root.classList.add("cl-booting");

  function ready(callback) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", callback, { once: true });
    } else {
      callback();
    }
  }

  function slice(nodes) {
    return Array.prototype.slice.call(nodes);
  }

  /* Icons created here are the vendored official Lucide files referenced as
     real <img> elements. This function never builds an inline <svg> string,
     never injects path data and never writes markup through innerHTML — the
     asset rule in P4R5 §4.1 forbids a hand-copied or hand-drawn icon in
     either the document or this script. */
  function icon(name) {
    var img = document.createElement("img");
    img.className = "cl-ico cl-ico--control";
    img.src = ICON_DIR + name + ".svg";
    img.alt = "";
    img.width = 24;
    img.height = 24;
    img.setAttribute("aria-hidden", "true");
    return img;
  }

  /* One shared polite live region. Individual controls do not each become
     an aria-live area, so a six-stage Factory pass announces its verified
     end state once instead of six times. */
  var announcer = null;

  function announce(message) {
    if (!announcer) {
      announcer = document.createElement("p");
      announcer.setAttribute("aria-live", "polite");
      announcer.setAttribute("role", "status");
      announcer.style.cssText =
        "position:absolute;width:1px;height:1px;overflow:hidden;clip-path:inset(50%);white-space:nowrap;";
      document.body.appendChild(announcer);
    }
    announcer.textContent = message;
  }

  /* ------------------------------------------------------------------ *
   * 1 · Rendered specimens are held inert                              *
   *                                                                    *
   * The warm / ink / compact / mobile header frames and the held        *
   * hover / active / focus action rows are visual specimens. `inert`    *
   * removes them from the tab order, from hit testing and from the      *
   * accessibility tree, so no specimen adds a duplicate stop or a       *
   * control that implies a route it does not have.                      *
   * ------------------------------------------------------------------ */

  function initInertStages() {
    var stages = document.querySelectorAll("[data-inert-stage]");
    Array.prototype.forEach.call(stages, function (stage) {
      stage.inert = true;
      if (!("inert" in stage)) {
        /* Fallback for a build without the `inert` IDL attribute: remove
           the stage's own focusables from the tab order by hand. */
        var focusables = stage.querySelectorAll("a[href], button, summary, input");
        Array.prototype.forEach.call(focusables, function (el) {
          el.setAttribute("tabindex", "-1");
          el.setAttribute("aria-hidden", "true");
        });
      }
    });
  }

  /* ------------------------------------------------------------------ *
   * 1b · Mobile disclosure icon                                        *
   *                                                                    *
   * The accepted P3 chrome.js toggles the Menu / Close *labels*. The    *
   * icon pair beside them is added by this package, so this package     *
   * keeps it in step — one listener on the same native toggle event, no *
   * second source of truth for the open state.                          *
   * ------------------------------------------------------------------ */

  function initDisclosureIcon() {
    var disclosure = document.querySelector("[data-disclosure]");
    if (!disclosure) {
      return;
    }
    var menuIcon = disclosure.querySelector("[data-icon-menu]");
    var closeIcon = disclosure.querySelector("[data-icon-close]");
    if (!menuIcon || !closeIcon) {
      return;
    }
    function sync() {
      menuIcon.hidden = disclosure.open;
      closeIcon.hidden = !disclosure.open;
    }
    disclosure.addEventListener("toggle", sync);
    sync();
  }

  /* ------------------------------------------------------------------ *
   * 2 · Build flyout — the right-hand proof inset                      *
   *                                                                    *
   * P4R5 §4.1: one right-hand proof inset with four states, driven by   *
   * hover AND by keyboard focus on each of the four destinations. A     *
   * permanently static inset is a P0 failure.                          *
   *                                                                    *
   * The four state blocks and the four destinations are the same DOM at *
   * both widths, not two copies of the same words:                      *
   *                                                                    *
   *   - at and above 940 px the list and its items are `display:        *
   *     contents`, so the four links stack down column 1 of the panel   *
   *     grid and all four states share the single column-2 area. One is *
   *     visible; the others are `visibility: hidden`, which keeps them  *
   *     in layout (so the outer panel cannot jump) while removing them  *
   *     from the reading order and the accessibility tree;              *
   *   - below it each item is a real per-destination disclosure inside  *
   *     the reading sheet, with a 48 px tap control created here so no  *
   *     inert control exists in the no-JavaScript DOM.                  *
   *                                                                    *
   * Timings: 120 ms content crossfade (100–140) in CSS, 200 ms height   *
   * morph (180–240) driven from the measured natural height of each     *
   * state. Under reduced motion no height is written at all and the CSS *
   * swaps the state with no transition.                                *
   * ------------------------------------------------------------------ */

  function initPreviewInset(flyout) {
    var panel = flyout.querySelector("[data-preview-scope]");
    if (!panel) {
      return null;
    }
    var links = slice(panel.querySelectorAll("[data-preview-key]"));
    var states = slice(panel.querySelectorAll("[data-preview-state]"));
    if (!links.length || links.length !== states.length) {
      return null;
    }

    var byKey = {};
    states.forEach(function (state) {
      byKey[state.getAttribute("data-preview-state")] = state;
    });

    /* The first destination's state carries the conclusion, so it is the
       default at both widths (P4R5 §4.1). */
    var firstKey = links[0].getAttribute("data-preview-key");
    var activeKey = firstKey;
    var openKey = firstKey;
    var heights = null;
    var reveals = [];
    var resizeTimer = 0;

    links.forEach(function (link) {
      var key = link.getAttribute("data-preview-key");
      var state = byKey[key];
      var name = link.querySelector("strong");
      if (!state) {
        return;
      }
      var button = document.createElement("button");
      button.type = "button";
      button.className = "cl-flyout__reveal";
      button.setAttribute("data-preview-reveal", key);
      button.setAttribute("aria-controls", state.id);
      button.setAttribute("aria-expanded", "false");
      if (flyout.getAttribute("data-flyout-id") === "header") {
        var copyKey = key === "agents" ? "agents-software" :
          (key === "trust" ? "trust-operation" : key);
        button.setAttribute(
          "data-copy-ref", "shared.header.build-preview." + copyKey);
        button.setAttribute("data-copy-kind", "functional");
        button.setAttribute("data-copy-scope", "shell");
      }
      var label = document.createElement("span");
      label.className = "cl-sr";
      label.textContent = "Preview " +
        (name ? name.textContent.trim() : key);
      button.appendChild(label);
      button.appendChild(icon("chevron-down"));
      button.addEventListener("click", function () {
        openKey = openKey === key ? null : key;
        apply();
      });
      state.parentNode.insertBefore(button, state);
      reveals.push({ key: key, button: button });
    });

    function measure() {
      heights = {};
      var max = 0;
      states.forEach(function (state) {
        state.style.height = "auto";
        var height = state.getBoundingClientRect().height;
        state.style.removeProperty("height");
        heights[state.getAttribute("data-preview-state")] = height;
        if (height > max) {
          max = height;
        }
      });
      if (!max) {
        /* Nothing was laid out — the panel is not open yet. Record no
           measurement rather than pinning the panel to a wrong height. */
        heights = null;
        panel.style.removeProperty("--fp-max-h");
        return;
      }
      panel.style.setProperty("--fp-max-h", Math.ceil(max) + "px");
    }

    function apply() {
      var mobile = !desktop.matches;
      links.forEach(function (link) {
        link.classList.toggle(
          "is-selected",
          !mobile && link.getAttribute("data-preview-key") === activeKey);
      });
      reveals.forEach(function (reveal) {
        reveal.button.setAttribute(
          "aria-expanded",
          mobile && reveal.key === openKey ? "true" : "false");
      });
      states.forEach(function (state) {
        var key = state.getAttribute("data-preview-state");
        if (mobile) {
          state.classList.remove("is-active");
          state.hidden = key !== openKey;
        } else {
          state.hidden = false;
          state.classList.toggle("is-active", key === activeKey);
        }
      });
      if (!mobile && heights && !reduceMotion.matches &&
          typeof heights[activeKey] === "number") {
        panel.style.setProperty(
          "--fp-h", Math.ceil(heights[activeKey]) + "px");
      } else {
        panel.style.removeProperty("--fp-h");
      }
    }

    function select(key) {
      if (!desktop.matches || key === activeKey || !byKey[key]) {
        return;
      }
      activeKey = key;
      apply();
    }

    links.forEach(function (link) {
      var key = link.getAttribute("data-preview-key");
      link.addEventListener("pointerenter", function (event) {
        if (event.pointerType === "touch") {
          return;
        }
        select(key);
      });
      /* Keyboard and assistive focus produce the same four states. */
      link.addEventListener("focus", function () {
        select(key);
      });
    });

    flyout.addEventListener("toggle", function () {
      if (!flyout.open) {
        activeKey = firstKey;
        openKey = firstKey;
        apply();
        return;
      }
      apply();
      if (heights === null && desktop.matches) {
        window.requestAnimationFrame(function () {
          measure();
          apply();
        });
      }
    });

    desktop.addEventListener("change", function () {
      heights = null;
      panel.style.removeProperty("--fp-h");
      panel.style.removeProperty("--fp-max-h");
      apply();
    });

    /* A width change inside the desktop range changes the natural height of
       every state, so the measurement is discarded and retaken while the
       panel is still open. */
    window.addEventListener("resize", function () {
      window.clearTimeout(resizeTimer);
      resizeTimer = window.setTimeout(function () {
        if (!desktop.matches) {
          heights = null;
          apply();
          return;
        }
        if (flyout.open) {
          measure();
        } else {
          heights = null;
        }
        apply();
      }, PREVIEW_MORPH_MS);
    });

    apply();
    return { measure: measure, apply: apply };
  }

  function initFlyout(flyout) {
    var trigger = flyout.querySelector("[data-flyout-trigger]");
    var panel = flyout.querySelector("[data-flyout-panel]");
    if (!trigger || !panel) {
      return;
    }
    initPreviewInset(flyout);
    var openTimer = 0;
    var closeTimer = 0;
    var returnFocusTo = null;

    function sync() {
      trigger.setAttribute("aria-expanded", flyout.open ? "true" : "false");
    }

    function clearTimers() {
      window.clearTimeout(openTimer);
      window.clearTimeout(closeTimer);
    }

    function open() {
      clearTimers();
      if (!flyout.open) {
        flyout.open = true;
      }
      sync();
    }

    function close() {
      clearTimers();
      if (flyout.open) {
        flyout.open = false;
      }
      sync();
    }

    flyout.addEventListener("toggle", function () {
      sync();
      if (flyout.open) {
        /* Remember where focus was so Escape can put it back, per the
           P4R3 §5 focus-restoration rule. */
        returnFocusTo = document.activeElement === trigger ? trigger : trigger;
      }
    });

    /* Pointer: intent to open, grace to close. Desktop only — below the
       940 px collapse the flyout is a stacked disclosure and hover is not
       an available input. */
    flyout.addEventListener("pointerenter", function (event) {
      if (event.pointerType === "touch" || !desktop.matches) {
        return;
      }
      clearTimers();
      openTimer = window.setTimeout(open, HOVER_INTENT_MS);
    });

    flyout.addEventListener("pointerleave", function (event) {
      if (event.pointerType === "touch" || !desktop.matches) {
        return;
      }
      clearTimers();
      closeTimer = window.setTimeout(close, CLOSE_GRACE_MS);
    });

    /* Keyboard and assistive focus: opening on focus-within, closing on
       focus leaving after the same grace period. */
    flyout.addEventListener("focusin", function (event) {
      if (!desktop.matches) {
        return;
      }
      /* Do not open merely because the native <summary> receives focus.
         Enter/Space must remain its single source of truth; opening here and
         then allowing the native key action would immediately toggle it shut.
         Focus inside an already-open panel still keeps the flyout open. */
      if (event.target === trigger) {
        clearTimers();
        return;
      }
      open();
    });

    flyout.addEventListener("focusout", function (event) {
      if (!desktop.matches) {
        return;
      }
      if (event.relatedTarget && flyout.contains(event.relatedTarget)) {
        return;
      }
      clearTimers();
      closeTimer = window.setTimeout(close, CLOSE_GRACE_MS);
    });

    flyout.addEventListener("keydown", function (event) {
      if (event.key !== "Escape" || !flyout.open) {
        return;
      }
      event.preventDefault();
      event.stopPropagation();
      close();
      (returnFocusTo || trigger).focus();
    });

    document.addEventListener("pointerdown", function (event) {
      if (flyout.open && !flyout.contains(event.target)) {
        close();
      }
    });

    desktop.addEventListener("change", close);
    sync();
  }

  /* ------------------------------------------------------------------ *
   * 3 · Machine Signal — one finite coarse -> resolved pass             *
   *                                                                    *
   * The hook is on the Machine Signal component itself, not on the      *
   * protected Home hero figure. The transition is real geometry — the   *
   * horizontal position, the width and the opacity of five strata, plus *
   * coral arriving once at the judgment stratum and sage arriving only  *
   * as the boundary verifies (ILS p.10 RESOLVE, p.11 REQUIRED). No      *
   * filter, blur, veil or colour remap is applied to any photograph.    *
   *                                                                    *
   * P4R5 §4.4 asks for "a finite Machine Signal before/after control    *
   * that resolves once and stops", with replay only above one second.   *
   * The pass is 900 ms, so the control is one-shot and is removed when  *
   * the pass has resolved: no dead control and no replay remain.        *
   *                                                                    *
   * The resolved state is the document default, so with JavaScript      *
   * absent or under reduced motion the strata are never left coarse.    *
   * ------------------------------------------------------------------ */

  function initSignal() {
    var carrier = document.querySelector("[data-signal-carrier]");
    if (!carrier) {
      return;
    }
    var status = carrier.querySelector("[data-signal-status]");
    var host = carrier.querySelector("[data-signal-control]");
    var strata = carrier.querySelector("[data-strata]");
    if (!status || !host || !strata) {
      /* One of the parts is missing: leave the document default — the
         resolved state — exactly as authored rather than half-wiring a
         transition that cannot complete. */
      return;
    }

    if (reduceMotion.matches) {
      carrier.classList.remove("is-coarse");
      status.textContent = "Resolved · held · reduced motion";
      host.hidden = true;
      return;
    }

    var button = document.createElement("button");
    button.type = "button";
    button.setAttribute("data-signal-run", "");
    button.appendChild(icon("play"));
    button.appendChild(document.createTextNode("Resolve the record"));
    button.addEventListener("click", function () {
      if (!carrier.classList.contains("is-coarse")) {
        return;
      }
      button.disabled = true;
      carrier.classList.remove("is-coarse");
      status.textContent = "Resolving · one pass of 900 ms";
      window.setTimeout(function () {
        status.textContent = "Resolved · held · one pass, no replay";
        host.hidden = true;
        while (host.firstChild) {
          host.removeChild(host.firstChild);
        }
        announce(
          "Machine Signal resolved. The five strata are aligned on one " +
          "origin, the judgment stratum is coral and the verified " +
          "boundary is sage."
        );
      }, SIGNAL_PASS_MS);
    });

    host.appendChild(button);
    host.hidden = false;
    carrier.classList.add("is-coarse");
    status.textContent = "Coarse signal · one resolution available";
  }

  /* ------------------------------------------------------------------ *
   * 4 · WorkGraph record — four sources over one retained record        *
   *                                                                    *
   * The controls switch panels, so this is a real tablist with a roving *
   * tabindex (P4R5 §5). The tabs are created here; without JavaScript   *
   * every source panel is rendered with its own heading and no inert    *
   * control exists.                                                    *
   * ------------------------------------------------------------------ */

  function initRecord() {
    var record = document.querySelector("[data-record]");
    if (!record) {
      return;
    }
    var tabsHost = record.querySelector("[data-record-tabs]");
    var panels = Array.prototype.slice.call(
      record.querySelectorAll("[data-record-panel]")
    );
    var label = record.querySelector("#record-sources-label");
    if (!tabsHost || panels.length < 2) {
      return;
    }

    tabsHost.hidden = false;
    tabsHost.setAttribute("role", "tablist");
    if (label) {
      tabsHost.setAttribute("aria-labelledby", label.id);
    }

    var tabs = panels.map(function (panel, index) {
      var key = panel.getAttribute("data-record-panel");
      var tab = document.createElement("button");
      tab.type = "button";
      tab.id = "record-tab-" + key;
      tab.setAttribute("role", "tab");
      tab.setAttribute("aria-controls", "record-panel-" + key);
      tab.textContent = panel.getAttribute("data-record-label") || key;
      tabsHost.appendChild(tab);

      panel.id = "record-panel-" + key;
      panel.setAttribute("role", "tabpanel");
      panel.setAttribute("aria-labelledby", tab.id);
      panel.tabIndex = 0;
      panel.hidden = index !== 0;
      return tab;
    });

    function select(index, moveFocus) {
      tabs.forEach(function (tab, i) {
        var selected = i === index;
        tab.setAttribute("aria-selected", selected ? "true" : "false");
        tab.tabIndex = selected ? 0 : -1;
        panels[i].hidden = !selected;
        if (selected && moveFocus) {
          tab.focus();
        }
      });
    }

    tabs.forEach(function (tab, index) {
      tab.addEventListener("click", function () {
        select(index, false);
      });
      tab.addEventListener("keydown", function (event) {
        var next = null;
        if (event.key === "ArrowRight" || event.key === "ArrowDown") {
          next = (index + 1) % tabs.length;
        } else if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
          next = (index - 1 + tabs.length) % tabs.length;
        } else if (event.key === "Home") {
          next = 0;
        } else if (event.key === "End") {
          next = tabs.length - 1;
        }
        if (next !== null) {
          event.preventDefault();
          select(next, true);
        }
      });
    });

    select(0, false);
  }

  /* ------------------------------------------------------------------ *
   * 5 · Factory build progression                                      *
   *                                                                    *
   * One pass of 7.2 s: six 900 ms stages plus a 900 ms hold at judgment *
   * (Product decision) and at verification (Evaluation). Because the    *
   * pass exceeds one second, pause and replay are mandatory (P4R5 §4.7, *
   * ILS p.08) and are created here. Reduced motion resolves to the same *
   * verified end state immediately with no timers at all.               *
   * ------------------------------------------------------------------ */

  var RESOLVED = [
    "Requirement linked to the company record",
    "Operating decision and human boundary explicit",
    "Sources, tools and permissions bounded",
    "Working context assembled from approved records",
    "Withheld release verified against the exception case",
    "Ready for governed review · release withheld from the agent",
  ];

  function initFactory() {
    var factory = document.querySelector("[data-factory]");
    if (!factory) {
      return;
    }
    var stages = Array.prototype.slice.call(
      factory.querySelectorAll(".cl-factory__stage")
    );
    var resolved = factory.querySelector("[data-factory-resolved]");
    var controlsHost = factory.querySelector("[data-factory-controls]");
    if (!stages.length || !resolved || !controlsHost) {
      return;
    }

    var index = -1;
    var timer = 0;
    var paused = false;
    var finished = false;
    var started = false;

    function paint(i) {
      stages.forEach(function (stage, s) {
        stage.classList.toggle("is-current", s === i);
        stage.classList.toggle("is-done", s < i);
      });
      resolved.textContent = RESOLVED[Math.max(0, i)];
    }

    function settle(speak) {
      finished = true;
      window.clearTimeout(timer);
      index = stages.length - 1;
      paint(index);
      renderControls();
      if (speak) {
        announce("Factory pass resolved: " + RESOLVED[RESOLVED.length - 1]);
      }
    }

    function step() {
      if (paused || finished) {
        return;
      }
      index += 1;
      if (index >= stages.length) {
        settle(true);
        return;
      }
      paint(index);
      var hold = stages[index].hasAttribute("data-hold");
      timer = window.setTimeout(step, FACTORY_STEP_MS + (hold ? FACTORY_HOLD_MS : 0));
    }

    var pauseButton = document.createElement("button");
    var replayButton = document.createElement("button");

    function renderControls() {
      controlsHost.hidden = false;
      pauseButton.hidden = finished;
      while (pauseButton.firstChild) {
        pauseButton.removeChild(pauseButton.firstChild);
      }
      pauseButton.appendChild(icon(paused ? "play" : "pause"));
      pauseButton.appendChild(
        document.createTextNode(paused ? "Resume motion" : "Pause motion")
      );
      pauseButton.setAttribute("aria-pressed", paused ? "true" : "false");
    }

    pauseButton.type = "button";
    pauseButton.addEventListener("click", function () {
      if (finished) {
        return;
      }
      paused = !paused;
      if (paused) {
        window.clearTimeout(timer);
      } else {
        timer = window.setTimeout(step, FACTORY_STEP_MS);
      }
      renderControls();
    });

    replayButton.type = "button";
    replayButton.appendChild(icon("rotate-ccw"));
    replayButton.appendChild(document.createTextNode("Replay"));
    replayButton.addEventListener("click", function () {
      window.clearTimeout(timer);
      finished = false;
      paused = false;
      index = -1;
      renderControls();
      step();
    });

    if (reduceMotion.matches) {
      /* No pass at all: the same verified end state, immediately. No
         control is offered, because there is no motion to pause or to
         replay — offering one would imply a state this mode does not have. */
      settle(false);
      controlsHost.hidden = true;
      return;
    }

    controlsHost.appendChild(pauseButton);
    controlsHost.appendChild(replayButton);
    renderControls();
    paint(0);
    index = 0;

    function start() {
      if (started) {
        return;
      }
      started = true;
      timer = window.setTimeout(step, FACTORY_STEP_MS);
    }

    if ("IntersectionObserver" in window) {
      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            observer.disconnect();
            start();
          }
        });
      /* The instrument is taller than some short laptop viewports. A 35%
         threshold can therefore become mathematically unreachable even
         when the component is clearly on screen. Ten percent still waits
         for genuine entry while remaining reachable at every supported
         viewport. */
      }, { threshold: 0.1 });
      observer.observe(factory);
    } else {
      start();
    }
  }

  /* ------------------------------------------------------------------ *
   * 6 · One capability, two surfaces                                   *
   *                                                                    *
   * The controls change the *mode of one object*, so this is a pressed- *
   * button group, not a tablist (P4R5 §5). The persistent company       *
   * record is outside both mode panels and is never re-rendered, so     *
   * switching mode provably changes context, action, permission and     *
   * evidence while the record itself does not move.                     *
   * ------------------------------------------------------------------ */

  function initSurfaces() {
    var scope = document.querySelector("[data-surfaces]");
    if (!scope) {
      return;
    }
    var buttons = Array.prototype.slice.call(
      scope.querySelectorAll("[data-surface-mode]")
    );
    var panels = Array.prototype.slice.call(
      scope.querySelectorAll("[data-surface-panel]")
    );
    if (!buttons.length || !panels.length) {
      return;
    }

    function select(key, speak) {
      var label = "";
      buttons.forEach(function (button) {
        var pressed = button.getAttribute("data-surface-mode") === key;
        button.setAttribute("aria-pressed", pressed ? "true" : "false");
        if (pressed) {
          label = button.textContent.trim();
        }
      });
      panels.forEach(function (panel) {
        panel.hidden = panel.getAttribute("data-surface-panel") !== key;
      });
      if (speak) {
        announce(
          "Surface: " + label +
          ". The company record, its permissions and its accountable owner are unchanged."
        );
      }
    }

    buttons.forEach(function (button) {
      button.addEventListener("click", function () {
        select(button.getAttribute("data-surface-mode"), true);
      });
    });

    select(buttons[0].getAttribute("data-surface-mode"), false);
  }

  /* ------------------------------------------------------------------ *
   * 7 · Strategic continuum — announcement only                        *
   *                                                                    *
   * Selection itself is pure CSS on a native radiogroup, so this adds   *
   * nothing to how it works. It only names the currently resolved       *
   * outcome for a screen reader, which CSS cannot do.                   *
   * ------------------------------------------------------------------ */

  function initContinuum() {
    var form = document.querySelector("[data-continuum]");
    if (!form) {
      return;
    }
    form.addEventListener("change", function (event) {
      var input = event.target;
      if (!input || input.name !== "outcome") {
        return;
      }
      var outcome = form.querySelector(
        '[data-outcome="' + input.value + '"] .cl-h3'
      );
      announce(
        outcome
          ? "Selected outcome: " + outcome.textContent
          : "Selected outcome: " + input.value
      );
    });
  }

  ready(function () {
    initInertStages();
    initDisclosureIcon();
    Array.prototype.forEach.call(
      document.querySelectorAll("[data-flyout]"),
      initFlyout
    );
    initSignal();
    initRecord();
    initFactory();
    initSurfaces();
    initContinuum();

    /* Every initial state is now written. Arm transitions on the next frame
       so nothing that was merely *set up* is also animated. */
    window.requestAnimationFrame(function () {
      window.requestAnimationFrame(function () {
        root.classList.remove("cl-booting");
      });
    });
  });
})();
