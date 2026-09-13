"""
ROBOMLM PLUS - V6 Normalizer

Purpose
-------
Normalizes legacy/current V6 runtime objects at the V6 bridge boundary.

This module performs structural normalization only.

It does NOT:
    - generate trading signals
    - make trading decisions
    - calculate intelligence
    - alter legacy V6 source objects
    - introduce V7+ intelligence
    - discard unknown source information
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any, Iterable, Mapping, Optional


V6_NORMALIZER_VERSION = "1.0.0"
V6_NORMALIZER_LAYER = "V6_NORMALIZER"


# ---------------------------------------------------------------------------
# Generic Helpers
# ---------------------------------------------------------------------------

def _get(source: Any, name: str, default: Any = None) -> Any:
    """Safely read a field from mappings or objects."""

    if source is None:
        return default

    if isinstance(source, Mapping):
        return source.get(name, default)

    try:
        return getattr(source, name, default)
    except Exception:
        return default


def _first(
    source: Any,
    aliases: Iterable[str],
    default: Any = None,
) -> Any:
    """Return the first available non-None alias value."""

    for name in aliases:
        value = _get(source, name, None)

        if value is not None:
            return value

    return default


def _serialize(value: Any) -> Any:
    """Convert common runtime values into safe serializable values."""

    if value is None:
        return None

    if isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, (datetime, date)):
        return value.isoformat()

    if is_dataclass(value):
        try:
            return {
                str(key): _serialize(item)
                for key, item in asdict(value).items()
            }
        except Exception:
            return str(value)

    if isinstance(value, Mapping):
        return {
            str(key): _serialize(item)
            for key, item in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [
            _serialize(item)
            for item in value
        ]

    try:
        return str(value)
    except Exception:
        return repr(value)


def _clean_key(key: Any) -> str:
    """Create a stable string field name."""

    return str(key).strip()


# ---------------------------------------------------------------------------
# Normalization Result
# ---------------------------------------------------------------------------

@dataclass
class NormalizationResult:
    """Result returned by a V6 normalization operation."""

    success: bool
    source_type: str = ""
    target_type: str = ""
    data: dict[str, Any] | None = None
    changed_fields: list[str] | None = None
    missing_fields: list[str] | None = None
    warnings: list[str] | None = None
    message: str = ""

    def __post_init__(self) -> None:
        if self.data is None:
            self.data = {}

        if self.changed_fields is None:
            self.changed_fields = []

        if self.missing_fields is None:
            self.missing_fields = []

        if self.warnings is None:
            self.warnings = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "source_type": self.source_type,
            "target_type": self.target_type,
            "data": dict(self.data or {}),
            "changed_fields": list(self.changed_fields or []),
            "missing_fields": list(self.missing_fields or []),
            "warnings": list(self.warnings or []),
            "message": self.message,
        }


# ---------------------------------------------------------------------------
# Canonical Alias Definitions
# ---------------------------------------------------------------------------

FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "symbol": (
        "symbol",
        "ticker",
        "instrument",
        "instrument_symbol",
    ),
    "market": (
        "market",
        "market_type",
        "asset_class",
    ),
    "exchange": (
        "exchange",
        "venue",
        "exchange_name",
    ),
    "price": (
        "price",
        "ltp",
        "last_price",
        "last_traded_price",
    ),
    "timestamp": (
        "timestamp",
        "time",
        "datetime",
        "event_time",
    ),
    "volume": (
        "volume",
        "traded_volume",
        "total_volume",
    ),
    "bid": (
        "bid",
        "bid_price",
        "best_bid",
    ),
    "ask": (
        "ask",
        "ask_price",
        "best_ask",
    ),
    "side": (
        "side",
        "direction",
        "order_side",
    ),
    "action": (
        "action",
        "decision",
        "signal",
    ),
    "confidence": (
        "confidence",
        "confidence_score",
    ),
    "score": (
        "score",
        "decision_score",
        "signal_score",
    ),
    "reason": (
        "reason",
        "rationale",
        "explanation",
    ),
}


# ---------------------------------------------------------------------------
# Core Normalizer
# ---------------------------------------------------------------------------

class V6Normalizer:
    """
    Controlled V6 normalizer.

    The normalizer creates new dictionaries and does not mutate the source.
    """

    def __init__(self) -> None:
        self.version = V6_NORMALIZER_VERSION

    # -----------------------------------------------------------------------
    # Object Conversion
    # -----------------------------------------------------------------------

    def to_dict(
        self,
        source: Any,
    ) -> dict[str, Any]:
        """Convert a V6 source object to a safe dictionary."""

        if source is None:
            return {}

        if isinstance(source, Mapping):
            return {
                _clean_key(key): _serialize(value)
                for key, value in source.items()
            }

        if is_dataclass(source):
            try:
                raw = asdict(source)

                return {
                    _clean_key(key): _serialize(value)
                    for key, value in raw.items()
                }
            except Exception:
                pass

        try:
            raw = vars(source)

            return {
                _clean_key(key): _serialize(value)
                for key, value in raw.items()
                if not str(key).startswith("_")
            }
        except Exception:
            return {}

    # -----------------------------------------------------------------------
    # Alias Normalization
    # -----------------------------------------------------------------------

    def normalize_aliases(
        self,
        source: Any,
        canonical_fields: Optional[Iterable[str]] = None,
    ) -> NormalizationResult:
        """
        Normalize known aliases into canonical field names.

        Unknown fields are preserved.
        """

        source_dict = self.to_dict(source)

        if source is None:
            return NormalizationResult(
                success=False,
                source_type="NoneType",
                target_type="mapping",
                message="Source object is None.",
            )

        result = dict(source_dict)
        changed_fields: list[str] = []

        if canonical_fields is None:
            fields = list(FIELD_ALIASES.keys())
        else:
            fields = list(canonical_fields)

        for canonical in fields:
            aliases = FIELD_ALIASES.get(
                canonical,
                (canonical,),
            )

            value = _first(
                source,
                aliases,
                None,
            )

            if value is None:
                continue

            if canonical not in result:
                result[canonical] = _serialize(value)
                changed_fields.append(canonical)

        return NormalizationResult(
            success=True,
            source_type=type(source).__name__,
            target_type="mapping",
            data=result,
            changed_fields=changed_fields,
            message="V6 aliases normalized successfully.",
        )

    # -----------------------------------------------------------------------
    # Market Snapshot
    # -----------------------------------------------------------------------

    def normalize_market_snapshot(
        self,
        source: Any,
    ) -> NormalizationResult:
        """
        Normalize a market snapshot without changing its meaning.
        """

        fields = (
            "market",
            "symbol",
            "exchange",
            "price",
            "timestamp",
            "volume",
            "bid",
            "ask",
        )

        return self.normalize_aliases(
            source,
            canonical_fields=fields,
        )

    # -----------------------------------------------------------------------
    # Decision
    # -----------------------------------------------------------------------

    def normalize_decision(
        self,
        source: Any,
    ) -> NormalizationResult:
        """
        Normalize a V6 decision structure.

        Decision semantics are preserved.
        """

        fields = (
            "action",
            "confidence",
            "score",
            "reason",
            "timestamp",
        )

        result = self.normalize_aliases(
            source,
            canonical_fields=fields,
        )

        if not result.success:
            return result

        data = result.data or {}

        # Preserve common side/direction information separately.
        side = _first(
            source,
            FIELD_ALIASES["side"],
            None,
        )

        if side is not None and "side" not in data:
            data["side"] = _serialize(side)
            result.changed_fields.append("side")

        return result

    # -----------------------------------------------------------------------
    # Identity
    # -----------------------------------------------------------------------

    def normalize_identity(
        self,
        source: Any,
    ) -> NormalizationResult:
        """
        Normalize market/instrument identity fields.
        """

        source_dict = self.to_dict(source)

        if source is None:
            return NormalizationResult(
                success=False,
                source_type="NoneType",
                target_type="identity",
                message="Source object is None.",
            )

        result = dict(source_dict)
        changed_fields: list[str] = []

        identity_aliases = {
            "market": FIELD_ALIASES["market"],
            "exchange": FIELD_ALIASES["exchange"],
            "symbol": FIELD_ALIASES["symbol"],
            "instrument_id": (
                "instrument_id",
                "instrumentId",
                "security_id",
            ),
            "contract_id": (
                "contract_id",
                "contractId",
            ),
        }

        for canonical, aliases in identity_aliases.items():
            value = _first(
                source,
                aliases,
                None,
            )

            if value is None:
                continue

            if canonical not in result:
                result[canonical] = _serialize(value)
                changed_fields.append(canonical)

        return NormalizationResult(
            success=True,
            source_type=type(source).__name__,
            target_type="identity",
            data=result,
            changed_fields=changed_fields,
            message="V6 identity normalized successfully.",
        )

    # -----------------------------------------------------------------------
    # Timestamp
    # -----------------------------------------------------------------------

    def normalize_timestamp(
        self,
        value: Any,
    ) -> Any:
        """
        Normalize timestamp-like values.

        Existing ISO-compatible strings are preserved.
        Datetime/date objects are converted to ISO strings.
        Numeric timestamps remain numeric.
        """

        if value is None:
            return None

        if isinstance(value, (datetime, date)):
            return value.isoformat()

        if isinstance(value, (int, float)):
            return value

        if isinstance(value, str):
            return value.strip()

        return _serialize(value)

    # -----------------------------------------------------------------------
    # Numeric Fields
    # -----------------------------------------------------------------------

    def normalize_numeric(
        self,
        value: Any,
    ) -> Any:
        """
        Normalize numeric-like values without changing their meaning.

        Non-numeric values are preserved as strings.
        """

        if value is None:
            return None

        if isinstance(value, bool):
            return value

        if isinstance(value, (int, float)):
            return value

        if isinstance(value, str):
            cleaned = value.strip()

            if not cleaned:
                return cleaned

            try:
                if "." in cleaned:
                    return float(cleaned)

                return int(cleaned)

            except (ValueError, TypeError):
                return cleaned

        return _serialize(value)

    # -----------------------------------------------------------------------
    # Single Field
    # -----------------------------------------------------------------------

    def normalize_field(
        self,
        source: Any,
        canonical_field: str,
    ) -> Any:
        """
        Resolve one canonical field from a V6 object.
        """

        aliases = FIELD_ALIASES.get(
            canonical_field,
            (canonical_field,),
        )

        value = _first(
            source,
            aliases,
            None,
        )

        if canonical_field == "timestamp":
            return self.normalize_timestamp(value)

        if canonical_field in {
            "price",
            "volume",
            "bid",
            "ask",
            "confidence",
            "score",
        }:
            return self.normalize_numeric(value)

        return _serialize(value)

    # -----------------------------------------------------------------------
    # Required Field Check
    # -----------------------------------------------------------------------

    def check_required(
        self,
        data: Mapping[str, Any],
        required_fields: Iterable[str],
    ) -> list[str]:
        """Return required fields that are absent or None."""

        missing: list[str] = []

        for field_name in required_fields:
            if field_name not in data:
                missing.append(field_name)
                continue

            if data.get(field_name) is None:
                missing.append(field_name)

        return missing

    # -----------------------------------------------------------------------
    # Generic Normalization
    # -----------------------------------------------------------------------

    def normalize(
        self,
        source: Any,
        *,
        target_type: str = "generic",
        canonical_fields: Optional[Iterable[str]] = None,
        required_fields: Optional[Iterable[str]] = None,
    ) -> NormalizationResult:
        """
        Generic V6 normalization entry point.
        """

        result = self.normalize_aliases(
            source,
            canonical_fields=canonical_fields,
        )

        result.target_type = target_type

        if not result.success:
            return result

        if required_fields is not None:
            missing = self.check_required(
                result.data or {},
                required_fields,
            )

            result.missing_fields.extend(missing)

            if missing:
                result.warnings.append(
                    "One or more required fields are missing."
                )

        return result

    # -----------------------------------------------------------------------
    # Batch Normalization
    # -----------------------------------------------------------------------

    def normalize_many(
        self,
        sources: Iterable[Any],
        *,
        target_type: str = "generic",
        canonical_fields: Optional[Iterable[str]] = None,
    ) -> list[NormalizationResult]:
        """Normalize multiple V6 objects."""

        return [
            self.normalize(
                source,
                target_type=target_type,
                canonical_fields=canonical_fields,
            )
            for source in sources
        ]

    # -----------------------------------------------------------------------
    # Health
    # -----------------------------------------------------------------------

    def health(self) -> dict[str, Any]:
        """Return V6 normalizer health information."""

        return {
            "layer": V6_NORMALIZER_LAYER,
            "version": V6_NORMALIZER_VERSION,
            "status": "ready",
            "mutates_source": False,
            "preserves_unknown_fields": True,
            "blackbox_logger_dependency": False,
            "v7_dependency": False,
        }


# ---------------------------------------------------------------------------
# Default Normalizer
# ---------------------------------------------------------------------------

_default_normalizer = V6Normalizer()


# ---------------------------------------------------------------------------
# Convenience Functions
# ---------------------------------------------------------------------------

def get_v6_normalizer() -> V6Normalizer:
    """Return the process-local V6 normalizer."""

    return _default_normalizer


def normalize_v6(
    source: Any,
    *,
    target_type: str = "generic",
    canonical_fields: Optional[Iterable[str]] = None,
    required_fields: Optional[Iterable[str]] = None,
) -> NormalizationResult:
    """Generic V6 normalization."""

    return _default_normalizer.normalize(
        source,
        target_type=target_type,
        canonical_fields=canonical_fields,
        required_fields=required_fields,
    )


def normalize_v6_market_snapshot(
    source: Any,
) -> NormalizationResult:
    """Normalize a V6 market snapshot."""

    return _default_normalizer.normalize_market_snapshot(source)


def normalize_v6_decision(
    source: Any,
) -> NormalizationResult:
    """Normalize a V6 decision."""

    return _default_normalizer.normalize_decision(source)


def normalize_v6_identity(
    source: Any,
) -> NormalizationResult:
    """Normalize V6 identity information."""

    return _default_normalizer.normalize_identity(source)


def v6_normalizer_health() -> dict[str, Any]:
    """Return V6 normalizer health."""

    return _default_normalizer.health()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

__all__ = [
    "V6_NORMALIZER_VERSION",
    "V6_NORMALIZER_LAYER",
    "NormalizationResult",
    "V6Normalizer",
    "FIELD_ALIASES",
    "get_v6_normalizer",
    "normalize_v6",
    "normalize_v6_market_snapshot",
    "normalize_v6_decision",
    "normalize_v6_identity",
    "v6_normalizer_health",
]