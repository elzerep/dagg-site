(function () {
  "use strict";

  var PERMITTED = "permitted";
  var EXCEPTION = "exception";
  var labels = {};
  var spoken = {};

  labels[PERMITTED] = "Show material exception";
  labels[EXCEPTION] = "Return to permitted path";

  spoken[PERMITTED] =
    "Permitted path. The draft is prepared; the Finance owner retains human approval for release. Intent, boundary, accountable owner and provenance are unchanged.";
  spoken[EXCEPTION] =
    "Material exception. A mismatch is found, so the draft is withheld and nothing is released. Intent, boundary, accountable owner and provenance are unchanged.";

  function ready(callback) {
    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", callback, { once: true });
      return;
    }
    callback();
  }

  function makeAnnouncer() {
    var announcer = document.createElement("p");
    announcer.className = "sr-only";
    announcer.setAttribute("aria-live", "polite");
    announcer.setAttribute("aria-atomic", "true");
    document.body.appendChild(announcer);
    return announcer;
  }

  function initExceptionControl() {
    var scope = document.querySelector("[data-c1-exception]");
    if (!scope) return;
    if (scope.getAttribute("data-enhanced") === "true") return;

    var controls = scope.querySelector("[data-c1-controls]");
    if (!controls) return;

    var announcer = makeAnnouncer();
    var current = PERMITTED;
    var button = document.createElement("button");
    button.type = "button";
    button.setAttribute("aria-pressed", "false");
    button.textContent = labels[current];
    controls.appendChild(button);
    scope.setAttribute("data-enhanced", "true");
    scope.setAttribute("data-state", current);

    button.addEventListener("click", function () {
      current = current === PERMITTED ? EXCEPTION : PERMITTED;
      scope.setAttribute("data-state", current);
      button.setAttribute("aria-pressed", current === EXCEPTION ? "true" : "false");
      button.textContent = labels[current];
      announcer.textContent = spoken[current];
    });
  }

  ready(initExceptionControl);
})();
