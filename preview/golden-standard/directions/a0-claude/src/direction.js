/* Dagg golden standard — P4R6 direction A0-Claude: composition behaviour
 *
 * Package: design/golden-standard/packages/P4R6-A0-CLAUDE.md
 * Loads:   last, after the accepted P3 chrome.js and the passed P4R5
 *          component-library/script.js.
 *
 * ------------------------------------------------------------------------
 * WHY THIS FILE IS SHORT
 * ------------------------------------------------------------------------
 * Every progressive-enhancement state the package requires already has an
 * accepted owner, and the shared-substrate contract forbids a direction from
 * forking it:
 *
 *   five strategic decisions   native radiogroup + CSS; the component script
 *                              only announces the resolved outcome
 *   WorkGraph source states     component script, created tablist
 *   finite Factory progression  component script, one pass, two holds,
 *                              pause and replay, reduced-motion end state
 *   both operating surfaces     component script, pressed-button mode group
 *   governed exception          static default state in act 7, so it is
 *                              present with scripts blocked
 *
 * Re-implementing any of those here would double-initialise them, which is
 * the exact failure the substrate acceptance record was written to prevent.
 *
 * ------------------------------------------------------------------------
 * WHAT THIS FILE DOES OWN
 * ------------------------------------------------------------------------
 * Direction A's own interaction model: the editorial reveal. It is a native
 * <details>, so it opens, reads and closes with scripts blocked and this
 * file is never the only way to reach the content. Enhancement adds the two
 * things the native element does not give and that P4R3 §5 requires of a
 * disclosure:
 *
 *   1. an explicit aria-expanded on the control, kept in sync with the one
 *      source of truth — the element's own `open` property;
 *   2. Escape closes the reveal and returns focus to the control that
 *      opened it.
 *
 * Nothing here animates, schedules a timer, loops, or writes a class the
 * shared layers own.
 */
(function () {
  "use strict";

  var reveals = document.querySelectorAll("[data-a0-reveal]");
  if (!reveals.length) {
    return;
  }

  Array.prototype.forEach.call(reveals, function (reveal) {
    var summary = reveal.querySelector("summary");
    if (!summary) {
      return;
    }

    function sync() {
      summary.setAttribute("aria-expanded", reveal.open ? "true" : "false");
    }

    reveal.addEventListener("toggle", sync);

    /* Escape is scoped to the reveal, and the handler stops propagation only
       when it actually closed something, so the shared chrome's own Escape
       handling for the mobile navigation panel is never swallowed. */
    reveal.addEventListener("keydown", function (event) {
      if (event.key !== "Escape" || !reveal.open) {
        return;
      }
      event.preventDefault();
      event.stopPropagation();
      reveal.open = false;
      summary.focus();
    });

    sync();
  });
})();
