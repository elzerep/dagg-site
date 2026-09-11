import { readFileSync } from "node:fs";
import vm from "node:vm";

const script = readFileSync(
  new URL("../../preview/golden-standard/directions/a2/src/direction.js", import.meta.url),
  "utf8",
);
const css = readFileSync(
  new URL("../../preview/golden-standard/directions/a2/src/direction.css", import.meta.url),
  "utf8",
);

function makeClassList() {
  const values = new Set();
  return {
    add(value) { values.add(value); },
    remove(value) { values.delete(value); },
    toggle(value, force) {
      if (force) values.add(value);
      else values.delete(value);
    },
    contains(value) { return values.has(value); },
  };
}

const steps = Array.from({ length: 4 }, () => ({ classList: makeClassList() }));
const proof = { querySelectorAll: () => steps };
const instrument = {};
const listeners = new Map();
const replay = {
  addEventListener(type, handler) { listeners.set(type, handler); },
};
const label = { textContent: "Play the pass" };
const icon = { src: "/assets/vendor/lucide-dagg/icons/play.svg" };
const status = { textContent: "" };
const reducedMedia = {
  matches: true,
  addEventListener() {},
};
let timerCount = 0;

const context = {
  document: {
    querySelector(selector) {
      if (selector === "[data-a2-instrument]") return instrument;
      if (selector === "[data-a2-proof]") return proof;
      if (selector === "[data-a2-replay]") return replay;
      if (selector === "[data-a2-control-label]") return label;
      if (selector === "[data-a2-control-icon]") return icon;
      if (selector === "[data-a2-status]") return status;
      return null;
    },
  },
  window: {
    matchMedia: () => reducedMedia,
    clearTimeout() {},
    setTimeout() { timerCount += 1; return timerCount; },
  },
  Array,
};

vm.runInNewContext(script, context, { filename: "direction.js" });

if (!listeners.has("click")) throw new Error("Replay click handler is missing.");
listeners.get("click")();

const active = steps.map((step) => step.classList.contains("is-active"));
if (active.join(",") !== "false,false,false,true") {
  throw new Error(`Reduced motion did not resolve immediately: ${active.join(",")}`);
}
if (timerCount !== 0) throw new Error(`Reduced motion scheduled ${timerCount} timer(s).`);
if (!/prefers-reduced-motion:\s*reduce/.test(css) || !/transition:\s*none/.test(css)) {
  throw new Error("Reduced-motion CSS does not remove the A2 transition.");
}
if (label.textContent !== "Replay the pass") {
  throw new Error(`Unexpected reduced-motion control label: ${label.textContent}`);
}
if (!icon.src.endsWith("/rotate-ccw.svg")) {
  throw new Error(`Unexpected reduced-motion control icon: ${icon.src}`);
}
if (status.textContent !== "Resolved state: draft withheld for Finance review.") {
  throw new Error(`Unexpected reduced-motion status: ${status.textContent}`);
}

console.log("PASS: reduced motion resolves immediately, schedules zero timers, and removes CSS transitions.");
