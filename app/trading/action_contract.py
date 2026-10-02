from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional, Tuple


class ActionSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class ActionSource(str, Enum):
    HTF = "HTF"
    BUYER = "BUYER"
    SCALPER = "SCALPER"
    AUTOROBOMLM = "AUTOROBOMLM"
    MANUAL = "MANUAL"


class ActionMode(str, Enum):
    AUTO = "AUTO"
    MANUAL = "MANUAL"


class ActionStatus(str, Enum):
    CREATED = "CREATED"
    VALID = "VALID"
    INVALID = "INVALID"
    BLOCKED = "BLOCKED"
    REVIEW = "REVIEW"
    AUTHORIZED = "AUTHORIZED"
    PREPARED = "PREPARED"
    SUBMITTED = "SUBMITTED"
    REJECTED = "REJECTED"


@dataclass(frozen=True)
class ActionSourceMetadata:
    source: ActionSource
    mode: ActionMode

    strategy: Optional[str] = None
    strategy_id: Optional[str] = None
    strategy_version: Optional[str] = None

    engine: Optional[str] = None
    engine_version: Optional[str] = None

    timeframe: Optional[str] = None
    parent_request_id: Optional[str] = None

    user_id: Optional[str] = None
    account_id: Optional[str] = None
    client_request_id: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ActionDecisionContext:
    decision_id: str
    direction: str
    state: str

    confidence: Optional[float] = None
    score: Optional[float] = None

    decision_engine: str = "D13"


@dataclass(frozen=True)
class ActionRiskContext:
    risk_id: str
    decision: str
    status: str

    score: Optional[float] = None
    confidence: Optional[float] = None

    risk_engine: str = "RISK"


@dataclass(frozen=True)
class ActionMarketContext:
    market: str
    instrument: str
    symbol: str

    contract: Optional[str] = None
    venue: Optional[str] = None
    segment: Optional[str] = None
    timeframe: Optional[str] = None


@dataclass(frozen=True)
class TradeActionRequest:
    request_id: str
    action: ActionSide

    market_context: ActionMarketContext
    source: ActionSourceMetadata

    decision: ActionDecisionContext
    risk: ActionRiskContext

    quantity: float

    order_type: str = "MARKET"
    price: Optional[float] = None

    reduce_only: bool = False
    close_only: bool = False

    current_position: Optional[Dict[str, Any]] = None
    proposed_position: Optional[Dict[str, Any]] = None

    current_exposure: Optional[float] = None
    proposed_exposure: Optional[float] = None

    broker: Optional[str] = None
    execution_channel: Optional[str] = None

    status: ActionStatus = ActionStatus.CREATED

    metadata: Dict[str, Any] = field(default_factory=dict)


def _valid_number(value: Optional[float]) -> bool:
    return value is not None and value >= 0


