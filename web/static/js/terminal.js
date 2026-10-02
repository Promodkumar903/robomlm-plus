// ROBOMLM â€” Terminal (chart + metrics + evidence + decision)

let CHART = null;
let SERIES = null;
let CURRENT_SYMBOL = "BTC/USDT";
let CURRENT_TF = "1m";

// ============================================================================
// CHART
// ============================================================================

function initChart() {
  const el = document.getElementById("chart");
  if (!el || typeof LightweightCharts === "undefined") return;

  CHART = LightweightCharts.createChart(el, {
    width: el.clientWidth,
    height: el.clientHeight,
    layout: { background: { color: "#0d1117" }, textColor: "#a8b4c8" },
    grid: { vertLines: { color: "#1e2738" }, horzLines: { color: "#1e2738" } },
    rightPriceScale: { borderColor: "#2a3446" },
    timeScale: { borderColor: "#2a3446", timeVisible: true, secondsVisible: false },
    crosshair: { mode: LightweightCharts.CrosshairMode.Normal },
  });

  SERIES = CHART.addCandlestickSeries({
    upColor: "#10b981", downColor: "#ef4444",
    borderUpColor: "#10b981", borderDownColor: "#ef4444",
    wickUpColor: "#10b981", wickDownColor: "#ef4444",
  });

  window.addEventListener("resize", () => {
    if (CHART && el) CHART.applyOptions({ width: el.clientWidth });
  });
}

async function loadChart(symbol, tf) {
  try {
    const cleanSymbol = symbol.replace("/", "").toUpperCase();
    const res = await fetch(`/api/live/candles/${cleanSymbol}?tf=${encodeURIComponent(tf)}&limit=200`);
    const data = await res.json();
    if (!SERIES || !data.candles) return;

    const candles = data.candles.map(c => ({
      time: c.time, open: c.open, high: c.high, low: c.low, close: c.close,
    }));
    SERIES.setData(candles);
    CHART.timeScale().fitContent();

    const last = candles[candles.length - 1];
    const first = candles[0];
    const change = ((last.close - first.open) / first.open) * 100;

    document.getElementById("sb-price").textContent =
      "$" + last.close.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    const chgEl = document.getElementById("sb-change");
    chgEl.textContent = (change >= 0 ? "â–² +" : "â–¼ ") + change.toFixed(2) + "%";
    chgEl.className = "symbol-change " + (change >= 0 ? "text-green" : "text-red");
  } catch (e) {
    console.error("Chart load failed:", e);
  }
}

// ============================================================================
// METRICS STRIP
// ============================================================================

function renderMetrics(metrics) {
  const el = document.getElementById("metrics-strip");
  if (!el) return;
  if (!metrics.length) { el.innerHTML = '<div style="color:#5a6478;font-size:12px">Loading...</div>'; return; }
  el.innerHTML = metrics.map(m => `
    <div class="strip-item" title="${m.desc || ''}">
      <div class="strip-item-id">${m.id}</div>
      <div class="strip-item-val">${m.score}</div>
      <div class="strip-item-sub">${m.name}</div>
    </div>
  `).join("");
}
// ============================================================================
// EVIDENCE STRIP
// ============================================================================

function renderEvidence(evidence) {
  const el = document.getElementById("evidence-strip");
  if (!el) return;
  if (!evidence.length) { el.innerHTML = '<div style="color:#5a6478;font-size:12px">Loading...</div>'; return; }
  el.innerHTML = evidence.map(e => {
        const state = e.status === "VALID" ? "valid"
                : (e.status === "INSUFFICIENT" || e.status === "PARTIAL") ? "partial"
                : "invalid";
        const dot = `<span class="ev-dot ev-dot-${state}"></span>`;
    return `
      <div class="strip-item evidence-item ${state}" title="${e.desc || ''}">
        <div class="strip-item-id">${e.id}</div>
        <div class="strip-item-dot">${dot}</div>
        <div class="strip-item-sub">${e.name}</div>
      </div>
    `;
  }).join("");
}
// ============================================================================
// DECISION
// ============================================================================

const GRADE_RANK = { "A+": 5, "A": 4, "B+": 3, "B": 2, "C": 1 };
let _currentDecision = null;
let _chosenSide = null;

