// Chart.js graphs for the dashboard: temperature, humidity and wind.
// Each chart is created once and then updated with new data.
(function () {
  const charts = {};

  const palette = {
    accent: "#4fa3ff",
    success: "#3ddc97",
    muted: "#a9b8dd",
    grid: "rgba(255, 255, 255, 0.08)",
  };

  // Settings shared by all three charts so they look consistent.
  function baseOptions(yTitle) {
    return {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: "index", intersect: false },
      plugins: {
        legend: { display: false },
        tooltip: { backgroundColor: "rgba(11, 20, 51, 0.95)", padding: 10 },
      },
      scales: {
        x: {
          ticks: { color: palette.muted, maxRotation: 0, autoSkip: true, maxTicksLimit: 8 },
          grid: { color: palette.grid },
        },
        y: {
          title: { display: true, text: yTitle, color: palette.muted },
          ticks: { color: palette.muted },
          grid: { color: palette.grid },
        },
      },
    };
  }

  function humidityOptions() {
    const options = baseOptions("%");
    options.scales.y.min = 0;
    options.scales.y.max = 100;
    return options;
  }

  // Create a chart the first time, or update the existing one afterwards.
  function upsert(id, config) {
    const canvas = document.getElementById(id);
    if (!canvas) return;
    if (charts[id]) {
      charts[id].data = config.data;
      charts[id].options = config.options;
      charts[id].update();
    } else {
      charts[id] = new Chart(canvas, config);
    }
    // Measure again after the layout settles. This fixes charts created
    // while their section was hidden or still animating.
    charts[id].resize();
  }

  function render(chart) {
    upsert("temp-chart", {
      type: "line",
      data: {
        labels: chart.labels,
        datasets: [{
          label: `Temperature (${chart.temp_unit})`,
          data: chart.temperature,
          borderColor: palette.accent,
          backgroundColor: "rgba(79, 163, 255, 0.2)",
          fill: true,
          tension: 0.4,
          pointRadius: 2,
        }],
      },
      options: baseOptions(chart.temp_unit),
    });

    upsert("humidity-chart", {
      type: "bar",
      data: {
        labels: chart.labels,
        datasets: [{
          label: "Humidity (%)",
          data: chart.humidity,
          backgroundColor: "rgba(61, 220, 151, 0.55)",
          borderRadius: 6,
        }],
      },
      options: humidityOptions(),
    });

    upsert("wind-chart", {
      type: "line",
      data: {
        labels: chart.labels,
        datasets: [{
          label: `Wind (${chart.wind_unit})`,
          data: chart.wind,
          borderColor: palette.success,
          backgroundColor: "rgba(61, 220, 151, 0.15)",
          fill: true,
          tension: 0.4,
          pointRadius: 2,
        }],
      },
      options: baseOptions(chart.wind_unit),
    });
  }

  // Chart.js resizes when the window changes, but not when a parent element
  // changes size on its own. ResizeObserver watches each chart's container.
  function watchContainers() {
    if (!("ResizeObserver" in window)) return;
    const observer = new ResizeObserver(() => {
      Object.values(charts).forEach((chart) => chart.resize());
    });
    document.querySelectorAll(".chart-wrap").forEach((box) => observer.observe(box));
  }

  window.SkyCastCharts = { render, watchContainers };
})();