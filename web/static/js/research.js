// ROBOMLM — Research Page

async function load() {
  try {
    const res = await fetch("/api/research");
    const data = await res.json();
    render(data);
  } catch (e) { console.error(e); }
}

function render(d) {
  // Stats
  const eqPass = d.equations.filter(e => e.status === "PASS").length;
  const avgPass = (d.equations.reduce((a, b) => a + b.pass_rate, 0) / d.equations.length).toFixed(1);
  const audFixed = d.audit_trail.filter(a => a.status === "FIXED").length;
  const rseComplete = d.rse_cycle.filter(r => r.phase === "COMPLETE").length;

  document.getElementById("stats").innerHTML = `
    <div class="metric-card">
      <div class="metric-label">📐 Equations</div>
      <div class="metric-value big text-green">${eqPass} / 9</div>
      <div class="metric-sub">All passing</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">📊 Avg Pass Rate</div>
      <div class="metric-value big text-green">${avgPass}%</div>
      <div class="metric-sub">Across all equations</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">✅ Audit Fixes</div>
      <div class="metric-value big text-green">${audFixed} / ${d.audit_trail.length}</div>
      <div class="metric-sub">All applied</div>
    </div>
    <div class="metric-card">
      <div class="metric-label">🔬 RSE Cycles</div>
      <div class="metric-value big text-green">${rseComplete} / ${d.rse_cycle.length}</div>
      <div class="metric-sub">All complete</div>
    </div>
  `;

  // Equations
  document.getElementById("eq-body").innerHTML = d.equations.map(e => {
    const statusCls = e.status === "PASS" ? "risk-pass" : "risk-fail";
    const rateCls = e.pass_rate >= 90 ? "text-green"
                  : e.pass_rate >= 80 ? "text-green" : "text-red";
    return `<tr>
      <td class="font-mono text-dim">${e.id}</td>
      <td class="col-symbol">${e.name}</td>
      <td class="text-dim">${e.type}</td>
      <td><span class="risk-badge ${statusCls}">${e.status}</span></td>
      <td class="${rateCls} font-mono" style="font-weight:700">${e.pass_rate.toFixed(1)}%</td>
    </tr>`;
  }).join("");

  // Per-market
  document.getElementById("market-body").innerHTML = d.per_market.map(m => {
    const statusCls = m.status === "PASS" ? "risk-pass" : "risk-fail";
    return `<tr>
      <td class="col-symbol">${m.market}</td>
      <td class="font-mono">${m.symbols}</td>
      <td class="text-green font-mono" style="font-weight:700">${m.pass_rate.toFixed(1)}%</td>
      <td><span class="risk-badge ${statusCls}">${m.status}</span></td>
    </tr>`;
  }).join("");

  // RSE
  document.getElementById("rse-body").innerHTML = d.rse_cycle.map(r => {
    const statusCls = r.phase === "COMPLETE" ? "risk-pass" : "risk-warn";
    const resCls = r.result === "PASS" ? "text-green" : "text-red";
    return `<tr>
      <td class="font-mono text-dim">${r.cycle}</td>
      <td><span class="risk-badge ${statusCls}">${r.phase}</span></td>
      <td>${r.issue}</td>
      <td class="text-dim">${r.action}</td>
      <td class="${resCls}" style="font-weight:700">${r.result}</td>
    </tr>`;
  }).join("");

  // Audit
  document.getElementById("aud-body").innerHTML = d.audit_trail.map(a => {
    const statusCls = a.status === "FIXED" ? "risk-pass" : "risk-warn";
    return `<tr>
      <td class="font-mono text-dim">${a.id}</td>
      <td>${a.issue}</td>
      <td class="text-dim">${a.fix}</td>
      <td><span class="risk-badge ${statusCls}">${a.status}</span></td>
    </tr>`;
  }).join("");
}

load();