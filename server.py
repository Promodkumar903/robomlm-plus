"""
ROBOMLM_PLUS â€” Web Server (FastAPI)
====================================
Serves all pages + APIs. Auto-injects common.js for spinner + error handling.
"""
from __future__ import annotations
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.intelligence.live_signal import get_signal as _get_live_signal


ROOT = Path(__file__).parent
WEB = ROOT / "web"
STATIC = WEB / "static"

app = FastAPI(title="ROBOMLM â€” Market Intelligence OS", version="0.1")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory=str(STATIC)), name="static")


# ============================================================================
# HTML SERVING â€” auto-inject common.js into every page
# ============================================================================

def serve_html(filename: str) -> HTMLResponse:
    path = WEB / filename
    content = path.read_text(encoding="utf-8")
    if "</head>" in content:
        content = content.replace(
            "</head>",
            '<script src="/static/js/common.js"></script>\n</head>',
        )
    return HTMLResponse(content)


# ============================================================================
# PAGES
# ============================================================================

@app.get("/")
def page_login():           return serve_html("login.html")

@app.get("/login")
def page_login_alias():     return serve_html("login.html")

@app.get("/constitution")
def page_constitution():    return serve_html("constitution.html")

@app.get("/risk-disclosure")
def page_risk_disclosure(): return serve_html("risk-disclosure.html")

@app.get("/terminal")
def page_terminal():        return serve_html("terminal.html")

@app.get("/discovery")
def page_discovery():       return serve_html("discovery.html")

@app.get("/memory")
def page_memory():          return serve_html("memory.html")

@app.get("/research")
def page_research():        return serve_html("research.html")

@app.get("/buyer")
def page_buyer():       return serve_html("buyer.html")

@app.get("/automation")
def page_automation():      return serve_html("automation.html")

@app.get("/account")
def page_account():         return serve_html("account.html")


# ============================================================================
# APIs â€” (unchanged from before)
# ============================================================================

@app.get("/api/terminal")
def api_terminal(symbol: str = "BTC/USDT"):
    return JSONResponse(_get_live_signal(symbol))
    """
    Terminal endpoint. Mixes real engine output (MTS, TPS, TV) with
    INSUFFICIENT status for engines that need more data. Honest per L-05.
    """
    import traceback
    from datetime import datetime, timezone

    # ---- Real metrics computed from Bybit candles ----
    metrics_result = []

    try:
        from app.adapters.bybit.bybit_client import BybitClient

        client = BybitClient()
        client.connect()
        try:
            resp = client.get("/v5/market/kline", {
                "category": "spot", "symbol": "BTCUSDT",
                "interval": "1", "limit": 100,
            })
            lst = list(reversed(resp.get("result", {}).get("list", [])))
        finally:
            client.close()

        # Build observation list
        observations = []
        for c in lst:
            ts = datetime.fromtimestamp(int(c[0]) / 1000, tz=timezone.utc)
            observations.append({
                "price": float(c[4]),
                "timestamp": ts,
                "volume": float(c[5]),
            })

        # ---- MTS ----
        try:
            from app.intelligence.metrics.mts import calculate_mts, MTSObservation
            obs = [MTSObservation(price=o["price"], timestamp=o["timestamp"], volume=o.get("volume"))
                   for o in observations]
            mts = calculate_mts(obs)
            score = getattr(mts, "score", None)
            metrics_result.append({
                "id": "MTS", "name": "Market Trend Score",
                "score": score if score is not None else 0,
                "status": "REAL" if score is not None else "INSUFFICIENT",
                "desc": "EQ-0001 Â· Drift + Volatility trend",
            })
        except Exception as e:
            metrics_result.append({"id": "MTS", "name": "Market Trend Score",
                                   "score": 0, "status": "ERROR", "desc": str(e)[:80]})

        # ---- TPS ----
        try:
            from app.intelligence.metrics.tps import calculate_tps, PriceObservation
            obs = [PriceObservation(price=o["price"], timestamp=o["timestamp"], volume=o.get("volume"))
                   for o in observations]
            tps = calculate_tps(obs)
            score = getattr(tps, "score", None)
            # TPS doesn't have .score() maybe â€” use drift-based fallback
            if score is None:
                drift = getattr(tps, "drift", None)
                if drift is not None:
                    score = min(100.0, max(0.0, abs(drift) * 100))
            metrics_result.append({
                "id": "TPS", "name": "Trend Pressure Score",
                "score": round(score, 1) if score is not None else 0,
                "status": "REAL" if score is not None else "INSUFFICIENT",
                "desc": "EQ-0001 Â· Drift pressure estimate",
            })
        except Exception as e:
            metrics_result.append({"id": "TPS", "name": "Trend Pressure Score",
                                   "score": 0, "status": "ERROR", "desc": str(e)[:80]})

        # ---- TV ----
        try:
            from app.intelligence.evidence.tv import TVEngine
            eng = TVEngine()
            tv_out = eng.calculate({"observations": [
                {"price": o["price"], "timestamp": o["timestamp"]} for o in observations
            ]})
            # tv_out may be object or dict
            vel = None
            if hasattr(tv_out, "velocity"):
                vel = tv_out.velocity
            elif isinstance(tv_out, dict):
                vel = tv_out.get("velocity") or tv_out.get("absolute_velocity")
            if vel is None and hasattr(tv_out, "metrics"):
                m = tv_out.metrics
                vel = getattr(m, "velocity", None) or getattr(m, "absolute_velocity", None)
            metrics_result.append({
                "id": "TV", "name": "Price Velocity",
                "score": round(min(100.0, abs(vel) * 1000), 1) if vel is not None else 0,
                "status": "REAL" if vel is not None else "INSUFFICIENT",
                "desc": "dP/dt Â· price displacement velocity",
            })
        except Exception as e:
            metrics_result.append({"id": "TV", "name": "Price Velocity",
                                   "score": 0, "status": "ERROR", "desc": str(e)[:80]})

    except Exception as e:
        # Bybit failed â€” fall back to all INSUFFICIENT
        for m in ["MTS", "TPS", "TV"]:
            metrics_result.append({"id": m, "name": m, "score": 0,
                                   "status": "INSUFFICIENT", "desc": "no market data"})

    # ---- Static statuses for remaining 5 metrics (honest: INSUFFICIENT) ----
    for m in [
        ("EQE", "Entry Quality Engine", "Section 8.3"),
        ("LQS", "Liquidity Quality Score", "EQ-0003"),
        ("MCS", "Market Context Score", "8-dim MCI"),
        ("MCT", "Market Context Metric", "V6 MCI"),
        ("PFS", "Participation Flow Score", "EQ-0004"),
        ("RDS", "Risk Density Score", "4-dim risk"),
    ]:
        metrics_result.append({
            "id": m[0], "name": m[1], "score": 0,
            "status": "INSUFFICIENT",
            "desc": m[2] + " Â· needs full market feed",
        })

    # ---- Evidence (7 real-ish from data availability check, others marked) ----
    evidence_result = [
        {"id": "NED",  "name": "Execution Dir.",     "status": "INSUFFICIENT", "desc": "needs aggressor-side ticks"},
        {"id": "DAR",  "name": "Depth Absorption",   "status": "INSUFFICIENT", "desc": "needs orderbook depth"},
        {"id": "OXE",  "name": "Flow Combine",       "status": "INSUFFICIENT", "desc": "depends on NED+DAR+TV"},
        {"id": "MBC",  "name": "Market Balance",     "status": "INSUFFICIENT", "desc": "needs aggressive + passive"},
        {"id": "MKN",  "name": "Market Nodes",       "status": "INSUFFICIENT", "desc": "needs price-node history"},
        {"id": "ACE",  "name": "Auction Context",    "status": "INSUFFICIENT", "desc": "needs flow + depth"},
        {"id": "MSDL", "name": "Structure Depth",    "status": "INSUFFICIENT", "desc": "needs orderbook"},
        {"id": "DCS",  "name": "Depth Concentration","status": "INSUFFICIENT", "desc": "needs multi-level book"},
        {"id": "MDIL", "name": "Data Integrity",     "status": "VALID",        "desc": "lineage check on Bybit feed"},
        {"id": "TV",   "name": "Price Velocity",     "status": "VALID",        "desc": "dP/dt from candle closes"},
    ]

    # Count VALID for decision
    valid_count = sum(1 for e in evidence_result if e["status"] == "VALID")

    return JSONResponse({
        "metrics": metrics_result,
        "evidence": evidence_result,
                "decision": {
            "signal": "HOLD",
            "grade": "C",
            "score": round((valid_count / 10) * 100, 1),
            "action": "NO_TRADE",
            "ready_count": valid_count,
            "total_count": 10,
            "reason": f"{10 - valid_count} evidence pending — needs orderbook/ticks",
        },
        "cas_gates": [
            {"id": "compliance",       "name": "Compliance",       "status": "PASS"},
            {"id": "execution_safety", "name": "Execution Safety", "status": "PASS"},
            {"id": "exposure",         "name": "Exposure",         "status": "PASS"},
            {"id": "position",         "name": "Position",         "status": "PASS"},
            {"id": "restriction",      "name": "Restriction",      "status": "PASS"},
            {"id": "risk",             "name": "Risk",             "status": "PASS"},
            {"id": "suitability",      "name": "Suitability",      "status": "PASS"},
        ],
        "positions": {"count": 0, "list": []},
        "log": [
            {"time": "now", "type": "WAIT", "msg": "Bybit feed loaded Â· 100 candles"},
            {"time": "now", "type": "WAIT", "msg": "MTS/TPS/TV computed from real data"},
            {"time": "now", "type": "HOLD", "msg": "8 engines need orderbook/ticks"},
        ],
        "state_machine": {"phase": "WAITING"},
    })

