from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from schemas.market.market_snapshot_pydantic import (
    InstrumentIdentityModel,
    InstrumentTypeModel,
    MarketDataQualityModel,
    MarketDataQualityStatusModel,
    MarketSessionStateModel,
    MarketStateModel,
)


# ---------------------------------------------------------------------------
# MarketDataQualityStatusModel
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    [
        MarketDataQualityStatusModel.VALID,
        MarketDataQualityStatusModel.DEGRADED,
        MarketDataQualityStatusModel.STALE,
        MarketDataQualityStatusModel.INVALID,
    ],
)
def test_market_data_quality_status_valid(
    value: MarketDataQualityStatusModel,
) -> None:
    model = MarketDataQualityModel(
        source="MASSIVE",
        source_timestamp="2026-09-18T10:00:00+00:00",
        received_timestamp="2026-09-18T10:00:01+00:00",
        status=value,
    )

    assert model.status == value


@pytest.mark.parametrize(
    "value",
    [
        "GOOD",
        "WARNING",
        "ERROR",
        "UNKNOWN_STATUS",
        "",
        "valid_status",
    ],
)
def test_market_data_quality_status_invalid(
    value: str,
) -> None:
    with pytest.raises(ValidationError):
        MarketDataQualityModel(
            source="MASSIVE",
            source_timestamp="2026-09-18T10:00:00+00:00",
            received_timestamp="2026-09-18T10:00:01+00:00",
            status=value,
        )


def test_market_data_quality_status_json_serialization() -> None:
    model = MarketDataQualityModel(
        source="MASSIVE",
        source_timestamp="2026-09-18T10:00:00+00:00",
        received_timestamp="2026-09-18T10:00:01+00:00",
        status=MarketDataQualityStatusModel.VALID,
    )

    payload = model.model_dump(mode="json")

    assert payload["status"] == "VALID"

    serialized = model.model_dump_json()

    decoded = json.loads(serialized)

    assert decoded["status"] == "VALID"


# ---------------------------------------------------------------------------
# MarketSessionStateModel
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    [
        MarketSessionStateModel.OPEN,
        MarketSessionStateModel.CLOSED,
        MarketSessionStateModel.PRE_OPEN,
        MarketSessionStateModel.POST_CLOSE,
        MarketSessionStateModel.HALTED,
        MarketSessionStateModel.UNKNOWN,
    ],
)
def test_market_session_state_valid(
    value: MarketSessionStateModel,
) -> None:
    model = MarketStateModel(
        session=value,
    )

    assert model.session == value


@pytest.mark.parametrize(
    "value",
    [
        "RUNNING",
        "ACTIVE",
        "STOPPED",
        "OPENED",
        "CLOSE",
        "",
        "invalid",
    ],
)
def test_market_session_state_invalid(
    value: str,
) -> None:
    with pytest.raises(ValidationError):
        MarketStateModel(
            session=value,
        )


def test_market_session_state_json_serialization() -> None:
    model = MarketStateModel(
        session=MarketSessionStateModel.OPEN,
    )

    payload = model.model_dump(mode="json")

    assert payload["session"] == "open"

    serialized = model.model_dump_json()

    decoded = json.loads(serialized)

    assert decoded["session"] == "open"


# ---------------------------------------------------------------------------
# InstrumentTypeModel
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "value",
    [
        InstrumentTypeModel.EQUITY,
        InstrumentTypeModel.INDEX,
        InstrumentTypeModel.FUTURES,
        InstrumentTypeModel.FUTURE,
        InstrumentTypeModel.OPTIONS,
        InstrumentTypeModel.OPTION,
        InstrumentTypeModel.SPOT,
        InstrumentTypeModel.FOREX,
        InstrumentTypeModel.CRYPTO,
        InstrumentTypeModel.COMMODITY,
        InstrumentTypeModel.ETF,
        InstrumentTypeModel.FUND,
        InstrumentTypeModel.BOND,
        InstrumentTypeModel.UNKNOWN,
    ],
)
def test_instrument_type_valid(
    value: InstrumentTypeModel,
) -> None:
    model = InstrumentIdentityModel(
        symbol="TEST",
        instrument_type=value,
        instrument_id="TEST-001",
    )

    assert model.instrument_type == value


@pytest.mark.parametrize(
    "value",
    [
        "STOCK",
        "SHARE",
        "CANDLE",
        "DERIVATIVE",
        "MAGIC_ASSET",
        "",
        "INVALID",
    ],
)
def test_instrument_type_invalid(
    value: str,
) -> None:
    with pytest.raises(ValidationError):
        InstrumentIdentityModel(
            symbol="TEST",
            instrument_type=value,
            instrument_id="TEST-001",
        )


@pytest.mark.parametrize(
    ("instrument_type", "expected_json"),
    [
        (
            InstrumentTypeModel.EQUITY,
            "EQUITY",
        ),
        (
            InstrumentTypeModel.FOREX,
            "FOREX",
        ),
        (
            InstrumentTypeModel.FUTURES,
            "FUTURES",
        ),
        (
            InstrumentTypeModel.COMMODITY,
            "COMMODITY",
        ),
        (
            InstrumentTypeModel.CRYPTO,
            "CRYPTO",
        ),
    ],
)
def test_instrument_type_json_serialization(
    instrument_type: InstrumentTypeModel,
    expected_json: str,
) -> None:
    model = InstrumentIdentityModel(
        symbol="TEST",
        instrument_type=instrument_type,
        instrument_id="TEST-001",
    )

    payload = model.model_dump(mode="json")

    assert payload["instrument_type"] == expected_json

    serialized = model.model_dump_json()

    decoded = json.loads(serialized)

    assert decoded["instrument_type"] == expected_json