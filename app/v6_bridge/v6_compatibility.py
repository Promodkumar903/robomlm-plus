"""
ROBOMLM PLUS - V6 Compatibility Layer

Purpose
-------
Provides a controlled compatibility boundary around the completed V6 engine.

Design principles
-----------------
1. V6 remains the authoritative legacy/core engine.
2. No dependency on the non-existent app.core.logging.blackbox_logger module.
3. No V7+ intelligence is introduced here.
4. Legacy V6 objects are normalized into predictable compatibility structures.
5. Missing optional attributes do not immediately break the bridge.
6. The compatibility layer must remain deterministic and side-effect aware.
7. Existing V6 behavior is preserved wherever possible.

This module is intentionally lightweight and self-contained.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, Iterable, Mapping, Optional


# ---------------------------------------------------------------------------
# Package / Layer Identity
# ---------------------------------------------------------------------------

V6_COMPATIBILITY_VERSION = "1.0.0"
V6_COMPATIBILITY_LAYER = "V6_COMPATIBILITY"


# ---------------------------------------------------------------------------
# Compatibility Status
# ---------------------------------------------------------------------------

class CompatibilityStatus(str, Enum):
    """
    Normalized compatibility states.
    """

    COMPATIBLE = "compatible"
    PARTIAL = "partial"
    INCOMPATIBLE = "incompatible"
    UNKNOWN = "unknown"


# ---------------------------------------------------------------------------
# Compatibility Result
# ---------------------------------------------------------------------------

@dataclass
class CompatibilityResult:
    """
    Standard result returned by compatibility checks.

    This structure deliberately contains only compatibility information.
    It does not make trading decisions.
    """

    status: CompatibilityStatus
    compatible: bool
    component: str = ""
    version: str = ""
    message: str = ""
    warnings: list[str] = field(default_factory=list)
    missing_fields: list[str] = field(default_factory=list)
    extra_fields: list[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status.value,
            "compatible": self.compatible,
            "component": self.component,
            "version": self.version,
            "message": self.message,
            "warnings": list(self.warnings),
            "missing_fields": list(self.missing_fields),
            "extra_fields": list(self.extra_fields),
            "metadata": dict(self.metadata),
        }


# ---------------------------------------------------------------------------
# Generic Value Helpers
# ---------------------------------------------------------------------------

def _safe_get(
    source: Any,
    name: str,
    default: Any = None,
) -> Any:
    """
    Safely retrieve an attribute or mapping key.

    Supports:
        - normal Python objects
        - dataclasses
        - dictionaries / mappings
    """

    if source is None:
        return default

    if isinstance(source, Mapping):
        return source.get(name, default)

    try:
        return getattr(source, name, default)
    except Exception:
        return default


def _safe_set(
    target: Any,
    name: str,
    value: Any,
) -> bool:
    """
    Safely set an attribute/key where possible.

    Returns True when the value was written.
    """

    if target is None:
        return False

    if isinstance(target, dict):
        target[name] = value
        return True

    try:
        setattr(target, name, value)
        return True
    except Exception:
        return False


def _serialize_value(value: Any) -> Any:
    """
    Convert common V6 values into JSON-friendly representations.

    This function does not attempt to serialize arbitrary runtime objects.
    """

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
                str(k): _serialize_value(v)
                for k, v in asdict(value).items()
            }
        except Exception:
            pass

    if isinstance(value, Mapping):
        return {
            str(k): _serialize_value(v)
            for k, v in value.items()
        }

    if isinstance(value, (list, tuple, set)):
        return [_serialize_value(item) for item in value]

    # Last-resort representation.
    try:
        return str(value)
    except Exception:
        return repr(value)


# ---------------------------------------------------------------------------
# V6 Field Compatibility
# ---------------------------------------------------------------------------

class V6FieldCompatibility:
    """
    Handles field-name compatibility between different V6 object shapes.

    The bridge may encounter slightly different names for the same concept.
    Only explicit aliases are supported here.
    """

    FIELD_ALIASES: Dict[str, tuple[str, ...]] = {
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
            "total_volume",
            "traded_volume",
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
            "order_side",
            "direction",
        ),
    }

    @classmethod
    def resolve(
        cls,
        source: Any,
        canonical_name: str,
        default: Any = None,
    ) -> Any:
        """
        Resolve a canonical field from known V6 aliases.
        """

        aliases = cls.FIELD_ALIASES.get(
            canonical_name,
            (canonical_name,),
        )

        for alias in aliases:
            value = _safe_get(source, alias, None)

            if value is not None:
                return value

        return default

    @classmethod
    def normalize(
        cls,
        source: Any,
        fields: Optional[Iterable[str]] = None,
    ) -> Dict[str, Any]:
        """
        Return a canonical field dictionary.
        """

        requested = (
            list(fields)
            if fields is not None
            else list(cls.FIELD_ALIASES.keys())
        )

        normalized: Dict[str, Any] = {}

        for field_name in requested:
            normalized[field_name] = _serialize_value(
                cls.resolve(source, field_name)
            )

        return normalized


# ---------------------------------------------------------------------------
# V6 Object Adapter
# ---------------------------------------------------------------------------

class V6ObjectAdapter:
    """
    Converts an arbitrary V6 object into a controlled dictionary view.

    It does not mutate the original object.
    """

    DEFAULT_FIELDS = (
        "symbol",
        "market",
        "exchange",
        "price",
        "timestamp",
        "volume",
        "bid",
        "ask",
        "side",
    )

    @classmethod
    def to_dict(
        cls,
        source: Any,
        fields: Optional[Iterable[str]] = None,
    ) -> Dict[str, Any]:
        """
        Convert a V6 object into a normalized dictionary.
        """

        if source is None:
            return {}

        if isinstance(source, Mapping):
            raw = dict(source)

            normalized = dict(raw)

            for canonical_name in cls.DEFAULT_FIELDS:
                resolved = V6FieldCompatibility.resolve(
                    source,
                    canonical_name,
                )

                if resolved is not None:
                    normalized[canonical_name] = _serialize_value(
                        resolved
                    )

            return {
                str(key): _serialize_value(value)
                for key, value in normalized.items()
            }

        if is_dataclass(source):
            try:
                raw = asdict(source)
                return cls.to_dict(raw, fields=fields)
            except Exception:
                pass

        requested = (
            list(fields)
            if fields is not None
            else list(cls.DEFAULT_FIELDS)
        )

        result: Dict[str, Any] = {}

        for name in requested:
            value = V6FieldCompatibility.resolve(
                source,
                name,
            )

            if value is not None:
                result[name] = _serialize_value(value)

        return result


# ---------------------------------------------------------------------------
# Required Interface Checks
# ---------------------------------------------------------------------------

def check_required_fields(
    source: Any,
    required_fields: Iterable[str],
    component: str = "",
) -> CompatibilityResult:
    """
    Check whether an object exposes the required canonical fields.
    """

    required = list(required_fields)
    missing: list[str] = []

    for field_name in required:
        value = V6FieldCompatibility.resolve(
            source,
            field_name,
        )

        if value is None:
            missing.append(field_name)

    if not missing:
        return CompatibilityResult(
            status=CompatibilityStatus.COMPATIBLE,
            compatible=True,
            component=component,
            version=V6_COMPATIBILITY_VERSION,
            message="Required V6 fields are available.",
        )

    return CompatibilityResult(
        status=CompatibilityStatus.PARTIAL,
        compatible=False,
        component=component,
        version=V6_COMPATIBILITY_VERSION,
        message="One or more required V6 fields are unavailable.",
        missing_fields=missing,
    )


# ---------------------------------------------------------------------------
# V6 Version Compatibility
# ---------------------------------------------------------------------------
def check_version_compatibility(
    version: Any,
    component: str = "",
) -> CompatibilityResult:
    """
    Strict V6 version compatibility check.

    Accepted:
        V6
        V6.x
        v6
        v6.x

    Rejected:
        V5
        V7
        V60
        V6XYZ
        V6-BAD
        blank / None

    Missing version information is UNKNOWN but is not considered
    compatible for a V6 boundary contract.
    """

    if version is None or str(version).strip() == "":
        return CompatibilityResult(
            status=CompatibilityStatus.UNKNOWN,
            compatible=False,
            component=component,
            version=V6_COMPATIBILITY_VERSION,
            message="V6 component version was not declared.",
            warnings=[
                "Version information is unavailable; explicit V6 "
                "compatibility cannot be established."
            ],
        )

    version_text = str(version).strip()

    import re

    if re.fullmatch(r"V6(?:\.\d+(?:\.\d+)*)?", version_text, re.IGNORECASE):
        return CompatibilityResult(
            status=CompatibilityStatus.COMPATIBLE,
            compatible=True,
            component=component,
            version=version_text,
            message="V6 component version is compatible.",
        )

    return CompatibilityResult(
        status=CompatibilityStatus.INCOMPATIBLE,
        compatible=False,
        component=component,
        version=version_text,
        message="Component version is not compatible with the V6 boundary.",
        warnings=[
            "Only explicit V6 version identifiers are accepted."
        ],
    )

# ---------------------------------------------------------------------------
# Snapshot Compatibility
# ---------------------------------------------------------------------------

def normalize_snapshot(snapshot: Any) -> Dict[str, Any]:
    """
    Normalize a V6 market/snapshot-like object.

    This is intentionally generic so the bridge does not become coupled
    to one specific V6 snapshot class.
    """

    result = V6ObjectAdapter.to_dict(snapshot)

    # Keep common compatibility aliases synchronized when values exist.
    price = result.get("price")

    if price is not None:
        result.setdefault("ltp", price)
        result.setdefault("last_price", price)

    timestamp = result.get("timestamp")

    if timestamp is not None:
        result.setdefault("time", timestamp)

    return result


# ---------------------------------------------------------------------------
# Decision Compatibility
# ---------------------------------------------------------------------------

def normalize_decision(decision: Any) -> Dict[str, Any]:
    """
    Normalize a V6 decision-like object without changing its meaning.
    """

    if decision is None:
        return {}

    if isinstance(decision, Mapping):
        source = dict(decision)
    elif is_dataclass(decision):
        try:
            source = asdict(decision)
        except Exception:
            source = {}
    else:
        source = {}

        candidate_fields = (
            "action",
            "decision",
            "signal",
            "direction",
            "side",
            "confidence",
            "score",
            "reason",
            "timestamp",
        )

        for field_name in candidate_fields:
            value = _safe_get(
                decision,
                field_name,
                None,
            )

            if value is not None:
                source[field_name] = _serialize_value(value)

    return {
        str(key): _serialize_value(value)
        for key, value in source.items()
    }


# ---------------------------------------------------------------------------
# Compatibility Validation
# ---------------------------------------------------------------------------

def validate_v6_component(
    component: Any,
    required_fields: Optional[Iterable[str]] = None,
    component_name: str = "",
    version: Any = None,
) -> CompatibilityResult:
    """
    Perform a non-destructive compatibility validation.

    The function intentionally does not import or instantiate any V6
    component. The caller supplies the already-created component.
    """

    if component is None:
        return CompatibilityResult(
            status=CompatibilityStatus.INCOMPATIBLE,
            compatible=False,
            component=component_name,
            version=V6_COMPATIBILITY_VERSION,
            message="V6 component is None.",
        )

    required = list(required_fields or [])

    field_result = check_required_fields(
        component,
        required,
        component=component_name,
    )

    version_result = check_version_compatibility(
        version,
        component=component_name,
    )

    warnings = list(field_result.warnings)
    warnings.extend(version_result.warnings)

    if not field_result.compatible:
        return CompatibilityResult(
            status=CompatibilityStatus.PARTIAL,
            compatible=False,
            component=component_name,
            version=str(version or V6_COMPATIBILITY_VERSION),
            message="V6 component failed required-field compatibility.",
            warnings=warnings,
            missing_fields=field_result.missing_fields,
        )

    if version_result.status == CompatibilityStatus.PARTIAL:
        return CompatibilityResult(
            status=CompatibilityStatus.PARTIAL,
            compatible=True,
            component=component_name,
            version=str(version or V6_COMPATIBILITY_VERSION),
            message="V6 component is usable with version warning.",
            warnings=warnings,
        )

    return CompatibilityResult(
        status=CompatibilityStatus.COMPATIBLE,
        compatible=True,
        component=component_name,
        version=str(version or V6_COMPATIBILITY_VERSION),
        message="V6 component is compatible.",
        warnings=warnings,
    )


# ---------------------------------------------------------------------------
# Safe Compatibility Invocation
# ---------------------------------------------------------------------------

def call_compatible(
    component: Any,
    method_name: str,
    *args: Any,
    default: Any = None,
    **kwargs: Any,
) -> Any:
    """
    Safely call a method exposed by a V6 component.

    This helper does not swallow arbitrary application failures silently.
    It only returns the supplied default when the requested method does
    not exist or is not callable.
    """

    method = _safe_get(
        component,
        method_name,
        None,
    )

    if not callable(method):
        return default

    return method(*args, **kwargs)


# ---------------------------------------------------------------------------
# Legacy Alias Helpers
# ---------------------------------------------------------------------------

def get_symbol(source: Any, default: Optional[str] = None) -> Optional[str]:
    return V6FieldCompatibility.resolve(
        source,
        "symbol",
        default,
    )


def get_price(source: Any, default: Any = None) -> Any:
    return V6FieldCompatibility.resolve(
        source,
        "price",
        default,
    )


def get_timestamp(source: Any, default: Any = None) -> Any:
    return V6FieldCompatibility.resolve(
        source,
        "timestamp",
        default,
    )


def get_volume(source: Any, default: Any = None) -> Any:
    return V6FieldCompatibility.resolve(
        source,
        "volume",
        default,
    )


# ---------------------------------------------------------------------------
# Module Health
# ---------------------------------------------------------------------------

def compatibility_health() -> Dict[str, Any]:
    """
    Return deterministic health information for this compatibility layer.
    """

    return {
        "layer": V6_COMPATIBILITY_LAYER,
        "version": V6_COMPATIBILITY_VERSION,
        "status": "ready",
        "blackbox_logger_dependency": False,
        "external_runtime_dependency": False,
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

__all__ = [
    "V6_COMPATIBILITY_VERSION",
    "V6_COMPATIBILITY_LAYER",
    "CompatibilityStatus",
    "CompatibilityResult",
    "V6FieldCompatibility",
    "V6ObjectAdapter",
    "check_required_fields",
    "check_version_compatibility",
    "normalize_snapshot",
    "normalize_decision",
    "validate_v6_component",
    "call_compatible",
    "get_symbol",
    "get_price",
    "get_timestamp",
    "get_volume",
    "compatibility_health",
]