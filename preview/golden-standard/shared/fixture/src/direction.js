/* Dagg golden standard — shared substrate assembly fixture: composition JS
 *
 * Contract: design/golden-standard/packages/P4R6-DUAL-CUT-HOME-DIRECTIONS.md §9.
 * Deferred, loaded after chrome.js.
 *
 * This file exists to prove one thing: a direction can hook its own
 * composition without touching the shared chrome. It does not add or remove
 * `cl-enhanced` or `cl-booting` — chrome.js owns both — and it writes its
 * initial state inside its own DOMContentLoaded handler, before chrome.js
 * arms transitions two frames later.
 *
 * The element it writes to carries a real static value in body.html, so with
 * scripts blocked the sentence still reads correctly and nothing inert is
 * left behind. That is the no-JavaScript rule in miniature.
 */
(function () {
  "use strict";

  function init() {
    var state = document.querySelector("[data-fixture-js-state]");
    if (!state) {
      return;
    }
    state.textContent = "ready";
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
