from dataclasses import dataclass

from schemas.cas.cas_result import EvidenceAggregator, EvidenceSummary


@dataclass
class SampleEvent:
    event_type: str
    status: str


def test_evidence_summary_constructor():
    summary = EvidenceSummary(
        total_events=3,
        successful_events=1,
        failed_events=1,
        event_types=("A", "B", "C"),
    )

    assert summary.total_events == 3
    assert summary.successful_events == 1
    assert summary.failed_events == 1
    assert summary.event_types == ("A", "B", "C")


def test_evidence_aggregator_summarizes_object_events():
    events = [
        SampleEvent("PRICE", "success"),
        SampleEvent("ORDER", "failed"),
        SampleEvent("SIGNAL", "pending"),
    ]

    summary = EvidenceAggregator().summarize(events)

    assert summary.total_events == 3
    assert summary.successful_events == 1
    assert summary.failed_events == 1
    assert summary.event_types == ("PRICE", "ORDER", "SIGNAL")


def test_evidence_aggregator_summarizes_dict_events():
    events = [
        {"event_type": "PRICE", "status": "succeeded"},
        {"event_type": "ORDER", "status": "error"},
        {"event_type": "SIGNAL", "status": "ok"},
    ]

    summary = EvidenceAggregator().summarize(events)

    assert summary.total_events == 3
    assert summary.successful_events == 2
    assert summary.failed_events == 1
    assert summary.event_types == ("PRICE", "ORDER", "SIGNAL")


def test_evidence_aggregator_handles_unknown_event():
    events = [
        object(),
        {},
        {"status": "success"},
    ]

    summary = EvidenceAggregator().summarize(events)

    assert summary.total_events == 3
    assert summary.successful_events == 1
    assert summary.failed_events == 0
    assert summary.event_types == ("unknown", "unknown", "unknown")


def test_evidence_aggregator_to_json_safe():
    summary = EvidenceSummary(
        total_events=2,
        successful_events=1,
        failed_events=1,
        event_types=("PRICE", "ORDER"),
    )

    result = EvidenceAggregator().to_json_safe(summary)

    assert isinstance(result, dict)
    assert result["total_events"] == 2
    assert result["successful_events"] == 1
    assert result["failed_events"] == 1
    assert result["event_types"] == ["PRICE", "ORDER"]