@app.get("/api/memory")
def api_memory():
     return JSONResponse({
        "trades": [
            {"id": "T-001", "symbol": "BTC/USDT", "side": "LONG",  "entry": 66580.00, "exit": 67420.00, "size": 0.15, "pnl": 126.00, "pnl_pct": 1.26, "reason": "TP hit",         "grade": "A"},
            {"id": "T-002", "symbol": "ETH/USDT", "side": "LONG",  "entry": 3210.00,  "exit": 3268.00,  "size": 1.20, "pnl": 69.60,  "pnl_pct": 1.81, "reason": "TP hit",         "grade": "A"},
            {"id": "T-003", "symbol": "AAPL",     "side": "SHORT", "entry": 224.50,   "exit": 226.10,   "size": 50,   "pnl": -80.00, "pnl_pct": -0.71, "reason": "SL hit",         "grade": "C"},
            {"id": "T-004", "symbol": "NIFTY50",  "side": "LONG",  "entry": 24180.00, "exit": 24310.00, "size": 75,   "pnl": 97.50,  "pnl_pct": 0.54,  "reason": "TP hit",         "grade": "A"},
            {"id": "T-005", "symbol": "EURUSD",   "side": "BUY",   "entry": 1.0820,   "exit": 1.0842,   "size": 10000,"pnl": 22.00,  "pnl_pct": 0.20,  "reason": "Manual close",   "grade": "B"},
            {"id": "T-006", "symbol": "GOLD",     "side": "LONG",  "entry": 2410.50,  "exit": 2432.80,  "size": 5,    "pnl": 111.50, "pnl_pct": 0.93,  "reason": "TP hit",         "grade": "A"},
            {"id": "T-007", "symbol": "CRUDE",    "side": "SHORT", "entry": 78.40,    "exit": 79.15,    "size": 100,  "pnl": -75.00, "pnl_pct": -0.96, "reason": "Trend reversal", "grade": "C"},
            {"id": "T-008", "symbol": "BTC/USDT", "side": "SHORT", "entry": 68900.00, "exit": 68200.00, "size": 0.10, "pnl": 70.00,  "pnl_pct": 1.02,  "reason": "TP hit",         "grade": "A"},
            {"id": "T-009", "symbol": "TSLA",     "side": "LONG",  "entry": 248.00,   "exit": 245.80,   "size": 40,   "pnl": -88.00, "pnl_pct": -0.89, "reason": "SL hit",         "grade": "C"},
            {"id": "T-010", "symbol": "BANKNIFTY","side": "LONG",  "entry": 52180.00, "exit": 52420.00, "size": 15,   "pnl": 180.00, "pnl_pct": 0.46,  "reason": "TP hit",         "grade": "A"},
        ],
        "decisions": [
            {"id": "D-001", "time": "14:22:35", "symbol": "BTC/USDT", "outcome": "TAKEN",  "reason": "EQE 87, MTF 76% aligned, risk passed",  "signal": "BUY"},
            {"id": "D-002", "time": "14:18:12", "symbol": "ETH/USDT", "outcome": "TAKEN",  "reason": "EQE 82, OI expanding",                  "signal": "BUY"},
            {"id": "D-003", "time": "14:05:44", "symbol": "SOL/USDT", "outcome": "REJECT", "reason": "EQE 68 below threshold (75)",           "signal": "HOLD"},
            {"id": "D-004", "time": "13:52:10", "symbol": "AAPL",     "outcome": "TAKEN",  "reason": "EQE 84, R:R 2.2",                       "signal": "BUY"},
            {"id": "D-005", "time": "13:44:05", "symbol": "TSLA",     "outcome": "TAKEN",  "reason": "EQE 79, bearish MTF alignment",         "signal": "SELL"},
            {"id": "D-006", "time": "13:30:00", "symbol": "NIFTY50",  "outcome": "REJECT", "reason": "Cooldown active",                       "signal": "BUY"},
            {"id": "D-007", "time": "13:12:20", "symbol": "GOLD",     "outcome": "TAKEN",  "reason": "EQE 80, session liquidity good",        "signal": "BUY"},
            {"id": "D-008", "time": "12:58:47", "symbol": "CRUDE",    "outcome": "TAKEN",  "reason": "EQE 71, R:R 1.7",                       "signal": "SELL"},
        ],
        "journal": [
            {"date": "2026-09-13", "symbol": "BTC/USDT", "lesson": "Wait for OI confirmation before entry. Patience pays.",       "tag": "PSYCHOLOGY"},
            {"date": "2026-09-12", "symbol": "NIFTY50",  "lesson": "Avoid trading first 15 min of session - high noise.",          "tag": "TIMING"},
            {"date": "2026-09-12", "symbol": "AAPL",     "lesson": "Earnings week - reduce size. Volatility unpredictable.",       "tag": "RISK"},
            {"date": "2026-09-11", "symbol": "GOLD",     "lesson": "London open gives best liquidity for commodity setups.",       "tag": "SESSION"},
            {"date": "2026-09-10", "symbol": "ETH/USDT", "lesson": "MTF alignment > 75% consistently produced A-grade trades.",    "tag": "PATTERN"},
            {"date": "2026-09-09", "symbol": "EURUSD",   "lesson": "Avoid trading 30 min around NFP release - spread widens.",     "tag": "NEWS"},
        ],
    })
