// ROBOMLM — Account Page

async function load() {
  try {
    const res = await fetch("/api/account");
    const data = await res.json();
    render(data);
  } catch (e) { console.error(e); }
}

function render(d) {
  // Profile
  document.getElementById("profile-body").innerHTML = `
    <div class="info-row"><span class="lbl">User ID</span><span class="val font-mono">${d.profile.user_id}</span></div>
    <div class="info-row"><span class="lbl">Display Name</span><span class="val">${d.profile.display_name}</span></div>
    <div class="info-row"><span class="lbl">Email</span><span class="val">${d.profile.email}</span></div>
    <div class="info-row"><span class="lbl">Joined</span><span class="val font-mono">${d.profile.joined}</span></div>
  `;

  // Plan
  document.getElementById("plan-body").innerHTML = `
    <div class="plan-card">
      <div class="plan-name">${d.plan.name}</div>
      <div class="plan-status">● ${d.plan.status}</div>
      <div class="plan-renew">Renews: ${d.plan.renews}</div>
      <div class="plan-features">
        ${d.plan.features.map(f => `<span class="feature-pill">✓ ${f}</span>`).join("")}
      </div>
    </div>
  `;

  // Keys
  document.getElementById("keys-body").innerHTML = d.api_keys.map(k => {
    const statusCls = k.status === "CONNECTED" ? "risk-pass"
                    : k.status === "NOT_SET" ? "risk-fail" : "risk-warn";
    return `<tr>
      <td class="col-symbol">${k.exchange}</td>
      <td><span class="risk-badge ${statusCls}">${k.status}</span></td>
      <td class="text-dim font-mono">${k.last_used}</td>
      <td><button class="btn btn-ghost btn-sm">Configure</button></td>
    </tr>`;
  }).join("");

  // Preferences
  const p = d.preferences;
  document.getElementById("prefs-body").innerHTML = `
    <div class="info-row"><span class="lbl">Theme</span><span class="val">${p.theme}</span></div>
    <div class="info-row"><span class="lbl">Mode</span><span class="val">${p.mode}</span></div>
    <div class="info-row"><span class="lbl">Notifications</span><span class="val">${p.notifications ? "✓ Enabled" : "✗ Disabled"}</span></div>
    <div class="info-row"><span class="lbl">Auto Refresh</span><span class="val font-mono">${p.auto_refresh}s</span></div>
  `;

  // Usage
  document.getElementById("usage-body").innerHTML = `
    <div class="info-row"><span class="lbl">Trades Today</span><span class="val font-mono">${d.usage.trades_today}</span></div>
    <div class="info-row"><span class="lbl">API Calls</span><span class="val font-mono">${d.usage.api_calls.toLocaleString()}</span></div>
    <div class="info-row"><span class="lbl">Data Used</span><span class="val font-mono">${d.usage.data_used_mb} MB</span></div>
  `;
}

load();