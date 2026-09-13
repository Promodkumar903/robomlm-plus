// ROBOMLM — Memory Page

let DATA = { trades: [], decisions: [], journal: [] };
let ACTIVE_TAB = "trades";

async function load() {
  try {
    const res = await fetch("/api/memory");
    DATA = await res.json();
    render();
  } catch (e) { console.error(e); }
}

function render() {
  // Tab styling
  document.querySelectorAll("#memory-tabs .tab").forEach(t => {
    t.classList.toggle("active", t.dataset.t === ACTIVE_TAB);
    t.onclick = () => { ACTIVE_TAB = t.dataset.t; render(); };
  });

  const title = document.getElementById("view-title");
  const body  = document.getElementById("view-body");

  if (ACTIVE_TAB === "trades") {
    title.innerHTML = '<span class="ct-icon">📊</span> Trade History';
    body.innerHTML = renderTrades();
  } else if (ACTIVE_TAB === "decisions") {
    title.innerHTML = '<span class="ct-icon">📋</span> Decision Lifecycle';
    body.innerHTML = renderDecisions();
  } else {
    title.innerHTML = '<span class="ct-icon">📝</span> Learning Journal';
    body.innerHTML = renderJournal();
  }
}

function renderTrades() {
  return `
    <table class="data-table">
      <thead>
        <tr>
          <th>ID</th><th>Symbol</th><th>Side</th>
          <th>Entry</th><th>Exit</th><th>Size</th>
          <th>PnL</th><th>Reason</th><th>Grade</th>
        </tr>
      </thead>
      <tbody>
        ${DATA.trades.map(t => {
          const sideCls = t.side === "LONG" || t.side === "BUY" ? "text-green" : "text-red";
          const pnlCls  = t.pnl >= 0 ? "text-green" : "text-red";
          const gradeCls = t.grade === "A" ? "grade-a"
                         : t.grade === "B" ? "grade-b" : "grade-c";
          return `<tr>
            <td class="font-mono text-dim">${t.id}</td>
            <td class="col-symbol">${t.symbol}</td>
            <td class="${sideCls}" style="font-weight:700">${t.side}</td>
            <td class="font-mono">${t.entry.toLocaleString()}</td>
            <td class="font-mono">${t.exit.toLocaleString()}</td>
            <td class="font-mono">${t.size}</td>
            <td class="${pnlCls} font-mono" style="font-weight:700">${t.pnl >= 0 ? "+" : ""}${t.pnl.toFixed(2)} (${t.pnl_pct >= 0 ? "+" : ""}${t.pnl_pct}%)</td>
            <td class="text-dim">${t.reason}</td>
            <td><span class="grade-badge ${gradeCls}">${t.grade}</span></td>
          </tr>`;
        }).join("")}
      </tbody>
    </table>
  `;
}

function renderDecisions() {
  return `
    <table class="data-table">
      <thead>
        <tr>
          <th>ID</th><th>Time</th><th>Symbol</th>
          <th>Signal</th><th>Outcome</th><th>Reason</th>
        </tr>
      </thead>
      <tbody>
        ${DATA.decisions.map(d => {
          const sigCls = d.signal === "BUY" ? "text-green"
                       : d.signal === "SELL" ? "text-red" : "text-mute";
          const outCls = d.outcome === "TAKEN" ? "risk-pass" : "risk-warn";
          return `<tr>
            <td class="font-mono text-dim">${d.id}</td>
            <td class="font-mono">${d.time}</td>
            <td class="col-symbol">${d.symbol}</td>
            <td class="${sigCls}" style="font-weight:700">${d.signal}</td>
            <td><span class="risk-badge ${outCls}">${d.outcome}</span></td>
            <td class="text-dim">${d.reason}</td>
          </tr>`;
        }).join("")}
      </tbody>
    </table>
  `;
}

function renderJournal() {
  return `
    <div class="journal-list">
      ${DATA.journal.map(j => `
        <div class="journal-item">
          <div class="journal-head">
            <span class="journal-date">${j.date}</span>
            <span class="journal-symbol">${j.symbol}</span>
            <span class="journal-tag">${j.tag}</span>
          </div>
          <div class="journal-lesson">${j.lesson}</div>
        </div>
      `).join("")}
    </div>
  `;
}

load();