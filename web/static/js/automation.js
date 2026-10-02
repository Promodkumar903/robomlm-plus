// ROBOMLM — AUTOROBOMLM Control

async function loadStatus() {
  try {
    const res = await fetch("/api/autorobomlm/status");
    const d = await res.json();
    render(d);
  } catch (e) { console.error(e); }
}

function render(d) {
  const badge = document.getElementById("auto-badge");
  const status = (d.status || "STOPPED").toUpperCase();
  badge.textContent = "● " + status;
  badge.className = "state-badge state-" + status.toLowerCase();

  document.getElementById("st-status").textContent = status;
  document.getElementById("st-grade").textContent = d.min_grade || "—";
  document.getElementById("st-rr").textContent =
    d.min_rr ? "1 : " + Number(d.min_rr).toFixed(1) : "—";
  document.getElementById("st-sltp").textContent =
    d.sl_pct && d.tp_pct
      ? `${Number(d.sl_pct).toFixed(1)}% / ${Number(d.tp_pct).toFixed(1)}%`
      : "—";
}

function getConfig() {
  return {
    min_grade: document.getElementById("cfg-min-grade").value,
    min_rr: parseFloat(document.getElementById("cfg-min-rr").value) || 2.0,
    sl_pct: parseFloat(document.getElementById("cfg-sl").value) || 1.5,
    tp_pct: parseFloat(document.getElementById("cfg-tp").value) || 3.0,
  };
}

async function startBot() {
  const cfg = getConfig();
  if (cfg.min_rr < 0.5) { alert("⚠ Min RR must be at least 0.5"); return; }
  try {
    const res = await fetch("/api/autorobomlm/start", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(cfg),
    });
    const d = await res.json();
    if (d.ok) {
      alert(`▶ Bot started · Min Grade ${cfg.min_grade} · Min RR 1:${cfg.min_rr}`);
      loadStatus();
    }
  } catch (e) { alert("Error: " + e.message); }
}

async function pauseBot() {
  try {
    await fetch("/api/autorobomlm/pause", { method: "POST" });
    loadStatus();
  } catch (e) { console.error(e); }
}

async function stopBot() {
  if (!confirm("⏹ Stop bot?")) return;
  try {
    await fetch("/api/autorobomlm/stop", { method: "POST" });
    loadStatus();
  } catch (e) { console.error(e); }
}

async function killBot() {
  if (!confirm("🚨 KILL SWITCH — Force stop?")) return;
  try {
    await fetch("/api/autorobomlm/stop", { method: "POST" });
    loadStatus();
    alert("🚨 Kill switch engaged.");
  } catch (e) { console.error(e); }
}

document.getElementById("btn-start").addEventListener("click", startBot);
document.getElementById("btn-pause").addEventListener("click", pauseBot);
document.getElementById("btn-stop").addEventListener("click", stopBot);
document.getElementById("btn-kill").addEventListener("click", killBot);

loadStatus();
setInterval(loadStatus, 5000);

// ============================================================================
// BOT FINANCE STRIP · TRADES · ACTIVITY
// ============================================================================

function botFmt(v, cur) {
  if (v == null) return "—";
  const n = Number(v);
  if (cur === "USD") return "$" + n.toLocaleString("en-US", { maximumFractionDigits: 2 });
  return "₹" + n.toLocaleString("en-IN", { maximumFractionDigits: 2 });
}

function botAge(isoStr) {
  if (!isoStr) return "—";
  try {
    const t = new Date(isoStr).getTime();
    const s = Math.floor((Date.now() - t) / 1000);
    if (s < 60) return s + "s";
    if (s < 3600) return Math.floor(s / 60) + "m";
    return Math.floor(s / 3600) + "h";
  } catch (e) { return "—"; }
}

async function botLoadFinance() {
  try {
    const r = await fetch("/api/bot/finance");
    const d = await r.json();
    if (!d.ok) return;

    const cur = (typeof ACC !== "undefined" && ACC.state) ? ACC.state.currency : "INR";

    document.getElementById("bot-alloc").textContent = botFmt(d.allocated_capital, cur);
    document.getElementById("bot-used").textContent = botFmt(d.used_capital, cur);

    const expoEl = document.getElementById("bot-expo");
    expoEl.textContent = d.exposure_pct + "%";
    expoEl.className = "bot-val " + (d.exposure_pct > d.max_exposure_pct ? "warn" : "");

    const realEl = document.getElementById("bot-real");
    realEl.textContent = (d.realized_pnl >= 0 ? "+" : "") + botFmt(d.realized_pnl, cur).replace(/^[₹$]/, "");
    realEl.className = "bot-val " + (d.realized_pnl > 0 ? "pos" : d.realized_pnl < 0 ? "neg" : "");

    const unrealEl = document.getElementById("bot-unreal");
    unrealEl.textContent = (d.unrealized_pnl >= 0 ? "+" : "") + botFmt(d.unrealized_pnl, cur).replace(/^[₹$]/, "");
    unrealEl.className = "bot-val " + (d.unrealized_pnl > 0 ? "pos" : d.unrealized_pnl < 0 ? "neg" : "");

    document.getElementById("bot-trades").textContent =
      `${d.trades_today} · ${d.wins_today}/${d.losses_today}`;
  } catch (e) { console.error(e); }
}

