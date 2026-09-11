/* Dagg golden standard — P4R6 · Direction C · Claude first cut (C0)
 *
 * Package: design/golden-standard/packages/P4R6-C0-CLAUDE.md
 *
 * This file adds exactly one behaviour: the inspectable governed exception
 * in act 07. Everything else on the page is driven by the passed P4R5
 * component script, which already owns the five strategic decisions, the
 * WorkGraph source inputs, the Factory stop and the two operating surfaces.
 * This direction does not re-implement, wrap or shadow any of them, and it
 * never writes the enhancement classes chrome.js owns.
 *
 * Progressive enhancement only:
 *
 *   - both exception states are authored in the document, under their own
 *     labels, so with JavaScript blocked the act is read in order and is
 *     complete;
 *   - the toggle is CREATED here, so the no-JavaScript document contains no
 *     inert control that implies a state it cannot reach;
 *   - the toggle changes state, not position or size. It runs no timer,
 *     starts no pass and loops nothing, so reduced motion reaches exactly
 *     the same states by exactly the same route.
 *
 * The point the interaction has to make is that the surface of the record
 * changes while intent, boundary, accountable owner and provenance do not.
 * Those four are printed once, beneath both states, and are never touched.
 */
(function () {
  "use strict";

  var PERMITTED = "permitted";
  var EXCEPTION = "exception";

  var LABEL = {};
  LABEL[PERMITTED] = "Hold the release";
  LABEL[EXCEPTION] = "Return to the permitted path";

  var SPOKEN = {};
  SPOKEN[PERMITTED] =
    "Permitted path. The draft is prepared and awaits the release decision. " +
    "Intent, boundary, accountable owner and provenance are unchanged.";
  SPOKEN[EXCEPTION] =
    "Material exception. The draft is withheld and nothing is released, " +
    "held for the accountable owner. Intent, boundary, accountable owner " +
    "and provenance are unchanged.";

  function ready(callback) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", callback, { once: true });
    } else {
      callback();
    }
  }

  /* One polite region for this direction's single control. It is created
     rather than authored so the no-JavaScript document carries no empty
     live region, and it announces the state the reader just chose. */
  function makeAnnouncer() {
    var region = document.createElement("p");
    region.setAttribute("aria-live", "polite");
    region.setAttribute("role", "status");
    region.style.cssText =
      "position:absolute;width:1px;height:1px;overflow:hidden;" +
      "clip-path:inset(50%);white-space:nowrap;";
    document.body.appendChild(region);
    return region;
  }

  function initException() {
    var scope = document.querySelector("[data-c0-exception]");
    if (!scope) {
      return;
    }

    var host = scope.querySelector("[data-c0-exception-control]");
    var states = Array.prototype.slice.call(
      scope.querySelectorAll("[data-c0-exception-state]")
    );
    if (!host || states.length !== 2) {
      /* A part is missing. Leave the authored document exactly as it is —
         both states readable — rather than half-wiring a control that
         cannot resolve. */
      return;
    }

    var announcer = null;
    var current = PERMITTED;

    var button = document.createElement("button");
    button.type = "button";
    button.setAttribute("data-c0-exception-toggle", "");

    var label = document.createTextNode(LABEL[PERMITTED]);
    button.appendChild(label);

    function apply(key, speak) {
      current = key;
      states.forEach(function (state) {
        state.hidden = state.getAttribute("data-c0-exception-state") !== key;
      });
      label.nodeValue = LABEL[key];
      button.setAttribute("aria-pressed", key === EXCEPTION ? "true" : "false");
      if (speak) {
        if (!announcer) {
          announcer = makeAnnouncer();
        }
        announcer.textContent = SPOKEN[key];
      }
    }

    button.addEventListener("click", function () {
      apply(current === PERMITTED ? EXCEPTION : PERMITTED, true);
    });

    host.appendChild(button);
    host.hidden = false;
    apply(PERMITTED, false);
  }

  ready(initException);
})();
