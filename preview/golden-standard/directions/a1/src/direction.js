/* Direction A1 — local progressive enhancement only.
 * The A04 hero asset remains still-only. Finite machine motion belongs to the
 * shared Factory mechanism; this file only reveals the accepted surface mode
 * controls after the shared component layer is available. */
(function () {
  "use strict";

  function init() {
    var surfaceControls = document.querySelector("[data-a-surface-controls]");
    if (surfaceControls) {
      surfaceControls.hidden = false;
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();