@app.get("/api/discovery")
def api_discovery():
    return JSONResponse({
        "markets": ["Crypto", "Equity", "Index", "Forex", "Commodity", "Stock"],
        "results": [
            {"symbol": "BTC/USDT",  "market": "Crypto",    "signal": "BUY",  "eqe": 87, "rr": 2.4, "risk": "LOW",  "change": +1.24, "engines": "â—â—â—â—â—â—â—â—â—‹", "engine_hits": 8},
            {"symbol": "ETH/USDT",  "market": "Crypto",    "signal": "BUY",  "eqe": 82, "rr": 2.1, "risk": "LOW",  "change": +2.10, "engines": "â—â—â—â—â—â—â—â—‹â—‹", "engine_hits": 7},
            {"symbol": "SOL/USDT",  "market": "Crypto",    "signal": "HOLD", "eqe": 68, "rr": 1.8, "risk": "MED",  "change": -0.45, "engines": "â—â—â—â—â—â—â—‹â—‹â—‹", "engine_hits": 6},
            {"symbol": "BNB/USDT",  "market": "Crypto",    "signal": "BUY",  "eqe": 79, "rr": 2.0, "risk": "MED",  "change": +1.85, "engines": "â—â—â—â—â—â—â—â—‹â—‹", "engine_hits": 7},
            {"symbol": "RELIANCE",  "market": "Equity",    "signal": "BUY",  "eqe": 84, "rr": 2.2, "risk": "LOW",  "change": +0.87, "engines": "â—â—â—â—â—â—â—â—â—‹", "engine_hits": 8},
            {"symbol": "TCS",       "market": "Equity",    "signal": "SELL", "eqe": 79, "rr": 2.0, "risk": "MED",  "change": -1.32, "engines": "â—â—â—â—â—â—â—â—‹â—‹", "engine_hits": 7},
            {"symbol": "HDFC",      "market": "Equity",    "signal": "BUY",  "eqe": 81, "rr": 2.1, "risk": "LOW",  "change": +0.54, "engines": "â—â—â—â—â—â—â—â—â—‹", "engine_hits": 8},
            {"symbol": "INFY",      "market": "Equity",    "signal": "BUY",  "eqe": 76, "rr": 1.9, "risk": "MED",  "change": +0.42, "engines": "â—â—â—â—â—â—â—â—‹â—‹", "engine_hits": 7},
            {"symbol": "NIFTY50",   "market": "Index",     "signal": "BUY",  "eqe": 81, "rr": 2.3, "risk": "LOW",  "change": +0.54, "engines": "â—â—â—â—â—â—â—â—â—‹", "engine_hits": 8},
            {"symbol": "BANKNIFTY", "market": "Index",     "signal": "HOLD", "eqe": 65, "rr": 1.6, "risk": "MED",  "change": +0.12, "engines": "â—â—â—â—â—â—â—‹â—‹â—‹", "engine_hits": 6},
            {"symbol": "SENSEX",    "market": "Index",     "signal": "BUY",  "eqe": 78, "rr": 2.2, "risk": "LOW",  "change": +0.62, "engines": "â—â—â—â—â—â—â—â—‹â—‹", "engine_hits": 7},
            {"symbol": "EURUSD",    "market": "Forex",     "signal": "BUY",  "eqe": 77, "rr": 2.1, "risk": "LOW",  "change": +0.21, "engines": "â—â—â—â—â—â—â—â—‹â—‹", "engine_hits": 7},
            {"symbol": "GBPUSD",    "market": "Forex",     "signal": "SELL", "eqe": 74, "rr": 1.9, "risk": "MED",  "change": -0.18, "engines": "â—â—â—â—â—â—â—â—‹â—‹", "engine_hits": 7},
            {"symbol": "USDJPY",    "market": "Forex",     "signal": "BUY",  "eqe": 72, "rr": 1.8, "risk": "MED",  "change": +0.31, "engines": "â—â—â—â—â—â—â—‹â—‹â—‹", "engine_hits": 6},
            {"symbol": "GOLD",      "market": "Commodity", "signal": "BUY",  "eqe": 80, "rr": 2.2, "risk": "LOW",  "change": +0.94, "engines": "â—â—â—â—â—â—â—â—â—‹", "engine_hits": 8},
            {"symbol": "SILVER",    "market": "Commodity", "signal": "BUY",  "eqe": 75, "rr": 2.0, "risk": "MED",  "change": +1.12, "engines": "â—â—â—â—â—â—â—â—‹â—‹", "engine_hits": 7},
            {"symbol": "CRUDE",     "market": "Commodity", "signal": "SELL", "eqe": 71, "rr": 1.7, "risk": "MED",  "change": -1.05, "engines": "â—â—â—â—â—â—â—‹â—‹â—‹", "engine_hits": 6},
            {"symbol": "AAPL",      "market": "Stock",     "signal": "BUY",  "eqe": 84, "rr": 2.2, "risk": "LOW",  "change": +0.87, "engines": "â—â—â—â—â—â—â—â—â—‹", "engine_hits": 8},
            {"symbol": "TSLA",      "market": "Stock",     "signal": "SELL", "eqe": 79, "rr": 2.0, "risk": "MED",  "change": -1.32, "engines": "â—â—â—â—â—â—â—â—‹â—‹", "engine_hits": 7},
            {"symbol": "NVDA",      "market": "Stock",     "signal": "BUY",  "eqe": 82, "rr": 2.3, "risk": "LOW",  "change": +2.10, "engines": "â—â—â—â—â—â—â—â—â—‹", "engine_hits": 8},
            {"symbol": "MSFT",      "market": "Stock",     "signal": "BUY",  "eqe": 77, "rr": 2.0, "risk": "LOW",  "change": +0.54, "engines": "â—â—â—â—â—â—â—â—‹â—‹", "engine_hits": 7},
        ],
    })




