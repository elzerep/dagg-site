/* Impact route enhancement. Progressive only: nothing here hides, reorders or
 * reveals public copy, and the page is complete without it.
 *
 * The one job is indexing prevention for an internal staging route. The
 * assembler's meta.json contract has no robots field and FS1 does not own a
 * head.html partial, so the robots directive is declared in meta.json for
 * the publication build and applied here at runtime for local staging. */
(function () {
  "use strict";
  var root = document.querySelector("[data-impact]");
  if (!root) return;

  if (!document.head.querySelector('meta[name="robots"]')) {
    var robots = document.createElement("meta");
    robots.setAttribute("name", "robots");
    robots.setAttribute("content", "noindex, nofollow");
    document.head.appendChild(robots);
  }

  root.setAttribute("data-impact-ready", "");
})();
