// ROBOMLM — Discovery Page

let ALL_RESULTS = [];
let ACTIVE_MARKET = "";

async function load() {
  try {
    const res = await fetch("/api/discovery");
    const data = await res.json();
    ALL_RESULTS = data.results;
    renderTabs(data.markets);
    render();
  } catch (e) { console.error(e); }
}

function renderTabs(markets) {
  const html = [`<div class="tab active" data-m="">All</div>`]
    .concat(markets.map(m => `<div class="tab" data-m="${m}">${m}</div>`))
    .join("");
  const el = document.getElementById("market-tabs");
  el.innerHTML = html;
  el.querySelectorAll(".tab").forEach(t => {
    t.onclick = () => {
      el.querySelectorAll(".tab").forEach(x => x.classList.remove("active"));
      t.classList.add("active");
      ACTIVE_MARKET = t.dataset.m;
      render();
    };
  });
}

function render() {
  const sig  = document.getElementById("f-signal").value;
  const eqe  = parseInt(document.getElementById("f-eqe").value);
  const risk = document.getElementById("f-risk").value;

  const rows = ALL_RESULTS.filter(r =>
    (!ACTIVE_MARKET || r.market === ACTIVE_MARKET) &&
    (!sig || r.signal === sig) &&
    (r.eqe >= eqe) &&
    (!risk || r.risk === risk)
  );

  document.getElementById("f-count").textContent = rows.length + " results";

  document.getElementById("results-body").innerHTML = rows.map(r => {
    const sigCls = r.signal === "BUY" ? "text-green"
                 : r.signal === "SELL" ? "text-red" : "text-mute";
    const chgCls = r.change >= 0 ? "text-green" : "text-red";
    const riskCls = r.risk === "LOW" ? "risk-pass"
                  : r.risk === "HIGH" ? "risk-fail" : "risk-warn";
        return `<tr>
        <td class="col-symbol">${r.symbol}</td>
        <td class="text-dim">${r.market}</td>
        <td class="${chgCls}">${r.change >= 0 ? "+" : ""}${r.change.toFixed(2)}%</td>
        <td class="${sigCls}" style="font-weight:700">${r.signal}</td>
        <td class="font-mono">${r.eqe}</td>
        <td class="engines-cell"><span class="engines-dots">${r.engines || ""}</span><span class="engines-count">${r.engine_hits || 0}/9</span></td>
        <td class="font-mono">1 : ${r.rr}</td>
        <td><span class="risk-badge ${riskCls}">${r.risk}</span></td>
        <td><a href="/terminal" class="btn btn-ghost btn-sm">Open</a></td>
      </tr>`;
  }).join("") || `<tr><td colspan="8" class="empty-state">No matches</td></tr>`;
}

["f-signal", "f-eqe", "f-risk"].forEach(id => {
  document.addEventListener("change", e => {
    if (e.target.id === id) render();
  });
});

load();