function renderDecision(dec) {
  _currentDecision = dec;
  _chosenSide = null;

  const ready = dec.ready_count || 0;
  const total = dec.total_count || 10;
  const pct = (ready / total) * 100;

  const signal = (dec.signal || "HOLD").toUpperCase();
  const grade = (dec.grade || "C").toUpperCase();
  const rr = dec.rr || 0;
  const conf = dec.confidence || 0;

  document.getElementById("decision-count").textContent = `${ready}/${total}`;
  document.getElementById("decision-reason").textContent = dec.reason || "";

  // D13 signal â€” big display
  const sigBox = document.getElementById("d13-signal-box");
  const sigText = document.getElementById("d13-signal-text");
  sigText.textContent = signal;
  sigBox.className = "d13-signal-box d13-" +
    (signal === "BUY" ? "buy" : signal === "SELL" ? "sell" : "hold");

  document.getElementById("d13-conf").textContent =
    conf ? (conf * 100).toFixed(0) + "%" : "â€”";
  document.getElementById("d13-grade").textContent = grade;
  document.getElementById("d13-rr").textContent =
    rr ? "1 : " + rr.toFixed(1) : "â€”";

   // Manual trading: user-first. Buttons enabled if EQE (confidence) >= 30.
  // D13 signal shown as advisory only — user decides to take the trade or not.
  const callBtn = document.getElementById("btn-call");
  const putBtn = document.getElementById("btn-put");
  const eqe = (dec.confidence || 0) * 100;
  const canTrade = eqe >= 30;

  callBtn.disabled = !canTrade;
  putBtn.disabled = !canTrade;

  // Show advisory note if D13 disagrees with user choice
  const advisory = document.getElementById("d13-advisory");
  if (advisory) {
    if (canTrade && (signal === "HOLD")) {
      advisory.textContent = "⚠ D13 suggests HOLD — but you can trade manually";
      advisory.style.display = "block";
    } else if (!canTrade) {
      advisory.textContent = "🚫 EQE " + eqe.toFixed(0) + " < 30 — trade blocked";
      advisory.style.display = "block";
    } else {
      advisory.style.display = "none";
    }
  }
  callBtn.disabled = !canTrade;
  putBtn.disabled = !canTrade;

  callBtn.classList.remove("selected");
  putBtn.classList.remove("selected");

  // Confirm button stays disabled until side chosen
  document.getElementById("btn-confirm").disabled = true;

  document.getElementById("decision-progress-bar").style.width = pct + "%";
}

// Side selection (CALL or PUT)
document.addEventListener("click", (e) => {
  if (e.target.closest("#btn-call")) {
    if (!document.getElementById("btn-call").disabled) {
      _chosenSide = "CALL";
      document.getElementById("btn-call").classList.add("selected");
      document.getElementById("btn-put").classList.remove("selected");
      document.getElementById("btn-confirm").disabled = false;
    }
  }
  if (e.target.closest("#btn-put")) {
    if (!document.getElementById("btn-put").disabled) {
      _chosenSide = "PUT";
      document.getElementById("btn-put").classList.add("selected");
      document.getElementById("btn-call").classList.remove("selected");
      document.getElementById("btn-confirm").disabled = false;
    }
  }
});

// Confirm trade
document.addEventListener("click", async (e) => {
  if (!e.target.closest("#btn-confirm")) return;
  if (!_chosenSide || !_currentDecision) return;

  const tpRaw = document.getElementById("in-tp").value;
  const slRaw = document.getElementById("in-sl").value;
  const tp = tpRaw ? parseFloat(tpRaw) : null;
  const sl = slRaw ? parseFloat(slRaw) : null;

  const symbol = (window.CURRENT_SYMBOL_FOR_TRADE) || "BTC/USDT";

  try {
    const res = await fetch("/api/trade/place", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ symbol, side: _chosenSide, tp, sl }),
    });
    const data = await res.json();
    if (data.ok) {
      alert(`âœ… ${_chosenSide} placed Â· ${data.trade_id}`);
      document.getElementById("in-tp").value = "";
      document.getElementById("in-sl").value = "";
      document.getElementById("btn-confirm").disabled = true;
      document.getElementById("btn-call").classList.remove("selected");
      document.getElementById("btn-put").classList.remove("selected");
      _chosenSide = null;
    } else {
      alert("âŒ Failed: " + (data.error || "unknown"));
    }
  } catch (err) {
    alert("âŒ Error: " + err.message);
  }
});
// ============================================================================
// CAS GATES
// ============================================================================

function renderCAS(gates) {
  document.getElementById("p-cas").innerHTML = gates.map(g => {
    const cls = g.status === "PASS" ? "risk-pass"
              : g.status === "FAIL" ? "risk-fail" : "risk-warn";
    return `
      <div class="mini-row">
        <span class="mini-lbl">${g.name}</span>
        <span class="risk-badge ${cls}">${g.status}</span>
      </div>
    `;
  }).join("");
}

// ============================================================================
// LIVE LOG
// ============================================================================

