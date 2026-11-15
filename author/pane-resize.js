(function () {
  "use strict";
  const divider = document.getElementById("pane-divider");
  const panes = divider.parentElement;
  let width = 50;

  function setWidth(value) {
    width = Math.max(20, Math.min(80, Math.round(value)));
    panes.style.setProperty("--write-width", width + "%");
    divider.setAttribute("aria-valuenow", String(width));
  }

  function move(event) {
    const bounds = panes.getBoundingClientRect();
    if (bounds.width) setWidth((event.clientX - bounds.left) / bounds.width * 100);
  }

  divider.addEventListener("pointerdown", (event) => {
    if (event.button !== 0) return;
    event.preventDefault();
    divider.setPointerCapture(event.pointerId);
    divider.classList.add("dragging");
    move(event);
  });
  divider.addEventListener("pointermove", (event) => {
    if (divider.hasPointerCapture(event.pointerId)) move(event);
  });
  divider.addEventListener("lostpointercapture", () => divider.classList.remove("dragging"));
  divider.addEventListener("keydown", (event) => {
    if (event.key === "ArrowLeft") setWidth(width - 2);
    else if (event.key === "ArrowRight") setWidth(width + 2);
    else if (event.key === "Home") setWidth(20);
    else if (event.key === "End") setWidth(80);
    else return;
    event.preventDefault();
  });
}());
