// ROBOMLM — Account page wiring

const ACC = {
  state: { mode: "PAPER", currency: "INR", rate: 83.33 },
  csvFiles: [
    "trade_history.csv", "decision_lifecycle.csv", "position_history.csv",
    "reject_log.csv", "eqe_history.csv", "mtf_history.csv",
    "tick_snapshot.csv", "phase_history.csv", "learning_journal.csv"
  ],
};

function fmt(val, cur) {
  if (val == null) return "—";
  const n = Number(val);
  if (cur === "USD") return "$ " + n.toLocaleString("en-US", { maximumFractionDigits: 2 });
  return "₹ " + n.toLocaleString("en-IN", { maximumFractionDigits: 2 });
}

async function loadSummary() {
  try {
    const r = await fetch("/api/account/summary");
    const d = await r.json();
    if (!d.ok) return;

    ACC.state.mode = d.mode;
    ACC.state.currency = d.currency;
    ACC.state.rate = d.usd_inr_rate || 83.33;

    const cur = d.currency;

    // Topbar
    const modeBtn = document.getElementById("acct-mode-btn");
    modeBtn.textContent = "● " + d.mode;
    modeBtn.className = "acct-mode-btn " + d.mode.toLowerCase();

    document.getElementById("acct-cur-btn").textContent = (cur === "INR" ? "₹ " : "$ ") + cur;
    document.getElementById("acct-topbar-balance").textContent = fmt(d.balance, cur);

    // Strip
    document.getElementById("acct-capital").textContent = fmt(d.capital, cur);
    document.getElementById("acct-balance").textContent = fmt(d.balance, cur);

    const pnl = d.today_pnl;
    const pnlEl = document.getElementById("acct-pnl");
    pnlEl.textContent = (pnl >= 0 ? "+ " : "− ") + fmt(Math.abs(pnl), cur).replace(/^[₹$]\s*/, "");
    pnlEl.className = "acct-box-val " + (pnl > 0 ? "acct-green" : pnl < 0 ? "acct-red" : "");

    document.getElementById("acct-pos").textContent = d.open_positions;

    // Mode buttons active state
    document.querySelectorAll(".acct-mc-btn[data-mode]").forEach(b => {
      b.classList.toggle("active", b.dataset.mode === d.mode);
    });
    document.querySelectorAll(".acct-mc-btn[data-cur]").forEach(b => {
      b.classList.toggle("active", b.dataset.cur === cur);
    });
  } catch (e) {
    console.error("summary failed", e);
  }
}

async function loadEquity() {
  try {
    const r = await fetch("/api/account/equity");
    const d = await r.json();
    if (!d.ok || !d.points.length) return;

    const svg = document.getElementById("acct-equity-svg");
    const pts = d.points;
    const W = 600, H = 90, pad = 6;

    const vals = pts.map(p => p.v);
    const min = Math.min(...vals), max = Math.max(...vals);
    const range = max - min || 1;

    const stepX = (W - pad * 2) / Math.max(pts.length - 1, 1);
    const path = pts.map((p, i) => {
      const x = pad + i * stepX;
      const y = H - pad - ((p.v - min) / range) * (H - pad * 2);
      return `${i === 0 ? "M" : "L"}${x.toFixed(1)},${y.toFixed(1)}`;
    }).join(" ");

    svg.innerHTML = `
      <defs>
        <linearGradient id="eqGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stop-color="#818cf8" stop-opacity="0.35"/>
          <stop offset="100%" stop-color="#818cf8" stop-opacity="0"/>
        </linearGradient>
      </defs>
      <path d="${path} L${W-pad},${H-pad} L${pad},${H-pad} Z" fill="url(#eqGrad)"/>
      <path d="${path}" fill="none" stroke="#818cf8" stroke-width="1.5"/>
    `;
  } catch (e) { console.error("equity failed", e); }
}

async function loadAllocation() {
  try {
    const r = await fetch("/api/account/allocation");
    const d = await r.json();
    if (!d.ok) return;

    const el = document.getElementById("acct-alloc-list");
    const a = d.allocation;
    const total = Object.values(a).reduce((s, v) => s + v, 0) || 1;

    el.innerHTML = Object.entries(a).map(([k, v]) => {
      const pct = ((v / total) * 100).toFixed(0);
      return `<div class="acct-alloc-row"><span class="k">${k}</span><span class="v">${v} · ${pct}%</span></div>`;
    }).join("");
  } catch (e) { console.error("alloc failed", e); }
}

function renderDownloads() {
  const el = document.getElementById("acct-dl-grid");
  el.innerHTML = ACC.csvFiles.map(f => `
    <button class="acct-dl-btn" data-file="${f}">
      <span>${f}</span>
      <span class="acct-dl-icon">⬇</span>
    </button>
  `).join("");

  el.querySelectorAll(".acct-dl-btn").forEach(b => {
    b.addEventListener("click", () => {
      window.location.href = "/api/account/download/" + b.dataset.file;
    });
  });
}

