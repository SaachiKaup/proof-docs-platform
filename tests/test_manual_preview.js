const assert = require("node:assert/strict");
const fs = require("node:fs");
const vm = require("node:vm");

class Element {
  constructor() { this.value = ""; this.hidden = false; this.children = []; this.options = []; this.listeners = {}; this.classList = {toggle() {}}; }
  append(...items) { this.children.push(...items); }
  replaceChildren(...items) { this.children = items; this.options = items; }
  addEventListener(name, callback) { this.listeners[name] = callback; }
  setAttribute() {}
  removeAttribute(name) { delete this[name]; }
  reset() { elements["topic-name"].value = ""; elements["topic-id"].value = ""; }
}

const ids = ["editor", "status", "topic-setup", "setup-status", "open-preview", "open-site", "preview", "topics", "pages", "frame", "topic-content", "setup-fields", "setup-continue", "topic-name", "topic-id", "add-topic", "save", "new-page", "editor-workspace"];
const elements = Object.fromEntries(ids.map((id) => [id, new Element()]));
elements["topic-setup"].hidden = true;
elements["open-site"].hidden = true;
const requests = [];
let failPreview = false;
let failSave = false;
const fetch = async (url, options) => {
  requests.push({url, body: options?.body && JSON.parse(options.body)});
  if (url === "/api/project") return {ok: true, json: async () => ({needs_topic_setup: false, topics: [], pages: ["one.md", "two.md"]})};
  if (url.startsWith("/api/page/")) return {ok: true, json: async () => ({content: `# ${url.slice(10)}`})};
  if (url === "/api/topics/add") return {ok: true, json: async () => ({topics: [JSON.parse(options.body).topic]})};
  if (url === "/api/preview") return {ok: !failPreview, json: async () => failPreview ? {error: "Broken reference"} : {url: "/preview/one/"}};
  if (url === "/api/save") return {ok: !failSave, json: async () => failSave ? {error: "Save failed"} : {ok: true, site_url: "/site/one/"}};
  throw Error(`Unexpected request: ${url}`);
};
const document = {getElementById: (id) => elements[id], createElement: () => new Element()};
const context = {document, window: {addEventListener() {}}, fetch, confirm: () => true, prompt: () => null, Option: function (label, value) { this.value = value; }};
vm.runInNewContext(fs.readFileSync("author/editor.js", "utf8"), context);
const countPreviews = () => requests.filter((request) => request.url === "/api/preview").length;

(async () => {
  await new Promise((resolve) => setImmediate(resolve));
  assert.equal(countPreviews(), 1, "opening a page generates its initial preview");
  const initialPreview = elements.frame.src;
  elements.editor.value = "# Draft";
  elements.editor.listeners.input();
  elements.editor.listeners.input();
  assert.equal(countPreviews(), 1, "typing must not generate a preview");
  assert.equal(elements.frame.src, initialPreview, "typing keeps the initial preview");
  elements["topic-name"].value = "Algebra";
  await elements["add-topic"].onsubmit({preventDefault() {}, currentTarget: elements["add-topic"]});
  assert.equal(countPreviews(), 1, "adding a topic must not generate a preview");
  await elements.preview.onclick();
  assert.equal(countPreviews(), 2);
  assert.equal(requests.filter((request) => request.url === "/api/preview")[1].body.content, "# Draft");
  assert.equal(elements["open-site"].hidden, true, "saved site link is hidden before saving");
  await elements.save.onclick();
  assert.equal(elements["open-site"].hidden, false);
  assert.equal(elements["open-site"].href, "/site/one/");
  const previousPreview = elements.frame.src;
  elements.editor.value = "# Later draft";
  elements.editor.listeners.input();
  assert.equal(elements.frame.src, previousPreview, "typing must not replace the preview");
  assert.equal(countPreviews(), 2);
  failPreview = true;
  await elements.preview.onclick();
  assert.equal(countPreviews(), 3);
  assert.equal(elements.frame.src, "about:blank", "failed previews clear the viewer");
  assert.match(elements.status.textContent, /Broken reference/);
  failPreview = false;
  await elements.pages.onchange({target: {value: "two.md"}});
  assert.equal(countPreviews(), 4, "switching pages generates the new page's preview");
  assert.equal(elements["open-site"].hidden, true, "site link resets when switching pages");
  failSave = true;
  await elements.save.onclick();
  assert.equal(elements["open-site"].hidden, true, "failed save must not reveal a site link");
  console.log("Preview: initial render, manual updates, errors and page switching passed");
})().catch((error) => { console.error(error); process.exitCode = 1; });