def validate_trade_action(
    request: TradeActionRequest,
) -> Tuple[bool, Tuple[str, ...]]:
    errors = []

    if not request.request_id.strip():
        errors.append("REQUEST_ID_REQUIRED")

    if request.action not in {
        ActionSide.BUY,
        ActionSide.SELL,
    }:
        errors.append("INVALID_ACTION")

    market = request.market_context

    if not market.market.strip():
        errors.append("MARKET_REQUIRED")

    if not market.instrument.strip():
        errors.append("INSTRUMENT_REQUIRED")

    if not market.symbol.strip():
        errors.append("SYMBOL_REQUIRED")

    if request.quantity <= 0:
        errors.append("QUANTITY_MUST_BE_POSITIVE")

    source = request.source

    if source.source not in {
        ActionSource.HTF,
        ActionSource.BUYER,
        ActionSource.SCALPER,
        ActionSource.AUTOROBOMLM,
        ActionSource.MANUAL,
    }:
        errors.append("UNSUPPORTED_ACTION_SOURCE")

    if source.source == ActionSource.MANUAL:
        if source.mode != ActionMode.MANUAL:
            errors.append("MANUAL_SOURCE_REQUIRES_MANUAL_MODE")
    else:
        if source.mode != ActionMode.AUTO:
            errors.append("AUTOMATED_SOURCE_REQUIRES_AUTO_MODE")

    decision = request.decision

    if not decision.decision_id.strip():
        errors.append("D13_DECISION_ID_REQUIRED")

    if not decision.direction.strip():
        errors.append("D13_DIRECTION_REQUIRED")

    if not decision.state.strip():
        errors.append("D13_STATE_REQUIRED")

    direction = decision.direction.upper()

    if request.action == ActionSide.BUY and direction != "UP":
        errors.append("BUY_REQUIRES_D13_UP")

    if request.action == ActionSide.SELL and direction != "DOWN":
        errors.append("SELL_REQUIRES_D13_DOWN")

    risk = request.risk

    if not risk.risk_id.strip():
        errors.append("RISK_ID_REQUIRED")

    if not risk.decision.strip():
        errors.append("RISK_DECISION_REQUIRED")

    if not risk.status.strip():
        errors.append("RISK_STATUS_REQUIRED")

    if decision.confidence is not None:
        if not 0 <= decision.confidence <= 100:
            errors.append("D13_CONFIDENCE_OUT_OF_RANGE")

    if decision.score is not None:
        if not 0 <= decision.score <= 100:
            errors.append("D13_SCORE_OUT_OF_RANGE")

    if risk.confidence is not None:
        if not 0 <= risk.confidence <= 100:
            errors.append("RISK_CONFIDENCE_OUT_OF_RANGE")

    if risk.score is not None:
        if not 0 <= risk.score <= 100:
            errors.append("RISK_SCORE_OUT_OF_RANGE")

    if request.price is not None and request.price <= 0:
        errors.append("PRICE_MUST_BE_POSITIVE")

    if not _valid_number(request.current_exposure):
        if request.current_exposure is not None:
            errors.append("CURRENT_EXPOSURE_INVALID")

    if not _valid_number(request.proposed_exposure):
        if request.proposed_exposure is not None:
            errors.append("PROPOSED_EXPOSURE_INVALID")

    if source.source == ActionSource.HTF:
        if not source.strategy:
            errors.append("HTF_STRATEGY_REQUIRED")

        if not source.strategy_id:
            errors.append("HTF_STRATEGY_ID_REQUIRED")

        if not source.timeframe:
            errors.append("HTF_TIMEFRAME_REQUIRED")

        if not source.engine:
            errors.append("HTF_ENGINE_REQUIRED")

    elif source.source == ActionSource.BUYER:
        if not source.strategy:
            errors.append("BUYER_STRATEGY_REQUIRED")

        if not source.strategy_id:
            errors.append("BUYER_STRATEGY_ID_REQUIRED")

        if not source.timeframe:
            errors.append("BUYER_TIMEFRAME_REQUIRED")

        if not source.engine:
            errors.append("BUYER_ENGINE_REQUIRED")

        if not source.user_id:
            errors.append("BUYER_USER_ID_REQUIRED")

    elif source.source == ActionSource.SCALPER:
        if not source.strategy:
            errors.append("SCALPER_STRATEGY_REQUIRED")

        if not source.strategy_id:
            errors.append("SCALPER_STRATEGY_ID_REQUIRED")

        if not source.timeframe:
            errors.append("SCALPER_TIMEFRAME_REQUIRED")

        if not source.engine:
            errors.append("SCALPER_ENGINE_REQUIRED")

        if not source.engine_version:
            errors.append("SCALPER_ENGINE_VERSION_REQUIRED")

        if not market.venue:
            errors.append("SCALPER_VENUE_REQUIRED")

    elif source.source == ActionSource.AUTOROBOMLM:
        if not source.engine:
            errors.append("AUTOROBOMLM_ENGINE_REQUIRED")

        if not source.engine_version:
            errors.append("AUTOROBOMLM_ENGINE_VERSION_REQUIRED")

        if not source.strategy:
            errors.append("AUTOROBOMLM_STRATEGY_REQUIRED")

        if not source.strategy_id:
            errors.append("AUTOROBOMLM_STRATEGY_ID_REQUIRED")

        if not source.timeframe:
            errors.append("AUTOROBOMLM_TIMEFRAME_REQUIRED")

        if not source.parent_request_id:
            errors.append("AUTOROBOMLM_PARENT_REQUEST_ID_REQUIRED")

    elif source.source == ActionSource.MANUAL:
        if not source.user_id:
            errors.append("MANUAL_USER_ID_REQUIRED")

        if not source.account_id:
            errors.append("MANUAL_ACCOUNT_ID_REQUIRED")

        if not source.client_request_id:
            errors.append("MANUAL_CLIENT_REQUEST_ID_REQUIRED")

        if not request.broker:
            errors.append("MANUAL_BROKER_REQUIRED")

        if not request.execution_channel:
            errors.append("MANUAL_EXECUTION_CHANNEL_REQUIRED")

    return len(errors) == 0, tuple(errors)


def validate_action_source(
    request: TradeActionRequest,
) -> Tuple[bool, Tuple[str, ...]]:
    valid, errors = validate_trade_action(request)
    return valid, errors


def validate_action_contract(
    request: TradeActionRequest,
) -> Tuple[bool, Tuple[str, ...]]:
    return validate_trade_action(request)


__all__ = [
    "ActionSide",
    "ActionSource",
    "ActionMode",
    "ActionStatus",
    "ActionSourceMetadata",
    "ActionDecisionContext",
    "ActionRiskContext",
    "ActionMarketContext",
    "TradeActionRequest",
    "validate_trade_action",
    "validate_action_source",
    "validate_action_contract",
]