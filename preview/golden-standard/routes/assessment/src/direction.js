(function () {
  "use strict";
  var root = document.querySelector("[data-assessment]");
  var form = root && root.querySelector("[data-assessment-form]");
  if (!form) return;
  var status = form.querySelector("[data-assessment-status]");
  var submit = form.querySelector("[data-assessment-submit]");
  var success = root.querySelector("[data-assessment-success]");
  var inFlight = false;
  form.hidden = false;
  submit.type = "submit";

  function setState(element, state, copy) {
    element.setAttribute("data-copy-state", state);
    element.textContent = copy;
  }

  function validate() {
    var first = null;
    Array.prototype.forEach.call(form.querySelectorAll("[required]"), function (field) {
      var valid = field.validity.valid && field.value.trim().length > 0;
      field.setAttribute("aria-invalid", valid ? "false" : "true");
      if (!valid && !first) first = field;
    });
    if (first) {
      setState(status, first.getAttribute("data-validation-state"), first.getAttribute("data-message"));
      first.focus();
      return false;
    }
    return true;
  }

  form.addEventListener("submit", function (event) {
    event.preventDefault();
    if (inFlight) {
      setState(submit, "duplicate", "Path received. No need to send it again.");
      setState(status, "duplicate", "Path received. No need to send it again.");
      return;
    }
    if (!validate()) return;
    inFlight = true;
    setState(submit, "submitting", "Checking the path locally…");
    setState(status, "submitting", "Checking the path locally…");
    window.setTimeout(function () {
      inFlight = false;
      form.hidden = true;
      success.hidden = false;
      success.focus();
    }, window.matchMedia("(prefers-reduced-motion: reduce)").matches ? 0 : 450);
  });
})();
