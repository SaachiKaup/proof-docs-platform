const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

const listeners = {};
const editor = {value: "", scrollTop: 0, addEventListener: (name, fn) => { listeners[name] = fn; }};
const gutter = {textContent: "", scrollTop: 0};
const document = {getElementById: (id) => id === "editor" ? editor : gutter};
const window = {};
vm.runInNewContext(fs.readFileSync("author/line-numbers.js", "utf8"), {document, window});

assert.equal(gutter.textContent, "1");
editor.value = "first\nsecond\n";
listeners.input();
assert.equal(gutter.textContent, "1\n2\n3");
editor.scrollTop = 42;
listeners.scroll();
assert.equal(gutter.scrollTop, 42);
editor.value = "loaded page\nsecond line";
window.updateEditorLineNumbers();
assert.equal(gutter.textContent, "1\n2");
console.log("Line numbers: input, scroll and page updates passed");