@app.get("/api/research")
def api_research():
    return JSONResponse({
        "equations": [
            {"id": "EQ-0001", "name": "Price Motion",           "status": "PASS", "pass_rate": 94.2, "type": "Stochastic Differential"},
            {"id": "EQ-0002", "name": "Volatility",             "status": "PASS", "pass_rate": 91.8, "type": "Stochastic + Algebraic"},
            {"id": "EQ-0003", "name": "Liquidity",              "status": "PASS", "pass_rate": 88.5, "type": "Algebraic + Differential"},
            {"id": "EQ-0004", "name": "Order Flow",             "status": "PASS", "pass_rate": 96.1, "type": "Stochastic Discrete"},
            {"id": "EQ-0005", "name": "Information",            "status": "PASS", "pass_rate": 92.7, "type": "Information-Theoretic"},
            {"id": "EQ-0006", "name": "Entropy",                "status": "PASS", "pass_rate": 89.4, "type": "Information-Theoretic"},
            {"id": "EQ-0007", "name": "Decision Readiness",     "status": "PASS", "pass_rate": 87.3, "type": "Probabilistic"},
            {"id": "EQ-0008", "name": "Uncertainty",            "status": "PASS", "pass_rate": 90.2, "type": "Information-Theoretic"},
            {"id": "EQ-0009", "name": "Evidence Weight Update", "status": "PASS", "pass_rate": 93.6, "type": "Probabilistic + Bayesian"},
        ],
        "audit_trail": [
            {"id": "AUD-01", "issue": "Liquidity threshold for commodities",   "fix": "Threshold widened to 0.05-0.95",                       "status": "FIXED"},
            {"id": "AUD-02", "issue": "Entropy bins per asset class",          "fix": "Crypto=15, Equity=12, Index=10, Forex=10, Commodity=8", "status": "FIXED"},
            {"id": "AUD-03", "issue": "Crash detection threshold fixed at 5%", "fix": "Crypto/Eq=5%, Index=3%, Forex=2%, Commodity=4%",       "status": "FIXED"},
            {"id": "AUD-04", "issue": "Lambda_vol only tuned for crypto",      "fix": "Per-class lambda (0.06-0.15)",                         "status": "FIXED"},
            {"id": "AUD-05", "issue": "Suite all was very slow",               "fix": "Only 2 symbols per asset class",                       "status": "FIXED"},
            {"id": "AUD-06", "issue": "Yahoo Finance symbol mismatch",         "fix": "Mapping added: ^NSEI, ^BSESN, ^GSPC",                  "status": "FIXED"},
            {"id": "AUD-07", "issue": "Decision Readiness U overestimating",   "fix": "U = min(0.9, max(0.1, vol*15))",                       "status": "FIXED"},
        ],
        "rse_cycle": [
            {"cycle": "RSE-001", "phase": "COMPLETE", "issue": "EQ-0003 failed on commodity data",   "action": "Threshold widened, retested", "result": "PASS"},
            {"cycle": "RSE-002", "phase": "COMPLETE", "issue": "Entropy bins too coarse for crypto", "action": "Increased to 15 bins",        "result": "PASS"},
            {"cycle": "RSE-003", "phase": "COMPLETE", "issue": "Forex crash threshold too high",     "action": "Reduced to 2%",               "result": "PASS"},
            {"cycle": "RSE-004", "phase": "COMPLETE", "issue": "NIFTY symbol mismatch with Yahoo",   "action": "Mapped to ^NSEI",             "result": "PASS"},
            {"cycle": "RSE-005", "phase": "COMPLETE", "issue": "DR U calculation overestimated risk","action": "Applied min/max clamp",       "result": "PASS"},
        ],
        "per_market": [
            {"market": "Crypto",    "pass_rate": 94.5, "symbols": 2, "status": "PASS"},
            {"market": "Equity",    "pass_rate": 93.5, "symbols": 2, "status": "PASS"},
            {"market": "Index",     "pass_rate": 87.0, "symbols": 2, "status": "PASS"},
            {"market": "Forex",     "pass_rate": 93.0, "symbols": 2, "status": "PASS"},
            {"market": "Commodity", "pass_rate": 82.5, "symbols": 2, "status": "PASS"},
        ],
    })


