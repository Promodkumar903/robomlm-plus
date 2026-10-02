// ROBOMLM — Buyer workflow

let STATE = { markets: [], strategies: [] };

async function boot() {
  try {
    const [m, s] = await Promise.all([
      fetch("/api/buyer/markets").then(r => r.json()),
      fetch("/api/buyer/strategies").then(r => r.json()),
    ]);
    STATE.markets = m || [];
    STATE.strategies = s || [];
    fillMarkets();
    fillStrategies();
  } catch (e) {
    console.error("boot failed", e);
  }
}

function fillMarkets() {
  const sel = document.getElementById("sel-market");
  STATE.markets.forEach(m => {
    const o = document.createElement("option");
    o.value = m.id;
    o.textContent = m.label;
    sel.appendChild(o);
  });
}

function fillStrategies() {
  const sel = document.getElementById("sel-strategy");
  STATE.strategies.forEach(s => {
    const o = document.createElement("option");
    o.value = s.id;
    o.textContent = `${s.name} · min ${s.min_grade}`;
    sel.appendChild(o);
  });
}

function onMarket() {
  const id = document.getElementById("sel-market").value;
  const inst = document.getElementById("sel-instrument");
  const con = document.getElementById("sel-contract");
  inst.innerHTML = "<option value=''>— select —</option>";
  con.innerHTML = "<option value=''>—</option>";
  con.disabled = true;
  inst.disabled = !id;
  document.getElementById("btn-apply").disabled = true;

  if (!id) return;
  const m = STATE.markets.find(x => x.id === id);
  m.instruments.forEach(i => {
    const o = document.createElement("option");
    o.value = i; o.textContent = i;
    inst.appendChild(o);
  });
}

function onInstrument() {
  const id = document.getElementById("sel-market").value;
  const con = document.getElementById("sel-contract");
  const iv = document.getElementById("sel-instrument").value;
  con.innerHTML = "<option value=''>— select —</option>";
  con.disabled = !iv;
  document.getElementById("btn-apply").disabled = true;

  if (!iv) return;
  const m = STATE.markets.find(x => x.id === id);
  m.contracts.forEach(c => {
    const o = document.createElement("option");
    o.value = c; o.textContent = c;
    con.appendChild(o);
  });
}

function onContract() {
  const c = document.getElementById("sel-contract").value;
  const s = document.getElementById("sel-strategy").value;
  document.getElementById("sel-strategy").disabled = !c;
  document.getElementById("btn-apply").disabled = !(c && s);
}

function onStrategy() {
  const c = document.getElementById("sel-contract").value;
  const s = document.getElementById("sel-strategy").value;
  document.getElementById("btn-apply").disabled = !(c && s);
}

async function apply() {
  const payload = {
    market: document.getElementById("sel-market").value,
    instrument: document.getElementById("sel-instrument").value,
    contract: document.getElementById("sel-contract").value,
    strategy: document.getElementById("sel-strategy").value,
  };

  const badge = document.getElementById("buyer-badge");
  badge.textContent = "● ANALYZING";
  badge.className = "state-badge state-paused";

  try {
    const res = await fetch("/api/buyer/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const d = await res.json();
    if (!d.ok) {
      alert("Failed: " + (d.error || "unknown"));
      badge.textContent = "● ERROR";
      badge.className = "state-badge state-stopped";
      return;
    }
    render(d);
    badge.textContent = "● " + d.plus.verdict;
    badge.className = "state-badge " + (d.plus.verdict === "READY" ? "state-running" : "state-stopped");
  } catch (e) {
    alert("Error: " + e.message);
  }
}

function set(id, v) {
  const el = document.getElementById(id);
  if (el) el.textContent = v == null ? "—" : v;
}

function render(d) {
  document.getElementById("buyer-result").style.display = "block";

  set("r-signal", d.intelligence.signal);
  set("r-grade", d.intelligence.grade);
  set("r-conf", (d.intelligence.confidence * 100).toFixed(0) + "%");
  set("r-regime", d.intelligence.regime);

  set("r-dir", d.decision.direction);
  set("r-entry", d.decision.entry);
  set("r-sl", d.decision.sl);
  set("r-tp", d.decision.tp);
  set("r-rr", "1 : " + d.decision.rr.toFixed(2));

  set("r-mloss", d.risk.max_loss_pct + "%");
  set("r-psize", d.risk.position_size_pct + "%");
  set("r-cas", d.cas.authorized ? "✅ YES" : "❌ NO");
  set("r-plus", d.plus.verdict);
  set("r-reason", d.cas.reason);
}

function reset() {
  document.getElementById("sel-market").value = "";
  document.getElementById("sel-instrument").innerHTML = "<option value=''>—</option>";
  document.getElementById("sel-instrument").disabled = true;
  document.getElementById("sel-contract").innerHTML = "<option value=''>—</option>";
  document.getElementById("sel-contract").disabled = true;
  document.getElementById("sel-strategy").value = "";
  document.getElementById("sel-strategy").disabled = true;
  document.getElementById("btn-apply").disabled = true;
  document.getElementById("buyer-result").style.display = "none";
  const badge = document.getElementById("buyer-badge");
  badge.textContent = "● IDLE";
  badge.className = "state-badge state-stopped";
}

document.getElementById("sel-market").addEventListener("change", onMarket);
document.getElementById("sel-instrument").addEventListener("change", onInstrument);
document.getElementById("sel-contract").addEventListener("change", onContract);
document.getElementById("sel-strategy").addEventListener("change", onStrategy);
document.getElementById("btn-apply").addEventListener("click", apply);
document.getElementById("btn-reset").addEventListener("click", reset);

boot();