function renderLog(log) {
  document.getElementById("p-log").innerHTML = log.map(ev => {
    const cls = ev.type === "BUY" || ev.type === "CALL" ? "log-buy"
              : ev.type === "SELL" || ev.type === "PUT" ? "log-sell"
              : ev.type === "WAIT" ? "log-wait" : "log-hold";
    return `
      <div class="log-line-mini">
        <span class="log-time-mini">${ev.time}</span>
        <span class="log-type-mini ${cls}">${ev.type}</span>
        <span class="log-msg-mini">${ev.msg}</span>
      </div>
    `;
  }).join("");
}

// ============================================================================
// STATE BADGE
// ============================================================================

function renderState(sm) {
  const el = document.getElementById("state-badge");
  const phase = (sm.phase || "WAITING").toUpperCase();
  el.textContent = "â— " + phase;
  el.className = "state-badge state-" + phase.toLowerCase();
}

// ============================================================================
// BOOT
// ============================================================================

async function loadAll() {
  try {
    const res = await fetch("/api/terminal");
    const d = await res.json();
    renderMetrics(d.metrics || []);
    renderEvidence(d.evidence || []);
    window.__lastDecision = d;
    renderDecision(d);
    renderCAS(d.cas_gates || []);
    renderLog(d.log || []);
    renderState(d.state_machine || {});
  } catch (e) {
    console.error("Terminal load failed:", e);
  }
}
function bindControls() {
  document.getElementById("symbol-select").addEventListener("change", e => {
    CURRENT_SYMBOL = e.target.value;
    loadChart(CURRENT_SYMBOL, CURRENT_TF);
  });
  document.querySelectorAll("#tf-group .tf-btn").forEach(b => {
    b.addEventListener("click", () => {
      document.querySelectorAll("#tf-group .tf-btn").forEach(x => x.classList.remove("active"));
      b.classList.add("active");
      CURRENT_TF = b.dataset.tf;
      loadChart(CURRENT_SYMBOL, CURRENT_TF);
    });
  });
}

window.addEventListener("load", () => {
  initChart();
  bindControls();
  loadChart(CURRENT_SYMBOL, CURRENT_TF);
  loadAll();
  setInterval(loadAll, 5000);
});

// ============================================================================
// PORTFOLIO STRIP + POSITIONS
// ============================================================================

function pfFmt(v, cur) {
  if (v == null) return "—";
  const n = Number(v);
  if (cur === "USD") return "$" + n.toLocaleString("en-US", { maximumFractionDigits: 2 });
  return "₹" + n.toLocaleString("en-IN", { maximumFractionDigits: 2 });
}

async function pfLoadOverview() {
  try {
    const r = await fetch("/api/portfolio/overview");
    const d = await r.json();
    if (!d.ok) return;

    document.getElementById("pf-capital").textContent = pfFmt(d.capital, d.currency);
    document.getElementById("pf-balance").textContent = pfFmt(d.balance, d.currency);

    const pnlEl = document.getElementById("pf-pnl");
    const pnl = d.today_pnl;
    pnlEl.textContent = (pnl >= 0 ? "+" : "−") + pfFmt(Math.abs(pnl), d.currency).replace(/^[₹$]/, "");
    pnlEl.className = "pf-val " + (pnl > 0 ? "pf-green" : pnl < 0 ? "pf-red" : "");

    document.getElementById("pf-open").textContent = d.open_positions;
    document.getElementById("pf-winrate").textContent = d.win_rate + "%";
    document.getElementById("pf-mode").textContent = d.mode;
  } catch (e) { console.error(e); }
}

async function pfLoadPositions() {
  try {
    const r = await fetch("/api/positions");
    const d = await r.json();
    if (!d.ok) return;

    const open = (d.positions || []).filter(p => p.status === "open");
    const el = document.getElementById("pf-pos-list");

    if (!open.length) {
      el.innerHTML = '<div class="pf-empty">No open positions</div>';
      return;
    }

    el.innerHTML = open.map(p => `
      <div class="pf-pos-row">
        <div class="dir ${p.direction.toLowerCase()}">${p.direction}</div>
        <div class="sym">${p.symbol}</div>
        <div class="num">${p.entry}</div>
        <div class="num">${p.sl}</div>
        <div class="num">${p.tp}</div>
        <div class="num">${p.grade}</div>
        <button class="close-btn" data-id="${p.id}">CLOSE</button>
      </div>
    `).join("");

    el.querySelectorAll(".close-btn").forEach(b => {
      b.addEventListener("click", async () => {
        if (!confirm("Close this position?")) return;
        await fetch("/api/positions/" + b.dataset.id + "/close", { method: "POST" });
        pfLoadPositions();
        pfLoadOverview();
      });
    });
  } catch (e) { console.error(e); }
}

function pfBoot() {
  pfLoadOverview();
  pfLoadPositions();
  setInterval(pfLoadOverview, 5000);
  setInterval(pfLoadPositions, 5000);
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", pfBoot);
} else {
  pfBoot();
}