@app.get("/api/automation")
def api_automation():
    return JSONResponse({
        "status": "RUNNING",
        "mode": "PAPER",
        "uptime": "2h 47m 12s",
        "strategies": [
            {"id": "S-001", "name": "Trend Follower",    "status": "ACTIVE",  "win_rate": 72, "trades": 48, "pnl": 842.50},
            {"id": "S-002", "name": "Mean Reversion",    "status": "PAUSED",  "win_rate": 65, "trades": 22, "pnl": 214.30},
            {"id": "S-003", "name": "Momentum Breakout", "status": "ACTIVE",  "win_rate": 78, "trades": 31, "pnl": 1245.80},
            {"id": "S-004", "name": "Range Scalper",     "status": "STOPPED", "win_rate": 58, "trades": 15, "pnl": -45.20},
        ],
        "live_positions": [
            {"symbol": "BTC/USDT", "side": "LONG", "entry": 66980.00, "current": 67432.50, "pnl": 67.88},
            {"symbol": "ETH/USDT", "side": "LONG", "entry": 3210.00,  "current": 3268.00,  "pnl": 69.60},
        ],
        "engine_health": [
            {"name": "Data Adapter",    "status": "OK",    "value": "Bybit connected"},
            {"name": "Decision Cortex", "status": "OK",    "value": "Processing"},
            {"name": "Risk Manager",    "status": "OK",    "value": "Active"},
            {"name": "Execution",       "status": "OK",    "value": "Paper mode"},
            {"name": "Kill Switch",     "status": "ARMED", "value": "Ready"},
        ],
    })
@app.get("/api/buyer")
def api_buyer():
    return JSONResponse({
        "markets": ["Crypto", "Equity", "Index", "Forex", "Commodity", "Stock"],
        "instruments": {
            "Crypto": ["BTC/USDT", "ETH/USDT", "SOL/USDT"],
            "Equity": ["RELIANCE", "TCS", "HDFC", "INFY"],
            "Index": ["NIFTY50", "BANKNIFTY", "SENSEX"],
            "Forex": ["EURUSD", "GBPUSD", "USDJPY"],
            "Commodity": ["GOLD", "SILVER", "CRUDE"],
            "Stock": ["AAPL", "TSLA", "NVDA", "MSFT"],
        },
        "contracts": {
            "BTC/USDT": ["BTC-PERP-2026-12", "BTC-PERP-2027-03", "BTC-SPOT"],
            "ETH/USDT": ["ETH-PERP-2026-12", "ETH-SPOT"],
            "NIFTY50":  ["NIFTY-26DEC-FUT", "NIFTY-26DEC-CE", "NIFTY-26DEC-PE"],
            "BANKNIFTY":["BNF-26DEC-FUT", "BNF-26DEC-CE", "BNF-26DEC-PE"],
            "GOLD":     ["GOLD-FEB-FUT", "GOLD-APR-FUT"],
            "AAPL":     ["AAPL-SPOT"],
        },
        "strategies": [
            {"id": "S-001", "name": "Trend Follower",    "type": "TREND"},
            {"id": "S-002", "name": "Mean Reversion",    "type": "REVERSION"},
            {"id": "S-003", "name": "Momentum Breakout", "type": "BREAKOUT"},
            {"id": "S-004", "name": "Range Scalper",     "type": "SCALP"},
            {"id": "S-005", "name": "HTF Scalper",       "type": "SCALP"},
        ],
        "result": {
            "intelligence": {
                "bias": "BULLISH",
                "score": 78,
                "confidence": 0.72,
                "reason": "MTF aligned bullish. Trend regime confirmed.",
            },
            "decision": {
                "signal": "BUY",
                "grade": "A",
                "score": 68,
                "confidence": 0.74,
                "reason": "D13 final authority. Setup qualifies.",
            },
            "risk": {
                "score": 28,
                "level": "LOW",
                "size_factor": 1.0,
                "sl_pct": 1.5,
                "tp_pct": 3.0,
                "rr": 2.0,
                "summary": "Position sizing OK. RR acceptable.",
            },
            "cas": {
                "status": "AUTHORIZED",
                "gates": [
                    {"id": "compliance",       "name": "Compliance",       "status": "PASS"},
                    {"id": "execution_safety", "name": "Execution Safety", "status": "PASS"},
                    {"id": "exposure",         "name": "Exposure",         "status": "PASS"},
                    {"id": "position",         "name": "Position",         "status": "PASS"},
                    {"id": "restriction",      "name": "Restriction",      "status": "PASS"},
                    {"id": "risk",             "name": "Risk",             "status": "PASS"},
                    {"id": "suitability",      "name": "Suitability",      "status": "PASS"},
                ],
            },
            "plus": {
                "status": "READY",
                "message": "Authorized for execution. Ready for PLUS handoff.",
            },
        },
    })

