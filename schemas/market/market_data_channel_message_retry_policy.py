"""
ROBOMLM PLUS
Market Data Channel Message Retry Policy Schema

Purpose:
    Defines retry-policy rules for market-data channel messages.

Rules:
    - Schema only.
    - No trading intelligence.
    - No decision logic.
    - No execution logic.
    - No broker-specific behavior.
    - No V7+ dependency.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, Optional


MARKET_DATA_CHANNEL_MESSAGE_RETRY_POLICY_VERSION = "1.0.0"
MARKET_DATA_CHANNEL_MESSAGE_RETRY_POLICY_SCHEMA = (
    "MARKET_DATA_CHANNEL_MESSAGE_RETRY_POLICY"
)


@dataclass(frozen=True)
class MarketDataChannelMessageRetryPolicy:
    """
    Immutable retry policy for a market-data channel message.
    """

    policy_id: str

    max_attempts: int = 3
    retryable: bool = True

    initial_delay_seconds: float = 1.0
    max_delay_seconds: float = 30.0
    backoff_multiplier: float = 2.0

    retry_on_timeout: bool = True
    retry_on_connection_error: bool = True
    retry_on_transport_error: bool = True
    retry_on_server_error: bool = True
    retry_on_client_error: bool = False

    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.policy_id:
            raise ValueError("policy_id is required.")

        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1.")

        if self.initial_delay_seconds < 0:
            raise ValueError(
                "initial_delay_seconds cannot be negative."
            )

        if self.max_delay_seconds < 0:
            raise ValueError(
                "max_delay_seconds cannot be negative."
            )

        if self.backoff_multiplier < 1:
            raise ValueError(
                "backoff_multiplier must be at least 1."
            )

        if self.max_delay_seconds < self.initial_delay_seconds:
            raise ValueError(
                "max_delay_seconds cannot be less than "
                "initial_delay_seconds."
            )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def delay_for_attempt(self, attempt_number: int) -> float:
        """
        Calculate retry delay for a given attempt.
        """

        if attempt_number < 1:
            raise ValueError(
                "attempt_number must be at least 1."
            )

        delay = self.initial_delay_seconds * (
            self.backoff_multiplier ** (attempt_number - 1)
        )

        return min(
            delay,
            self.max_delay_seconds,
        )

    def can_retry(self) -> bool:
        return self.retryable and self.max_attempts > 1


def create_market_data_channel_message_retry_policy(
    policy_id: str,
    *,
    max_attempts: int = 3,
    retryable: bool = True,
    initial_delay_seconds: float = 1.0,
    max_delay_seconds: float = 30.0,
    backoff_multiplier: float = 2.0,
    retry_on_timeout: bool = True,
    retry_on_connection_error: bool = True,
    retry_on_transport_error: bool = True,
    retry_on_server_error: bool = True,
    retry_on_client_error: bool = False,
    metadata: Optional[Mapping[str, Any]] = None,
) -> MarketDataChannelMessageRetryPolicy:
    """
    Factory for creating a retry policy.
    """

    return MarketDataChannelMessageRetryPolicy(
        policy_id=policy_id,
        max_attempts=max_attempts,
        retryable=retryable,
        initial_delay_seconds=initial_delay_seconds,
        max_delay_seconds=max_delay_seconds,
        backoff_multiplier=backoff_multiplier,
        retry_on_timeout=retry_on_timeout,
        retry_on_connection_error=retry_on_connection_error,
        retry_on_transport_error=retry_on_transport_error,
        retry_on_server_error=retry_on_server_error,
        retry_on_client_error=retry_on_client_error,
        metadata=dict(metadata or {}),
    )


def market_data_channel_message_retry_policy_health() -> dict[str, Any]:
    """
    Return schema health information.
    """

    return {
        "schema": MARKET_DATA_CHANNEL_MESSAGE_RETRY_POLICY_SCHEMA,
        "version": MARKET_DATA_CHANNEL_MESSAGE_RETRY_POLICY_VERSION,
        "status": "ready",
        "immutable": True,
        "attempt_limit_supported": True,
        "backoff_supported": True,
        "error_classification_supported": True,
        "decision_logic": False,
        "execution_logic": False,
        "broker_dependency": False,
        "v7_dependency": False,
    }


__all__ = [
    "MARKET_DATA_CHANNEL_MESSAGE_RETRY_POLICY_VERSION",
    "MARKET_DATA_CHANNEL_MESSAGE_RETRY_POLICY_SCHEMA",
    "MarketDataChannelMessageRetryPolicy",
    "create_market_data_channel_message_retry_policy",
    "market_data_channel_message_retry_policy_health",
]