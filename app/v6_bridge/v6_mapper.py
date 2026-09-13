"""
ROBOMLM PLUS - V6 Mapper

Purpose
-------
Maps legacy/current V6 structures into the canonical structures expected
at the V6 bridge boundary.

This module performs structural mapping only.

It does NOT:
    - generate trading signals
    - make decisions
    - calculate new intelligence
    - modify V6 source objects
    - depend on blackbox_logger
    - introduce V7+ intelligence
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, is_dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any, Iterable, Mapping, Optional


V6_MAPPER_VERSION = "1.0.0"
V6_MAPPER_LAYER = "V6_MAPPER"


# ---------------------------------------------------------------------------
# Generic Helpers
# ---------------------------------------------------------------------------

def _get(source: Any, name: str, default: Any = None) -> Any:
    """Safely read a field from an object or mapping."""

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
    names: Iterable[str],
    default: Any = None,
) -> Any:
    """Return the first non-None value from a list of aliases."""

    for name in names:
        value = _get(source, name, None)

        if value is not None:
            return value

    return default


def _serialize(value: Any) -> Any:
    """Convert common runtime values to safe primitive structures."""

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
                str(k): _serialize(v)
                for k, v in asdict(value).items()
            }
        except Exception:
            return str(value)

    if isinstance(value, Mapping):
        return {
            str(k): _serialize(v)
            for k, v in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [_serialize(item) for item in value]

    try:
        return str(value)
    except Exception:
        return repr(value)


# ---------------------------------------------------------------------------
# Mapping Specification
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class FieldMap:
    """Definition of one canonical V6 field and its accepted aliases."""

    canonical: str
    aliases: tuple[str, ...]


# ---------------------------------------------------------------------------
# Canonical V6 Field Maps
# ---------------------------------------------------------------------------

MARKET_FIELDS = (
    FieldMap(
        "market",
        ("market", "market_type", "asset_class"),
    ),
    FieldMap(
        "symbol",
        ("symbol", "ticker", "instrument", "instrument_symbol"),
    ),
    FieldMap(
        "exchange",
        ("exchange", "venue", "exchange_name"),
    ),
    FieldMap(
        "price",
        ("price", "ltp", "last_price", "last_traded_price"),
    ),
    FieldMap(
        "timestamp",
        ("timestamp", "time", "datetime", "event_time"),
    ),
    FieldMap(
        "volume",
        ("volume", "traded_volume", "total_volume"),
    ),
    FieldMap(
        "bid",
        ("bid", "bid_price", "best_bid"),
    ),
    FieldMap(
        "ask",
        ("ask", "ask_price", "best_ask"),
    ),
)

DECISION_FIELDS = (
    FieldMap(
        "action",
        ("action", "decision", "signal", "direction", "side"),
    ),
    FieldMap(
        "confidence",
        ("confidence", "confidence_score"),
    ),
    FieldMap(
        "score",
        ("score", "decision_score", "signal_score"),
    ),
    FieldMap(
        "reason",
        ("reason", "rationale", "explanation"),
    ),
    FieldMap(
        "timestamp",
        ("timestamp", "time", "datetime", "event_time"),
    ),
)

IDENTITY_FIELDS = (
    FieldMap(
        "market",
        ("market", "market_type", "asset_class"),
    ),
    FieldMap(
        "exchange",
        ("exchange", "venue", "exchange_name"),
    ),
    FieldMap(
        "symbol",
        ("symbol", "ticker", "instrument", "instrument_symbol"),
    ),
    FieldMap(
        "instrument_id",
        ("instrument_id", "instrumentId", "security_id"),
    ),
    FieldMap(
        "contract_id",
        ("contract_id", "contractId"),
    ),
)


# ---------------------------------------------------------------------------
# Mapping Result
# ---------------------------------------------------------------------------

@dataclass
class MappingResult:
    """
    Result of a mapping operation.

    Mapping is considered successful when the source was processed without
    a structural exception. Missing optional fields are reported separately.
    """

    success: bool
    source_type: str = ""
    target_type: str = ""
    mapped: dict[str, Any] | None = None
    missing: list[str] | None = None
    warnings: list[str] | None = None
    message: str = ""

    def __post_init__(self) -> None:
        if self.mapped is None:
            self.mapped = {}

        if self.missing is None:
            self.missing = []

        if self.warnings is None:
            self.warnings = []

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "source_type": self.source_type,
            "target_type": self.target_type,
            "mapped": dict(self.mapped or {}),
            "missing": list(self.missing or []),
            "warnings": list(self.warnings or []),
            "message": self.message,
        }


# ---------------------------------------------------------------------------
# Core Mapper
# ---------------------------------------------------------------------------

class V6Mapper:
    """
    Controlled mapper for V6 structures.

    The mapper never mutates the source object.
    """

    def __init__(self) -> None:
        self.version = V6_MAPPER_VERSION

    # -----------------------------------------------------------------------
    # Generic Mapping
    # -----------------------------------------------------------------------

    def map_fields(
        self,
        source: Any,
        field_maps: Iterable[FieldMap],
        *,
        include_missing: bool = False,
    ) -> MappingResult:
        """
        Map source aliases into canonical field names.
        """

        if source is None:
            return MappingResult(
                success=False,
                source_type="NoneType",
                target_type="mapping",
                message="Source object is None.",
            )

        mapped: dict[str, Any] = {}
        missing: list[str] = []

        for field_map in field_maps:
            value = _first(
                source,
                field_map.aliases,
                None,
            )

            if value is None:
                missing.append(field_map.canonical)

                if include_missing:
                    mapped[field_map.canonical] = None

                continue

            mapped[field_map.canonical] = _serialize(value)

        return MappingResult(
            success=True,
            source_type=type(source).__name__,
            target_type="mapping",
            mapped=mapped,
            missing=missing,
            message="V6 fields mapped successfully.",
        )

    # -----------------------------------------------------------------------
    # Market Snapshot
    # -----------------------------------------------------------------------

    def map_market_snapshot(
        self,
        source: Any,
    ) -> MappingResult:
        """
        Map a V6 market/snapshot-like object.
        """

        return self.map_fields(
            source,
            MARKET_FIELDS,
            include_missing=False,
        )

    # -----------------------------------------------------------------------
    # Decision
    # -----------------------------------------------------------------------

    def map_decision(
        self,
        source: Any,
    ) -> MappingResult:
        """
        Map a V6 decision-like object.

        Original decision semantics are preserved; this function only
        normalizes field names.
        """

        return self.map_fields(
            source,
            DECISION_FIELDS,
            include_missing=False,
        )

    # -----------------------------------------------------------------------
    # Identity
    # -----------------------------------------------------------------------

    def map_identity(
        self,
        source: Any,
    ) -> MappingResult:
        """
        Map market/instrument/contract identity fields.
        """

        return self.map_fields(
            source,
            IDENTITY_FIELDS,
            include_missing=False,
        )

    # -----------------------------------------------------------------------
    # Arbitrary Object
    # -----------------------------------------------------------------------

    def map_object(
        self,
        source: Any,
        fields: Optional[Iterable[str]] = None,
    ) -> MappingResult:
        """
        Produce a safe dictionary representation of an arbitrary V6 object.

        When explicit fields are supplied, only those fields are mapped.
        """

        if source is None:
            return MappingResult(
                success=False,
                source_type="NoneType",
                target_type="mapping",
                message="Source object is None.",
            )

        if isinstance(source, Mapping):
            source_dict = dict(source)

        elif is_dataclass(source):
            try:
                source_dict = asdict(source)
            except Exception:
                source_dict = {}

        else:
            source_dict = {}

            if fields is not None:
                for field_name in fields:
                    value = _get(
                        source,
                        field_name,
                        None,
                    )

                    if value is not None:
                        source_dict[field_name] = value

            else:
                # Only inspect explicitly exposed instance attributes.
                try:
                    source_dict = vars(source)
                except Exception:
                    source_dict = {}

        mapped = {
            str(key): _serialize(value)
            for key, value in source_dict.items()
        }

        return MappingResult(
            success=True,
            source_type=type(source).__name__,
            target_type="mapping",
            mapped=mapped,
            message="V6 object mapped successfully.",
        )

    # -----------------------------------------------------------------------
    # Batch Mapping
    # -----------------------------------------------------------------------

    def map_many(
        self,
        sources: Iterable[Any],
        mapping_type: str = "object",
    ) -> list[MappingResult]:
        """
        Map multiple V6 objects using the requested mapping type.
        """

        mapper = {
            "market": self.map_market_snapshot,
            "snapshot": self.map_market_snapshot,
            "decision": self.map_decision,
            "identity": self.map_identity,
            "object": self.map_object,
        }.get(mapping_type.lower())

        if mapper is None:
            return [
                MappingResult(
                    success=False,
                    target_type=mapping_type,
                    message=f"Unsupported mapping type: {mapping_type}",
                )
            ]

        return [
            mapper(source)
            for source in sources
        ]

    # -----------------------------------------------------------------------
    # Compatibility Projection
    # -----------------------------------------------------------------------

    def project(
        self,
        source: Any,
        target_fields: Iterable[str],
    ) -> dict[str, Any]:
        """
        Project a source object into a requested canonical field set.

        This is useful when a downstream V6 bridge component requires
        only a defined subset of fields.
        """

        result: dict[str, Any] = {}

        for field_name in target_fields:
            value = _get(
                source,
                field_name,
                None,
            )

            if value is None:
                # Try known aliases.
                known_aliases: tuple[str, ...] = ()

                for field_map in (
                    *MARKET_FIELDS,
                    *DECISION_FIELDS,
                    *IDENTITY_FIELDS,
                ):
                    if field_map.canonical == field_name:
                        known_aliases = field_map.aliases
                        break

                if known_aliases:
                    value = _first(
                        source,
                        known_aliases,
                        None,
                    )

            result[field_name] = _serialize(value)

        return result

    # -----------------------------------------------------------------------
    # Health
    # -----------------------------------------------------------------------

    def health(self) -> dict[str, Any]:
        """
        Return mapper health information.
        """

        return {
            "layer": V6_MAPPER_LAYER,
            "version": V6_MAPPER_VERSION,
            "status": "ready",
            "mutates_source": False,
            "blackbox_logger_dependency": False,
            "v7_dependency": False,
        }


# ---------------------------------------------------------------------------
# Default Mapper
# ---------------------------------------------------------------------------

_default_mapper = V6Mapper()


# ---------------------------------------------------------------------------
# Convenience Functions
# ---------------------------------------------------------------------------

def get_v6_mapper() -> V6Mapper:
    """Return the process-local V6 mapper."""

    return _default_mapper


def map_v6_market_snapshot(
    source: Any,
) -> MappingResult:
    """Map a V6 market snapshot."""

    return _default_mapper.map_market_snapshot(source)


def map_v6_decision(
    source: Any,
) -> MappingResult:
    """Map a V6 decision."""

    return _default_mapper.map_decision(source)


def map_v6_identity(
    source: Any,
) -> MappingResult:
    """Map V6 market/instrument/contract identity."""

    return _default_mapper.map_identity(source)


def map_v6_object(
    source: Any,
    fields: Optional[Iterable[str]] = None,
) -> MappingResult:
    """Map an arbitrary V6 object."""

    return _default_mapper.map_object(
        source,
        fields=fields,
    )


def v6_mapper_health() -> dict[str, Any]:
    """Return V6 mapper health."""

    return _default_mapper.health()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

__all__ = [
    "V6_MAPPER_VERSION",
    "V6_MAPPER_LAYER",
    "FieldMap",
    "MappingResult",
    "V6Mapper",
    "get_v6_mapper",
    "map_v6_market_snapshot",
    "map_v6_decision",
    "map_v6_identity",
    "map_v6_object",
    "v6_mapper_health",
]