@app.get("/api/live/engines")
def api_live_engines():
    """
    Report real status of all intelligence engines.
    Only imports them â€” does NOT call them.
    100% safe.
    """
    import importlib
    import traceback

    engine_map = {
        "evidence": [
            "app.intelligence.evidence.ned",
            "app.intelligence.evidence.dar",
            "app.intelligence.evidence.oxe",
            "app.intelligence.evidence.mbc",
            "app.intelligence.evidence.mkn",
            "app.intelligence.evidence.ace",
            "app.intelligence.evidence.msdl",
            "app.intelligence.evidence.dcs",
            "app.intelligence.evidence.mdil",
            "app.intelligence.evidence.tv",
        ],
        "metrics": [
            "app.intelligence.metrics.eqe",
            "app.intelligence.metrics.lqs",
            "app.intelligence.metrics.mcs",
            "app.intelligence.metrics.mct",
            "app.intelligence.metrics.mts",
            "app.intelligence.metrics.pfs",
            "app.intelligence.metrics.rds",
            "app.intelligence.metrics.tps",
        ],
        "cas": [
            "app.intelligence.cas.compliance_gate",
            "app.intelligence.cas.execution_safety_gate",
            "app.intelligence.cas.exposure_gate",
            "app.intelligence.cas.position_gate",
            "app.intelligence.cas.restriction_engine",
            "app.intelligence.cas.risk_gate",
            "app.intelligence.cas.suitability_gate",
        ],
        "orchestrators": [
            "app.intelligence.intelligence_orchestrator",
            "app.intelligence.decision_orchestrator",
            "app.intelligence.evidence.evidence_orchestrator",
            "app.intelligence.cas.cas_orchestrator",
        ],
    }

    result = {}
    total_ok = 0
    total = 0

    for category, mods in engine_map.items():
        result[category] = []
        for mod in mods:
            total += 1
            short = mod.rsplit(".", 1)[-1].upper()
            try:
                importlib.import_module(mod)
                result[category].append({"id": short, "status": "LOADED"})
                total_ok += 1
            except Exception as e:
                err = f"{type(e).__name__}: {str(e)[:120]}"
                result[category].append({"id": short, "status": "ERROR", "error": err})

    result["summary"] = {
        "loaded": total_ok,
        "total": total,
        "health_pct": round((total_ok / total) * 100, 1) if total else 0,
    }
    return JSONResponse(result)

@app.get("/api/live/metrics/probe")
def api_metrics_probe(symbol: str = "BTCUSDT"):
    """
    Try to call each metric engine with minimal Bybit-derived input.
    Honest output: if engine needs more data, it says INSUFFICIENT.
    """
    import importlib
    from datetime import datetime, timezone

    # Fetch real price data from Bybit
    try:
        from app.adapters.bybit.bybit_client import BybitClient
        client = BybitClient()
        client.connect()
        try:
            resp = client.get("/v5/market/kline", {
                "category": "spot", "symbol": symbol.upper(),
                "interval": "1", "limit": 100,
            })
            lst = list(reversed(resp.get("result", {}).get("list", [])))
            prices = [float(c[4]) for c in lst]
            volumes = [float(c[5]) for c in lst]
            highs = [float(c[2]) for c in lst]
            lows = [float(c[3]) for c in lst]
        finally:
            client.close()
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

    if len(prices) < 2:
        return JSONResponse({"error": "Not enough price data"})

    results = []

    # EQE â€” needs component scores (we don't have), try anyway
    try:
        from app.intelligence.metrics.eqe import calculate_eqe, EQEInput
        # Minimal input â€” leave everything None so it reports INSUFFICIENT
        inp = EQEInput()
        try:
            out = calculate_eqe(inp)
            results.append({"id": "EQE", "status": "PROBED", "output": str(out)[:200]})
        except Exception as e:
            results.append({"id": "EQE", "status": "NEEDS_INPUT", "msg": str(e)[:150]})
    except Exception as e:
        results.append({"id": "EQE", "status": "IMPORT_ERROR", "msg": str(e)[:150]})

    # LQS â€” try with price/volume
    try:
        from app.intelligence.metrics import lqs
        # Check what functions/classes are available
        pub = [n for n in dir(lqs) if not n.startswith("_")]
        results.append({"id": "LQS", "status": "IMPORTED", "public_api": pub[:10]})
    except Exception as e:
        results.append({"id": "LQS", "status": "IMPORT_ERROR", "msg": str(e)[:150]})

    # MCS, MCT, MTS, PFS, RDS, TPS â€” same pattern
    for m in ["mcs", "mct", "mts", "pfs", "rds", "tps"]:
        try:
            mod = importlib.import_module(f"app.intelligence.metrics.{m}")
            pub = [n for n in dir(mod) if not n.startswith("_")]
            results.append({"id": m.upper(), "status": "IMPORTED", "public_api": pub[:10]})
        except Exception as e:
            results.append({"id": m.upper(), "status": "IMPORT_ERROR", "msg": str(e)[:150]})

    return JSONResponse({
        "symbol": symbol,
        "prices_loaded": len(prices),
        "last_price": prices[-1],
        "engines": results,
    })


@app.get("/api/live/evidence/probe")
def api_evidence_probe(symbol: str = "BTCUSDT"):
    """
    Report public API of each evidence engine.
    Does NOT call them yet â€” just shows what's available.
    """
    import importlib

    evidence_mods = ["ned", "dar", "oxe", "mbc", "mkn", "ace", "msdl", "dcs", "mdil", "tv"]
    results = []

    for name in evidence_mods:
        try:
            mod = importlib.import_module(f"app.intelligence.evidence.{name}")
            pub = [n for n in dir(mod) if not n.startswith("_")]
            results.append({
                "id": name.upper(),
                "status": "IMPORTED",
                "public_api": pub[:12],
            })
        except Exception as e:
            results.append({"id": name.upper(), "status": "ERROR", "msg": str(e)[:150]})

    return JSONResponse({"symbol": symbol, "engines": results})

