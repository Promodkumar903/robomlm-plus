// ROBOMLM — Buyer Workspace

let DATA = null;

async function load() {
  try {
    const res = await fetch("/api/buyer");
    DATA = await res.json();
    initSelectors();
  } catch (e) {
    console.error("Buyer load failed:", e);
  }
}

function initSelectors() {
  const mSel = document.getElementById("sel-market");
  mSel.innerHTML = DATA.markets.map(m => `<option value="${m}">${m}</option>`).join("");
  mSel.addEventListener("change", () => {
    refreshInstruments();
    refreshContracts();
  });

  document.getElementById("sel-instrument").addEventListener("change", refreshContracts);

  const sSel = document.getElementById("sel-strategy");
  sSel.innerHTML = DATA.strategies.map(s => `<option value="${s.id}">${s.name}</option>`).join("");

  refreshInstruments();
  refreshContracts();

  document.getElementById("btn-apply").addEventListener("click", applyForAnalysis);
}

function refreshInstruments() {
  const m = document.getElementById("sel-market").value;
  const iSel = document.getElementById("sel-instrument");
  const list = DATA.instruments[m] || [];
  iSel.innerHTML = list.map(i => `<option value="${i}">${i}</option>`).join("");
}

function refreshContracts() {
  const i = document.getElementById("sel-instrument").value;
  const cSel = document.getElementById("sel-contract");
  const list = DATA.contracts[i] || [`${i}-SPOT`];
  cSel.innerHTML = list.map(c => `<option value="${c}">${c}</option>`).join("");
}

function applyForAnalysis() {
  const d = DATA.result;
  const wrap = document.getElementById("buyer-result");
  wrap.style.display = "block";

  // Intelligence
  document.getElementById("r-int-bias").textContent = d.intelligence.bias;
  document.getElementById("r-int-score").textContent = d.intelligence.score;
  document.getElementById("r-int-conf").textContent = d.intelligence.confidence.toFixed(2);
  document.getElementById("r-int-reason").textContent = d.intelligence.reason;

  // Decision
  const sigEl = document.getElementById("r-dec-signal");
  sigEl.textContent = d.decision.signal;
  sigEl.className = "badge-signal " +
    (d.decision.signal === "BUY" ? "call" :
     d.decision.signal === "SELL" ? "put" : "hold");
  document.getElementById("r-dec-grade").textContent = d.decision.grade;
  document.getElementById("r-dec-score").textContent = d.decision.score;
  document.getElementById("r-dec-conf").textContent = d.decision.confidence.toFixed(2);
  document.getElementById("r-dec-reason").textContent = d.decision.reason;

  // Risk
  document.getElementById("r-risk-score").textContent = d.risk.score;
  document.getElementById("r-risk-level").textContent = d.risk.level;
  document.getElementById("r-risk-size").textContent = d.risk.size_factor;
  document.getElementById("r-risk-sltp").textContent = `${d.risk.sl_pct}% / ${d.risk.tp_pct}%`;
  document.getElementById("r-risk-rr").textContent = "1 : " + d.risk.rr;
  document.getElementById("r-risk-reason").textContent = d.risk.summary;

  // CAS
  document.getElementById("r-cas-status").textContent = "● " + d.cas.status;
  document.getElementById("r-cas-grid").innerHTML = d.cas.gates.map(g => `
    <div class="cas-item">
      <span class="cas-item-name">${g.name}</span>
      <span class="risk-badge risk-pass">${g.status}</span>
    </div>
  `).join("");

  // PLUS
  document.getElementById("r-plus-status").textContent = "● " + d.plus.status;
  document.getElementById("r-plus-message").textContent = d.plus.message;
  document.getElementById("btn-plus").disabled = (d.plus.status !== "READY");

  // Scroll to results
  wrap.scrollIntoView({ behavior: "smooth", block: "start" });
}

document.getElementById("btn-plus").addEventListener("click", () => {
  alert("PLUS handoff — backend integration pending.");
});

load();