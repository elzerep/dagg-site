/* Dagg golden standard — shared global chrome enhancement
 *
 * Contract: design/golden-standard/packages/P3-GLOBAL-CHROME.md, section 7.
 *
 * This script only enhances the native <details>/<summary> disclosure and
 * the sticky header that chrome.css already renders correctly with no
 * JavaScript. It never becomes the only way to reach a route.
 */
(function () {
  "use strict";

  var header = document.querySelector("[data-chrome-header]");
  var disclosure = document.querySelector("[data-disclosure]");
  if (!header || !disclosure) {
    return;
  }

  var summary = disclosure.querySelector("[data-summary]");
  var panel = disclosure.querySelector("[data-panel]");
  var labelOpen = disclosure.querySelector("[data-label-menu]");
  var labelClose = disclosure.querySelector("[data-label-close]");
  var desktopQuery = window.matchMedia("(min-width: 940px)");
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  var lastScrollY = window.scrollY;
  var hideThreshold = 160;

  /* ------------------------------------------------------------------ *
   * Menu / Close label + explicit aria-expanded                         *
   * ------------------------------------------------------------------ */

  function syncDisclosureState() {
    var open = disclosure.open;
    summary.setAttribute("aria-expanded", open ? "true" : "false");
    if (labelOpen && labelClose) {
      labelOpen.hidden = open;
      labelClose.hidden = !open;
    }
    if (open && !desktopQuery.matches) {
      document.documentElement.style.overflow = "hidden";
      revealHeader();
    } else if (!desktopQuery.matches) {
      document.documentElement.style.overflow = "";
    }
  }

  disclosure.addEventListener("toggle", syncDisclosureState);
  syncDisclosureState();

  function closeDisclosure(restoreFocus) {
    if (!disclosure.open) {
      return;
    }
    disclosure.open = false;
    document.documentElement.style.overflow = "";
    if (restoreFocus) {
      summary.focus();
    }
  }

  panel.addEventListener("click", function (event) {
    var link = event.target.closest("a");
    if (link && !desktopQuery.matches) {
      closeDisclosure(false);
    }
  });

  document.addEventListener("click", function (event) {
    if (
      disclosure.open &&
      !desktopQuery.matches &&
      !disclosure.contains(event.target)
    ) {
      closeDisclosure(false);
    }
  });

  document.addEventListener("keydown", function (event) {
    if (event.key !== "Escape" || !disclosure.open || desktopQuery.matches) {
      return;
    }
    event.preventDefault();
    closeDisclosure(true);
  });

  /* Focus trap: while the mobile panel is open, Tab cannot leave the
     header navigation surface. */
  document.addEventListener("keydown", function (event) {
    if (event.key !== "Tab" || !disclosure.open || desktopQuery.matches) {
      return;
    }
    var focusable = header.querySelectorAll(
      'a[href], summary, [tabindex]:not([tabindex="-1"])'
    );
    if (!focusable.length) {
      return;
    }
    var first = focusable[0];
    var last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });

  desktopQuery.addEventListener("change", function (query) {
    if (query.matches) {
      closeDisclosure(false);
    }
  });

  /* ------------------------------------------------------------------ *
   * Sticky hide / reveal                                                *
   * ------------------------------------------------------------------ */

  function hideHeader() {
    if (disclosure.open) {
      return;
    }
    header.classList.add("chrome-header--hidden");
  }

  function revealHeader() {
    header.classList.remove("chrome-header--hidden");
  }

  window.addEventListener(
    "scroll",
    function () {
      var y = window.scrollY;
      if (y <= hideThreshold) {
        revealHeader();
      } else if (y > lastScrollY) {
        hideHeader();
      } else if (y < lastScrollY) {
        revealHeader();
      }
      lastScrollY = y;
    },
    { passive: true }
  );

  header.addEventListener("focusin", revealHeader);

  /* ------------------------------------------------------------------ *
   * Adaptive warm / ink header ground                                    *
   * ------------------------------------------------------------------ */

  var themedSections = document.querySelectorAll("[data-header-theme]");
  if (themedSections.length && "IntersectionObserver" in window) {
    var headerHeight = header.getBoundingClientRect().height || 68;
    var boundaryLine = Math.round(headerHeight + 1);
    var boundaryBottom = Math.max(
      0,
      Math.round(window.innerHeight - boundaryLine - 1)
    );
    var observer = new IntersectionObserver(
      function (entries) {
        var current = null;
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            current = entry.target;
          }
        });
        if (current) {
          var theme = current.getAttribute("data-header-theme");
          if (theme !== header.getAttribute("data-theme")) {
            header.setAttribute("data-theme", theme);
            if (!reduceMotion.matches) {
              revealHeader();
            }
          }
        }
      },
      {
        /* A one-pixel line fixed at the header's own bottom edge: only the
           section actually touching the header can ever be "current". A
           wider band would let a section still far down the viewport steal
           "current" the instant its edge grazes the band, flipping the
           theme before the header ever reaches it. */
        rootMargin: "-" + boundaryLine + "px 0px -" + boundaryBottom + "px 0px",
        threshold: 0,
      }
    );
    themedSections.forEach(function (section) {
      observer.observe(section);
    });
  }
})();
