// ROBOMLM — Common utilities
// Auto-adds spinner + error banner to all /api/ fetches.
// Loaded by server automatically into every page.

(function () {
  const origFetch = window.fetch;

  function ensureEls() {
    if (!document.body) return;
    if (!document.getElementById("robo-spinner")) {
      const s = document.createElement("div");
      s.id = "robo-spinner";
      s.className = "spinner-overlay";
      s.innerHTML = '<div class="spinner"></div>';
      document.body.appendChild(s);
    }
    if (!document.getElementById("robo-error")) {
      const b = document.createElement("div");
      b.id = "robo-error";
      b.className = "error-banner";
      document.body.appendChild(b);
    }
  }

  window.fetch = async function (url, opts) {
    const isApi = typeof url === "string" && url.startsWith("/api/");
    if (!isApi) return origFetch(url, opts);

    ensureEls();
    const spinner = document.getElementById("robo-spinner");
    const errEl   = document.getElementById("robo-error");

    if (spinner) spinner.style.display = "flex";
    if (errEl)   errEl.style.display = "none";

    try {
      const res = await origFetch(url, opts);
      if (!res.ok) throw new Error("HTTP " + res.status);
      return res;
    } catch (e) {
      if (errEl) {
        errEl.textContent = "⚠️ Failed to load: " + e.message;
        errEl.style.display = "block";
        setTimeout(() => { errEl.style.display = "none"; }, 5000);
      }
      throw e;
    } finally {
      if (spinner) spinner.style.display = "none";
    }
  };

  // Ensure elements exist on DOM ready too
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", ensureEls);
  } else {
    ensureEls();
  }
})();