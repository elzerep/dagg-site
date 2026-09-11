/* Direction B0 Codex — finite, progressive product-mechanism enhancement.
 * Static HTML remains complete with scripts blocked. */
(function () {
  "use strict";

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)");
  var STEP_MS = 650;
  var HOLD_MS = 650;
  var ICON_DIR = "/assets/vendor/lucide-dagg/icons/";
  var factoryController = null;

  var FACTORY_MODELS = {
    preserve: {
      messages: ["Work retained.", "Human judgment retained.", "Context preserved.", "No build opened.", "Review condition recorded.", "Refusal recorded."],
      bodies: ["Confirm the work remains proportionate.", "Preserve human judgment.", "Retain approved context.", "No build opened.", "Name the review condition.", "Record the refusal."]
    },
    simplify: {
      messages: ["Duplicate approval identified.", "Removal approved.", "Control retained.", "Workflow simplified.", "Outcome checked.", "Change recorded."],
      bodies: ["Identify the duplicate approval.", "Approve its removal.", "Retain the material control.", "Simplify the workflow.", "Verify the same outcome.", "Record the change."]
    },
    automate: {
      messages: ["Requirement linked to WG-034.", "Human release boundary retained.", "Approved context attached.", "Agent and tool boundary assembled.", "Mismatch hold verified.", "Ready for governed review."],
      bodies: ["Resolve before release.", "Prepare; preserve release.", "Link approved records.", "Bind agent and permission.", "Withhold mismatched release.", "Return evidence."]
    },
    rebuild: {
      messages: ["Target workflow defined.", "Rebuild selected.", "Context retained.", "Workflow layer rebuilt.", "Boundary verified.", "Release record ready."],
      bodies: ["Define the target workflow.", "Choose a rebuilt layer.", "Retain approved context.", "Build the new workflow layer.", "Verify the release boundary.", "Return release evidence."]
    },
    retire: {
      messages: ["Dependency checked.", "Retirement approved.", "Context archived.", "Requirement removed.", "Absence verified.", "Retirement recorded."],
      bodies: ["Check every dependency.", "Approve retirement.", "Archive retained context.", "Remove the requirement.", "Verify no material dependency.", "Record retirement."]
    }
  };

  function icon(name) {
    var image = document.createElement("img");
    image.src = ICON_DIR + name + ".svg";
    image.alt = "";
    image.width = 24;
    image.height = 24;
    image.setAttribute("aria-hidden", "true");
    return image;
  }

  function initPlan() {
    var decision = document.querySelector("[data-b-decision]");
    var plan = document.querySelector("[data-b-plan]");
    var factoryPlan = document.querySelector("[data-b-factory-plan]");
    if (!decision || !plan || !factoryPlan) return;

    decision.addEventListener("change", function (event) {
      var input = event.target;
      if (!input || input.name !== "outcome") return;
      var value = input.getAttribute("data-plan");
      if (!value) return;
      plan.textContent = value;
      factoryPlan.textContent = value;
      if (factoryController) factoryController.setModel(input.value);
    });
  }

  function initFactory() {
    var factory = document.querySelector("[data-b-factory]");
    if (!factory) return;
    var stages = Array.prototype.slice.call(factory.querySelectorAll(".cl-factory__stage"));
    var resolved = factory.querySelector("[data-b-factory-resolved]");
    var host = factory.querySelector("[data-b-factory-controls]");
    if (!stages.length || !resolved || !host) return;

    var timer = 0;
    var index = 0;
    var paused = false;
    var finished = false;
    var started = false;
    var messages = FACTORY_MODELS.automate.messages.slice();
    var bodies = stages.map(function (stage) { return stage.querySelector(".cl-factory__body"); });

    var pause = document.createElement("button");
    var replay = document.createElement("button");
    pause.type = "button";
    replay.type = "button";

    function paint(position) {
      stages.forEach(function (stage, stageIndex) {
        stage.classList.toggle("is-current", stageIndex === position);
        stage.classList.toggle("is-done", stageIndex < position);
      });
      resolved.textContent = messages[position];
    }

    function labelPause() {
      while (pause.firstChild) pause.removeChild(pause.firstChild);
      pause.appendChild(icon(paused ? "play" : "pause"));
      pause.appendChild(document.createTextNode(paused ? "Resume motion" : "Pause motion"));
      pause.setAttribute("aria-pressed", paused ? "true" : "false");
      pause.hidden = finished;
    }

    function finish() {
      window.clearTimeout(timer);
      finished = true;
      index = stages.length - 1;
      paint(index);
      labelPause();
    }

    function step() {
      if (paused || finished) return;
      index += 1;
      if (index >= stages.length) {
        finish();
        return;
      }
      paint(index);
      timer = window.setTimeout(step, STEP_MS + (stages[index].hasAttribute("data-hold") ? HOLD_MS : 0));
    }

    pause.addEventListener("click", function () {
      if (finished) return;
      paused = !paused;
      window.clearTimeout(timer);
      if (!paused) timer = window.setTimeout(step, STEP_MS);
      labelPause();
    });

    replay.appendChild(icon("rotate-ccw"));
    replay.appendChild(document.createTextNode("Replay"));
    replay.addEventListener("click", function () {
      window.clearTimeout(timer);
      index = 0;
      paused = false;
      finished = false;
      paint(index);
      labelPause();
      timer = window.setTimeout(step, STEP_MS);
    });

    host.appendChild(pause);
    host.appendChild(replay);
    host.hidden = false;

    factoryController = {
      setModel: function (key) {
        var model = FACTORY_MODELS[key];
        if (!model) return;
        window.clearTimeout(timer);
        messages = model.messages.slice();
        bodies.forEach(function (body, bodyIndex) {
          if (body) body.textContent = model.bodies[bodyIndex];
        });
        paused = false;
        if (reduced.matches) {
          finished = true;
          index = stages.length - 1;
          paint(index);
          host.hidden = true;
          return;
        }
        index = 0;
        finished = false;
        paint(0);
        labelPause();
        if (started) timer = window.setTimeout(step, STEP_MS);
      }
    };

    if (reduced.matches) {
      finish();
      host.hidden = true;
      return;
    }

    paint(0);
    labelPause();
    function start() {
      if (started) return;
      started = true;
      timer = window.setTimeout(step, STEP_MS);
    }
    if ("IntersectionObserver" in window) {
      var observer = new IntersectionObserver(function (entries) {
        if (entries.some(function (entry) { return entry.isIntersecting; })) {
          observer.disconnect();
          start();
        }
      }, { threshold: 0.1 });
      observer.observe(factory);
    } else {
      start();
    }

  }

  function initRecordAnnouncement() {
    var record = document.querySelector("[data-b-record]");
    if (!record) return;
    record.addEventListener("change", function (event) {
      var input = event.target;
      if (!input || input.name !== "record-state") return;
      var label = input.closest("label");
      if (!label) return;
      var title = label.querySelector("span");
      var detail = label.querySelector("small");
      record.setAttribute("aria-label", (title ? title.textContent : input.value) + ": " + (detail ? detail.textContent : ""));
    });
  }

  function init() {
    initPlan();
    initFactory();
    initRecordAnnouncement();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
