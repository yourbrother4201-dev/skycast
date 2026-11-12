// Dashboard: fetches processed weather data and renders the cards.
// Owns the application state (current city and unit), so the unit toggle
// can refresh the data without a new search.
(function () {
  // Maps the icon names from Phase 3 to emoji. Emoji need no image files.
  const ICONS = {
    "sun": "☀️",
    "moon": "🌙",
    "cloud-sun": "⛅",
    "cloud-moon": "☁️",
    "cloud": "☁️",
    "fog": "🌫️",
    "drizzle": "🌦️",
    "rain": "🌧️",
    "snow": "❄️",
    "storm": "⛈️",
  };

  // Application state in one object. Nothing else keeps its own copy.
  const state = {
    city: null,   // { name, country, latitude, longitude }
    unit: "C",    // "C" or "F"
    data: null,   // last dashboard JSON from the server
  };

  const $ = (id) => document.getElementById(id);

  // Create an element with a class and text. textContent (not innerHTML)
  // means city names or other text can never inject HTML into the page.
  function el(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined && text !== null) node.textContent = text;
    return node;
  }

  function iconFor(name) {
    return ICONS[name] || "🌡️";
  }

  function showState(which, message) {
    $("dash-loading").hidden = which !== "loading";
    $("dash-error").hidden = which !== "error";
    $("dash-content").hidden = which !== "content";
    $("dash-section").hidden = false;
    if (which === "error") $("dash-error-text").textContent = message;
  }

  function setActiveUnit(unit) {
    document.querySelectorAll("[data-unit]").forEach((btn) => {
      btn.classList.toggle("is-active", btn.dataset.unit === unit);
    });
  }

  async function request(params) {
    const query = new URLSearchParams(params).toString();
    const response = await fetch(`/api/weather?${query}`);
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Weather could not be loaded.");
    }
    return data;
  }

  // Called when the user picks a city. Passing name and country tells the
  // server to save this search. Unit changes never pass them.
  async function loadCity(city) {
    state.city = city;
    showState("loading");
    try {
      state.data = await request({
        lat: city.latitude,
        lon: city.longitude,
        unit: state.unit,
        name: city.name,
        country: city.country || "",
      });
      render();
      document.dispatchEvent(new CustomEvent("skycast:searched"));
    } catch (err) {
      showState("error", err.message);
    }
  }

  // Called by the unit toggle or the refresh button. Re-uses the current city.
  async function refresh() {
    if (!state.city) return;
    showState("loading");
    try {
      state.data = await request({
        lat: state.city.latitude,
        lon: state.city.longitude,
        unit: state.unit,
      });
      render();
    } catch (err) {
      showState("error", err.message);
    }
  }

  function setUnit(unit) {
    if (unit === state.unit) return;
    state.unit = unit;
    setActiveUnit(unit);
    refresh();
  }

  function renderCurrent(current, cityLabel) {
    $("cur-city").textContent = cityLabel;
    $("cur-icon").textContent = iconFor(current.icon);
    $("cur-temp").textContent = current.temperature;
    $("cur-condition").textContent = current.condition;
    $("cur-feels").textContent = `Feels like ${current.feels_like}`;
    $("cur-humidity").textContent = current.humidity;
    $("cur-wind").textContent = current.wind;
    $("cur-pressure").textContent = current.pressure;
  }

  function renderHourly(hours) {
    const strip = $("hourly-strip");
    strip.innerHTML = "";
    hours.forEach((h) => {
      const item = el("div", "hour-item");
      item.append(
        el("span", "hour-time", h.time),
        el("span", "hour-icon", iconFor(h.icon)),
        el("span", "hour-temp", `${h.temperature}°`),
        el("span", "hour-precip", h.precipitation)
      );
      item.title = h.label;
      strip.appendChild(item);
    });
  }

  function renderDaily(days) {
    const list = $("daily-list");
    list.innerHTML = "";
    days.forEach((d) => {
      const row = el("li", "day-row");
      row.append(
        el("span", "day-name", d.day),
        el("span", "day-icon", iconFor(d.icon)),
        el("span", "day-precip", d.precipitation),
        el("span", "day-range", `${d.temp_max} / ${d.temp_min}`)
      );
      row.title = d.label;
      list.appendChild(row);
    });
  }

  function render() {
    const data = state.data;
    if (!data || !data.current) {
      showState("error", "The weather data was incomplete. Please try again.");
      return;
    }
    const cityLabel = state.city
      ? [state.city.name, state.city.country].filter(Boolean).join(", ")
      : "Your location";

    renderCurrent(data.current, cityLabel);
    renderHourly(data.hourly || []);
    renderDaily(data.daily || []);
    if (data.chart && window.SkyCastCharts) {
      window.SkyCastCharts.render(data.chart);
    }
    setActiveUnit(state.unit);
    showState("content");
    $("dash-section").scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function init() {
    document.querySelectorAll("[data-unit]").forEach((btn) => {
      btn.addEventListener("click", () => setUnit(btn.dataset.unit));
    });
    $("refresh-btn").addEventListener("click", refresh);
    $("retry-btn").addEventListener("click", refresh);
    setActiveUnit(state.unit);
  }

  window.SkyCastDashboard = {
    init,
    loadCity,
    refresh,
    setUnit,
    getState: () => state,
  };
})();