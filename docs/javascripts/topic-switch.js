(function () {
  "use strict";
  const key = "proof-docs-known-topics-v1";
  let selected = new Set();
  try { selected = new Set(JSON.parse(localStorage.getItem(key) || "[]")); } catch (_) {}

  function apply() {
    document.querySelectorAll(".md-content__inner .knowledge-block").forEach((block) => {
      const tags = (block.dataset.knowledgeTags || "").split(",").filter(Boolean);
      const understood = tags.length > 0 && tags.every((tag) => selected.has(tag));
      const content = block.querySelector(".knowledge-content");
      const reveal = block.querySelector(".knowledge-reveal");
      if (!content || !reveal) return;
      content.hidden = understood && block.dataset.expanded !== "true";
      reveal.hidden = !understood;
      reveal.textContent = content.hidden ? "Show explanation" : "Hide explanation";
    });
    document.querySelectorAll("[data-knowledge-topic]").forEach((checkbox) => {
      checkbox.checked = selected.has(checkbox.dataset.knowledgeTopic);
    });
  }
  function initialise() {
    document.querySelectorAll(".knowledge-selector").forEach((el) => { el.hidden = false; });
    apply();
    revealHash();
  }
  function reveal(target) {
    for (let el = target; el; el = el.parentElement) {
      if (!el.classList.contains("knowledge-block")) continue;
      const content = el.querySelector(".knowledge-content");
      if (!content) continue;
      content.hidden = false;
      el.dataset.expanded = "true";
      const button = el.querySelector(".knowledge-reveal");
      if (button) button.textContent = "Hide explanation";
    }
  }
  function revealHash() {
    if (!location.hash) return;
    try { const target = document.getElementById(decodeURIComponent(location.hash.slice(1))); if (target) reveal(target); } catch (_) {}
  }
  document.addEventListener("change", (event) => {
    const box = event.target.closest("[data-knowledge-topic]");
    if (!box) return;
    if (box.checked) selected.add(box.dataset.knowledgeTopic); else selected.delete(box.dataset.knowledgeTopic);
    try { localStorage.setItem(key, JSON.stringify([...selected])); } catch (_) {}
    apply();
  });
  document.addEventListener("click", (event) => {
    const button = event.target.closest(".knowledge-reveal");
    if (!button) return;
    const block = button.closest(".knowledge-block");
    const content = block?.querySelector(".knowledge-content");
    if (!content) return;
    content.hidden = !content.hidden;
    block.dataset.expanded = String(!content.hidden);
    const understood = (block.dataset.knowledgeTags || "").split(",").filter(Boolean)
      .every((tag) => selected.has(tag));
    button.hidden = !understood;
    button.textContent = content.hidden ? "Show explanation" : "Hide explanation";
  });
  document.addEventListener("click", (event) => {
    const link = event.target.closest('a[href^="#"]');
    if (!link || link.hash.length < 2) return;
    try { const target = document.getElementById(decodeURIComponent(link.hash.slice(1))); if (target) reveal(target); } catch (_) {}
  });
  window.addEventListener("hashchange", revealHash);
  if (window.document$) window.document$.subscribe(initialise);
  else document.addEventListener("DOMContentLoaded", initialise);
}());