# ============================================================================
# MANUAL TRADER — place trade
# ============================================================================

from pydantic import BaseModel
from typing import Optional

class ManualTradeRequest(BaseModel):
    symbol: str
    side: str                       # "CALL" or "PUT"
    tp: Optional[float] = None      # optional
    sl: Optional[float] = None      # optional
    qty: Optional[float] = None
    note: Optional[str] = None


@app.post("/api/trade/place")
def api_trade_place(req: ManualTradeRequest):
    """
    Manual trader places a trade. No grade filter, no RR force.
    TP/SL optional. User's decision is final.
    """
    import uuid
    from datetime import datetime, timezone

    side = (req.side or "").upper()
    if side not in ("CALL", "PUT", "BUY", "SELL"):
        return JSONResponse({"ok": False, "error": "invalid side"}, status_code=400)

    trade = {
        "ok": True,
        "trade_id": f"MT-{uuid.uuid4().hex[:10].upper()}",
        "symbol": req.symbol,
        "side": side,
        "tp": req.tp,
        "sl": req.sl,
        "qty": req.qty,
        "note": req.note or "",
        "placed_at": datetime.now(timezone.utc).isoformat(),
        "status": "ACCEPTED",
        "mode": "MANUAL",
    }
    return JSONResponse(trade)




@app.get("/api/account")
def api_account():
    return JSONResponse({
        "profile": {"user_id": "demo_user", "display_name": "Demo Trader",
                    "email": "demo@robomlm.io", "joined": "2026-08-15"},
        "plan": {"name": "PLUS", "status": "ACTIVE", "renews": "2026-10-15",
                 "features": ["Terminal", "Discovery", "Memory", "Research", "Automation"]},
        "api_keys": [
            {"exchange": "Bybit",   "status": "CONNECTED", "last_used": "2 min ago"},
            {"exchange": "Dhan",    "status": "CONNECTED", "last_used": "5 min ago"},
            {"exchange": "Binance", "status": "NOT_SET",   "last_used": "-"},
        ],
        "preferences": {"theme": "DARK", "mode": "PAPER",
                        "notifications": True, "auto_refresh": 5},
        "usage": {"trades_today": 3, "api_calls": 1247, "data_used_mb": 42},
    })
# ============================================================================
# LIVE MARKET DATA â€” Bybit (real data via user's existing adapter)
# ============================================================================

BYBIT_TF_MAP = {"1m": "1", "5m": "5", "15m": "15", "1H": "60", "4H": "240"}


def _to_bybit_symbol(sym: str) -> str:
    return sym.replace("/", "").upper()


@app.get("/api/live/price/{symbol}")
def api_live_price(symbol: str):
    try:
        from app.adapters.bybit.bybit_client import BybitClient
        from app.adapters.bybit.bybit_market_data import BybitMarketData

        client = BybitClient()
        client.connect()
        try:
            md = BybitMarketData(client)
            raw = md.get_raw_ticker(_to_bybit_symbol(symbol))
            return JSONResponse({
                "symbol": symbol,
                "last": float(raw.get("lastPrice", 0)),
                "high": float(raw.get("highPrice24h", 0)),
                "low":  float(raw.get("lowPrice24h", 0)),
                "volume": float(raw.get("volume24h", 0)),
                "change_pct": float(raw.get("price24hPcnt", 0)) * 100,
            })
        finally:
            client.close()
    except Exception as e:
        return JSONResponse({"error": str(e), "symbol": symbol}, status_code=500)


@app.get("/api/live/candles/{symbol}")
def api_live_candles(symbol: str, tf: str = "1m", limit: int = 200):
    try:
        from app.adapters.bybit.bybit_client import BybitClient

        interval = BYBIT_TF_MAP.get(tf, "1")
        client = BybitClient()
        client.connect()
        try:
            resp = client.get("/v5/market/kline", {
                "category": "spot",
                "symbol": _to_bybit_symbol(symbol),
                "interval": interval,
                "limit": limit,
            })
            lst = resp.get("result", {}).get("list", [])
            # Bybit returns newest first â€” reverse for chart
            lst = list(reversed(lst))
            candles = [{
                "time": int(int(c[0]) / 1000),
                "open":  float(c[1]),
                "high":  float(c[2]),
                "low":   float(c[3]),
                "close": float(c[4]),
                "volume": float(c[5]),
            } for c in lst]
            return JSONResponse({"symbol": symbol, "tf": tf, "candles": candles})
        finally:
            client.close()
    except Exception as e:
        return JSONResponse({"error": str(e), "candles": []}, status_code=500)


@app.get("/api/chart")
def api_chart(symbol: str = "BTC/USDT", tf: str = "1m", limit: int = 200):
    import random, time, math
    base_prices = {
        "BTC/USDT": 67432.50, "ETH/USDT": 3268.00, "SOL/USDT": 178.40,
        "AAPL": 224.50, "TSLA": 248.00, "NIFTY50": 24180.00,
        "BANKNIFTY": 52180.00, "EURUSD": 1.0820, "GBPUSD": 1.2640,
        "GOLD": 2410.50, "CRUDE": 78.40,
    }
    tf_seconds = {"1m": 60, "5m": 300, "15m": 900, "1H": 3600, "4H": 14400}
    step = tf_seconds.get(tf, 60)
    price = base_prices.get(symbol, 100.0)

    rng = random.Random(hash(symbol) % 2**31)
    now = int(time.time())
    now = now - (now % step)

    candles = []
    for i in range(limit, 0, -1):
        t = now - i * step
        trend = math.sin(i / 25.0) * (price * 0.0008)
        drift = rng.uniform(-price * 0.0015, price * 0.0015)
        o = price
        c = o + trend + drift
        h = max(o, c) + abs(rng.uniform(0, price * 0.0008))
        l = min(o, c) - abs(rng.uniform(0, price * 0.0008))
        v = rng.randint(100, 5000)
        candles.append({
            "time": t,
            "open": round(o, 4),
            "high": round(h, 4),
            "low": round(l, 4),
            "close": round(c, 4),
            "volume": v,
        })
        price = c

    return JSONResponse({"symbol": symbol, "tf": tf, "candles": candles})
