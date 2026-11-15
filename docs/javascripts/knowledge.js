(function () {
  "use strict";
  const key = "proof-docs-known-topics-v1";
  let selected = new Set();
  try { selected = new Set(JSON.parse(localStorage.getItem(key) || "[]")); } catch (_) {}

  function apply() {
    document.querySelectorAll(".md-content__inner .knowledge-block").forEach((block) => {
      const tags = (block.dataset.knowledgeTags || "").split(",").filter(Boolean);
      block.hidden = tags.length > 0 && tags.every((tag) => selected.has(tag));
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
      if (el.classList.contains("knowledge-block")) el.hidden = false;
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
    const link = event.target.closest('a[href^="#"]');
    if (!link || link.hash.length < 2) return;
    try { const target = document.getElementById(decodeURIComponent(link.hash.slice(1))); if (target) reveal(target); } catch (_) {}
  });
  window.addEventListener("hashchange", revealHash);
  if (window.document$) window.document$.subscribe(initialise);
  else document.addEventListener("DOMContentLoaded", initialise);
}());