async function botLoadTrades() {
  try {
    const r = await fetch("/api/bot/trades?status=all&limit=50");
    const d = await r.json();
    if (!d.ok) return;

    const el = document.getElementById("bot-trade-list");
    const countEl = document.getElementById("bot-trade-count");
    const trades = d.trades || [];
    countEl.textContent = trades.length;

    if (!trades.length) {
      el.innerHTML = '<div class="bot-empty">No trades yet</div>';
      return;
    }

    el.innerHTML = trades.map(t => {
      const pl = t.pnl || 0;
      const plCls = pl > 0 ? "pos" : pl < 0 ? "neg" : "";
      const plTxt = (pl >= 0 ? "+" : "") + pl.toFixed(2);
      const closeBtn = t.status === "open"
        ? `<button class="close-btn" data-id="${t.id}">CLOSE</button>`
        : `<span style="color:var(--text-4);font-size:9px;">closed</span>`;

      return `
        <div class="bot-trade-row">
          <span class="dir ${(t.direction||'').toLowerCase()}">${t.direction || '—'}</span>
          <span class="sym">${t.symbol || '—'}</span>
          <span class="num">${t.entry ?? '—'}</span>
          <span class="num">${t.sl ?? '—'}</span>
          <span class="num">${t.tp ?? '—'}</span>
          <span class="num">${t.size ?? '—'}</span>
          <span class="pl ${plCls}">${plTxt}</span>
          <span class="grade">${t.grade || '—'}</span>
          <span class="num">${botAge(t.opened_at)}</span>
          <span>${closeBtn}</span>
        </div>
      `;
    }).join("");

    el.querySelectorAll(".close-btn").forEach(b => {
      b.addEventListener("click", async () => {
        if (!confirm("Close this trade?")) return;
        await fetch("/api/positions/" + b.dataset.id + "/close", { method: "POST" });
        botLoadTrades();
        botLoadFinance();
      });
    });
  } catch (e) { console.error(e); }
}

async function botLoadActivity() {
  try {
    const r = await fetch("/api/bot/activity?limit=30");
    const d = await r.json();
    if (!d.ok) return;

    const el = document.getElementById("bot-activity-list");
    const act = d.activity || [];

    if (!act.length) {
      el.innerHTML = '<div class="bot-empty">No activity yet</div>';
      return;
    }

    el.innerHTML = act.map(a => `
      <div class="bot-act-row">
        <span class="ts">${a.ts}</span>
        <span class="kind ${a.kind}">${a.kind}</span>
        <span class="msg">${a.msg}</span>
      </div>
    `).join("");
  } catch (e) { console.error(e); }
}

function botBoot() {
  botLoadFinance();
  botLoadTrades();
  botLoadActivity();
  setInterval(botLoadFinance, 5000);
  setInterval(botLoadTrades, 5000);
  setInterval(botLoadActivity, 5000);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", botBoot);
} else {
  botBoot();
}

// ============================================================================
// BOT FUND ALLOCATION
// ============================================================================
let ALLOC = { total: 100000, currency: "INR" };

async function loadAlloc() {
  try {
    const r = await fetch("/api/bot/allocation");
    const d = await r.json();
    if (!d.ok) return;
    ALLOC.total = d.total_capital;
    ALLOC.currency = d.currency;
    document.getElementById("alloc-auto").value = Math.round(d.auto_alloc_pct);
    document.getElementById("alloc-mission").value = Math.round(d.mission_alloc_pct);
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
  const cur = ALLOC.currency;
  const fmtN = n => cur === "USD" ? "$" + n.toLocaleString("en-US") : "₹" + n.toLocaleString("en-IN");
  document.getElementById("alloc-auto-cap").textContent = fmtN(autoCap);
  document.getElementById("alloc-mission-cap").textContent = fmtN(missCap);
  const hintEl = document.getElementById("alloc-hint");
  if (a + m > 100) { hintEl.textContent = "⚠ Total exceeds 100%"; hintEl.style.color = "#f87171"; }
  else { hintEl.textContent = (100 - a - m) + "% unallocated · " + fmtN(freeCap) + " safe in account"; hintEl.style.color = ""; }
}

function onAllocSlide(which) {
  const aEl = document.getElementById("alloc-auto");
  const mEl = document.getElementById("alloc-mission");
  let a = parseInt(aEl.value) || 0;
  let m = parseInt(mEl.value) || 0;
  if (which === "auto" && a + m > 100) mEl.value = 100 - a;
  else if (which === "mission" && a + m > 100) aEl.value = 100 - m;
  refreshAllocUI();
}

async function saveAlloc() {
  const a = parseInt(document.getElementById("alloc-auto").value) || 0;
  const m = parseInt(document.getElementById("alloc-mission").value) || 0;
  if (a + m > 100) { alert("Total cannot exceed 100%"); return; }
  const r = await fetch("/api/bot/allocation", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ auto_alloc_pct: a, mission_alloc_pct: m }),
  });
  const d = await r.json();
  if (d.ok) {
    document.getElementById("alloc-hint").textContent = "✅ Saved";
    setTimeout(() => refreshAllocUI(), 1500);
  }
}

if (document.getElementById("alloc-auto")) {
  loadAlloc();
  document.getElementById("alloc-auto").addEventListener("input", () => onAllocSlide("auto"));
  document.getElementById("alloc-mission").addEventListener("input", () => onAllocSlide("mission"));
  document.getElementById("alloc-save").addEventListener("click", saveAlloc);
}