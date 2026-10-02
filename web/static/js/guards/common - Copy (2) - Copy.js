// ROBOMLM â€” Common utilities
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
      if (!res.ok) throw new Error('HTTP ' + res.status);
      return res;
    } catch (e) {
      if (errEl) {
        errEl.textContent = "âš ï¸ Failed to load: " + e.message;
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

// ============================================================================
// AUTH GUARD â€” DEVELOPMENT DIRECT-PAGE MODE
// ============================================================================

(function() {
  const PATH = window.location.pathname.replace(/\/$/, "") || "/";

  // Local development: allow direct access to every frontend page.
  // Production authentication remains available by removing/disable this mode.
  const DEV_DIRECT_PAGE_MODE = true;

  if (DEV_DIRECT_PAGE_MODE) {
    window.ROBOMLM_DEV_AUTH_BYPASS = true;
    return;
  }

  const PUBLIC_PAGES = ["/login", "/constitution", "/risk-disclosure"];

  if (PUBLIC_PAGES.includes(PATH)) return;

  const token = localStorage.getItem("robomlm_token");

  if (!token) {
    window.location.href = "/login";
    return;
  }

  fetch("/api/auth/status?token=" + encodeURIComponent(token))
    .then(r => r.json())
    .then(d => {
      if (!d.logged_in) {
        localStorage.removeItem("robomlm_token");
        window.location.href = "/login";
      } else if (!d.constitution_accepted) {
        window.location.href = "/constitution";
      } else if (!d.risk_accepted) {
        window.location.href = "/risk-disclosure";
      }
    })
    .catch(() => {
      window.location.href = "/login";
    });
})();
// ============================================================================
// LOGOUT BUTTON â€” auto-inject into sidebar footer
// ============================================================================
(function() {
  function injectLogout() {
    const footer = document.querySelector(".sidebar-footer");
    if (!footer || footer.querySelector(".logout-btn")) return;

    const btn = document.createElement("button");
    btn.className = "logout-btn";
    btn.innerHTML = "âŽ‹ Sign Out";
    btn.addEventListener("click", doLogout);
    footer.appendChild(btn);
  }

  window.doLogout = async function() {
    if (!confirm("Sign out?")) return;
    const token = localStorage.getItem("robomlm_token") || "";
    try {
      await fetch("/api/auth/logout?token=" + encodeURIComponent(token), { method: "POST" });
    } catch (e) {}
    localStorage.removeItem("robomlm_token");
    localStorage.removeItem("robomlm_user");
    localStorage.removeItem("robomlm_email");
    window.location.href = "/login";
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", injectLogout);
  } else {
    injectLogout();
  }
})();
