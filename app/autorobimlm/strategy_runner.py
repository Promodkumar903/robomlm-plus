from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Callable


@dataclass(frozen=True)
class StrategySignal:
    strategy: str
    symbol: str
    action: str
    confidence: float
    timestamp: datetime
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


@dataclass(frozen=True)
class StrategyRunResult:
    success: bool
    strategy: str
    signal: StrategySignal | None
    message: str
    timestamp: datetime

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()

        if self.signal is not None:
            data["signal"] = self.signal.to_dict()

        return data


class StrategyRunner:
    """
    Strategy orchestration layer for AUTOROBIMLM.

    Strategy functions receive market/context data and may return
    a StrategySignal or a compatible dictionary.

    This layer generates signals only. It does not directly place
    orders. Execution, risk and kill-switch controls remain separate.
    """

    VALID_ACTIONS = frozenset({
        "BUY",
        "SELL",
        "HOLD",
        "EXIT",
    })

    def __init__(self) -> None:
        self._strategies: dict[
            str,
            Callable[[dict[str, Any]], Any],
        ] = {}
        self._history: list[StrategyRunResult] = []
        self._lock = RLock()

    @staticmethod
    def _normalize(value: str, field: str) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{field} must be a string")

        value = value.strip()

        if not value:
            raise ValueError(f"{field} is required")

        return value

    def register(
        self,
        name: str,
        strategy: Callable[[dict[str, Any]], Any],
    ) -> None:
        name = self._normalize(name, "name")

        if not callable(strategy):
            raise TypeError("strategy must be callable")

        with self._lock:
            self._strategies[name] = strategy

    def unregister(self, name: str) -> bool:
        name = self._normalize(name, "name")

        with self._lock:
            return self._strategies.pop(name, None) is not None

    def registered_strategies(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(sorted(self._strategies))

    def run(
        self,
        strategy_name: str,
        market_data: dict[str, Any],
    ) -> StrategyRunResult:
        timestamp = datetime.now(timezone.utc)
        strategy_name = self._normalize(
            strategy_name,
            "strategy_name",
        )

        if not isinstance(market_data, dict):
            raise TypeError("market_data must be a dictionary")

        with self._lock:
            strategy = self._strategies.get(strategy_name)

        if strategy is None:
            result = StrategyRunResult(
                success=False,
                strategy=strategy_name,
                signal=None,
                message="Strategy is not registered",
                timestamp=timestamp,
            )

            with self._lock:
                self._history.append(result)

            return result

        try:
            raw_signal = strategy(dict(market_data))
            signal = self._coerce_signal(
                strategy_name,
                raw_signal,
            )

            result = StrategyRunResult(
                success=True,
                strategy=strategy_name,
                signal=signal,
                message="Strategy executed successfully",
                timestamp=datetime.now(timezone.utc),
            )

        except Exception as exc:
            result = StrategyRunResult(
                success=False,
                strategy=strategy_name,
                signal=None,
                message=f"Strategy execution failed: {exc}",
                timestamp=datetime.now(timezone.utc),
            )

        with self._lock:
            self._history.append(result)

        return result

    def _coerce_signal(
        self,
        strategy_name: str,
        raw_signal: Any,
    ) -> StrategySignal:
        if isinstance(raw_signal, StrategySignal):
            if raw_signal.strategy != strategy_name:
                return StrategySignal(
                    strategy=strategy_name,
                    symbol=raw_signal.symbol,
                    action=raw_signal.action,
                    confidence=raw_signal.confidence,
                    timestamp=raw_signal.timestamp,
                    metadata=raw_signal.metadata,
                )

            self._validate_signal(raw_signal)
            return raw_signal

        if not isinstance(raw_signal, dict):
            raise TypeError(
                "Strategy must return StrategySignal or dictionary"
            )

        symbol = self._normalize(
            str(raw_signal.get("symbol", "")),
            "symbol",
        )

        action = self._normalize(
            str(raw_signal.get("action", "")),
            "action",
        ).upper()

        confidence = raw_signal.get("confidence", 0.0)

        if not isinstance(confidence, (int, float)):
            raise TypeError("confidence must be numeric")

        confidence = float(confidence)

        if not 0.0 <= confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0.0 and 1.0"
            )

        signal_timestamp = raw_signal.get("timestamp")

        if signal_timestamp is None:
            signal_timestamp = datetime.now(timezone.utc)

        if not isinstance(signal_timestamp, datetime):
            raise TypeError(
                "timestamp must be a datetime"
            )

        metadata = raw_signal.get("metadata")

        if metadata is not None and not isinstance(metadata, dict):
            raise TypeError(
                "metadata must be a dictionary"
            )

        signal = StrategySignal(
            strategy=strategy_name,
            symbol=symbol,
            action=action,
            confidence=confidence,
            timestamp=signal_timestamp,
            metadata=dict(metadata) if metadata else None,
        )

        self._validate_signal(signal)
        return signal

    def _validate_signal(
        self,
        signal: StrategySignal,
    ) -> None:
        if signal.action not in self.VALID_ACTIONS:
            raise ValueError(
                f"Unsupported strategy action: {signal.action}"
            )

        if not 0.0 <= signal.confidence <= 1.0:
            raise ValueError(
                "confidence must be between 0.0 and 1.0"
            )

        if not signal.symbol.strip():
            raise ValueError("signal symbol is required")

    def last_result(
        self,
        strategy_name: str | None = None,
    ) -> StrategyRunResult | None:
        with self._lock:
            if strategy_name is None:
                return (
                    self._history[-1]
                    if self._history
                    else None
                )

            strategy_name = self._normalize(
                strategy_name,
                "strategy_name",
            )

            for result in reversed(self._history):
                if result.strategy == strategy_name:
                    return result

            return None

    def history(
        self,
        strategy_name: str | None = None,
    ) -> tuple[StrategyRunResult, ...]:
        with self._lock:
            if strategy_name is None:
                return tuple(self._history)

            strategy_name = self._normalize(
                strategy_name,
                "strategy_name",
            )

            return tuple(
                result
                for result in self._history
                if result.strategy == strategy_name
            )

    def successful_runs(self) -> int:
        with self._lock:
            return sum(
                1
                for result in self._history
                if result.success
            )

    def failed_runs(self) -> int:
        with self._lock:
            return sum(
                1
                for result in self._history
                if not result.success
            )

    def clear_history(self) -> None:
        with self._lock:
            self._history.clear()

    def clear(self) -> None:
        with self._lock:
            self._strategies.clear()
            self._history.clear()

    def health_check(self) -> dict[str, Any]:
        with self._lock:
            return {
                "status": "healthy",
                "strategy_count": len(self._strategies),
                "run_count": len(self._history),
                "successful_runs": sum(
                    1
                    for result in self._history
                    if result.success
                ),
                "failed_runs": sum(
                    1
                    for result in self._history
                    if not result.success
                ),
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat(),
            }