async function setMode(m) {
  const r = await fetch("/api/account/mode", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mode: m }),
  });
  const d = await r.json();
  if (d.ok) loadSummary();
}

async function setCurrency(c) {
  const r = await fetch("/api/account/currency", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ currency: c }),
  });
  const d = await r.json();
  if (d.ok) loadSummary();
}

async function resetSeed() {
  if (!confirm("Reset seed capital? Current balance will be replaced.")) return;
  await fetch("/api/account/reset-seed", { method: "POST" });
  loadSummary();
  loadEquity();
}

function boot() {
  renderDownloads();
  loadSummary();
  loadEquity();
  loadAllocation();

  document.querySelectorAll(".acct-mc-btn[data-mode]").forEach(b => {
    b.addEventListener("click", () => setMode(b.dataset.mode));
  });
  document.querySelectorAll(".acct-mc-btn[data-cur]").forEach(b => {
    b.addEventListener("click", () => setCurrency(b.dataset.cur));
  });
  document.getElementById("acct-reset-btn").addEventListener("click", resetSeed);

  // Topbar mode button quick toggle
  document.getElementById("acct-mode-btn").addEventListener("click", () => {
    setMode(ACC.state.mode === "PAPER" ? "LIVE" : "PAPER");
  });
  document.getElementById("acct-cur-btn").addEventListener("click", () => {
    setCurrency(ACC.state.currency === "INR" ? "USD" : "INR");
  });

  setInterval(loadSummary, 10000);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", boot);
} else {
  boot();
}

// ============================================================================
// BOT FUND ALLOCATION
// ============================================================================

let ALLOC = { total: 100000, currency: "INR", auto: 50, mission: 50 };

async function loadAlloc() {
  try {
    const r = await fetch("/api/bot/allocation");
    const d = await r.json();
    if (!d.ok) return;

    ALLOC.total = d.total_capital;
    ALLOC.currency = d.currency;
    ALLOC.auto = Math.round(d.auto_alloc_pct);
    ALLOC.mission = Math.round(d.mission_alloc_pct);

    document.getElementById("alloc-auto").value = ALLOC.auto;
    document.getElementById("alloc-mission").value = ALLOC.mission;
    refreshAllocUI();
  } catch (e) { console.error(e); }
}

function refreshAllocUI() {
  const a = parseInt(document.getElementById("alloc-auto").value) || 0;
  const m = parseInt(document.getElementById("alloc-mission").value) || 0;

  document.getElementById("alloc-auto-val").textContent = a + "%";
  document.getElementById("alloc-mission-val").textContent = m + "%";

  const autoCap = ALLOC.total * a / 100;
  const missCap = ALLOC.total * m / 100;
  const freeCap = ALLOC.total - autoCap - missCap;

  document.getElementById("alloc-auto-cap").textContent = fmt(autoCap, ALLOC.currency);
  document.getElementById("alloc-mission-cap").textContent = fmt(missCap, ALLOC.currency);

  const hintEl = document.getElementById("alloc-hint");
  if (a + m > 100) {
    hintEl.textContent = "⚠ Total exceeds 100%";
    hintEl.style.color = "#f87171";
  } else {
    hintEl.textContent = (100 - a - m) + "% unallocated · " + fmt(freeCap, ALLOC.currency) + " safe in account";
    hintEl.style.color = "";
  }
}

function onAllocSlide(which) {
  const aEl = document.getElementById("alloc-auto");
  const mEl = document.getElementById("alloc-mission");
  let a = parseInt(aEl.value) || 0;
  let m = parseInt(mEl.value) || 0;

  if (which === "auto" && a + m > 100) {
    mEl.value = 100 - a;
  } else if (which === "mission" && a + m > 100) {
    aEl.value = 100 - m;
  }
  refreshAllocUI();
}

async function saveAlloc() {
  const a = parseInt(document.getElementById("alloc-auto").value) || 0;
  const m = parseInt(document.getElementById("alloc-mission").value) || 0;

  if (a + m > 100) {
    alert("Total allocation cannot exceed 100%");
    return;
  }

  try {
    const r = await fetch("/api/bot/allocation", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ auto_alloc_pct: a, mission_alloc_pct: m }),
    });
    const d = await r.json();
    if (d.ok) {
      document.getElementById("alloc-hint").textContent = "✅ Saved";
      setTimeout(() => refreshAllocUI(), 1500);
    } else {
      alert("Failed: " + (d.error || "unknown"));
    }
  } catch (e) { alert("Error: " + e.message); }
}

// wire
const _oldBoot = (typeof boot === "function") ? boot : null;
function allocBoot() {
  loadAlloc();
  document.getElementById("alloc-auto").addEventListener("input", () => onAllocSlide("auto"));
  document.getElementById("alloc-mission").addEventListener("input", () => onAllocSlide("mission"));
  document.getElementById("alloc-save").addEventListener("click", saveAlloc);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", allocBoot);
} else {
  allocBoot();
}