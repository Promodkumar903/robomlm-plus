"""
ROBOMLM_PLUS
Opportunity Intelligence
Universe Engine

Purpose
-------
Build and validate the instrument universe available to the
Opportunity Discovery pipeline.

Design principles
-----------------
1. Universe discovery is NOT opportunity scoring.
2. No BUY/SELL decision is produced here.
3. No future information is allowed.
4. Market/instrument identity is preserved.
5. Downstream liquidity, risk, timing, ranking and opportunity
   engines receive normalized records.
6. Engine is dependency-light and can operate with dictionaries,
   dataclasses or compatible objects.
7. Unknown fields are preserved in metadata instead of silently
   discarded.
8. Deterministic output is preferred for reproducibility/testing.

Pipeline position
-----------------
Market Registry / Instrument Registry
                |
                v
        UniverseEngine
                |
                v
       Liquidity Filter
                |
                v
          Risk Filter
                |
                v
         Timing Engine
                |
                v
        Ranking / Scanner
                |
                v
       Opportunity Engine

Version
-------
OPPORTUNITY-UNIVERSE-1.0
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
import math
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence


ENGINE_NAME = "UniverseEngine"
ENGINE_VERSION = "OPPORTUNITY-UNIVERSE-1.0"


# ---------------------------------------------------------------------------
# ENUMS
# ---------------------------------------------------------------------------

class UniverseStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    BLOCKED = "BLOCKED"
    UNKNOWN = "UNKNOWN"


class InstrumentType(str, Enum):
    INDEX = "INDEX"
    EQUITY = "EQUITY"
    FUTURE = "FUTURE"
    OPTION = "OPTION"
    FOREX = "FOREX"
    CRYPTO = "CRYPTO"
    COMMODITY = "COMMODITY"
    ETF = "ETF"
    OTHER = "OTHER"
    UNKNOWN = "UNKNOWN"


class ValidationStatus(str, Enum):
    VALID = "VALID"
    INVALID = "INVALID"
    PARTIAL = "PARTIAL"


# ---------------------------------------------------------------------------
# DATA CONTRACTS
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class UniverseInstrument:
    """
    Normalized instrument record.

    This is intentionally an opportunity-discovery contract, not
    a trading/execution contract.
    """

    instrument_id: str
    symbol: str

    market_id: Optional[str] = None
    venue_id: Optional[str] = None

    instrument_type: str = InstrumentType.UNKNOWN.value
    asset_class: Optional[str] = None

    exchange_symbol: Optional[str] = None
    underlying_symbol: Optional[str] = None

    currency: Optional[str] = None
    expiry: Optional[str] = None
    strike: Optional[float] = None
    option_type: Optional[str] = None

    status: str = UniverseStatus.UNKNOWN.value

    tradable: bool = True
    enabled: bool = True

    # Discovery metadata
    source: Optional[str] = None
    source_timestamp: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class UniverseValidation:
    status: str
    instrument_id: Optional[str]
    reasons: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class UniverseResult:
    """
    Complete output contract.

    `instruments` contains only normalized instruments accepted by
    the universe policy.

    `rejected` preserves rejected candidates and reasons so the
    discovery pipeline remains auditable.
    """

    status: str
    as_of: str

    market_id: Optional[str]

    instruments: List[UniverseInstrument] = field(default_factory=list)

    rejected: List[Dict[str, Any]] = field(default_factory=list)

    total_input: int = 0
    total_eligible: int = 0
    total_rejected: int = 0

    validation_errors: List[str] = field(default_factory=list)

    provenance: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class UniversePolicy:
    """
    Policy controls universe eligibility.

    Important:
    These are eligibility controls, NOT opportunity thresholds.
    """

    include_inactive: bool = False
    require_enabled: bool = True
    require_tradable: bool = True

    allowed_markets: Optional[Sequence[str]] = None
    allowed_instrument_types: Optional[Sequence[str]] = None
    blocked_symbols: Sequence[str] = field(default_factory=tuple)
    blocked_instrument_ids: Sequence[str] = field(default_factory=tuple)

    deduplicate: bool = True
    preserve_order: bool = True


# ---------------------------------------------------------------------------
# ENGINE
# ---------------------------------------------------------------------------

class UniverseEngine:
    """
    Builds the normalized opportunity universe.

    The engine accepts:
        - mappings/dictionaries
        - UniverseInstrument instances
        - ordinary objects exposing compatible attributes

    It does NOT:
        - calculate opportunity scores
        - rank instruments
        - generate BUY/SELL
        - predict future prices
        - fabricate missing market data
        - use future outcomes
    """

    name = ENGINE_NAME
    version = ENGINE_VERSION

    def __init__(
        self,
        policy: Optional[UniversePolicy] = None,
    ) -> None:
        self.policy = policy or UniversePolicy()

    # -----------------------------------------------------------------------
    # PUBLIC API
    # -----------------------------------------------------------------------

    def build(
        self,
        instruments: Optional[Iterable[Any]],
        *,
        market_id: Optional[str] = None,
        as_of: Optional[Any] = None,
        source: Optional[str] = None,
    ) -> UniverseResult:
        """
        Build a validated opportunity universe.

        Parameters
        ----------
        instruments:
            Candidate instrument records.

        market_id:
            Optional market identity gate.

        as_of:
            Point-in-time timestamp. Records explicitly carrying a
            future timestamp are rejected.

        source:
            Optional source/provenance label.
        """

        effective_as_of = self._normalize_timestamp(as_of)

        candidates = list(instruments or [])

        accepted: List[UniverseInstrument] = []
        rejected: List[Dict[str, Any]] = []

        seen_ids = set()
        seen_symbols = set()

        for index, candidate in enumerate(candidates):
            normalized = self.normalize(
                candidate,
                source=source,
                default_market_id=market_id,
            )

            validation = self.validate(
                normalized,
                market_id=market_id,
                as_of=effective_as_of,
            )

            if validation.status == ValidationStatus.INVALID.value:
                rejected.append(
                    {
                        "index": index,
                        "instrument_id": normalized.instrument_id,
                        "symbol": normalized.symbol,
                        "reasons": list(validation.reasons),
                        "warnings": list(validation.warnings),
                    }
                )
                continue

            if self.policy.deduplicate:
                duplicate_key = (
                    normalized.instrument_id
                    or normalized.exchange_symbol
                    or normalized.symbol
                )

                if duplicate_key in seen_ids or normalized.symbol in seen_symbols:
                    rejected.append(
                        {
                            "index": index,
                            "instrument_id": normalized.instrument_id,
                            "symbol": normalized.symbol,
                            "reasons": ["DUPLICATE_INSTRUMENT"],
                            "warnings": [],
                        }
                    )
                    continue

                seen_ids.add(duplicate_key)
                seen_symbols.add(normalized.symbol)

            accepted.append(normalized)

        status = (
            "READY"
            if accepted
            else "EMPTY"
        )

        return UniverseResult(
            status=status,
            as_of=effective_as_of,
            market_id=market_id,
            instruments=accepted,
            rejected=rejected,
            total_input=len(candidates),
            total_eligible=len(accepted),
            total_rejected=len(rejected),
            validation_errors=[],
            provenance={
                "engine": self.name,
                "engine_version": self.version,
                "policy": self._policy_dict(),
                "market_id": market_id,
                "as_of": effective_as_of,
                "source": source,
                "future_data_used": False,
            },
        )

    def discover(
        self,
        instruments: Optional[Iterable[Any]],
        *,
        market_id: Optional[str] = None,
        as_of: Optional[Any] = None,
        source: Optional[str] = None,
    ) -> UniverseResult:
        """
        Alias for build().

        Kept because scanner/discovery layers commonly use the
        semantic operation name `discover`.
        """
        return self.build(
            instruments,
            market_id=market_id,
            as_of=as_of,
            source=source,
        )

    # -----------------------------------------------------------------------
    # NORMALIZATION
    # -----------------------------------------------------------------------

    def normalize(
        self,
        candidate: Any,
        *,
        source: Optional[str] = None,
        default_market_id: Optional[str] = None,
    ) -> UniverseInstrument:
        """
        Convert an arbitrary instrument representation into the
        normalized UniverseInstrument contract.
        """

        if isinstance(candidate, UniverseInstrument):
            if source is None and default_market_id is None:
                return candidate

            data = asdict(candidate)

            if default_market_id is not None and not data.get("market_id"):
                data["market_id"] = default_market_id

            if source is not None and not data.get("source"):
                data["source"] = source

            return UniverseInstrument(**data)

        raw = self._to_mapping(candidate)

        instrument_id = self._first(
            raw,
            "instrument_id",
            "instrumentId",
            "security_id",
            "securityId",
            "token",
            "id",
        )

        symbol = self._first(
            raw,
            "symbol",
            "ticker",
            "trading_symbol",
            "tradingSymbol",
            "exchange_symbol",
            "exchangeSymbol",
        )

        market = self._first(
            raw,
            "market_id",
            "marketId",
            "market",
            "segment",
        )

        venue = self._first(
            raw,
            "venue_id",
            "venueId",
            "exchange",
            "venue",
        )

        instrument_type = self._normalize_instrument_type(
            self._first(
                raw,
                "instrument_type",
                "instrumentType",
                "type",
                "security_type",
            )
        )

        status = self._normalize_status(
            self._first(raw, "status", "state")
        )

        tradable = self._to_bool(
            self._first(
                raw,
                "tradable",
                "tradeable",
                "is_tradable",
                "isTradable",
            ),
            default=True,
        )

        enabled = self._to_bool(
            self._first(
                raw,
                "enabled",
                "active",
                "is_active",
                "isActive",
            ),
            default=True,
        )

        strike = self._to_float(
            self._first(raw, "strike", "strike_price", "strikePrice")
        )

        metadata = dict(raw)

        # Remove canonical fields from metadata.
        canonical_keys = {
            "instrument_id",
            "instrumentId",
            "security_id",
            "securityId",
            "token",
            "id",
            "symbol",
            "ticker",
            "trading_symbol",
            "tradingSymbol",
            "exchange_symbol",
            "exchangeSymbol",
            "market_id",
            "marketId",
            "market",
            "segment",
            "venue_id",
            "venueId",
            "exchange",
            "venue",
            "instrument_type",
            "instrumentType",
            "type",
            "security_type",
            "status",
            "state",
            "tradable",
            "tradeable",
            "is_tradable",
            "isTradable",
            "enabled",
            "active",
            "is_active",
            "isActive",
            "strike",
            "strike_price",
            "strikePrice",
        }

        for key in canonical_keys:
            metadata.pop(key, None)

        return UniverseInstrument(
            instrument_id=str(instrument_id or symbol or ""),
            symbol=str(symbol or ""),
            market_id=(
                str(market)
                if market is not None
                else default_market_id
            ),
            venue_id=str(venue) if venue is not None else None,
            instrument_type=instrument_type,
            asset_class=self._optional_str(
                self._first(raw, "asset_class", "assetClass", "asset")
            ),
            exchange_symbol=self._optional_str(
                self._first(
                    raw,
                    "exchange_symbol",
                    "exchangeSymbol",
                )
            ),
            underlying_symbol=self._optional_str(
                self._first(
                    raw,
                    "underlying_symbol",
                    "underlyingSymbol",
                    "underlying",
                )
            ),
            currency=self._optional_str(
                self._first(raw, "currency", "quote_currency", "quoteCurrency")
            ),
            expiry=self._optional_str(
                self._first(raw, "expiry", "expiry_date", "expiryDate")
            ),
            strike=strike,
            option_type=self._optional_str(
                self._first(raw, "option_type", "optionType")
            ),
            status=status,
            tradable=tradable,
            enabled=enabled,
            source=(
                str(
                    self._first(
                        raw,
                        "source",
                        "data_source",
                        "dataSource",
                    )
                    or source
                )
                if (
                    self._first(
                        raw,
                        "source",
                        "data_source",
                        "dataSource",
                    )
                    or source
                )
                is not None
                else None
            ),
            source_timestamp=self._optional_str(
                self._first(
                    raw,
                    "source_timestamp",
                    "sourceTimestamp",
                    "timestamp",
                    "as_of",
                )
            ),
            metadata=metadata,
        )

    # -----------------------------------------------------------------------
    # VALIDATION
    # -----------------------------------------------------------------------

    def validate(
        self,
        instrument: UniverseInstrument,
        *,
        market_id: Optional[str] = None,
        as_of: Optional[str] = None,
    ) -> UniverseValidation:
        """
        Validate identity and universe eligibility.

        No scoring is performed here.
        """

        reasons: List[str] = []
        warnings: List[str] = []

        if not instrument.instrument_id:
            reasons.append("MISSING_INSTRUMENT_ID")

        if not instrument.symbol:
            reasons.append("MISSING_SYMBOL")

        if market_id is not None:
            if instrument.market_id is None:
                reasons.append("MISSING_MARKET_ID")
            elif str(instrument.market_id) != str(market_id):
                reasons.append("MARKET_ID_MISMATCH")

        if self.policy.require_enabled and not instrument.enabled:
            reasons.append("INSTRUMENT_DISABLED")

        if self.policy.require_tradable and not instrument.tradable:
            reasons.append("INSTRUMENT_NOT_TRADABLE")

        if not self.policy.include_inactive:
            if instrument.status in {
                UniverseStatus.INACTIVE.value,
                UniverseStatus.BLOCKED.value,
            }:
                reasons.append("INSTRUMENT_INACTIVE_OR_BLOCKED")

        if self.policy.allowed_markets:
            allowed = {
                str(item).upper()
                for item in self.policy.allowed_markets
            }

            if (
                instrument.market_id is None
                or str(instrument.market_id).upper() not in allowed
            ):
                reasons.append("MARKET_NOT_ALLOWED")

        if self.policy.allowed_instrument_types:
            allowed_types = {
                str(item).upper()
                for item in self.policy.allowed_instrument_types
            }

            if instrument.instrument_type.upper() not in allowed_types:
                reasons.append("INSTRUMENT_TYPE_NOT_ALLOWED")

        if instrument.symbol.upper() in {
            str(item).upper()
            for item in self.policy.blocked_symbols
        }:
            reasons.append("SYMBOL_BLOCKED")

        if instrument.instrument_id in set(
            str(item) for item in self.policy.blocked_instrument_ids
        ):
            reasons.append("INSTRUMENT_ID_BLOCKED")

        # Point-in-time protection.
        if as_of is not None and instrument.source_timestamp:
            candidate_ts = self._parse_timestamp(
                instrument.source_timestamp
            )
            as_of_ts = self._parse_timestamp(as_of)

            if candidate_ts is not None and as_of_ts is not None:
                if candidate_ts > as_of_ts:
                    reasons.append("FUTURE_DATA")

        # Instrument-specific sanity checks.
        if instrument.instrument_type == InstrumentType.OPTION.value:
            if instrument.option_type is not None:
                option_type = instrument.option_type.upper()
                if option_type not in {"CE", "PE", "CALL", "PUT"}:
                    warnings.append("UNKNOWN_OPTION_TYPE")

        if instrument.instrument_type == InstrumentType.OPTION.value:
            if instrument.strike is None:
                warnings.append("OPTION_STRIKE_MISSING")

        if not instrument.venue_id:
            warnings.append("VENUE_ID_MISSING")

        if not instrument.market_id:
            warnings.append("MARKET_ID_MISSING")

        if reasons:
            status = ValidationStatus.INVALID.value
        elif warnings:
            status = ValidationStatus.PARTIAL.value
        else:
            status = ValidationStatus.VALID.value

        return UniverseValidation(
            status=status,
            instrument_id=instrument.instrument_id or None,
            reasons=reasons,
            warnings=warnings,
        )

    # -----------------------------------------------------------------------
    # FILTERING HELPERS
    # -----------------------------------------------------------------------

    def filter_market(
        self,
        instruments: Iterable[UniverseInstrument],
        market_id: str,
    ) -> List[UniverseInstrument]:
        """
        Return instruments belonging to one market identity.
        """
        target = str(market_id)

        return [
            instrument
            for instrument in instruments
            if instrument.market_id is not None
            and str(instrument.market_id) == target
        ]

    def filter_type(
        self,
        instruments: Iterable[UniverseInstrument],
        instrument_type: str,
    ) -> List[UniverseInstrument]:
        """
        Return instruments matching an instrument type.
        """
        target = str(instrument_type).upper()

        return [
            instrument
            for instrument in instruments
            if instrument.instrument_type.upper() == target
        ]

    def active_only(
        self,
        instruments: Iterable[UniverseInstrument],
    ) -> List[UniverseInstrument]:
        """
        Return active/enabled/tradable instruments.
        """
        return [
            instrument
            for instrument in instruments
            if instrument.status == UniverseStatus.ACTIVE.value
            and instrument.enabled
            and instrument.tradable
        ]

    # -----------------------------------------------------------------------
    # SERIALIZATION
    # -----------------------------------------------------------------------

    @staticmethod
    def instrument_to_dict(
        instrument: UniverseInstrument,
    ) -> Dict[str, Any]:
        """
        Stable dictionary representation for downstream engines.
        """
        return asdict(instrument)

    @staticmethod
    def result_to_dict(
        result: UniverseResult,
    ) -> Dict[str, Any]:
        """
        Stable dictionary representation for logging/API/UI layers.
        """
        return {
            "status": result.status,
            "as_of": result.as_of,
            "market_id": result.market_id,
            "instruments": [
                asdict(item)
                for item in result.instruments
            ],
            "rejected": list(result.rejected),
            "total_input": result.total_input,
            "total_eligible": result.total_eligible,
            "total_rejected": result.total_rejected,
            "validation_errors": list(result.validation_errors),
            "provenance": dict(result.provenance),
        }

    # -----------------------------------------------------------------------
    # INTERNAL HELPERS
    # -----------------------------------------------------------------------

    @staticmethod
    def _to_mapping(value: Any) -> Dict[str, Any]:
        if value is None:
            return {}

        if isinstance(value, Mapping):
            return dict(value)

        if hasattr(value, "__dict__"):
            return dict(vars(value))

        # Dataclass-like fallback.
        try:
            return asdict(value)
        except (TypeError, ValueError):
            return {}

    @staticmethod
    def _first(
        mapping: Mapping[str, Any],
        *keys: str,
    ) -> Any:
        for key in keys:
            if key in mapping and mapping[key] is not None:
                return mapping[key]
        return None

    @staticmethod
    def _optional_str(value: Any) -> Optional[str]:
        if value is None:
            return None

        text = str(value).strip()
        return text if text else None

    @staticmethod
    def _to_float(value: Any) -> Optional[float]:
        if value is None or value == "":
            return None

        try:
            number = float(value)
        except (TypeError, ValueError):
            return None

        if not math.isfinite(number):
            return None

        return number

    @staticmethod
    def _to_bool(
        value: Any,
        *,
        default: bool,
    ) -> bool:
        if value is None:
            return default

        if isinstance(value, bool):
            return value

        if isinstance(value, (int, float)):
            return bool(value)

        text = str(value).strip().lower()

        if text in {
            "true",
            "1",
            "yes",
            "y",
            "active",
            "enabled",
            "tradable",
            "tradeable",
        }:
            return True

        if text in {
            "false",
            "0",
            "no",
            "n",
            "inactive",
            "disabled",
            "blocked",
            "not_tradable",
            "not tradable",
        }:
            return False

        return default

    @staticmethod
    def _normalize_status(value: Any) -> str:
        if value is None:
            return UniverseStatus.UNKNOWN.value

        text = str(value).strip().upper()

        aliases = {
            "ACTIVE": UniverseStatus.ACTIVE.value,
            "ENABLED": UniverseStatus.ACTIVE.value,
            "LIVE": UniverseStatus.ACTIVE.value,
            "TRADABLE": UniverseStatus.ACTIVE.value,

            "INACTIVE": UniverseStatus.INACTIVE.value,
            "DISABLED": UniverseStatus.INACTIVE.value,

            "BLOCKED": UniverseStatus.BLOCKED.value,
            "HALTED": UniverseStatus.BLOCKED.value,
            "SUSPENDED": UniverseStatus.BLOCKED.value,
        }

        return aliases.get(
            text,
            UniverseStatus.UNKNOWN.value,
        )

    @staticmethod
    def _normalize_instrument_type(value: Any) -> str:
        if value is None:
            return InstrumentType.UNKNOWN.value

        text = str(value).strip().upper()

        aliases = {
            "INDEX": InstrumentType.INDEX.value,
            "INDICES": InstrumentType.INDEX.value,

            "STOCK": InstrumentType.EQUITY.value,
            "EQUITY": InstrumentType.EQUITY.value,
            "SHARE": InstrumentType.EQUITY.value,

            "FUT": InstrumentType.FUTURE.value,
            "FUTURE": InstrumentType.FUTURE.value,
            "FUTURES": InstrumentType.FUTURE.value,

            "OPT": InstrumentType.OPTION.value,
            "OPTION": InstrumentType.OPTION.value,
            "OPTIONS": InstrumentType.OPTION.value,

            "FX": InstrumentType.FOREX.value,
            "FOREX": InstrumentType.FOREX.value,
            "CURRENCY": InstrumentType.FOREX.value,

            "CRYPTO": InstrumentType.CRYPTO.value,
            "DIGITAL_ASSET": InstrumentType.CRYPTO.value,

            "COMMODITY": InstrumentType.COMMODITY.value,
            "METAL": InstrumentType.COMMODITY.value,

            "ETF": InstrumentType.ETF.value,
        }

        return aliases.get(
            text,
            InstrumentType.OTHER.value,
        )

    @staticmethod
    def _normalize_timestamp(value: Any) -> str:
        if value is None:
            return datetime.now(timezone.utc).isoformat()

        if isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=timezone.utc)
            return value.astimezone(timezone.utc).isoformat()

        parsed = UniverseEngine._parse_timestamp(str(value))

        if parsed is not None:
            return parsed.astimezone(timezone.utc).isoformat()

        # Do not fabricate a different timestamp from invalid input.
        return str(value)

    @staticmethod
    def _parse_timestamp(value: Any) -> Optional[datetime]:
        if value is None:
            return None

        if isinstance(value, datetime):
            dt = value
        else:
            text = str(value).strip()

            if not text:
                return None

            text = text.replace("Z", "+00:00")

            try:
                dt = datetime.fromisoformat(text)
            except ValueError:
                return None

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        return dt.astimezone(timezone.utc)

    def _policy_dict(self) -> Dict[str, Any]:
        return {
            "include_inactive": self.policy.include_inactive,
            "require_enabled": self.policy.require_enabled,
            "require_tradable": self.policy.require_tradable,
            "allowed_markets": (
                list(self.policy.allowed_markets)
                if self.policy.allowed_markets is not None
                else None
            ),
            "allowed_instrument_types": (
                list(self.policy.allowed_instrument_types)
                if self.policy.allowed_instrument_types is not None
                else None
            ),
            "blocked_symbols": list(self.policy.blocked_symbols),
            "blocked_instrument_ids": list(
                self.policy.blocked_instrument_ids
            ),
            "deduplicate": self.policy.deduplicate,
            "preserve_order": self.policy.preserve_order,
        }


# ---------------------------------------------------------------------------
# FUNCTIONAL API
# ---------------------------------------------------------------------------

def build_universe(
    instruments: Optional[Iterable[Any]],
    *,
    market_id: Optional[str] = None,
    as_of: Optional[Any] = None,
    policy: Optional[UniversePolicy] = None,
    source: Optional[str] = None,
) -> UniverseResult:
    """
    Functional convenience API.
    """
    engine = UniverseEngine(policy=policy)

    return engine.build(
        instruments,
        market_id=market_id,
        as_of=as_of,
        source=source,
    )


# ---------------------------------------------------------------------------
# SELF TESTS
# ---------------------------------------------------------------------------

def _self_test() -> None:
    """
    Lightweight deterministic tests.

    These tests do not require external APIs.
    """

    engine = UniverseEngine()

    # 1. Basic normalization.
    result = engine.build(
        [
            {
                "instrument_id": "NIFTY",
                "symbol": "NIFTY",
                "market_id": "NSE",
                "exchange": "NSE",
                "instrument_type": "INDEX",
                "status": "ACTIVE",
                "tradable": True,
                "enabled": True,
            }
        ],
        market_id="NSE",
        as_of="2026-09-05T09:30:00+00:00",
    )

    assert result.status == "READY"
    assert result.total_input == 1
    assert result.total_eligible == 1
    assert result.instruments[0].symbol == "NIFTY"

    # 2. Market identity protection.
    wrong_market = engine.build(
        [
            {
                "instrument_id": "BTCUSDT",
                "symbol": "BTCUSDT",
                "market_id": "BINANCE",
                "instrument_type": "CRYPTO",
                "status": "ACTIVE",
            }
        ],
        market_id="NSE",
        as_of="2026-09-05T09:30:00+00:00",
    )

    assert wrong_market.total_eligible == 0
    assert wrong_market.total_rejected == 1
    assert "MARKET_ID_MISMATCH" in (
        wrong_market.rejected[0]["reasons"]
    )

    # 3. Disabled instrument protection.
    disabled = engine.build(
        [
            {
                "instrument_id": "TEST",
                "symbol": "TEST",
                "market_id": "NSE",
                "instrument_type": "EQUITY",
                "status": "DISABLED",
                "enabled": False,
                "tradable": False,
            }
        ],
        market_id="NSE",
        as_of="2026-09-05T09:30:00+00:00",
    )

    assert disabled.total_eligible == 0

    # 4. Future-data protection.
    future = engine.build(
        [
            {
                "instrument_id": "FUTURE",
                "symbol": "FUTURE",
                "market_id": "NSE",
                "instrument_type": "EQUITY",
                "status": "ACTIVE",
                "source_timestamp": "2026-09-05T10:00:00+00:00",
            }
        ],
        market_id="NSE",
        as_of="2026-09-05T09:30:00+00:00",
    )

    assert future.total_eligible == 0
    assert "FUTURE_DATA" in (
        future.rejected[0]["reasons"]
    )

    # 5. Duplicate protection.
    duplicates = engine.build(
        [
            {
                "instrument_id": "ABC",
                "symbol": "ABC",
                "market_id": "NSE",
                "instrument_type": "EQUITY",
                "status": "ACTIVE",
            },
            {
                "instrument_id": "ABC",
                "symbol": "ABC",
                "market_id": "NSE",
                "instrument_type": "EQUITY",
                "status": "ACTIVE",
            },
        ],
        market_id="NSE",
        as_of="2026-09-05T09:30:00+00:00",
    )

    assert duplicates.total_eligible == 1
    assert duplicates.total_rejected == 1
    assert (
        "DUPLICATE_INSTRUMENT"
        in duplicates.rejected[0]["reasons"]
    )

    # 6. Option normalization.
    option_result = engine.build(
        [
            {
                "instrument_id": "NIFTY-CE",
                "symbol": "NIFTYCE",
                "market_id": "NSE",
                "instrument_type": "OPTION",
                "option_type": "CE",
                "strike_price": 25000,
                "status": "ACTIVE",
            }
        ],
        market_id="NSE",
        as_of="2026-09-05T09:30:00+00:00",
    )

    assert option_result.total_eligible == 1
    option = option_result.instruments[0]
    assert option.instrument_type == "OPTION"
    assert option.option_type == "CE"
    assert option.strike == 25000.0

    print(
        f"{ENGINE_NAME} {ENGINE_VERSION}: SELF-TEST PASS"
    )


if __name__ == "__main__":
    _self_test()