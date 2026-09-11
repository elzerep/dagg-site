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

