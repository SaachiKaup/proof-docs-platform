const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

class Element {
  constructor() { this.value = ""; this.hidden = false; this.children = []; this.options = []; this.classList = {toggle() {}}; }
  append(...items) { this.children.push(...items); }
  replaceChildren(...items) { this.children = items; }
  addEventListener() {}
  setAttribute() {}
  removeAttribute() {}
  reset() { elements["topic-name"].value = ""; elements["topic-id"].value = ""; }
}

const ids = ["editor", "status", "topic-setup", "setup-status", "open-preview", "topics", "pages", "frame", "topic-content", "setup-fields", "setup-continue", "topic-name", "topic-id", "add-topic", "save", "new-page", "editor-workspace"];
const elements = Object.fromEntries(ids.map((id) => [id, new Element()]));
elements["topic-setup"].hidden = true;
const savedTopics = [];
const fetch = async (url, options) => {
  if (url === "/api/project") return {ok: true, json: async () => ({needs_topic_setup: false, topics: [...savedTopics], pages: []})};
  if (url === "/api/topics/add") {
    const topic = JSON.parse(options.body).topic;
    if (savedTopics.some((item) => item.id === topic.id)) return {ok: false, json: async () => ({error: "Duplicate topic"})};
    savedTopics.push(topic);
    return {ok: true, json: async () => ({topics: [...savedTopics]})};
  }
  throw Error(`Unexpected request: ${url}`);
};
const document = {getElementById: (id) => elements[id], createElement: () => new Element()};
const context = {document, window: {addEventListener() {}}, fetch, setTimeout() {}, clearTimeout() {}, Option: function () {}};
vm.runInNewContext(fs.readFileSync("author/editor.js", "utf8"), context);

async function add(name, id = "") {
  elements["topic-name"].value = name;
  elements["topic-id"].value = id;
  await elements["add-topic"].onsubmit({preventDefault() {}, currentTarget: elements["add-topic"]});
}

(async () => {
  await new Promise((resolve) => setImmediate(resolve));
  await add("  Number   Theory  ");
  assert.deepEqual(savedTopics[0], {id: "number-theory", label: "Number   Theory"});
  await add("Abstract Algebra", "algebra-2");
  assert.deepEqual(savedTopics[1], {id: "algebra-2", label: "Abstract Algebra"});
  await elements.topics.children[0].children[1].onclick();
  assert.equal(elements.topics.children.length, 1);
  await add("Number   Theory");
  assert.equal(elements.topics.children.length, 2);
  assert.match(elements.topics.children[0].children[0].textContent, /Number   Theory/);
  assert.equal(savedTopics.length, 2);
  await elements.topics.children[0].children[1].onclick();
  await add("Number Theory", "number-theory");
  assert.match(elements.topics.children[0].children[0].textContent, /Number Theory/);
  await add("Number Theory");
  assert.match(elements.status.textContent, /already exists/);
  await add("2 Categories");
  assert.match(elements.status.textContent, /must start with a letter/);
  assert.equal(savedTopics.length, 2);
  console.log("Topic authoring: automatic IDs, overrides, duplicates and invalid IDs passed");
})().catch((error) => { console.error(error); process.exitCode = 1; });
