// SkyCast front-end entry point.
// Starts the page features. Search logic lives in search.js.
document.addEventListener("DOMContentLoaded", () => {
  document.body.dataset.ready = "true";
  if (window.SkyCastSearch) {
    window.SkyCastSearch.init();
  }
});