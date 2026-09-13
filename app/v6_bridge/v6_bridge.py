"""
ROBOMLM PLUS - V6 Bridge

Purpose:
    Provide the central compatibility boundary between the completed V6
    engine and the ROBOMLM PLUS application.

Design principles:
    - V6 remains an isolated compatibility source.
    - V7+ intelligence does not depend directly on V6 implementation details.
    - Translation is explicit and deterministic.
    - No network, broker, exchange, or order-execution side effects.
    - Unknown V6 fields are preserved rather than silently discarded.
    - The bridge can be disabled without changing the V7+ intelligence core.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Callable, Mapping, Optional


class V6BridgeError(Exception):
    """Base exception for V6 bridge errors."""


class V6BridgeValidationError(V6BridgeError):
    """Raised when V6 bridge input is invalid."""


class V6BridgeDisabledError(V6BridgeError):
    """Raised when an operation requires an enabled bridge."""


@dataclass(frozen=True)
class V6BridgeConfig:
    """
    Configuration for the V6 compatibility boundary.

    The bridge is enabled by default because V6 is part of the completed
    compatibility layer. Runtime execution remains outside this object.
    """

    enabled: bool = True
    preserve_unknown_fields: bool = True
    preserve_original_payload: bool = True
    source_label: str = "V6"
    bridge_version: str = "1.0"

    def __post_init__(self) -> None:
        if not str(self.source_label).strip():
            raise V6BridgeValidationError(
                "source_label cannot be empty."
            )

        if not str(self.bridge_version).strip():
            raise V6BridgeValidationError(
                "bridge_version cannot be empty."
            )


@dataclass
class V6BridgeResult:
    """
    Result of a V6 bridge translation operation.
    """

    success: bool
    operation: str
    translated: dict[str, Any] = field(default_factory=dict)
    original: dict[str, Any] = field(default_factory=dict)
    preserved_fields: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "operation": self.operation,
            "translated": dict(self.translated),
            "original": dict(self.original),
            "preserved_fields": list(self.preserved_fields),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "timestamp": self.timestamp.isoformat(),
        }


class V6Bridge:
    """
    Central compatibility bridge for V6.

    Responsibilities:
        - Validate bridge configuration.
        - Normalize common V6 field naming.
        - Translate V6 payloads into canonical PLUS structures.
        - Preserve source information.
        - Optionally invoke a supplied translation handler.

    Non-responsibilities:
        - Market-data retrieval.
        - Broker connectivity.
        - Order placement.
        - Position management.
        - Trade execution.
        - V7+ intelligence decisions.
    """

    REQUIRED_CANONICAL_FIELDS = (
        "event_type",
        "action",
    )

    FIELD_ALIASES: dict[str, tuple[str, ...]] = {
        "event_id": (
            "event_id",
            "Event_ID",
            "eventId",
            "id",
            "ID",
        ),
        "sequence": (
            "sequence",
            "Sequence",
            "seq",
        ),
        "timestamp": (
            "timestamp",
            "Timestamp",
            "time",
            "Time",
            "created_at",
            "Created_At",
        ),
        "event_type": (
            "event_type",
            "Event_Type",
            "eventType",
            "type",
            "Type",
        ),
        "source": (
            "source",
            "Source",
        ),
        "component": (
            "component",
            "Component",
        ),
        "action": (
            "action",
            "Action",
            "event_action",
            "Event_Action",
        ),
        "status": (
            "status",
            "Status",
            "event_status",
            "Event_Status",
        ),
        "mode": (
            "mode",
            "Mode",
        ),
        "request_id": (
            "request_id",
            "Request_ID",
            "requestId",
        ),
        "session_id": (
            "session_id",
            "Session_ID",
            "sessionId",
        ),
        "user_id": (
            "user_id",
            "User_ID",
            "userId",
        ),
        "market": (
            "market",
            "Market",
        ),
        "instrument": (
            "instrument",
            "Instrument",
            "symbol",
            "Symbol",
        ),
        "venue": (
            "venue",
            "Venue",
            "exchange",
            "Exchange",
        ),
        "metadata": (
            "metadata",
            "Metadata",
        ),
        "payload": (
            "payload",
            "Payload",
        ),
    }

    def __init__(
        self,
        config: Optional[V6BridgeConfig] = None,
        translation_handler: Optional[
            Callable[[dict[str, Any]], Any]
        ] = None,
    ) -> None:
        self.config = config or V6BridgeConfig()
        self.translation_handler = translation_handler
        self._lock = RLock()
        self._translation_count = 0
        self._error_count = 0
        self._last_operation_at: Optional[datetime] = None

    # ------------------------------------------------------------------
    # Configuration
    # ------------------------------------------------------------------

    @property
    def enabled(self) -> bool:
        """Return whether the bridge is enabled."""
        return self.config.enabled

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the bridge."""
        with self._lock:
            self.config = V6BridgeConfig(
                enabled=bool(enabled),
                preserve_unknown_fields=self.config.preserve_unknown_fields,
                preserve_original_payload=self.config.preserve_original_payload,
                source_label=self.config.source_label,
                bridge_version=self.config.bridge_version,
            )

    def require_enabled(self) -> None:
        """Raise an error if the bridge is disabled."""
        if not self.enabled:
            raise V6BridgeDisabledError(
                "V6 compatibility bridge is disabled."
            )

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(
        self,
        payload: Mapping[str, Any],
    ) -> bool:
        """
        Validate a V6 payload.

        Validation is detection-only and has no external side effects.
        """
        if not isinstance(payload, Mapping):
            raise V6BridgeValidationError(
                "V6 payload must be a mapping."
            )

        for field_name in self.REQUIRED_CANONICAL_FIELDS:
            value = self._get_alias_value(
                payload,
                field_name,
            )

            if value is None:
                raise V6BridgeValidationError(
                    f"Required V6 field missing: {field_name}"
                )

            if isinstance(value, str) and not value.strip():
                raise V6BridgeValidationError(
                    f"Required V6 field is empty: {field_name}"
                )

        return True

    # ------------------------------------------------------------------
    # Normalization
    # ------------------------------------------------------------------

    def normalize(
        self,
        payload: Mapping[str, Any],
    ) -> dict[str, Any]:
        """
        Normalize V6 field names into canonical lowercase names.
        """
        self.require_enabled()

        if not isinstance(payload, Mapping):
            raise V6BridgeValidationError(
                "V6 payload must be a mapping."
            )

        self.validate(payload)

        data = dict(payload)
        normalized: dict[str, Any] = {}

        for canonical_name, aliases in self.FIELD_ALIASES.items():
            value = self._get_alias_value(
                data,
                canonical_name,
            )

            if value is not None:
                normalized[canonical_name] = value

        if "status" not in normalized:
            normalized["status"] = "INFO"

        if "source" not in normalized:
            normalized["source"] = self.config.source_label

        if "component" not in normalized:
            normalized["component"] = "V6_BRIDGE"

        timestamp = normalized.get("timestamp")

        if timestamp is None:
            normalized["timestamp"] = datetime.now(
                timezone.utc
            ).isoformat()
        elif isinstance(timestamp, datetime):
            normalized["timestamp"] = self._normalize_datetime(
                timestamp
            ).isoformat()
        elif isinstance(timestamp, str):
            normalized["timestamp"] = self._normalize_timestamp_string(
                timestamp
            )

        if self.config.preserve_unknown_fields:
            known_aliases = {
                alias
                for aliases in self.FIELD_ALIASES.values()
                for alias in aliases
            }

            unknown_fields = {
                key: value
                for key, value in data.items()
                if key not in known_aliases
            }

            if unknown_fields:
                normalized["unknown_fields"] = unknown_fields

        if self.config.preserve_original_payload:
            normalized["original_payload"] = dict(data)

        normalized["bridge"] = {
            "name": "V6Bridge",
            "version": self.config.bridge_version,
            "source": self.config.source_label,
        }

        return normalized

    # ------------------------------------------------------------------
    # Translation
    # ------------------------------------------------------------------

    def translate(
        self,
        payload: Mapping[str, Any],
    ) -> V6BridgeResult:
        """
        Translate a V6 payload into the canonical PLUS representation.
        """
        operation = "translate"

        try:
            normalized = self.normalize(payload)

            preserved_fields = list(
                normalized.get(
                    "unknown_fields",
                    {},
                ).keys()
            )

            result = V6BridgeResult(
                success=True,
                operation=operation,
                translated=normalized,
                original=dict(payload),
                preserved_fields=preserved_fields,
            )

            with self._lock:
                self._translation_count += 1
                self._last_operation_at = datetime.now(
                    timezone.utc
                )

            return result

        except V6BridgeError:
            with self._lock:
                self._error_count += 1
                self._last_operation_at = datetime.now(
                    timezone.utc
                )
            raise

    def translate_or_result(
        self,
        payload: Mapping[str, Any],
    ) -> V6BridgeResult:
        """
        Translate without raising bridge validation errors.

        Intended for inspection and diagnostics.
        """
        try:
            return self.translate(payload)

        except V6BridgeError as exc:
            return V6BridgeResult(
                success=False,
                operation="translate",
                original=dict(payload)
                if isinstance(payload, Mapping)
                else {},
                errors=[str(exc)],
            )

    def translate_many(
        self,
        payloads: list[Mapping[str, Any]],
        *,
        strict: bool = True,
    ) -> list[V6BridgeResult]:
        """
        Translate multiple V6 payloads.

        strict=True:
            Stop at the first invalid payload.

        strict=False:
            Return failed results for invalid payloads and continue.
        """
        if payloads is None:
            raise V6BridgeValidationError(
                "payloads cannot be None."
            )

        results: list[V6BridgeResult] = []

        for payload in payloads:
            if strict:
                results.append(
                    self.translate(payload)
                )
            else:
                results.append(
                    self.translate_or_result(payload)
                )

        return results

    # ------------------------------------------------------------------
    # Handler integration
    # ------------------------------------------------------------------

    def set_translation_handler(
        self,
        handler: Optional[
            Callable[[dict[str, Any]], Any]
        ],
    ) -> None:
        """
        Set an optional application-owned translation handler.

        The handler is not called automatically by normalize().
        """
        if handler is not None and not callable(handler):
            raise V6BridgeValidationError(
                "translation handler must be callable or None."
            )

        with self._lock:
            self.translation_handler = handler

    def dispatch(
        self,
        payload: Mapping[str, Any],
    ) -> Any:
        """
        Translate a payload and pass the translated structure to the
        configured handler.

        No handler means the translated result is returned directly.
        """
        result = self.translate(payload)

        handler = self.translation_handler

        if handler is None:
            return result

        return handler(dict(result.translated))

    # ------------------------------------------------------------------
    # Compatibility helpers
    # ------------------------------------------------------------------

    def canonical_field(
        self,
        payload: Mapping[str, Any],
        field_name: str,
        default: Any = None,
    ) -> Any:
        """Read a canonical field using known V6 aliases."""
        if not isinstance(payload, Mapping):
            raise V6BridgeValidationError(
                "payload must be a mapping."
            )

        canonical = str(field_name).strip()

        if canonical not in self.FIELD_ALIASES:
            return payload.get(
                canonical,
                default,
            )

        value = self._get_alias_value(
            payload,
            canonical,
        )

        return default if value is None else value

    def preserve_payload(
        self,
        payload: Mapping[str, Any],
    ) -> dict[str, Any]:
        """
        Return a detached copy of the original V6 payload.
        """
        if not isinstance(payload, Mapping):
            raise V6BridgeValidationError(
                "payload must be a mapping."
            )

        return dict(payload)

    # ------------------------------------------------------------------
    # Statistics
    # ------------------------------------------------------------------

    def stats(self) -> dict[str, Any]:
        """Return bridge runtime statistics."""
        with self._lock:
            return {
                "enabled": self.enabled,
                "translation_count": self._translation_count,
                "error_count": self._error_count,
                "last_operation_at": (
                    self._last_operation_at.isoformat()
                    if self._last_operation_at
                    else None
                ),
                "bridge_version": self.config.bridge_version,
                "source_label": self.config.source_label,
                "preserve_unknown_fields": (
                    self.config.preserve_unknown_fields
                ),
                "preserve_original_payload": (
                    self.config.preserve_original_payload
                ),
            }

    def reset_stats(self) -> None:
        """Reset bridge counters."""
        with self._lock:
            self._translation_count = 0
            self._error_count = 0
            self._last_operation_at = None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @classmethod
    def _get_alias_value(
        cls,
        payload: Mapping[str, Any],
        canonical_name: str,
    ) -> Any:
        aliases = cls.FIELD_ALIASES.get(
            canonical_name,
            (canonical_name,),
        )

        for alias in aliases:
            if alias in payload:
                return payload[alias]

        return None

    @staticmethod
    def _normalize_datetime(
        value: datetime,
    ) -> datetime:
        if value.tzinfo is None:
            return value.replace(
                tzinfo=timezone.utc
            )

        return value.astimezone(timezone.utc)

    @classmethod
    def _normalize_timestamp_string(
        cls,
        value: str,
    ) -> str:
        text = value.strip()

        if not text:
            raise V6BridgeValidationError(
                "timestamp cannot be empty."
            )

        try:
            parsed = datetime.fromisoformat(
                text.replace("Z", "+00:00")
            )
        except ValueError as exc:
            raise V6BridgeValidationError(
                f"Invalid timestamp: {value}"
            ) from exc

        return cls._normalize_datetime(
            parsed
        ).isoformat()


# ---------------------------------------------------------------------------
# Global bridge
# ---------------------------------------------------------------------------

v6_bridge = V6Bridge()


# ---------------------------------------------------------------------------
# Convenience functions
# ---------------------------------------------------------------------------

def normalize_v6(
    payload: Mapping[str, Any],
) -> dict[str, Any]:
    """Normalize a V6 payload."""
    return v6_bridge.normalize(payload)


def translate_v6(
    payload: Mapping[str, Any],
) -> V6BridgeResult:
    """Translate a V6 payload."""
    return v6_bridge.translate(payload)


def translate_v6_or_result(
    payload: Mapping[str, Any],
) -> V6BridgeResult:
    """Translate a V6 payload without raising validation errors."""
    return v6_bridge.translate_or_result(payload)


def validate_v6(
    payload: Mapping[str, Any],
) -> bool:
    """Validate a V6 payload."""
    return v6_bridge.validate(payload)


def dispatch_v6(
    payload: Mapping[str, Any],
) -> Any:
    """Translate and dispatch a V6 payload."""
    return v6_bridge.dispatch(payload)


def v6_bridge_stats() -> dict[str, Any]:
    """Return V6 bridge statistics."""
    return v6_bridge.stats()