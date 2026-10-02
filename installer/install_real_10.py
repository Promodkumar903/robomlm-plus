"""Fix derivatives_engine: symbol normalize + correct basis endpoint"""
from pathlib import Path
import shutil
from datetime import datetime

ROOT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\intelligence\real")
TARGET = ROOT / "derivatives_engine.py"

if not TARGET.exists():
    print(f"ERROR: {TARGET} not found")
    raise SystemExit(1)

content = TARGET.read_text(encoding="utf-8")
backup = TARGET.with_suffix(f".py.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
shutil.copy2(TARGET, backup)
print(f"BACKUP: {backup}")

applied = []

# FIX 1 — Add symbol normalizer
if "_norm_symbol" not in content:
    old = '''def _f(v, default=None):
    try:
        n = float(v)
        return n if isfinite(n) else default
    except (TypeError, ValueError):
        return default'''
    new = '''def _f(v, default=None):
    try:
        n = float(v)
        return n if isfinite(n) else default
    except (TypeError, ValueError):
        return default


def _norm_symbol(symbol):
    """BTC/USDT -> BTCUSDT (Bybit format)"""
    return str(symbol).replace("/", "").upper()


def _get_spot_price(symbol):
    raw = _get(
        "/v5/market/tickers",
        {"category": "spot", "symbol": _norm_symbol(symbol)},
    )
    if not raw:
        return None
    items = ((raw.get("result") or {}).get("list") or [])
    if not items:
        return None
    return _f(items[0].get("lastPrice"))


def _get_perp_price(symbol):
    raw = _get(
        "/v5/market/tickers",
        {"category": "linear", "symbol": _norm_symbol(symbol)},
    )
    if not raw:
        return None
    items = ((raw.get("result") or {}).get("list") or [])
    if not items:
        return None
    return _f(items[0].get("lastPrice"))'''
    if old in content:
        content = content.replace(old, new, 1)
        applied.append("1: symbol normalizer + price fetchers")

# FIX 2 — Replace _compute_basis to use two tickers
old_basis = '''    def _compute_basis(self, symbol, spot_price):
        raw = self._fetch_basis(symbol)
        if not raw:
            return None, "NEUTRAL", (), "STABLE"

        items = ((raw.get("result") or {}).get("list") or [])
        if not items:
            return None, "NEUTRAL", (), "STABLE"

        history = []
        for row in items:
            try:
                close = float(row[4])  # index price close
                # premium-index gives index price, need perp price from spot
                history.append(close)
            except (IndexError, ValueError, TypeError):
                continue

        if not history:
            return None, "NEUTRAL", (), "STABLE"

        latest = history[0]
        if spot_price and spot_price > 0:
            basis_pct = (latest - spot_price) / spot_price * 100
        else:
            basis_pct = 0.0

        if basis_pct > 0.05:
            state = "PREMIUM"
        elif basis_pct < -0.05:
            state = "DISCOUNT"
        else:
            state = "NEUTRAL"

        # Trend
        if len(history) >= 3:
            diff = history[0] - history[-1]
            if diff > 0.05:
                trend = "RISING"
            elif diff < -0.05:
                trend = "FALLING"
            else:
                trend = "STABLE"
        else:
            trend = "STABLE"

        return basis_pct, state, tuple(history[:12]), trend'''

new_basis = '''    def _compute_basis(self, symbol, spot_price):
        # Get spot and perp prices
        spot = spot_price if spot_price else _get_spot_price(symbol)
        perp = _get_perp_price(symbol)

        if spot is None or perp is None or spot <= 0:
            return None, "NEUTRAL", (), "STABLE"

        basis_pct = (perp - spot) / spot * 100

        if basis_pct > 0.05:
            state = "PREMIUM"
        elif basis_pct < -0.05:
            state = "DISCOUNT"
        else:
            state = "NEUTRAL"

        # Trend from funding history (basis history not directly available)
        raw = self._fetch_funding(symbol)
        history = []
        if raw:
            items = ((raw.get("result") or {}).get("list") or [])
            for row in items:
                r = _f(row.get("fundingRate"))
                if r is not None:
                    history.append(r)

        if len(history) >= 3:
            if history[0] > history[-1] * 1.2:
                trend = "RISING"
            elif history[0] < history[-1] * 0.8:
                trend = "FALLING"
            else:
                trend = "STABLE"
        else:
            trend = "STABLE"

        return basis_pct, state, tuple(history[:12]), trend'''

if "Get spot and perp prices" in content:
    print("Basis fix already applied")
elif old_basis in content:
    content = content.replace(old_basis, new_basis, 1)
    applied.append("2: basis uses spot + perp tickers")
else:
    print("WARNING: basis patch skipped (marker not found)")

# FIX 3 — Normalize symbol in all fetch methods
replacements = [
    ('f"basis:{symbol}"', 'f"basis:{_norm_symbol(symbol)}"'),
    ('f"oi_hist:{symbol}"', 'f"oi_hist:{_norm_symbol(symbol)}"'),
    ('f"funding:{symbol}"', 'f"funding:{_norm_symbol(symbol)}"'),
    ('f"ls_ratio:{symbol}"', 'f"ls_ratio:{_norm_symbol(symbol)}"'),
    ('"symbol": symbol,', '"symbol": _norm_symbol(symbol),'),
]

for old, new in replacements:
    if new in content:
        continue
    if old in content:
        content = content.replace(old, new)
        applied.append(f"3: normalized {old}")

# FIX 4 — Fix OI fetch with symbol normalize  
old_oi = '''    def _fetch_oi_history(self, symbol):
        def fetch():
            return _get(
                "/v5/market/open-interest",
                {"category": "linear", "symbol": symbol,
                 "intervalTime": "5min", "limit": 24},
            )
        return self._cached(f"oi_hist:{symbol}", fetch)'''

new_oi = '''    def _fetch_oi_history(self, symbol):
        def fetch():
            return _get(
                "/v5/market/open-interest",
                {"category": "linear", "symbol": _norm_symbol(symbol),
                 "intervalTime": "5min", "limit": 24},
            )
        return self._cached(f"oi_hist:{_norm_symbol(symbol)}", fetch)'''

if '"symbol": _norm_symbol(symbol),\n                 "intervalTime": "5min"' in content:
    print("OI fix already applied")
elif old_oi in content:
    content = content.replace(old_oi, new_oi, 1)
    applied.append("4: OI fetch normalized")
else:
    print("WARNING: OI patch skipped")

# FIX 5 — Funding fetch
old_fund = '''    def _fetch_funding(self, symbol):
        def fetch():
            return _get(
                "/v5/market/funding/history",
                {"category": "linear", "symbol": symbol, "limit": 8},
            )
        return self._cached(f"funding:{symbol}", fetch)'''

new_fund = '''    def _fetch_funding(self, symbol):
        def fetch():
            return _get(
                "/v5/market/funding/history",
                {"category": "linear", "symbol": _norm_symbol(symbol), "limit": 8},
            )
        return self._cached(f"funding:{_norm_symbol(symbol)}", fetch)'''

if '"symbol": _norm_symbol(symbol), "limit": 8' in content:
    print("Funding fix already applied")
elif old_fund in content:
    content = content.replace(old_fund, new_fund, 1)
    applied.append("5: funding fetch normalized")
else:
    print("WARNING: funding patch skipped")

# FIX 6 — L/S ratio fetch
old_ls = '''    def _fetch_ls_ratio(self, symbol):
        def fetch():
            return _get(
                "/v5/market/account-ratio",
                {"category": "linear", "symbol": symbol,
                 "period": "5min", "limit": 1},
            )
        return self._cached(f"ls_ratio:{symbol}", fetch)'''

new_ls = '''    def _fetch_ls_ratio(self, symbol):
        def fetch():
            return _get(
                "/v5/market/account-ratio",
                {"category": "linear", "symbol": _norm_symbol(symbol),
                 "period": "5min", "limit": 1},
            )
        return self._cached(f"ls_ratio:{_norm_symbol(symbol)}", fetch)'''

if '"symbol": _norm_symbol(symbol),\n                 "period": "5min"' in content:
    print("LS fix already applied")
elif old_ls in content:
    content = content.replace(old_ls, new_ls, 1)
    applied.append("6: LS ratio fetch normalized")
else:
    print("WARNING: LS patch skipped")

# FIX 7 — Remove _fetch_basis (no longer used)
old_fb = '''    def _fetch_basis(self, symbol):
        def fetch():
            return _get(
                "/v5/market/premium-index-price-kline",
                {"category": "linear", "symbol": symbol,
                 "interval": "5", "limit": 12},
            )
        return self._cached(f"basis:{symbol}", fetch)

'''
if "def _fetch_basis" in content and "premium-index-price-kline" in content:
    # Only remove if not referenced in compute anymore
    if "self._fetch_basis(symbol)" not in content.replace(old_fb, ""):
        content = content.replace(old_fb, "", 1)
        applied.append("7: removed obsolete _fetch_basis")

TARGET.write_text(content, encoding="utf-8")

print()
print("APPLIED:")
for a in applied:
    print(f"  + {a}")
print()
print(f"UPDATED: {TARGET}")
print()
print("Test:")
print('  python -c "from app.intelligence.real.derivatives_engine import get_derivatives_engine; d = get_derivatives_engine().analyze(\\"BTC/USDT\\"); print(\\"basis:\\", d.basis_pct, d.basis_state); print(\\"OI:\\", d.open_interest); print(\\"funding:\\", d.funding_rate); print(\\"L/S:\\", d.ls_ratio_retail); print(\\"direction:\\", d.derivative_direction, d.derivative_strength); [print(\\"  -\\", r) for r in d.reasons]"')