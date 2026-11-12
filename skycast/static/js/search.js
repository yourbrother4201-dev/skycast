// Search, suggestions, geolocation and recent searches.
// Talks to the Flask JSON endpoints: /api/search, /api/weather, /api/recent.
(function () {
  const DEBOUNCE_MS = 350;

  const form = () => document.getElementById("search-form");
  const input = () => document.getElementById("city-input");
  const suggestions = () => document.getElementById("suggestions");
  const message = () => document.getElementById("message");
  const preview = () => document.getElementById("result-preview");
  const recentList = () => document.getElementById("recent-list");
  const locateBtn = () => document.getElementById("locate-btn");

  function showMessage(text, isError = false) {
    const el = message();
    el.textContent = text;
    el.classList.toggle("is-error", isError);
  }

  function hideSuggestions() {
    suggestions().hidden = true;
    suggestions().innerHTML = "";
  }

  // Wait until the user stops typing before calling the API.
  function debounce(fn, ms) {
    let timer = null;
    return (...args) => {
      clearTimeout(timer);
      timer = setTimeout(() => fn(...args), ms);
    };
  }

  async function fetchJson(url) {
    const response = await fetch(url);
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Something went wrong.");
    }
    return data;
  }

  function renderSuggestions(results) {
    const list = suggestions();
    list.innerHTML = "";
    if (!results.length) {
      hideSuggestions();
      return;
    }
    results.forEach((city) => {
      const li = document.createElement("li");
      const btn = document.createElement("button");
      btn.type = "button";
      const place = [city.name, city.admin1, city.country].filter(Boolean).join(", ");
      btn.textContent = place;
      btn.addEventListener("click", () => chooseCity(city));
      li.appendChild(btn);
      list.appendChild(li);
    });
    list.hidden = false;
  }

  const loadSuggestions = debounce(async () => {
    const query = input().value.trim();
    if (query.length < 2) {
      hideSuggestions();
      return;
    }
    try {
      const data = await fetchJson(`/api/search?q=${encodeURIComponent(query)}`);
      renderSuggestions(data.results || []);
      if (!data.results || !data.results.length) {
        showMessage(data.message || "No matching city found.", true);
      } else {
        showMessage("");
      }
    } catch (err) {
      hideSuggestions();
      showMessage(err.message, true);
    }
  }, DEBOUNCE_MS);

  async function chooseCity(city) {
    hideSuggestions();
    input().value = city.name;
    await loadWeather(city.latitude, city.longitude, city.name, city.country);
  }

  async function loadWeather(lat, lon, name = "", country = "") {
    const button = form().querySelector("button[type=submit]");
    button.disabled = true;
    showMessage("Loading weather...");
    try {
      const params = new URLSearchParams({ lat, lon, unit: "C", name, country });
      const data = await fetchJson(`/api/weather?${params.toString()}`);
      preview().hidden = false;
      preview().textContent = JSON.stringify(data, null, 2);
      showMessage(`Weather loaded for ${name || "your location"}.`);
      loadRecent();
    } catch (err) {
      showMessage(err.message, true);
    } finally {
      button.disabled = false;
    }
  }

  async function loadRecent() {
    try {
      const data = await fetchJson("/api/recent");
      const list = recentList();
      list.innerHTML = "";
      data.results.forEach((city) => {
        const li = document.createElement("li");
        const btn = document.createElement("button");
        btn.type = "button";
        btn.textContent = city.name;
        btn.addEventListener("click", () =>
          loadWeather(city.latitude, city.longitude, city.name, city.country)
        );
        li.appendChild(btn);
        list.appendChild(li);
      });
    } catch (err) {
      // Recent searches are optional, so a failure here is not shown to the user.
    }
  }

  function useMyLocation() {
    if (!navigator.geolocation) {
      showMessage("Your browser does not support location. Please search for a city.", true);
      return;
    }
    showMessage("Asking for your location...");
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        loadWeather(pos.coords.latitude.toFixed(4), pos.coords.longitude.toFixed(4));
      },
      (err) => {
        const denied = err.code === err.PERMISSION_DENIED;
        showMessage(
          denied
            ? "Location permission was denied. You can still search for any city."
            : "Could not get your location. Please search for a city.",
          true
        );
      },
      { timeout: 10000 }
    );
  }

  function handleSubmit(event) {
    event.preventDefault();
    const query = input().value.trim();
    if (query.length < 2) {
      showMessage("Please type at least 2 characters.", true);
      return;
    }
    const first = suggestions().querySelector("button");
    if (first) {
      first.click();
    } else {
      showMessage("Pick a city from the suggestions list.", true);
    }
  }

  window.SkyCastSearch = {
    init() {
      input().addEventListener("input", loadSuggestions);
      form().addEventListener("submit", handleSubmit);
      locateBtn().addEventListener("click", useMyLocation);
      loadRecent();
    },
  };
})();