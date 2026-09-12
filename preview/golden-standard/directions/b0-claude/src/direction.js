/* Dagg Home direction B0 — Claude first cut: composition behaviour
 *
 * Package: design/golden-standard/packages/P4R6-B0-CLAUDE.md
 *
 * ------------------------------------------------------------------------
 * WHAT THIS FILE IS ALLOWED TO BE
 * ------------------------------------------------------------------------
 * The shared substrate contract forbids a direction script from forking
 * shared chrome behaviour, tokens or component behaviour. So this file adds
 * exactly one thing, and it is the one thing the accepted P4R5 library does
 * not provide: the governed-exception mode in act 07.
 *
 * Everything else on this page that moves is already the accepted shared
 * behaviour, initialised by the passed component script from the accepted
 * markup this direction composed:
 *
 *   five strategic decisions   data-continuum  (CSS selection + announce)
 *   WorkGraph inputs           data-record     (tablist, roving tabindex)
 *   Factory state              data-factory    (one pass, pause, replay)
 *   two surfaces               data-surfaces   (pressed-button mode group)
 *   Machine Signal             data-signal-carrier (one finite pass)
 *
 * This file re-implements none of them and reads none of their state.
 *
 * ------------------------------------------------------------------------
 * PROGRESSIVE ENHANCEMENT
 * ------------------------------------------------------------------------
 * Act 07 renders both boundary states as static markup, in reading order.
 * With scripts blocked that is the whole act and it is complete: no control
 * is in the document, so no control can be inert. This file creates the
 * two-button group first and only then hides the second state, so the
 * document is never left with a hidden state and no way to reach it.
 *
 * The controls change the mode of one object rather than switching between
 * two independent panels, so this is a pressed-button group and not a
 * tablist — the same distinction the shared two-surface carrier makes.
 *
 * ------------------------------------------------------------------------
 * MOTION
 * ------------------------------------------------------------------------
 * The enhancement is a state swap. There is no timer, no loop, no ambient
 * animation and nothing to pause, so reduced motion reaches an identical
 * final state through the identical code path; direction.css removes the
 * one 180 ms colour response on the control itself.
 */
(function () {
  "use strict";

  /* The shared script owns the document-level enhancement classes and the
     shared live region. This file writes neither. It announces through the
     button's own pressed state, which assistive technology already
     reports, so no second live region is created. */

  function initGovernedException() {
    var scope = document.querySelector("[data-b-exception]");
    if (!scope) {
      return;
    }

    var host = scope.querySelector("[data-b-exception-controls]");
    var panels = Array.prototype.slice.call(
      scope.querySelectorAll("[data-b-exception-panel]")
    );
    if (!host || panels.length < 2) {
      /* A part is missing. Leave the static reading — both states, in
         order — exactly as authored rather than half-wiring a control. */
      return;
    }

    var LABELS = {
      bounded: "Within bounds",
      exception: "Governed exception",
    };

    var buttons = panels.map(function (panel, index) {
      var key = panel.getAttribute("data-b-exception-panel");
      var button = document.createElement("button");
      button.type = "button";
      button.setAttribute("data-b-exception-mode", key);
      button.setAttribute("aria-pressed", index === 0 ? "true" : "false");

      /* aria-controls needs a real id. The panels are authored without
         one so that nothing in the static document points at an element
         that only enhancement makes conditional. */
      if (!panel.id) {
        panel.id = "b-boundary-state-" + key;
      }
      button.setAttribute("aria-controls", panel.id);
      button.appendChild(
        document.createTextNode(LABELS[key] || key)
      );
      host.appendChild(button);
      return button;
    });

    function select(key) {
      buttons.forEach(function (button) {
        button.setAttribute(
          "aria-pressed",
          button.getAttribute("data-b-exception-mode") === key ? "true" : "false"
        );
      });
      panels.forEach(function (panel) {
        panel.hidden = panel.getAttribute("data-b-exception-panel") !== key;
      });
    }

    buttons.forEach(function (button) {
      button.addEventListener("click", function () {
        select(button.getAttribute("data-b-exception-mode"));
      });
    });

    /* The control exists before anything is hidden. */
    host.hidden = false;
    select(panels[0].getAttribute("data-b-exception-panel"));
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initGovernedException, {
      once: true,
    });
  } else {
    initGovernedException();
  }
})();
