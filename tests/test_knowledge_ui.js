const assert = require("node:assert/strict");
const vm = require("node:vm");
const fs = require("node:fs");
const listeners = {}, windowListeners = {}, storage = {};
function block(tags) { return { dataset: { knowledgeTags: tags }, hidden: false }; }
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
  addEventListener(name, fn) { listeners[name] = fn; },
  getElementById() { return null; },
};
const window = {addEventListener(name, fn) { windowListeners[name] = fn; }};
const localStorage = {getItem(key) { return storage[key] || null; }, setItem(key, value) { storage[key] = value; }};
vm.runInNewContext(fs.readFileSync("docs/javascripts/topic-switch.js", "utf8"), {document, window, localStorage, location: {hash: ""}, Set, JSON});
listeners.DOMContentLoaded();
assert.equal(selector.hidden, false);
assert.equal(single.hidden, false); assert.equal(multi.hidden, false);
algebra.checked = true; listeners.change({target: algebra});
assert.equal(single.hidden, true); assert.equal(multi.hidden, false);
numbers.checked = true; listeners.change({target: numbers});
assert.equal(multi.hidden, true);
algebra.checked = false; listeners.change({target: algebra});
assert.equal(single.hidden, false); assert.equal(multi.hidden, false);
assert.deepEqual(JSON.parse(storage["proof-docs-known-topics-v1"]), ["number-theory"]);
console.log("Knowledge filtering: all-topic rule, restoration, and persistence passed");
