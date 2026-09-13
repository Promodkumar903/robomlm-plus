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