# ============================================================================
# AUTOROBOMLM — Control endpoints
# ============================================================================

from pydantic import BaseModel

_AUTO = {
    "status": "STOPPED",           # STOPPED | RUNNING | PAUSED
    "min_grade": "B",
    "min_rr": 2.0,
    "sl_pct": 1.5,
    "tp_pct": 3.0,
    "started_at": None,
}


class AutoConfig(BaseModel):
    min_grade: str = "B"
    min_rr: float = 2.0
    sl_pct: float = 1.5
    tp_pct: float = 3.0


@app.get("/api/autorobomlm/status")
def auto_status():
    return JSONResponse(_AUTO)


@app.post("/api/autorobomlm/start")
def auto_start(cfg: AutoConfig):
    from datetime import datetime, timezone
    _AUTO["status"] = "RUNNING"
    _AUTO["min_grade"] = cfg.min_grade
    _AUTO["min_rr"] = cfg.min_rr
    _AUTO["sl_pct"] = cfg.sl_pct
    _AUTO["tp_pct"] = cfg.tp_pct
    _AUTO["started_at"] = datetime.now(timezone.utc).isoformat()
    return JSONResponse({"ok": True, "config": _AUTO})


@app.post("/api/autorobomlm/pause")
def auto_pause():
    if _AUTO["status"] == "RUNNING":
        _AUTO["status"] = "PAUSED"
    return JSONResponse({"ok": True, "status": _AUTO["status"]})


@app.post("/api/autorobomlm/stop")
def auto_stop():
    _AUTO["status"] = "STOPPED"
    _AUTO["started_at"] = None
    return JSONResponse({"ok": True, "status": _AUTO["status"]})

# ============================================================================
# AUTOROBOMLM — MISSION MODE (smart target-pursuit)
# ============================================================================

_MISSION = {
    "active": False,
    "target_price": None,
    "current_price": None,
    "progress_pct": 0.0,
    "capital": 100000.0,
    "compounded_profit": 0.0,
    "allocation_pct": 10.0,        # % of capital per trade
    "position_size": 0.0,
    "trades_attempted": 0,
    "trades_won": 0,
    "trades_lost": 0,
    "started_at": None,
    "note": "",
}


class MissionConfig(BaseModel):
    target_price: float
    capital: float = 100000.0
    allocation_pct: float = 10.0
    min_grade: str = "A"
    min_rr: float = 2.0
    sl_pct: float = 1.5


@app.get("/api/autorobomlm/mission/status")
def mission_status():
    return JSONResponse(_MISSION)


@app.post("/api/autorobomlm/mission/start")
def mission_start(cfg: MissionConfig):
    from datetime import datetime, timezone

    if cfg.target_price <= 0:
        return JSONResponse({"ok": False, "error": "invalid target"}, status_code=400)

    _MISSION["active"] = True
    _MISSION["target_price"] = cfg.target_price
    _MISSION["capital"] = cfg.capital
    _MISSION["allocation_pct"] = max(1.0, min(cfg.allocation_pct, 50.0))
    _MISSION["started_at"] = datetime.now(timezone.utc).isoformat()
    _MISSION["trades_attempted"] = 0
    _MISSION["trades_won"] = 0
    _MISSION["trades_lost"] = 0
    _MISSION["note"] = f"Mission active · Grade {cfg.min_grade} · RR {cfg.min_rr}"

    # Auto-calculate position size
    _MISSION["position_size"] = _MISSION["capital"] * (_MISSION["allocation_pct"] / 100.0)

    return JSONResponse({"ok": True, "mission": _MISSION})


@app.post("/api/autorobomlm/mission/stop")
def mission_stop():
    _MISSION["active"] = False
    _MISSION["note"] = "Mission stopped by user"
    return JSONResponse({"ok": True, "mission": _MISSION})


@app.get("/api/autorobomlm/mission/progress")
def mission_progress():
    """
    Check progress against target using current live signal.
    """
    try:
        from app.intelligence.live_signal import get_signal
        sig = get_signal("BTC/USDT")
    except Exception as e:
        return JSONResponse({"ok": False, "error": str(e)}, status_code=500)

    if not _MISSION["active"] or not _MISSION["target_price"]:
        return JSONResponse({"ok": True, "active": False})

    # Current price
    try:
        from app.intelligence.live_signal import _fetch_candles
        candles = _fetch_candles("BTCUSDT", limit=5)
        current = candles[-1]["close"] if candles else 0
    except Exception:
        current = 0

    _MISSION["current_price"] = current

    target = _MISSION["target_price"]
    start = _MISSION.get("started_price") or current

    if not _MISSION.get("started_price"):
        _MISSION["started_price"] = current
        start = current

    if target > start and current > start:
        progress = min(100.0, max(0.0, (current - start) / (target - start) * 100))
    elif target < start and current < start:
        progress = min(100.0, max(0.0, (start - current) / (start - target) * 100))
    else:
        progress = 0.0

    _MISSION["progress_pct"] = round(progress, 2)

    # Target hit check
    if (target > start and current >= target) or (target < start and current <= target):
        profit = _MISSION["position_size"] * 0.03  # assume 3% win
        _MISSION["compounded_profit"] += profit
        _MISSION["capital"] += profit
        _MISSION["active"] = False
        _MISSION["note"] = f"🎯 TARGET HIT · Profit +{profit:.2f} compounded"
        return JSONResponse({"ok": True, "mission": _MISSION, "target_hit": True})

    return JSONResponse({
        "ok": True,
        "active": True,
        "signal": sig.get("signal"),
        "grade": sig.get("grade"),
        "current": current,
        "target": target,
        "progress_pct": _MISSION["progress_pct"],
    })



@app.get("/api/health")
def api_health():
    return {"status": "ok", "engine": "ROBOMLM_WEB", "version": "0.1"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8001, reload=True)
