from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Mapping


MessageHandler = Callable[[dict[str, Any]], Awaitable[None]]


@dataclass(frozen=True)
class MarketStreamMessage:
    """
    Canonical message exchanged through the market websocket layer.
    """

    message_id: str
    channel: str
    event_type: str
    payload: Mapping[str, Any] = field(default_factory=dict)

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "message_id": self.message_id,
            "channel": self.channel,
            "event_type": self.event_type,
            "payload": dict(self.payload),
            "timestamp": self.timestamp.isoformat(),
        }

    def is_valid(self) -> bool:
        return bool(
            self.message_id
            and self.channel
            and self.event_type
        )


class MarketStream:
    """
    In-process market streaming boundary.

    The class manages subscriptions, message publication, and lifecycle
    state. A concrete websocket/network adapter can be connected above
    this boundary without coupling the core stream contract to a vendor.
    """

    def __init__(
        self,
        *,
        stream_name: str = "MARKET_STREAM",
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        self.stream_name = stream_name
        self._metadata: dict[str, Any] = dict(metadata or {})

        self._subscriptions: dict[str, set[MessageHandler]] = {}
        self._running = False
        self._message_counter = 0

    @property
    def running(self) -> bool:
        return self._running

    @property
    def metadata(self) -> dict[str, Any]:
        return dict(self._metadata)

    def start(self) -> None:
        """
        Start the stream lifecycle.
        """

        self._running = True

    def stop(self) -> None:
        """
        Stop the stream lifecycle.
        """

        self._running = False

    def _next_message_id(self) -> str:
        self._message_counter += 1
        return f"WS-MSG-{self._message_counter:08d}"

    def subscribe(
        self,
        channel: str,
        handler: MessageHandler,
    ) -> None:
        """
        Subscribe an async handler to a channel.
        """

        if not channel or not channel.strip():
            raise ValueError("channel must not be empty")

        if not callable(handler):
            raise TypeError("handler must be callable")

        normalized_channel = channel.strip()

        self._subscriptions.setdefault(
            normalized_channel,
            set(),
        ).add(handler)

    def unsubscribe(
        self,
        channel: str,
        handler: MessageHandler,
    ) -> bool:
        """
        Remove a handler from a channel.

        Returns True when the handler was subscribed.
        """

        normalized_channel = channel.strip()

        handlers = self._subscriptions.get(normalized_channel)

        if not handlers:
            return False

        if handler not in handlers:
            return False

        handlers.remove(handler)

        if not handlers:
            self._subscriptions.pop(normalized_channel, None)

        return True

    def subscribed_channels(self) -> tuple[str, ...]:
        """
        Return currently subscribed channels.
        """

        return tuple(self._subscriptions.keys())

    def create_message(
        self,
        *,
        channel: str,
        event_type: str,
        payload: Mapping[str, Any] | None = None,
    ) -> MarketStreamMessage:
        """
        Create a validated canonical stream message.
        """

        if not channel or not channel.strip():
            raise ValueError("channel must not be empty")

        if not event_type or not event_type.strip():
            raise ValueError("event_type must not be empty")

        return MarketStreamMessage(
            message_id=self._next_message_id(),
            channel=channel.strip(),
            event_type=event_type.strip(),
            payload=dict(payload or {}),
        )

    async def publish(
        self,
        message: MarketStreamMessage,
    ) -> int:
        """
        Publish a message to all handlers subscribed to its channel.

        Returns the number of handlers successfully invoked.
        """

        if not isinstance(message, MarketStreamMessage):
            raise TypeError(
                "message must be a MarketStreamMessage"
            )

        if not message.is_valid():
            raise ValueError("invalid stream message")

        if not self._running:
            raise RuntimeError("market stream is not running")

        handlers = tuple(
            self._subscriptions.get(message.channel, set())
        )

        if not handlers:
            return 0

        payload = message.to_dict()

        results = await asyncio.gather(
            *(handler(payload) for handler in handlers),
            return_exceptions=True,
        )

        return sum(
            1
            for result in results
            if not isinstance(result, Exception)
        )

    async def publish_event(
        self,
        *,
        channel: str,
        event_type: str,
        payload: Mapping[str, Any] | None = None,
    ) -> MarketStreamMessage:
        """
        Create and publish a stream message.
        """

        message = self.create_message(
            channel=channel,
            event_type=event_type,
            payload=payload,
        )

        await self.publish(message)

        return message

    def subscription_count(
        self,
        channel: str | None = None,
    ) -> int:
        """
        Return the number of active handlers.

        When channel is omitted, returns the total across all channels.
        """

        if channel is not None:
            return len(
                self._subscriptions.get(channel.strip(), set())
            )

        return sum(
            len(handlers)
            for handlers in self._subscriptions.values()
        )

    def clear_subscriptions(self) -> None:
        """
        Remove all stream subscriptions.
        """

        self._subscriptions.clear()

    def health_check(self) -> dict[str, Any]:
        """
        Return stream health information.
        """

        return {
            "stream": self.stream_name,
            "status": "RUNNING" if self._running else "STOPPED",
            "channels": list(self._subscriptions.keys()),
            "subscription_count": self.subscription_count(),
            "message_count": self._message_counter,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": dict(self._metadata),
        }