const assert = require("node:assert/strict");
const vm = require("node:vm");
const fs = require("node:fs");
const listeners = {}, windowListeners = {}, storage = {};
function dispatch(name, event = {}) { (listeners[name] || []).forEach((listener) => listener(event)); }
function block(tags) {
  const content = {hidden: false}, reveal = {hidden: true, textContent: "Show explanation"};
  const result = {dataset: {knowledgeTags: tags}, content, reveal, querySelector(selector) {
    return selector === ".knowledge-content" ? content : selector === ".knowledge-reveal" ? reveal : null;
  }};
  reveal.closest = (selector) => selector === ".knowledge-block" ? result : null;
  return result;
}
const single = block("algebra"), multi = block("algebra,number-theory");
function checkbox(topic) { return {dataset: {knowledgeTopic: topic}, checked: false, closest() { return this; }}; }
const algebra = checkbox("algebra"), numbers = checkbox("number-theory");
const selector = {hidden: true};
const document = {
  querySelectorAll(query) {
    if (query === ".md-content__inner .knowledge-block") return [single, multi];
    if (query === "[data-knowledge-topic]") return [algebra, numbers];
    if (query === ".knowledge-selector") return [selector];
    return [];
  },
  addEventListener(name, fn) { (listeners[name] ||= []).push(fn); },
  getElementById() { return null; },
};
const window = {addEventListener(name, fn) { windowListeners[name] = fn; }};
const localStorage = {getItem(key) { return storage[key] || null; }, setItem(key, value) { storage[key] = value; }};
vm.runInNewContext(fs.readFileSync("docs/javascripts/topic-switch.js", "utf8"), {document, window, localStorage, location: {hash: ""}, Set, JSON});
dispatch("DOMContentLoaded");
assert.equal(selector.hidden, false);
assert.equal(single.content.hidden, false); assert.equal(single.reveal.hidden, true);
assert.equal(multi.content.hidden, false); assert.equal(multi.reveal.hidden, true);
algebra.checked = true; dispatch("change", {target: algebra});
assert.equal(single.content.hidden, true); assert.equal(single.reveal.hidden, false);
assert.equal(multi.content.hidden, false);
numbers.checked = true; dispatch("change", {target: numbers});
assert.equal(multi.content.hidden, true); assert.equal(multi.reveal.hidden, false);
dispatch("click", {target: {closest(selector) { return selector === ".knowledge-reveal" ? single.reveal : null; }}});
// The reader can temporarily expand content even while all of its tags are selected.
assert.equal(single.content.hidden, false);
assert.equal(single.reveal.textContent, "Hide explanation");
algebra.checked = false; dispatch("change", {target: algebra});
assert.equal(single.content.hidden, false); assert.equal(single.reveal.hidden, true);
assert.equal(multi.content.hidden, false); assert.equal(multi.reveal.hidden, true);
assert.deepEqual(JSON.parse(storage["proof-docs-known-topics-v1"]), ["number-theory"]);
console.log("Topic switch: all-topic filtering, manual expansion, restoration, and persistence passed");
