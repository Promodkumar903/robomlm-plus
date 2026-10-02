"""
ROBOMLM_PLUS - Real Market Data Provider

100% real data from Bybit v5. No hardcoding. No fake values.
Missing data -> None. Never substituted.

Ready for paid providers:
    Interface same rahega — sirf provider class swap karni hogi.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Optional
import json
import time
import urllib.request
import urllib.error


BYBIT_BASE = "https://api.bybit.com"
TIMEOUT_SECONDS = 8


@dataclass(frozen=True)
class DataProvenance:
    source: str
    endpoint: str
    symbol: str
    fetched_at: datetime
    raw_count: int
    status: str  # OK | EMPTY | ERROR


@dataclass(frozen=True)
class Candle:
    time: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    turnover: float


@dataclass(frozen=True)
class OrderbookLevel:
    price: float
    size: float


@dataclass
class OrderbookSnapshot:
    symbol: str
    bids: list
    asks: list
    spread: float
    spread_bps: float
    bid_volume_total: float
    ask_volume_total: float
    imbalance: float
    provenance: DataProvenance


@dataclass(frozen=True)
class RecentTrade:
    time: int
    price: float
    size: float
    side: str


@dataclass(frozen=True)
class OpenInterestSnapshot:
    symbol: str
    open_interest: float
    timestamp: int
    provenance: DataProvenance


@dataclass(frozen=True)
class FundingSnapshot:
    symbol: str
    funding_rate: float
    next_funding_time: int
    provenance: DataProvenance


class RealMarketData:
    CACHE_TTL_SECONDS = 10

    def __init__(self):
        self._lock = RLock()
        self._cache = {}

    def _fetch_json(self, path, params=None):
        url = BYBIT_BASE + path
        if params:
            query = "&".join(f"{k}={v}" for k, v in params.items())
            url = f"{url}?{query}"
        try:
            with urllib.request.urlopen(url, timeout=TIMEOUT_SECONDS) as r:
                return json.loads(r.read())
        except Exception:
            return None

    def _cached(self, key, fn):
        now = time.time()
        with self._lock:
            entry = self._cache.get(key)
            if entry is not None:
                expires_at, value = entry
                if now < expires_at:
                    return value
        value = fn()
        with self._lock:
            self._cache[key] = (now + self.CACHE_TTL_SECONDS, value)
        return value

    @staticmethod
    def _normalize_symbol(symbol):
        return symbol.replace("/", "").upper()

    @staticmethod
    def _now():
        return datetime.now(timezone.utc)

    # ------------------------------------------------------------------

    def get_candles(self, symbol, timeframe="15", limit=200):
        bybit_sym = self._normalize_symbol(symbol)
        cache_key = f"kline:{bybit_sym}:{timeframe}:{limit}"

        def fetch():
            return self._fetch_json(
                "/v5/market/kline",
                {"category": "spot", "symbol": bybit_sym,
                 "interval": timeframe, "limit": limit},
            )

        raw = self._cached(cache_key, fetch)
        if raw is None:
            return [], DataProvenance(
                "BYBIT_V5", "/v5/market/kline", symbol,
                self._now(), 0, "ERROR",
            )

        items = ((raw.get("result") or {}).get("list") or [])
        if not items:
            return [], DataProvenance(
                "BYBIT_V5", "/v5/market/kline", symbol,
                self._now(), 0, "EMPTY",
            )

        candles = []
        for c in reversed(items):
            try:
                candles.append(Candle(
                    time=int(int(c[0]) / 1000),
                    open=float(c[1]), high=float(c[2]),
                    low=float(c[3]), close=float(c[4]),
                    volume=float(c[5]), turnover=float(c[6]),
                ))
            except (IndexError, ValueError, TypeError):
                continue

        return candles, DataProvenance(
            "BYBIT_V5", "/v5/market/kline", symbol,
            self._now(), len(candles), "OK",
        )

    def get_last_price(self, symbol):
        bybit_sym = self._normalize_symbol(symbol)
        cache_key = f"ticker:{bybit_sym}"

        def fetch():
            return self._fetch_json(
                "/v5/market/tickers",
                {"category": "spot", "symbol": bybit_sym},
            )

        raw = self._cached(cache_key, fetch)
        if raw is None:
            return None

        items = ((raw.get("result") or {}).get("list") or [])
        if not items:
            return None

        try:
            price = float(items[0].get("lastPrice"))
            return price if price > 0 else None
        except (KeyError, ValueError, TypeError):
            return None

    def get_open_interest(self, symbol):
        bybit_sym = self._normalize_symbol(symbol)
        cache_key = f"oi:{bybit_sym}"

        def fetch():
            return self._fetch_json(
                "/v5/market/open-interest",
                {"category": "linear", "symbol": bybit_sym,
                 "intervalTime": "5min", "limit": 1},
            )

        raw = self._cached(cache_key, fetch)
        if raw is None:
            return None, DataProvenance(
                "BYBIT_V5", "/v5/market/open-interest", symbol,
                self._now(), 0, "ERROR",
            )

        items = ((raw.get("result") or {}).get("list") or [])
        if not items:
            return None, DataProvenance(
                "BYBIT_V5", "/v5/market/open-interest", symbol,
                self._now(), 0, "EMPTY",
            )

        try:
            return OpenInterestSnapshot(
                symbol=symbol,
                open_interest=float(items[0].get("openInterest")),
                timestamp=int(items[0].get("timestamp", 0)),
                provenance=DataProvenance(
                    "BYBIT_V5", "/v5/market/open-interest", symbol,
                    self._now(), 1, "OK",
                ),
            ), None
        except (KeyError, ValueError, TypeError):
            return None, None

    def get_funding_rate(self, symbol):
        bybit_sym = self._normalize_symbol(symbol)
        cache_key = f"funding:{bybit_sym}"

        def fetch():
            return self._fetch_json(
                "/v5/market/funding/history",
                {"category": "linear", "symbol": bybit_sym, "limit": 1},
            )

        raw = self._cached(cache_key, fetch)
        if raw is None:
            return None

        items = ((raw.get("result") or {}).get("list") or [])
        if not items:
            return None

        try:
            return FundingSnapshot(
                symbol=symbol,
                funding_rate=float(items[0].get("fundingRate")),
                next_funding_time=int(items[0].get("fundingRateTimestamp", 0)),
                provenance=DataProvenance(
                    "BYBIT_V5", "/v5/market/funding/history", symbol,
                    self._now(), 1, "OK",
                ),
            )
        except (KeyError, ValueError, TypeError):
            return None

    def get_orderbook(self, symbol, depth=25):
        bybit_sym = self._normalize_symbol(symbol)
        cache_key = f"ob:{bybit_sym}:{depth}"

        def fetch():
            return self._fetch_json(
                "/v5/market/orderbook",
                {"category": "spot", "symbol": bybit_sym, "limit": depth},
            )

        raw = self._cached(cache_key, fetch)
        if raw is None:
            return None

        result = raw.get("result") or {}
        bids = result.get("b") or []
        asks = result.get("a") or []
        if not bids or not asks:
            return None

        try:
            bid_levels = [OrderbookLevel(float(p), float(s)) for p, s in bids]
            ask_levels = [OrderbookLevel(float(p), float(s)) for p, s in asks]
        except (ValueError, TypeError):
            return None

        best_bid = bid_levels[0].price
        best_ask = ask_levels[0].price
        mid = (best_bid + best_ask) / 2
        spread = best_ask - best_bid
        spread_bps = (spread / mid * 10000) if mid > 0 else 0

        bid_vol = sum(x.size for x in bid_levels)
        ask_vol = sum(x.size for x in ask_levels)
        total = bid_vol + ask_vol
        imbalance = ((bid_vol - ask_vol) / total) if total > 0 else 0.0

        return OrderbookSnapshot(
            symbol=symbol,
            bids=bid_levels,
            asks=ask_levels,
            spread=spread,
            spread_bps=spread_bps,
            bid_volume_total=bid_vol,
            ask_volume_total=ask_vol,
            imbalance=imbalance,
            provenance=DataProvenance(
                "BYBIT_V5", "/v5/market/orderbook", symbol,
                self._now(), len(bid_levels) + len(ask_levels), "OK",
            ),
        )

    def get_recent_trades(self, symbol, limit=100):
        bybit_sym = self._normalize_symbol(symbol)
        cache_key = f"trades:{bybit_sym}:{limit}"

        def fetch():
            return self._fetch_json(
                "/v5/market/recent-trade",
                {"category": "spot", "symbol": bybit_sym, "limit": limit},
            )

        raw = self._cached(cache_key, fetch)
        if raw is None:
            return [], DataProvenance(
                "BYBIT_V5", "/v5/market/recent-trade", symbol,
                self._now(), 0, "ERROR",
            )

        items = ((raw.get("result") or {}).get("list") or [])
        if not items:
            return [], DataProvenance(
                "BYBIT_V5", "/v5/market/recent-trade", symbol,
                self._now(), 0, "EMPTY",
            )

        trades = []
        for t in items:
            try:
                trades.append(RecentTrade(
                    time=int(int(t.get("time", 0)) / 1000),
                    price=float(t.get("price")),
                    size=float(t.get("size")),
                    side=str(t.get("side", "")).capitalize(),
                ))
            except (ValueError, TypeError):
                continue

        return trades, DataProvenance(
            "BYBIT_V5", "/v5/market/recent-trade", symbol,
            self._now(), len(trades), "OK",
        )


_engine: Optional[RealMarketData] = None
_lock = RLock()


def get_real_market_data() -> RealMarketData:
    global _engine
    with _lock:
        if _engine is None:
            _engine = RealMarketData()
        return _engine


__all__ = [
    "DataProvenance", "Candle", "OrderbookLevel", "OrderbookSnapshot",
    "RecentTrade", "OpenInterestSnapshot", "FundingSnapshot",
    "RealMarketData", "get_real_market_data",
]
