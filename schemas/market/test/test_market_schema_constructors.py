from datetime import datetime, timezone

from schemas.market.market_snapshot import (
    MarketDataQuality as SnapshotDataQuality,
    MarketIdentity,
    InstrumentIdentity,
    MarketObservation,
    MarketSnapshot,
    MarketState,
    VenueIdentity,
)


def _market_snapshot() -> MarketSnapshot:
    now = datetime.now(timezone.utc)

    return MarketSnapshot(
        market=MarketIdentity(
            market="NSE",
            segment="EQUITY",
            country="IN",
        ),
        instrument=InstrumentIdentity(
            symbol="NIFTY",
            instrument_type="INDEX",
        ),
        venue=VenueIdentity(
            venue="NSE",
        ),
        observed_at=now,
        observation=MarketObservation(
            price=None,
        ),
        data_quality=SnapshotDataQuality(
            source="TEST",
            source_timestamp=now,
            received_timestamp=now,
        ),
        state=MarketState(),
    )


def test_market_snapshot_constructor():
    obj = _market_snapshot()

    assert obj.instrument.symbol == "NIFTY"

    data = obj.to_dict()

    assert isinstance(data, dict)
    assert data["instrument"]["symbol"] == "NIFTY"


def test_market_snapshot_missing_required_components():
    try:
        MarketSnapshot()
        assert False, "MarketSnapshot should require canonical components"
    except TypeError:
        pass


def test_required_market_schema_constructors():
    from schemas.market.market_cashflow_type import CashflowTypeDefinition
    from schemas.market.market_data_acknowledgement import MarketDataAcknowledgement
    from schemas.market.market_data_channel import MarketDataChannel
    from schemas.market.market_data_channel_event import MarketDataChannelEvent
    from schemas.market.market_data_channel_message import MarketDataChannelMessage
    from schemas.market.market_data_channel_message_acknowledgement import MarketDataChannelMessageAcknowledgement
    from schemas.market.market_data_channel_message_error import MarketDataChannelMessageError
    from schemas.market.market_data_channel_message_event import MarketDataChannelMessageEvent
    from schemas.market.market_data_channel_message_retry import MarketDataChannelMessageRetry
    from schemas.market.market_data_channel_message_retry_policy import MarketDataChannelMessageRetryPolicy
    from schemas.market.market_data_quality import DataQuality
    from schemas.market.market_data_source import MarketDataSource
    from schemas.market.market_data_status import MarketDataStatus
    from schemas.market.market_data_field import MarketDataField
    from schemas.market.market_data_packet import MarketDataPacket
    from schemas.market.market_data_record import MarketDataRecord
    from schemas.market.market_data_request import MarketDataRequest
    from schemas.market.market_data_response import MarketDataResponse

    now = datetime.now(timezone.utc)

    objs = [
        CashflowTypeDefinition((code="DEPOSIT", name="Deposit", category="FUNDING", direction="IN", balance_effect="INCREASE", description="Test"),
        MarketDataAcknowledgement(acknowledgement_id="ACK001"),
        MarketDataChannel(channel_id="CH001"),
        MarketDataChannelEvent(event_id="EV001", channel_id="CH001", event_type="CONNECTED"),
        MarketDataChannelMessage(message_id="MSG001", channel_id="CH001", message_type="SNAPSHOT"),
        MarketDataChannelMessageAcknowledgement(acknowledgement_id="ACK001", message_id="MSG001", channel_id="CH001"),
        MarketDataChannelMessageError(error_id="ERR001", message_id="MSG001", channel_id="CH001", error_code="TEST", error_message="TEST ERROR"),
        MarketDataChannelMessageEvent(event_id="EV001", message_id="MSG001", channel_id="CH001", event_type="RECEIVED"),
        MarketDataChannelMessageRetry(retry_id="RET001", message_id="MSG001", channel_id="CH001"),
        MarketDataChannelMessageRetryPolicy(policy_id="POL001"),
        DataQuality(source="TEST_SOURCE", observed_at=now, received_at=now),
        MarketDataSource(source_id="SRC001", source_name="TEST_SOURCE"),
        MarketDataStatus(ource_id="SRC001", status="ACTIVE"),
        MarketDataField(name="price"),
        MarketDataPacket(packet_id="PKT001"),
        MarketDataRecord(record_id="REC001"),
        MarketDataRequest(request_id="RET001"),
        MarketDataResponse(response_id="RESP001"),
    ]

    for obj in objs:
        assert obj is not None

        if hasattr(obj, "to_dict"):
            data = obj.to_dict()
        elif hasattr(obj, "model_dump"):
            data = obj.model_dump()
        elif hasattr(obj, "__dict__"):
            data = obj.__dict__
        else:
            raise AssertionError(f""{type(obj).__name__} has no supported serialization path")

        assert isinstance(data, dict)
