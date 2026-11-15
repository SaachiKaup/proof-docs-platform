(function () {
  "use strict";
  const $ = (id) => document.getElementById(id);
  const editor = $("editor"), status = $("status");
  let topics = [], page = "", saved = "", savedTopics = "", timer, busy = false, pending = false, revision = 0;
  const dirty = () => editor.value !== saved || JSON.stringify(topics) !== savedTopics;
  const message = (text, isError = false) => { status.textContent = text; status.classList.toggle("error", isError); };
  const disablePreviewLink = () => { $("open-preview").removeAttribute("href"); $("open-preview").setAttribute("aria-disabled", "true"); };
  async function api(url, data) {
    const response = await fetch(url, data === undefined ? {} : {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(data)});
    const result = await response.json(); if (!response.ok) throw Error(result.error || response.statusText); return result;
  }
  function renderTopics() {
    $("topics").replaceChildren();
    topics.forEach((topic) => {
      const row = document.createElement("div"); row.className = "topic";
      const text = document.createElement("span"); text.textContent = `${topic.label} (${topic.id})`;
      const remove = document.createElement("button"); remove.textContent = "Remove"; remove.type = "button";
      remove.onclick = () => { topics = topics.filter((t) => t.id !== topic.id); renderTopics(); schedule(); };
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
    if (dirty() && !confirm("Discard unsaved changes?")) { $("pages").value = page; return; }
    revision++; disablePreviewLink();
    const result = await api("/api/page/" + name); page = name; editor.value = result.content; saved = result.content;
    const project = await api("/api/project"); topics = project.topics; savedTopics = JSON.stringify(topics); renderTopics();
    $("pages").value = page; preview();
  }
  $("add-topic").onsubmit = (event) => { event.preventDefault(); const id = $("topic-id").value.trim(), label = $("topic-name").value.trim(); if (!label || !/^[a-z][a-z0-9-]*$/.test(id) || topics.some((t) => t.id === id)) return message("Enter a unique lowercase topic ID and a name."); topics.push({id, label}); event.target.reset(); renderTopics(); schedule(); };
  $("save").onclick = async () => { if (busy) return message("Wait for the preview to finish before saving."); const snapshot = {page, content: editor.value, topics: JSON.parse(JSON.stringify(topics))}; try { await api("/api/save", snapshot); if (page === snapshot.page) { saved = snapshot.content; savedTopics = JSON.stringify(snapshot.topics); } const project = await api("/api/project"); updatePages(project.pages); $("pages").value = page; message(dirty() ? "Saved previous version; newer changes are not saved." : "Saved."); } catch (error) { $("frame").src = "about:blank"; disablePreviewLink(); message("Save failed: " + error.message, true); } };
  $("pages").onchange = (event) => openPage(event.target.value).catch((error) => { $("frame").src = "about:blank"; message(error.message, true); });
  $("new-page").onclick = () => { if (dirty() && !confirm("Discard unsaved changes?")) return; const name = prompt("New page path, for example chapters/my-proof.md"); if (!name) return; if (!/^[a-z0-9][a-z0-9-]*(\/[a-z0-9][a-z0-9-]*)*\.md$/.test(name)) return message("Use a lowercase Markdown path such as chapters/my-proof.md."); if ([...$("pages").options].some((o) => o.value === name)) return message("That page already exists."); page = name; editor.value = "# New proof\n"; saved = ""; const option = new Option(name, name); $("pages").add(option); $("pages").value = name; revision++; disablePreviewLink(); preview(); };
  editor.addEventListener("input", schedule);
  window.addEventListener("beforeunload", (event) => { if (dirty()) { event.preventDefault(); event.returnValue = ""; } });
  function updatePages(pages) { $("pages").replaceChildren(...pages.map((name) => new Option(name, name))); }
  api("/api/project").then((project) => { topics = project.topics; savedTopics = JSON.stringify(topics); renderTopics(); updatePages(project.pages); return openPage(project.pages[0]); }).catch((error) => { $("frame").src = "about:blank"; message(error.message, true); });
}());
