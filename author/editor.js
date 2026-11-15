(function () {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const editor = $("editor"), status = $("status");
  let topics = [], page = "", saved = "", savedTopics = "", timer, busy = false, pending = false, revision = 0;
  let topicBusy = false, saving = false, setupCreated = false;
  const dirty = () => editor.value !== saved || JSON.stringify(topics) !== savedTopics;
  const message = (text, isError = false) => { const target = $("topic-setup").hidden ? status : $("setup-status"); target.textContent = text; target.classList.toggle("error", isError); };
  const disablePreviewLink = () => { $("open-preview").removeAttribute("href"); $("open-preview").setAttribute("aria-disabled", "true"); };
  async function api(url, data) {
    const response = await fetch(url, data === undefined ? {} : {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(data)});
    const result = await response.json(); if (!response.ok) throw Error(result.error || response.statusText); return result;
  }
  async function removeTopic(topic) {
    if (topicBusy || saving) return;
    if (!$('topic-setup').hidden) {
      topicBusy = true;
      try {
        const result = await api("/api/topics/remove", {topic});
        savedTopics = JSON.stringify(result.topics);
      } catch (error) { message(error.message, true); return; }
      finally { topicBusy = false; }
    }
    topics = topics.filter((item) => item.id !== topic.id);
    renderTopics();
    schedule();
  }
  function renderTopics() {
    $("topics").replaceChildren();
    topics.forEach((topic) => {
      const row = document.createElement("div"); row.className = "topic";
      const text = document.createElement("span"); text.textContent = `${topic.label} (${topic.id})`;
      const remove = document.createElement("button"); remove.textContent = "Remove"; remove.type = "button";
      remove.onclick = () => removeTopic(topic);
      row.append(text, remove); $("topics").append(row);
    });
  }
  async function preview() {
    if (!page) return;
    if (busy) { pending = true; return; }
    busy = true; disablePreviewLink(); message("Updating…");
    const currentRevision = revision;
    try {
      const result = await api("/api/preview", {page, content: editor.value, topics});
      if (currentRevision === revision) {
        const url = result.url + "?v=" + Date.now();
        $("frame").src = url; $("open-preview").href = url; $("open-preview").setAttribute("aria-disabled", "false");
        message(dirty() ? "Unsaved changes" : "");
      }
    } catch (error) { if (currentRevision === revision) { $("frame").src = "about:blank"; disablePreviewLink(); message("Preview failed: " + error.message, true); } }
    finally { busy = false; if (pending) { pending = false; preview(); } }
  }
  function schedule() { revision++; disablePreviewLink(); clearTimeout(timer); timer = setTimeout(preview, 900); }
  async function openPage(name) {
    if (topicBusy || saving) { $("pages").value = page; return message("Wait for the current operation to finish."); }
    if (dirty() && !confirm("Discard unsaved changes?")) { $("pages").value = page; return; }
    revision++; disablePreviewLink();
    const result = await api("/api/page/" + name); page = name; editor.value = result.content; saved = result.content;
    const project = await api("/api/project"); topics = project.topics; savedTopics = JSON.stringify(topics); renderTopics();
    $("pages").value = page; preview();
  }
  function restoreTopic(topic, previous) {
    const index = previous.findIndex((item) => item.id === topic.id);
    if (index < 0) return false;
    const next = previous.slice(index + 1).find((item) => topics.some((current) => current.id === item.id));
    const position = next ? topics.findIndex((item) => item.id === next.id) : topics.length;
    topics = [...topics.slice(0, position), topic, ...topics.slice(position)];
    return true;
  }
  async function addTopic(event) {
    event.preventDefault();
    const form = event.currentTarget, label = $("topic-name").value.trim();
    const id = $("topic-id").value.trim() || label.toLowerCase().replace(/\s+/g, "-");
    if (topicBusy || saving) return;
    if (!label || !/^[a-z][a-z0-9-]*$/.test(id)) return message("Enter a topic name or ID using letters, numbers, spaces, and hyphens; the ID must start with a letter.", true);
    if (topics.some((t) => t.id === id)) return message(`Topic ID '${id}' already exists. Choose a different ID.`, true);
    const topic = {id, label}, previous = savedTopics ? JSON.parse(savedTopics) : [];
    if (restoreTopic(topic, previous)) {
      form.reset(); message(""); renderTopics(); schedule();
      return;
    }
    topicBusy = true;
    try {
      const result = await api("/api/topics/add", {topic});
      const removed = new Set(previous.filter((item) => !topics.some((current) => current.id === item.id)).map((item) => item.id));
      topics = result.topics.filter((item) => !removed.has(item.id));
      savedTopics = JSON.stringify(result.topics);
      if (!$("topic-setup").hidden) setupCreated = true;
      form.reset(); message(""); renderTopics(); schedule();
    } catch (error) { message(error.message, true); }
    finally { topicBusy = false; }
  }
  $("add-topic").onsubmit = addTopic;
  $("save").onclick = async () => { if (busy || topicBusy || saving) return message("Wait for the current operation to finish before saving."); saving = true; const snapshot = {page, content: editor.value, topics: JSON.parse(JSON.stringify(topics))}; try { await api("/api/save", snapshot); if (page === snapshot.page) { saved = snapshot.content; savedTopics = JSON.stringify(snapshot.topics); } const project = await api("/api/project"); updatePages(project.pages); $("pages").value = page; message(dirty() ? "Saved previous version; newer changes are not saved." : "Saved."); } catch (error) { $("frame").src = "about:blank"; disablePreviewLink(); message("Save failed: " + error.message, true); } finally { saving = false; } };
  $("pages").onchange = (event) => openPage(event.target.value).catch((error) => { $("frame").src = "about:blank"; message(error.message, true); });
  $("new-page").onclick = () => { if (topicBusy || saving) return message("Wait for the current operation to finish."); if (dirty() && !confirm("Discard unsaved changes?")) return; const name = prompt("New page path, for example chapters/my-proof.md"); if (!name) return; if (!/^[a-z0-9][a-z0-9-]*(\/[a-z0-9][a-z0-9-]*)*\.md$/.test(name)) return message("Use a lowercase Markdown path such as chapters/my-proof.md."); if ([...$("pages").options].some((o) => o.value === name)) return message("That page already exists."); page = name; editor.value = "# New proof\n"; saved = ""; const option = new Option(name, name); $("pages").add(option); $("pages").value = name; revision++; disablePreviewLink(); preview(); };
  editor.addEventListener("input", schedule);
  window.addEventListener("beforeunload", (event) => { if (dirty()) { event.preventDefault(); event.returnValue = ""; } });
  function updatePages(pages) { $("pages").replaceChildren(...pages.map((name) => new Option(name, name))); }
  function setupTopics() {
    const screen = $("topic-setup"), fields = $("topic-content"), home = fields.parentElement;
    $("setup-fields").append(fields);
    screen.hidden = false;
    return new Promise((resolve) => {
      $("setup-continue").onclick = async (event) => {
        if (topicBusy) return message("Wait for the topic to finish saving.", true);
        if ($("topic-name").value.trim() || $("topic-id").value.trim()) return message("Add the topic above, or clear the fields before continuing.", true);
        const button = event.currentTarget;
        button.disabled = true;
        try {
          if (!setupCreated) await api("/api/topics/initialize", {topics});
          home.append(fields);
          screen.hidden = true;
          resolve();
        } catch (error) { message(error.message, true); button.disabled = false; }
      };
    });
  }
  async function start() {
    let project = await api("/api/project");
    if (project.needs_topic_setup) {
      await setupTopics();
      project = await api("/api/project");
    }
    topics = project.topics;
    savedTopics = JSON.stringify(topics);
    renderTopics();
    updatePages(project.pages);
    $("editor-workspace").hidden = false;
    if (project.pages.length) await openPage(project.pages[0]);
    else message("No pages yet. Select New page to begin.");
  }
  start().catch((error) => { $("editor-workspace").hidden = false; $("frame").src = "about:blank"; message(error.message, true); });
}());
