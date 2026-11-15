(function () {
  "use strict";
  const editor = document.getElementById("editor");
  const gutter = document.getElementById("line-numbers");

  function updateLineNumbers() {
    const count = editor.value.split("\n").length;
    gutter.textContent = Array.from({length: count}, (_, index) => index + 1).join("\n");
    gutter.scrollTop = editor.scrollTop;
  }

  editor.addEventListener("input", updateLineNumbers);
  editor.addEventListener("scroll", () => { gutter.scrollTop = editor.scrollTop; });
  window.updateEditorLineNumbers = updateLineNumbers;
  updateLineNumbers();
}());
