// SkyCast front-end entry point.
// Starts each feature once the HTML is ready.
document.addEventListener("DOMContentLoaded", () => {
  document.body.dataset.ready = "true";
  if (window.SkyCastSearch) window.SkyCastSearch.init();
  if (window.SkyCastDashboard) window.SkyCastDashboard.init();
  if (window.SkyCastCharts) window.SkyCastCharts.watchContainers();
});