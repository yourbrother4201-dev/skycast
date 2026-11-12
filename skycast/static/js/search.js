// Search box, suggestions and recent searches.
// Choosing a city hands it to the dashboard module.
(function () {
  const DEBOUNCE_MS = 350;

  const $ = (id) => document.getElementById(id);

  function showMessage(text, isError = false) {
    const el = $("message");
    el.textContent = text;
    el.classList.toggle("is-error", isError);
  }

  function hideSuggestions() {
    const list = $("suggestions");
    list.hidden = true;
    list.innerHTML = "";
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

  function chooseCity(city) {
    hideSuggestions();
    $("city-input").value = city.name;
    showMessage("");
    window.SkyCastDashboard.loadCity(city);
  }

  function renderSuggestions(results) {
    const list = $("suggestions");
    list.innerHTML = "";
    results.forEach((city) => {
      const li = document.createElement("li");
      const btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = [city.name, city.admin1, city.country].filter(Boolean).join(", ");
      btn.addEventListener("click", () => chooseCity(city));
      li.appendChild(btn);
      list.appendChild(li);
    });
    list.hidden = results.length === 0;
  }

  const loadSuggestions = debounce(async () => {
    const query = $("city-input").value.trim();
    if (query.length < 2) {
      hideSuggestions();
      return;
    }
    try {
      const data = await fetchJson(`/api/search?q=${encodeURIComponent(query)}`);
      renderSuggestions(data.results || []);
      showMessage(data.results && data.results.length ? "" : data.message || "No matching city found.", !(data.results && data.results.length));
    } catch (err) {
      hideSuggestions();
      showMessage(err.message, true);
    }
  }, DEBOUNCE_MS);

  async function loadRecent() {
    try {
      const data = await fetchJson("/api/recent");
      const list = $("recent-list");
      list.innerHTML = "";
      data.results.forEach((city) => {
        const li = document.createElement("li");
        const btn = document.createElement("button");
        btn.type = "button";
        btn.textContent = city.name;
        btn.addEventListener("click", () => chooseCity(city));
        li.appendChild(btn);
        list.appendChild(li);
      });
    } catch (err) {
      // Recent searches are optional, so a failure is not shown to the user.
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
        hideSuggestions();
        $("city-input").value = "";
        showMessage("");
        window.SkyCastDashboard.loadCity({
          name: "",
          country: "",
          latitude: pos.coords.latitude.toFixed(4),
          longitude: pos.coords.longitude.toFixed(4),
        });
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
    const query = $("city-input").value.trim();
    if (query.length < 2) {
      showMessage("Please type at least 2 characters.", true);
      return;
    }
    const first = $("suggestions").querySelector("button");
    if (first) {
      first.click();
    } else {
      showMessage("Pick a city from the suggestions list.", true);
    }
  }

  window.SkyCastSearch = {
    init() {
      $("city-input").addEventListener("input", loadSuggestions);
      $("search-form").addEventListener("submit", handleSubmit);
      $("locate-btn").addEventListener("click", useMyLocation);
      document.addEventListener("skycast:searched", loadRecent);
      loadRecent();
    },
  };
})();