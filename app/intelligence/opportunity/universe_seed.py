"""
ROBOMLM PLUS
Universe Seed Provider

Supplies a canonical instrument universe per market for the
Opportunity Discovery pipeline.

This module:
- Returns identity + intelligence seed records per market.
- Does NOT invent market data outside declared fields.
- Does NOT generate BUY/SELL instructions.
- Provides the UniverseEngine with a starting set of instruments.

When the backend's real intelligence engines are wired, this seed
can be reduced to identity-only, and the intelligence fields can
come from upstream providers.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def _inst(
    instrument_id: str,
    symbol: str,
    market: str,
    venue: str,
    instrument_type: str,
    **extras: Any,
) -> Dict[str, Any]:
    base: Dict[str, Any] = {
        "instrument_id": instrument_id,
        "symbol": symbol,
        "market_id": market,
        "venue_id": venue,
        "instrument_type": instrument_type,
        "status": "ACTIVE",
        "tradable": True,
        "enabled": True,
        "eligible": True,
        "liquidity_status": "PASS",
        "risk_status": "PASS",
        "timing_status": "PASS",
        "intraday_status": "PASS",
        "direction": "LONG",
        "opportunity_type": "TREND",
        "source": "universe_seed",
    }
    base["market"] = market
    base["score"] = (
        extras.get("eqe")
        or extras.get("pfs")
        or extras.get("mci")
    )
    base.update(extras)
    return base


# ---------------------------------------------------------------------------
# STATIC REFERENCE PRICES
# Display fallback until real providers (MASSIVE etc.) are wired.
# These are illustrative reference values, not live quotes.
# ---------------------------------------------------------------------------

_STATIC_REFERENCE_PRICES: Dict[str, Dict[str, float]] = {
    # EQUITY
    "AAPL": {"price": 178.42, "change_pct": 0.55},
    "MSFT": {"price": 415.20, "change_pct": 0.32},
    "TSLA": {"price": 245.80, "change_pct": 1.24},
    "RELIANCE": {"price": 2450.30, "change_pct": 1.18},
    "HDFC": {"price": 1620.55, "change_pct": 0.84},
    "TCS": {"price": 3890.10, "change_pct": -0.31},
    "INFY": {"price": 1520.45, "change_pct": 0.42},
    "ICICIBANK": {"price": 1085.70, "change_pct": 0.95},
    "SBIN": {"price": 785.30, "change_pct": 1.35},
    "WIPRO": {"price": 495.60, "change_pct": -0.22},

    # INDEX
    "SPX": {"price": 5180.20, "change_pct": 0.34},
    "NDX": {"price": 18250.50, "change_pct": 0.48},
    "DJI": {"price": 39200.80, "change_pct": 0.12},
    "NIFTY": {"price": 24250.60, "change_pct": 0.28},
    "BANKNIFTY": {"price": 51580.15, "change_pct": 0.42},
    "SENSEX": {"price": 79540.80, "change_pct": 0.24},

    # FOREX
    "EUR/USD": {"price": 1.0842, "change_pct": -0.12},
    "GBP/USD": {"price": 1.2655, "change_pct": 0.08},
    "USD/JPY": {"price": 149.85, "change_pct": 0.22},
    "AUD/USD": {"price": 0.6585, "change_pct": -0.18},
    "USD/CAD": {"price": 1.3620, "change_pct": 0.10},
    "USD/CHF": {"price": 0.8845, "change_pct": 0.14},
    "NZD/USD": {"price": 0.6020, "change_pct": -0.08},
    "EUR/GBP": {"price": 0.8568, "change_pct": 0.04},

    # FUTURES
    "ES": {"price": 5180.50, "change_pct": 0.34},
    "NQ": {"price": 18260.75, "change_pct": 0.48},
    "YM": {"price": 39210.25, "change_pct": 0.12},
    "CL": {"price": 68.45, "change_pct": 0.62},
    "GC": {"price": 2680.40, "change_pct": 0.19},
    "SI": {"price": 31.25, "change_pct": -0.45},

    # COMMODITY
    "GC.COMM": {"price": 2680.40, "change_pct": 0.19},
    "SI.COMM": {"price": 31.25, "change_pct": -0.45},
    "CL.COMM": {"price": 68.45, "change_pct": 0.62},
    "NG.COMM": {"price": 2.845, "change_pct": 1.15},
    "HG.COMM": {"price": 4.125, "change_pct": -0.32},

    # OPTIONS
    "BTC-31DEC25-100000-C": {"price": 1850.00, "change_pct": 4.20},
    "BTC-31DEC25-100000-P": {"price": 485.50, "change_pct": -2.15},
    "ETH-31DEC25-4000-C": {"price": 68.50, "change_pct": 6.80},
    "ETH-31DEC25-4000-P": {"price": 22.30, "change_pct": -3.45},
    "SOL-31DEC25-200-C": {"price": 12.75, "change_pct": 8.20},
    "NIFTY-31DEC25-25000-CE": {"price": 185.40, "change_pct": 12.50},
    "NIFTY-31DEC25-25000-PE": {"price": 95.20, "change_pct": -8.30},
    "BANKNIFTY-31DEC25-50000-CE": {"price": 420.80, "change_pct": 15.20},
    "BANKNIFTY-31DEC25-50000-PE": {"price": 215.60, "change_pct": -10.45},
    "AAPL-16OCT25-250-C": {"price": 3.85, "change_pct": 5.40},
    "AAPL-16OCT25-250-P": {"price": 1.20, "change_pct": -4.80},
    "RELIANCE-30OCT25-2800-CE": {"price": 45.60, "change_pct": 8.30},
    "RELIANCE-30OCT25-2800-PE": {"price": 18.90, "change_pct": -5.20},
    "HDFC-30OCT25-1800-CE": {"price": 32.45, "change_pct": 6.80},
    "HDFC-30OCT25-1800-PE": {"price": 12.80, "change_pct": -4.10},
}


# ---------------------------------------------------------------------------
# CRYPTO (BINANCE)
# ---------------------------------------------------------------------------

CRYPTO_SEED: List[Dict[str, Any]] = [
    _inst("BTCUSDT",  "BTC/USDT",  "CRYPTO", "BINANCE", "CRYPTO",
          eqe=82.5, pfs=84.0, mci=79.0,
          mts=72.0, lqs=92.0, rds=45.0, mcs=75.0,
          trend_strength=85.0, volume_ratio=1.8, liquidity_score=92.0,
          risk_score=28.0, timing_score=74.0, derivatives_score=70.0,
          participation_score=78.0, relationship_score=68.0,
          confidence=82.0, direction="LONG", opportunity_type="TREND"),
    _inst("ETHUSDT",  "ETH/USDT",  "CRYPTO", "BINANCE", "CRYPTO",
          eqe=76.5, pfs=78.0, mci=74.0,
          mts=70.0, lqs=88.0, rds=42.0, mcs=72.0,
          trend_strength=78.0, volume_ratio=1.5, liquidity_score=88.0,
          risk_score=32.0, timing_score=70.0, derivatives_score=68.0,
          participation_score=72.0, relationship_score=64.0,
          confidence=76.0, direction="LONG", opportunity_type="MOMENTUM"),
    _inst("SOLUSDT",  "SOL/USDT",  "CRYPTO", "BINANCE", "CRYPTO",
          eqe=71.0, pfs=73.0, mci=68.0,
          mts=68.0, lqs=82.0, rds=48.0, mcs=70.0,
          trend_strength=75.0, volume_ratio=1.7, liquidity_score=82.0,
          risk_score=38.0, timing_score=68.0, derivatives_score=62.0,
          participation_score=70.0, relationship_score=60.0,
          confidence=71.0, direction="LONG", opportunity_type="BREAKOUT"),
    _inst("BNBUSDT",  "BNB/USDT",  "CRYPTO", "BINANCE", "CRYPTO",
          eqe=66.5, pfs=68.0, mci=64.0,
          mts=64.0, lqs=80.0, rds=52.0, mcs=66.0,
          trend_strength=70.0, volume_ratio=1.3, liquidity_score=80.0,
          risk_score=42.0, timing_score=64.0, derivatives_score=58.0,
          participation_score=64.0, relationship_score=56.0,
          confidence=66.0, direction="LONG", opportunity_type="DEVELOPING"),
    _inst("XRPUSDT",  "XRP/USDT",  "CRYPTO", "BINANCE", "CRYPTO",
          eqe=58.0, pfs=60.0, mci=56.0,
          mts=58.0, lqs=76.0, rds=55.0, mcs=60.0,
          trend_strength=62.0, volume_ratio=1.2, liquidity_score=76.0,
          risk_score=48.0, timing_score=58.0, derivatives_score=52.0,
          participation_score=58.0, relationship_score=52.0,
          confidence=58.0, direction="LONG", opportunity_type="DEVELOPING"),
    _inst("ADAUSDT",  "ADA/USDT",  "CRYPTO", "BINANCE", "CRYPTO",
          eqe=62.0, pfs=64.0, mci=60.0,
          mts=60.0, lqs=74.0, rds=50.0, mcs=62.0,
          trend_strength=66.0, volume_ratio=1.3, liquidity_score=74.0,
          risk_score=44.0, timing_score=62.0, derivatives_score=56.0,
          participation_score=60.0, relationship_score=54.0,
          confidence=62.0, direction="LONG", opportunity_type="DEVELOPING"),
    _inst("DOGEUSDT", "DOGE/USDT", "CRYPTO", "BINANCE", "CRYPTO",
          eqe=54.0, pfs=56.0, mci=52.0,
          mts=54.0, lqs=70.0, rds=58.0, mcs=56.0,
          trend_strength=58.0, volume_ratio=1.4, liquidity_score=70.0,
          risk_score=52.0, timing_score=54.0, derivatives_score=50.0,
          participation_score=54.0, relationship_score=48.0,
          confidence=54.0, direction="NEUTRAL", opportunity_type="WATCHLIST"),
    _inst("MATICUSDT","MATIC/USDT","CRYPTO", "BINANCE", "CRYPTO",
          eqe=60.0, pfs=62.0, mci=58.0,
          mts=58.0, lqs=72.0, rds=52.0, mcs=60.0,
          trend_strength=64.0, volume_ratio=1.2, liquidity_score=72.0,
          risk_score=46.0, timing_score=60.0, derivatives_score=54.0,
          participation_score=58.0, relationship_score=52.0,
          confidence=60.0, direction="LONG", opportunity_type="DEVELOPING"),
    _inst("DOTUSDT",  "DOT/USDT",  "CRYPTO", "BINANCE", "CRYPTO",
          eqe=64.0, pfs=66.0, mci=62.0,
          mts=62.0, lqs=74.0, rds=50.0, mcs=62.0,
          trend_strength=68.0, volume_ratio=1.3, liquidity_score=74.0,
          risk_score=44.0, timing_score=62.0, derivatives_score=58.0,
          participation_score=60.0, relationship_score=54.0,
          confidence=64.0, direction="LONG", opportunity_type="DEVELOPING"),
    _inst("LINKUSDT", "LINK/USDT", "CRYPTO", "BINANCE", "CRYPTO",
          eqe=68.0, pfs=70.0, mci=66.0,
          mts=66.0, lqs=78.0, rds=48.0, mcs=66.0,
          trend_strength=72.0, volume_ratio=1.4, liquidity_score=78.0,
          risk_score=40.0, timing_score=66.0, derivatives_score=60.0,
          participation_score=64.0, relationship_score=58.0,
          confidence=68.0, direction="LONG", opportunity_type="MOMENTUM"),
]


# ---------------------------------------------------------------------------
# EQUITY (MASSIVE)
# ---------------------------------------------------------------------------

EQUITY_SEED: List[Dict[str, Any]] = [
    _inst("AAPL",     "AAPL",     "EQUITY", "MASSIVE", "EQUITY",
          eqe=74.0, pfs=76.0, mci=72.0,
          mts=70.0, lqs=94.0, rds=35.0, mcs=74.0,
          trend_strength=76.0, volume_ratio=1.2, liquidity_score=94.0,
          risk_score=32.0, timing_score=72.0,
          confidence=74.0, direction="LONG", opportunity_type="TREND"),
    _inst("MSFT",     "MSFT",     "EQUITY", "MASSIVE", "EQUITY",
          eqe=78.0, pfs=80.0, mci=76.0,
          mts=74.0, lqs=95.0, rds=32.0, mcs=78.0,
          trend_strength=80.0, volume_ratio=1.3, liquidity_score=95.0,
          risk_score=28.0, timing_score=76.0,
          confidence=78.0, direction="LONG", opportunity_type="TREND"),
    _inst("TSLA",     "TSLA",     "EQUITY", "MASSIVE", "EQUITY",
          eqe=66.0, pfs=68.0, mci=64.0,
          mts=62.0, lqs=88.0, rds=45.0, mcs=66.0,
          trend_strength=70.0, volume_ratio=1.6, liquidity_score=88.0,
          risk_score=48.0, timing_score=62.0,
          confidence=66.0, direction="LONG", opportunity_type="BREAKOUT"),
    _inst("RELIANCE", "RELIANCE", "EQUITY", "MASSIVE", "EQUITY",
          eqe=82.0, pfs=84.0, mci=80.0,
          mts=76.0, lqs=90.0, rds=30.0, mcs=80.0,
          trend_strength=84.0, volume_ratio=1.5, liquidity_score=90.0,
          risk_score=30.0, timing_score=78.0,
          confidence=82.0, direction="LONG", opportunity_type="TREND"),
    _inst("HDFC",     "HDFC",     "EQUITY", "MASSIVE", "EQUITY",
          eqe=79.0, pfs=81.0, mci=77.0,
          mts=74.0, lqs=89.0, rds=32.0, mcs=78.0,
          trend_strength=80.0, volume_ratio=1.4, liquidity_score=89.0,
          risk_score=32.0, timing_score=74.0,
          confidence=79.0, direction="LONG", opportunity_type="TREND"),
    _inst("TCS",      "TCS",      "EQUITY", "MASSIVE", "EQUITY",
          eqe=72.0, pfs=74.0, mci=70.0,
          mts=68.0, lqs=88.0, rds=36.0, mcs=72.0,
          trend_strength=74.0, volume_ratio=1.2, liquidity_score=88.0,
          risk_score=34.0, timing_score=70.0,
          confidence=72.0, direction="LONG", opportunity_type="MOMENTUM"),
    _inst("INFY",     "INFY",     "EQUITY", "MASSIVE", "EQUITY",
          eqe=70.0, pfs=72.0, mci=68.0,
          mts=66.0, lqs=86.0, rds=38.0, mcs=70.0,
          trend_strength=72.0, volume_ratio=1.2, liquidity_score=86.0,
          risk_score=36.0, timing_score=68.0,
          confidence=70.0, direction="LONG", opportunity_type="MOMENTUM"),
    _inst("ICICIBANK","ICICIBANK","EQUITY", "MASSIVE", "EQUITY",
          eqe=75.0, pfs=77.0, mci=73.0,
          mts=71.0, lqs=89.0, rds=34.0, mcs=74.0,
          trend_strength=76.0, volume_ratio=1.3, liquidity_score=89.0,
          risk_score=32.0, timing_score=72.0,
          confidence=75.0, direction="LONG", opportunity_type="TREND"),
    _inst("SBIN",     "SBIN",     "EQUITY", "MASSIVE", "EQUITY",
          eqe=73.0, pfs=75.0, mci=71.0,
          mts=70.0, lqs=88.0, rds=35.0, mcs=72.0,
          trend_strength=74.0, volume_ratio=1.3, liquidity_score=88.0,
          risk_score=34.0, timing_score=70.0,
          confidence=73.0, direction="LONG", opportunity_type="TREND"),
    _inst("WIPRO",    "WIPRO",    "EQUITY", "MASSIVE", "EQUITY",
          eqe=64.0, pfs=66.0, mci=62.0,
          mts=62.0, lqs=82.0, rds=42.0, mcs=64.0,
          trend_strength=66.0, volume_ratio=1.2, liquidity_score=82.0,
          risk_score=42.0, timing_score=62.0,
          confidence=64.0, direction="LONG", opportunity_type="DEVELOPING"),
]


# ---------------------------------------------------------------------------
# INDEX
# ---------------------------------------------------------------------------

INDEX_SEED: List[Dict[str, Any]] = [
    _inst("SPX",       "SPX",       "INDEX", "MASSIVE", "INDEX",
          eqe=72.0, pfs=74.0, mci=70.0, mts=68.0, lqs=98.0,
          trend_strength=74.0, volume_ratio=1.1, risk_score=30.0,
          timing_score=70.0, confidence=72.0,
          direction="LONG", opportunity_type="TREND"),
    _inst("NDX",       "NDX",       "INDEX", "MASSIVE", "INDEX",
          eqe=75.0, pfs=77.0, mci=73.0, mts=70.0, lqs=97.0,
          trend_strength=76.0, volume_ratio=1.2, risk_score=32.0,
          timing_score=72.0, confidence=75.0,
          direction="LONG", opportunity_type="TREND"),
    _inst("DJI",       "DJI",       "INDEX", "MASSIVE", "INDEX",
          eqe=68.0, pfs=70.0, mci=66.0, mts=64.0, lqs=96.0,
          trend_strength=70.0, volume_ratio=1.1, risk_score=34.0,
          timing_score=66.0, confidence=68.0,
          direction="LONG", opportunity_type="MOMENTUM"),
    _inst("NIFTY",     "NIFTY",     "INDEX", "MASSIVE", "INDEX",
          eqe=74.0, pfs=76.0, mci=72.0, mts=70.0, lqs=96.0,
          trend_strength=76.0, volume_ratio=1.2, risk_score=32.0,
          timing_score=72.0, confidence=74.0,
          direction="LONG", opportunity_type="TREND"),
    _inst("BANKNIFTY", "BANKNIFTY", "INDEX", "MASSIVE", "INDEX",
          eqe=70.0, pfs=72.0, mci=68.0, mts=66.0, lqs=94.0,
          trend_strength=72.0, volume_ratio=1.2, risk_score=36.0,
          timing_score=68.0, confidence=70.0,
          direction="LONG", opportunity_type="MOMENTUM"),
    _inst("SENSEX",    "SENSEX",    "INDEX", "MASSIVE", "INDEX",
          eqe=71.0, pfs=73.0, mci=69.0, mts=67.0, lqs=95.0,
          trend_strength=73.0, volume_ratio=1.1, risk_score=34.0,
          timing_score=69.0, confidence=71.0,
          direction="LONG", opportunity_type="TREND"),
]


# ---------------------------------------------------------------------------
# FOREX
# ---------------------------------------------------------------------------

FOREX_SEED: List[Dict[str, Any]] = [
    _inst("EURUSD", "EUR/USD", "FOREX", "MASSIVE", "FOREX",
          eqe=64.0, pfs=66.0, mci=62.0, mts=60.0, lqs=94.0,
          trend_strength=66.0, volume_ratio=1.1, risk_score=38.0,
          timing_score=62.0, confidence=64.0,
          direction="LONG", opportunity_type="TREND"),
    _inst("GBPUSD", "GBP/USD", "FOREX", "MASSIVE", "FOREX",
          eqe=60.0, pfs=62.0, mci=58.0, mts=58.0, lqs=92.0,
          trend_strength=62.0, volume_ratio=1.1, risk_score=42.0,
          timing_score=58.0, confidence=60.0,
          direction="LONG", opportunity_type="DEVELOPING"),
    _inst("USDJPY", "USD/JPY", "FOREX", "MASSIVE", "FOREX",
          eqe=62.0, pfs=64.0, mci=60.0, mts=60.0, lqs=93.0,
          trend_strength=64.0, volume_ratio=1.1, risk_score=40.0,
          timing_score=60.0, confidence=62.0,
          direction="LONG", opportunity_type="DEVELOPING"),
    _inst("AUDUSD", "AUD/USD", "FOREX", "MASSIVE", "FOREX",
          eqe=56.0, pfs=58.0, mci=54.0, mts=54.0, lqs=90.0,
          trend_strength=58.0, volume_ratio=1.0, risk_score=46.0,
          timing_score=54.0, confidence=56.0,
          direction="NEUTRAL", opportunity_type="WATCHLIST"),
    _inst("USDCAD", "USD/CAD", "FOREX", "MASSIVE", "FOREX",
          eqe=58.0, pfs=60.0, mci=56.0, mts=56.0, lqs=91.0,
          trend_strength=60.0, volume_ratio=1.0, risk_score=44.0,
          timing_score=56.0, confidence=58.0,
          direction="LONG", opportunity_type="DEVELOPING"),
    _inst("USDCHF", "USD/CHF", "FOREX", "MASSIVE", "FOREX",
          eqe=54.0, pfs=56.0, mci=52.0, mts=52.0, lqs=88.0,
          trend_strength=56.0, volume_ratio=1.0, risk_score=48.0,
          timing_score=52.0, confidence=54.0,
          direction="NEUTRAL", opportunity_type="WATCHLIST"),
    _inst("NZDUSD", "NZD/USD", "FOREX", "MASSIVE", "FOREX",
          eqe=52.0, pfs=54.0, mci=50.0, mts=50.0, lqs=87.0,
          trend_strength=54.0, volume_ratio=1.0, risk_score=50.0,
          timing_score=50.0, confidence=52.0,
          direction="NEUTRAL", opportunity_type="WATCHLIST"),
    _inst("EURGBP", "EUR/GBP", "FOREX", "MASSIVE", "FOREX",
          eqe=50.0, pfs=52.0, mci=48.0, mts=48.0, lqs=86.0,
          trend_strength=52.0, volume_ratio=1.0, risk_score=52.0,
          timing_score=48.0, confidence=50.0,
          direction="NEUTRAL", opportunity_type="WATCHLIST"),
]


# ---------------------------------------------------------------------------
# FUTURES
# ---------------------------------------------------------------------------

FUTURES_SEED: List[Dict[str, Any]] = [
    _inst("ES",  "ES",  "FUTURES", "MASSIVE", "FUTURE",
          eqe=72.0, pfs=74.0, mci=70.0, mts=68.0, lqs=96.0,
          trend_strength=74.0, volume_ratio=1.2, risk_score=32.0,
          timing_score=70.0, confidence=72.0,
          direction="LONG", opportunity_type="TREND"),
    _inst("NQ",  "NQ",  "FUTURES", "MASSIVE", "FUTURE",
          eqe=76.0, pfs=78.0, mci=74.0, mts=72.0, lqs=95.0,
          trend_strength=78.0, volume_ratio=1.3, risk_score=34.0,
          timing_score=74.0, confidence=76.0,
          direction="LONG", opportunity_type="TREND"),
    _inst("YM",  "YM",  "FUTURES", "MASSIVE", "FUTURE",
          eqe=66.0, pfs=68.0, mci=64.0, mts=62.0, lqs=92.0,
          trend_strength=68.0, volume_ratio=1.1, risk_score=36.0,
          timing_score=64.0, confidence=66.0,
          direction="LONG", opportunity_type="MOMENTUM"),
    _inst("CL",  "CL",  "FUTURES", "MASSIVE", "FUTURE",
          eqe=60.0, pfs=62.0, mci=58.0, mts=56.0, lqs=90.0,
          trend_strength=62.0, volume_ratio=1.2, risk_score=48.0,
          timing_score=58.0, confidence=60.0,
          direction="LONG", opportunity_type="DEVELOPING"),
    _inst("GC",  "GC",  "FUTURES", "MASSIVE", "FUTURE",
          eqe=68.0, pfs=70.0, mci=66.0, mts=64.0, lqs=94.0,
          trend_strength=70.0, volume_ratio=1.2, risk_score=38.0,
          timing_score=66.0, confidence=68.0,
          direction="LONG", opportunity_type="TREND"),
    _inst("SI",  "SI",  "FUTURES", "MASSIVE", "FUTURE",
          eqe=58.0, pfs=60.0, mci=56.0, mts=54.0, lqs=88.0,
          trend_strength=60.0, volume_ratio=1.1, risk_score=46.0,
          timing_score=56.0, confidence=58.0,
          direction="LONG", opportunity_type="DEVELOPING"),
]


# ---------------------------------------------------------------------------
# COMMODITY
# ---------------------------------------------------------------------------

COMMODITY_SEED: List[Dict[str, Any]] = [
    _inst("GC.COMM", "GC",  "COMMODITY", "MASSIVE", "COMMODITY",
          eqe=68.0, pfs=70.0, mci=66.0, mts=64.0, lqs=94.0,
          trend_strength=70.0, volume_ratio=1.2, risk_score=38.0,
          timing_score=66.0, confidence=68.0,
          direction="LONG", opportunity_type="TREND"),
    _inst("SI.COMM", "SI",  "COMMODITY", "MASSIVE", "COMMODITY",
          eqe=58.0, pfs=60.0, mci=56.0, mts=54.0, lqs=88.0,
          trend_strength=60.0, volume_ratio=1.1, risk_score=48.0,
          timing_score=56.0, confidence=58.0,
          direction="LONG", opportunity_type="DEVELOPING"),
    _inst("CL.COMM", "CL",  "COMMODITY", "MASSIVE", "COMMODITY",
          eqe=62.0, pfs=64.0, mci=60.0, mts=58.0, lqs=91.0,
          trend_strength=64.0, volume_ratio=1.2, risk_score=46.0,
          timing_score=60.0, confidence=62.0,
          direction="LONG", opportunity_type="DEVELOPING"),
    _inst("NG.COMM", "NG",  "COMMODITY", "MASSIVE", "COMMODITY",
          eqe=56.0, pfs=58.0, mci=54.0, mts=52.0, lqs=86.0,
          trend_strength=58.0, volume_ratio=1.1, risk_score=52.0,
          timing_score=54.0, confidence=56.0,
          direction="NEUTRAL", opportunity_type="WATCHLIST"),
    _inst("HG.COMM", "HG",  "COMMODITY", "MASSIVE", "COMMODITY",
          eqe=60.0, pfs=62.0, mci=58.0, mts=56.0, lqs=88.0,
          trend_strength=62.0, volume_ratio=1.1, risk_score=44.0,
          timing_score=58.0, confidence=60.0,
          direction="LONG", opportunity_type="DEVELOPING"),
]


# ---------------------------------------------------------------------------
# OPTIONS (crypto + index + equity)
# ---------------------------------------------------------------------------

OPTIONS_SEED: List[Dict[str, Any]] = [
    _inst("BTC-31DEC25-100000-C", "BTC-31DEC25-100000-C", "OPTIONS", "BINANCE", "OPTION_CE",
          eqe=78.0, pfs=80.0, mci=76.0, mts=72.0, lqs=88.0,
          trend_strength=82.0, volume_ratio=1.5, liquidity_score=88.0,
          risk_score=42.0, timing_score=74.0, derivatives_score=86.0,
          confidence=78.0, direction="LONG", opportunity_type="BREAKOUT",
          option_type="CE", strike=100000.0, expiry="2025-12-31",
          underlying_symbol="BTC/USDT"),
    _inst("BTC-31DEC25-100000-P", "BTC-31DEC25-100000-P", "OPTIONS", "BINANCE", "OPTION_PE",
          eqe=62.0, pfs=64.0, mci=60.0, mts=58.0, lqs=85.0,
          trend_strength=62.0, volume_ratio=1.3, liquidity_score=85.0,
          risk_score=48.0, timing_score=58.0, derivatives_score=70.0,
          confidence=62.0, direction="SHORT", opportunity_type="REVERSAL",
          option_type="PE", strike=100000.0, expiry="2025-12-31",
          underlying_symbol="BTC/USDT"),
    _inst("ETH-31DEC25-4000-C", "ETH-31DEC25-4000-C", "OPTIONS", "BINANCE", "OPTION_CE",
          eqe=72.0, pfs=74.0, mci=70.0, mts=68.0, lqs=86.0,
          trend_strength=76.0, volume_ratio=1.4, liquidity_score=86.0,
          risk_score=44.0, timing_score=70.0, derivatives_score=82.0,
          confidence=72.0, direction="LONG", opportunity_type="BREAKOUT",
          option_type="CE", strike=4000.0, expiry="2025-12-31",
          underlying_symbol="ETH/USDT"),
    _inst("ETH-31DEC25-4000-P", "ETH-31DEC25-4000-P", "OPTIONS", "BINANCE", "OPTION_PE",
          eqe=58.0, pfs=60.0, mci=56.0, mts=54.0, lqs=82.0,
          trend_strength=58.0, volume_ratio=1.2, liquidity_score=82.0,
          risk_score=50.0, timing_score=54.0, derivatives_score=66.0,
          confidence=58.0, direction="SHORT", opportunity_type="REVERSAL",
          option_type="PE", strike=4000.0, expiry="2025-12-31",
          underlying_symbol="ETH/USDT"),
    _inst("SOL-31DEC25-200-C", "SOL-31DEC25-200-C", "OPTIONS", "BINANCE", "OPTION_CE",
          eqe=68.0, pfs=70.0, mci=66.0, mts=64.0, lqs=80.0,
          trend_strength=72.0, volume_ratio=1.6, liquidity_score=80.0,
          risk_score=46.0, timing_score=66.0, derivatives_score=76.0,
          confidence=68.0, direction="LONG", opportunity_type="BREAKOUT",
          option_type="CE", strike=200.0, expiry="2025-12-31",
          underlying_symbol="SOL/USDT"),
    _inst("NIFTY-31DEC25-25000-CE", "NIFTY-31DEC25-25000-CE", "OPTIONS", "MASSIVE", "OPTION_CE",
          eqe=80.0, pfs=82.0, mci=78.0, mts=74.0, lqs=94.0,
          trend_strength=84.0, volume_ratio=1.5, liquidity_score=94.0,
          risk_score=32.0, timing_score=76.0, derivatives_score=88.0,
          confidence=80.0, direction="LONG", opportunity_type="BREAKOUT",
          option_type="CE", strike=25000.0, expiry="2025-12-31",
          underlying_symbol="NIFTY"),
    _inst("NIFTY-31DEC25-25000-PE", "NIFTY-31DEC25-25000-PE", "OPTIONS", "MASSIVE", "OPTION_PE",
          eqe=60.0, pfs=62.0, mci=58.0, mts=56.0, lqs=92.0,
          trend_strength=60.0, volume_ratio=1.2, liquidity_score=92.0,
          risk_score=48.0, timing_score=56.0, derivatives_score=72.0,
          confidence=60.0, direction="SHORT", opportunity_type="REVERSAL",
          option_type="PE", strike=25000.0, expiry="2025-12-31",
          underlying_symbol="NIFTY"),
    _inst("BANKNIFTY-31DEC25-50000-CE", "BANKNIFTY-31DEC25-50000-CE", "OPTIONS", "MASSIVE", "OPTION_CE",
          eqe=76.0, pfs=78.0, mci=74.0, mts=70.0, lqs=93.0,
          trend_strength=80.0, volume_ratio=1.4, liquidity_score=93.0,
          risk_score=34.0, timing_score=72.0, derivatives_score=84.0,
          confidence=76.0, direction="LONG", opportunity_type="BREAKOUT",
          option_type="CE", strike=50000.0, expiry="2025-12-31",
          underlying_symbol="BANKNIFTY"),
    _inst("BANKNIFTY-31DEC25-50000-PE", "BANKNIFTY-31DEC25-50000-PE", "OPTIONS", "MASSIVE", "OPTION_PE",
          eqe=56.0, pfs=58.0, mci=54.0, mts=52.0, lqs=90.0,
          trend_strength=56.0, volume_ratio=1.2, liquidity_score=90.0,
          risk_score=50.0, timing_score=52.0, derivatives_score=68.0,
          confidence=56.0, direction="NEUTRAL", opportunity_type="WATCHLIST",
          option_type="PE", strike=50000.0, expiry="2025-12-31",
          underlying_symbol="BANKNIFTY"),
    _inst("AAPL-16OCT25-250-C", "AAPL-16OCT25-250-C", "OPTIONS", "MASSIVE", "OPTION_CE",
          eqe=74.0, pfs=76.0, mci=72.0, mts=68.0, lqs=92.0,
          trend_strength=78.0, volume_ratio=1.3, liquidity_score=92.0,
          risk_score=34.0, timing_score=70.0, derivatives_score=80.0,
          confidence=74.0, direction="LONG", opportunity_type="BREAKOUT",
          option_type="CE", strike=250.0, expiry="2025-10-16",
          underlying_symbol="AAPL"),
    _inst("AAPL-16OCT25-250-P", "AAPL-16OCT25-250-P", "OPTIONS", "MASSIVE", "OPTION_PE",
          eqe=54.0, pfs=56.0, mci=52.0, mts=50.0, lqs=88.0,
          trend_strength=54.0, volume_ratio=1.1, liquidity_score=88.0,
          risk_score=52.0, timing_score=50.0, derivatives_score=64.0,
          confidence=54.0, direction="NEUTRAL", opportunity_type="WATCHLIST",
          option_type="PE", strike=250.0, expiry="2025-10-16",
          underlying_symbol="AAPL"),
    _inst("RELIANCE-30OCT25-2800-CE", "RELIANCE-30OCT25-2800-CE", "OPTIONS", "MASSIVE", "OPTION_CE",
          eqe=78.0, pfs=80.0, mci=76.0, mts=72.0, lqs=90.0,
          trend_strength=82.0, volume_ratio=1.4, liquidity_score=90.0,
          risk_score=32.0, timing_score=74.0, derivatives_score=84.0,
          confidence=78.0, direction="LONG", opportunity_type="BREAKOUT",
          option_type="CE", strike=2800.0, expiry="2025-10-30",
          underlying_symbol="RELIANCE"),
    _inst("RELIANCE-30OCT25-2800-PE", "RELIANCE-30OCT25-2800-PE", "OPTIONS", "MASSIVE", "OPTION_PE",
          eqe=58.0, pfs=60.0, mci=56.0, mts=54.0, lqs=86.0,
          trend_strength=58.0, volume_ratio=1.2, liquidity_score=86.0,
          risk_score=48.0, timing_score=54.0, derivatives_score=68.0,
          confidence=58.0, direction="SHORT", opportunity_type="REVERSAL",
          option_type="PE", strike=2800.0, expiry="2025-10-30",
          underlying_symbol="RELIANCE"),
    _inst("HDFC-30OCT25-1800-CE", "HDFC-30OCT25-1800-CE", "OPTIONS", "MASSIVE", "OPTION_CE",
          eqe=72.0, pfs=74.0, mci=70.0, mts=68.0, lqs=89.0,
          trend_strength=76.0, volume_ratio=1.3, liquidity_score=89.0,
          risk_score=34.0, timing_score=70.0, derivatives_score=80.0,
          confidence=72.0, direction="LONG", opportunity_type="BREAKOUT",
          option_type="CE", strike=1800.0, expiry="2025-10-30",
          underlying_symbol="HDFC"),
    _inst("HDFC-30OCT25-1800-PE", "HDFC-30OCT25-1800-PE", "OPTIONS", "MASSIVE", "OPTION_PE",
          eqe=56.0, pfs=58.0, mci=54.0, mts=52.0, lqs=86.0,
          trend_strength=56.0, volume_ratio=1.1, liquidity_score=86.0,
          risk_score=50.0, timing_score=52.0, derivatives_score=66.0,
          confidence=56.0, direction="NEUTRAL", opportunity_type="WATCHLIST",
          option_type="PE", strike=1800.0, expiry="2025-10-30",
          underlying_symbol="HDFC"),
]


# ---------------------------------------------------------------------------
# REGISTRY
# ---------------------------------------------------------------------------

_SEED_BY_MARKET: Dict[str, List[Dict[str, Any]]] = {
    "CRYPTO":    CRYPTO_SEED,
    "EQUITY":    EQUITY_SEED,
    "INDEX":     INDEX_SEED,
    "FOREX":     FOREX_SEED,
    "FUTURES":   FUTURES_SEED,
    "COMMODITY": COMMODITY_SEED,
    "OPTIONS":   OPTIONS_SEED,
}


def get_universe_seed(
    market: Optional[str] = None,
    venue: Optional[str] = None,
    timeframe: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Real universe — computed from live market data via unified_signal.

    Falls back to static seed if real bridge unavailable or fails.
    """
    if market is None or str(market).strip() == "":
        normalized = "CRYPTO"
    else:
        normalized = str(market).strip().upper()

    # Try real bridge first
    if normalized in {"CRYPTO", "EQUITY", "INDEX", "FOREX"}:
        try:
            from app.intelligence.real.real_discovery_bridge import (
                get_real_crypto_opportunities,
            )
            real = get_real_crypto_opportunities(normalized, limit=15)
            if real:
                return real
        except Exception as _e:
            # Fall through to static seed
            pass

    # Fallback — static seed
    if normalized == "ALL":
        combined: List[Dict[str, Any]] = []
        for items in _SEED_BY_MARKET.values():
            combined.extend(dict(item) for item in items)
        return combined

    items = _SEED_BY_MARKET.get(normalized, CRYPTO_SEED)

    result: List[Dict[str, Any]] = []
    for item in items:
        copy_item = dict(item)
        symbol = copy_item.get("symbol", "")

        if "price" not in copy_item:
            static = _STATIC_REFERENCE_PRICES.get(symbol)
            if static:
                copy_item["price"] = static["price"]
                copy_item["change_pct"] = static["change_pct"]

        result.append(copy_item)

    return result


__all__ = [
    "CRYPTO_SEED",
    "EQUITY_SEED",
    "INDEX_SEED",
    "FOREX_SEED",
    "FUTURES_SEED",
    "COMMODITY_SEED",
    "OPTIONS_SEED",
    "get_universe_seed",
]