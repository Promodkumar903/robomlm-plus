from datetime import datetime, timezone
import importlib

from schemas.market.market_cashflow_type import CashflowTypeDefinition
from schemas.market.market_snapshot import (
    MarketDataQuality as SnapshotDataQuality,
    MarketIdentity,
    InstrumentIdentity,
    MarketObservation,
    MarketSnapshot,
    MarketState,
    VenueIdentity,
)


def _dump(obj):
    if hasattr(obj, "to_dict":
        return obj.to_dict()
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "__dict__"):
        return dict(obj.__dict__)
    raise AssertionError(f""{type(obj).__name__} has no supported serialization method")

def _market_snapshot() -> MarketSnapshot:
    now = datetime.now(timezone.utc)
    return MarketSnapshot(
        market=MarketIdentity(market="NSE", segment="EQUITY", country="IN"),
        instrument=InstrumentIdentity(symbol="NIFTY", instrument_type="INDEX"),
        venue=VenueIdentity(venue="NSE"),
        observed_at=now,
        observation=MarketObservation(),
        data_quality=SnapshotDataQuality(source="TEST", source_timestamp=now, received_timestamp=now),
        state=MarketState(),
    )

def test_market_snapshot_serialization(s):
    original = _market_snapshot()
    data = _dump(original)
    assert isinstance(data, dict)
    assert data["instrument"]["symbol"] == "NIFTY"

def test_cashflow_type_definition_serialization():
    original = CashflowTypeDefinition(code="TEST", name="Test Cashflow", category="TEST", direction="IN", balance_effect="INCREASE", description="Test cashflow definition")
    data = _dump(original)
    assert isinstance(data, dict)
    assert data["code"] == "TEST"
    assert data["name"] == "Test Cashflow"

def test_market_schema_objects_have_serialization_path():
    checks = [
        ("schemas.market.market_snapshot", "MarketSnapshot", None),
        ("schemas.market.market_cashflow_type", "CashflowTypeDefinition", {"code":"TEST","name":"Test","category":"TEST","direction":"IN","balance_effect":"INCREASE","description":"Test"}),
    ]
    for module_name, class_name, kwargs in checks:
        module = importlib.import_module(module_name)
        cls = getattr(module, class_name)
        obj = _market_snapshot() if kwargs is None else cls(**kwargs)
        data = _dump(obj)
        assert isinstance(data, dict), f"{module_name}.{class_name} did not serialize to dict"