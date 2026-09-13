from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from threading import RLock
from typing import Any, Callable


@dataclass(frozen=True)
class ExecutionRequest:
    request_id: str
    symbol: str
    side: str
    quantity: float
    order_type: str
    price: float | None
    metadata: dict[str, Any] | None
    created_at: datetime

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        return data


@dataclass(frozen=True)
class ExecutionResult:
    success: bool
    request_id: str
    status: str
    message: str
    timestamp: datetime
    execution_id: str | None = None
    filled_quantity: float = 0.0
    average_price: float | None = None

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data


class ExecutionManager:
    """
    AUTOROBIMLM execution orchestration layer.

    This component validates and tracks execution requests and delegates
    actual execution to a registered adapter/handler.

    Risk approval, authorization and kill-switch checks are intentionally
    external gates. This class must not bypass those controls.
    """

    VALID_SIDES = frozenset({"BUY", "SELL"})
    VALID_ORDER_TYPES = frozenset({
        "MARKET",
        "LIMIT",
        "STOP",
        "STOP_LIMIT",
    })

    VALID_STATUSES = frozenset({
        "PENDING",
        "SUBMITTED",
        "PARTIAL",
        "FILLED",
        "REJECTED",
        "CANCELLED",
        "FAILED",
    })

    def __init__(self) -> None:
        self._requests: dict[str, ExecutionRequest] = {}
        self._results: dict[str, ExecutionResult] = {}
        self._handlers: dict[str, Callable[[ExecutionRequest], Any]] = {}
        self._counter = 0
        self._lock = RLock()

    @staticmethod
    def _normalize(value: str, field: str) -> str:
        if not isinstance(value, str):
            raise TypeError(f"{field} must be a string")

        value = value.strip()

        if not value:
            raise ValueError(f"{field} is required")

        return value

    @staticmethod
    def _validate_positive(
        value: float,
        field: str,
    ) -> float:
        if not isinstance(value, (int, float)):
            raise TypeError(f"{field} must be numeric")

        value = float(value)

        if value <= 0:
            raise ValueError(f"{field} must be greater than zero")

        return value

    def _next_request_id(self) -> str:
        self._counter += 1
        return f"EXEC-{self._counter:08d}"

    def register_handler(
        self,
        venue: str,
        handler: Callable[[ExecutionRequest], Any],
    ) -> None:
        venue = self._normalize(venue, "venue")

        if not callable(handler):
            raise TypeError("handler must be callable")

        with self._lock:
            self._handlers[venue] = handler

    def unregister_handler(self, venue: str) -> bool:
        venue = self._normalize(venue, "venue")

        with self._lock:
            return self._handlers.pop(venue, None) is not None

    def create_request(
        self,
        symbol: str,
        side: str,
        quantity: float,
        order_type: str = "MARKET",
        price: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ExecutionRequest:
        symbol = self._normalize(symbol, "symbol")
        side = self._normalize(side, "side").upper()
        order_type = self._normalize(
            order_type,
            "order_type",
        ).upper()

        if side not in self.VALID_SIDES:
            raise ValueError(
                f"Unsupported side: {side}"
            )

        if order_type not in self.VALID_ORDER_TYPES:
            raise ValueError(
                f"Unsupported order type: {order_type}"
            )

        quantity = self._validate_positive(
            quantity,
            "quantity",
        )

        if order_type in {"LIMIT", "STOP_LIMIT"}:
            if price is None:
                raise ValueError(
                    "price is required for limit orders"
                )

        if price is not None:
            price = self._validate_positive(
                price,
                "price",
            )

        timestamp = datetime.now(timezone.utc)

        with self._lock:
            request = ExecutionRequest(
                request_id=self._next_request_id(),
                symbol=symbol,
                side=side,
                quantity=quantity,
                order_type=order_type,
                price=price,
                metadata=dict(metadata) if metadata else None,
                created_at=timestamp,
            )

            self._requests[request.request_id] = request

        return request

    def submit(
        self,
        request: ExecutionRequest,
        venue: str | None = None,
    ) -> ExecutionResult:
        if not isinstance(request, ExecutionRequest):
            raise TypeError(
                "request must be an ExecutionRequest"
            )

        timestamp = datetime.now(timezone.utc)

        with self._lock:
            if request.request_id not in self._requests:
                self._requests[request.request_id] = request

            handler = None

            if venue is not None:
                venue = self._normalize(venue, "venue")
                handler = self._handlers.get(venue)

        if handler is None:
            result = ExecutionResult(
                success=False,
                request_id=request.request_id,
                status="REJECTED",
                message="No execution handler is registered",
                timestamp=timestamp,
            )

            with self._lock:
                self._results[request.request_id] = result

            return result

        try:
            response = handler(request)
            result = self._normalize_handler_result(
                request,
                response,
            )

        except Exception as exc:
            result = ExecutionResult(
                success=False,
                request_id=request.request_id,
                status="FAILED",
                message=f"Execution handler failed: {exc}",
                timestamp=datetime.now(timezone.utc),
            )

        with self._lock:
            self._results[request.request_id] = result

        return result

    def _normalize_handler_result(
        self,
        request: ExecutionRequest,
        response: Any,
    ) -> ExecutionResult:
        timestamp = datetime.now(timezone.utc)

        if isinstance(response, ExecutionResult):
            if response.request_id != request.request_id:
                return ExecutionResult(
                    success=response.success,
                    request_id=request.request_id,
                    status=response.status,
                    message=response.message,
                    timestamp=response.timestamp,
                    execution_id=response.execution_id,
                    filled_quantity=response.filled_quantity,
                    average_price=response.average_price,
                )

            return response

        if not isinstance(response, dict):
            raise TypeError(
                "Execution handler must return "
                "ExecutionResult or dictionary"
            )

        status = str(
            response.get("status", "SUBMITTED")
        ).upper()

        if status not in self.VALID_STATUSES:
            raise ValueError(
                f"Unsupported execution status: {status}"
            )

        success = bool(
            response.get(
                "success",
                status in {"SUBMITTED", "PARTIAL", "FILLED"},
            )
        )

        filled_quantity = response.get(
            "filled_quantity",
            0.0,
        )

        if not isinstance(
            filled_quantity,
            (int, float),
        ):
            raise TypeError(
                "filled_quantity must be numeric"
            )

        average_price = response.get(
            "average_price"
        )

        if average_price is not None:
            if not isinstance(
                average_price,
                (int, float),
            ):
                raise TypeError(
                    "average_price must be numeric"
                )

            if average_price <= 0:
                raise ValueError(
                    "average_price must be greater than zero"
                )

            average_price = float(average_price)

        return ExecutionResult(
            success=success,
            request_id=request.request_id,
            status=status,
            message=str(
                response.get(
                    "message",
                    "Execution request processed",
                )
            ),
            timestamp=timestamp,
            execution_id=response.get("execution_id"),
            filled_quantity=float(filled_quantity),
            average_price=average_price,
        )

    def get_request(
        self,
        request_id: str,
    ) -> ExecutionRequest | None:
        request_id = self._normalize(
            request_id,
            "request_id",
        )

        with self._lock:
            return self._requests.get(request_id)

    def get_result(
        self,
        request_id: str,
    ) -> ExecutionResult | None:
        request_id = self._normalize(
            request_id,
            "request_id",
        )

        with self._lock:
            return self._results.get(request_id)

    def cancel(
        self,
        request_id: str,
    ) -> ExecutionResult:
        request_id = self._normalize(
            request_id,
            "request_id",
        )

        timestamp = datetime.now(timezone.utc)

        with self._lock:
            request = self._requests.get(request_id)

            if request is None:
                return ExecutionResult(
                    success=False,
                    request_id=request_id,
                    status="FAILED",
                    message="Execution request not found",
                    timestamp=timestamp,
                )

            current = self._results.get(request_id)

            if current is not None and current.status in {
                "FILLED",
                "CANCELLED",
                "REJECTED",
                "FAILED",
            }:
                return ExecutionResult(
                    success=False,
                    request_id=request_id,
                    status=current.status,
                    message="Request cannot be cancelled",
                    timestamp=timestamp,
                )

            result = ExecutionResult(
                success=True,
                request_id=request_id,
                status="CANCELLED",
                message="Execution request cancelled",
                timestamp=timestamp,
            )

            self._results[request_id] = result
            return result

    def requests(self) -> tuple[ExecutionRequest, ...]:
        with self._lock:
            return tuple(self._requests.values())

    def results(self) -> tuple[ExecutionResult, ...]:
        with self._lock:
            return tuple(self._results.values())

    def pending_count(self) -> int:
        with self._lock:
            return sum(
                1
                for result in self._results.values()
                if result.status in {"PENDING", "SUBMITTED", "PARTIAL"}
            )

    def filled_count(self) -> int:
        with self._lock:
            return sum(
                1
                for result in self._results.values()
                if result.status == "FILLED"
            )

    def clear(self) -> None:
        with self._lock:
            self._requests.clear()
            self._results.clear()
            self._handlers.clear()
            self._counter = 0

    def health_check(self) -> dict[str, Any]:
        with self._lock:
            return {
                "status": "healthy",
                "request_count": len(self._requests),
                "result_count": len(self._results),
                "handler_count": len(self._handlers),
                "pending_count": sum(
                    1
                    for result in self._results.values()
                    if result.status in {
                        "PENDING",
                        "SUBMITTED",
                        "PARTIAL",
                    }
                ),
                "filled_count": sum(
                    1
                    for result in self._results.values()
                    if result.status == "FILLED"
                ),
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat(),
            }