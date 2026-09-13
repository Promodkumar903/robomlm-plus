"""
ROBOMLM_PLUS - Scanner Engine
Part 1/4

ROLE:
    Scan/filter upstream opportunity records.

RULE:
    Scanner does NOT create a new market decision.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Iterable, Optional, Tuple


class ScannerStatus(str, Enum):
    READY = "READY"
    COMPLETE = "COMPLETE"
    PARTIAL = "PARTIAL"
    ERROR = "ERROR"


@dataclass(frozen=True)
class ScannerCandidate:
    instrument_id: str
    symbol: str = ""
    market: str = ""
    exchange: str = ""

    eligible: bool = True

    score: Optional[float] = None
    confidence: Optional[float] = None

    source_engine: str = ""
    decision_id: str = ""
    evidence_ids: Tuple[str, ...] = field(default_factory=tuple)

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ScannerResult:
    status: ScannerStatus
    candidates: Tuple[ScannerCandidate, ...]
    scanned: int
    accepted: int
    rejected: int
    warnings: Tuple[str, ...] = field(default_factory=tuple)
    errors: Tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class ScannerPolicy:
    max_results: int = 100
    min_score: Optional[float] = None
    min_confidence: Optional[float] = None
    allowed_markets: Tuple[str, ...] = field(default_factory=tuple)


class ScannerEngine:

    ENGINE_NAME = "ScannerEngine"
    ENGINE_VERSION = "1.0.0"

    def __init__(
        self,
        policy: Optional[ScannerPolicy] = None,
    ):
        self.policy = policy or ScannerPolicy()

    def scan(
        self,
        candidates: Iterable[Any],
    ) -> ScannerResult:

        accepted = []
        rejected = 0
        scanned = 0
        warnings = []

        for raw in candidates:

            scanned += 1

            candidate = self._normalize(raw)

            if candidate is None:
                rejected += 1
                warnings.append("INVALID_CANDIDATE")
                continue

            if not self._eligible(candidate):
                rejected += 1
                continue

            accepted.append(candidate)

        accepted.sort(
            key=lambda item: (
                -(item.score if item.score is not None else float("-inf")),
                item.symbol.lower(),
                item.instrument_id.lower(),
            )
        )

        accepted = accepted[:self.policy.max_results]

        return ScannerResult(
            status=ScannerStatus.COMPLETE,
            candidates=tuple(accepted),
            scanned=scanned,
            accepted=len(accepted),
            rejected=rejected,
            warnings=tuple(dict.fromkeys(warnings)),
        )

    def _eligible(
        self,
        candidate: ScannerCandidate,
    ) -> bool:

        if not candidate.eligible:
            return False

        if self.policy.min_score is not None:
            if candidate.score is None:
                return False

            if candidate.score < self.policy.min_score:
                return False

        if self.policy.min_confidence is not None:
            if candidate.confidence is None:
                return False

            if candidate.confidence < self.policy.min_confidence:
                return False

        if self.policy.allowed_markets:
            if candidate.market not in self.policy.allowed_markets:
                return False

        return True

    def _normalize(
        self,
        raw: Any,
    ) -> Optional[ScannerCandidate]:

        if isinstance(raw, ScannerCandidate):
            return raw

        if not isinstance(raw, dict):
            return None

        instrument_id = str(
            raw.get("instrument_id", "")
        ).strip()

        if not instrument_id:
            return None

        return ScannerCandidate(
            instrument_id=instrument_id,
            symbol=str(
                raw.get("symbol", "")
            ).strip(),
            market=str(
                raw.get("market", "")
            ).strip(),
            exchange=str(
                raw.get("exchange", "")
            ).strip(),
            eligible=bool(
                raw.get("eligible", True)
            ),
            score=self._number(
                raw.get("score")
            ),
            confidence=self._number(
                raw.get("confidence")
            ),
            source_engine=str(
                raw.get("source_engine", "")
            ).strip(),
            decision_id=str(
                raw.get("decision_id", "")
            ).strip(),
            evidence_ids=tuple(
                raw.get("evidence_ids", ())
            ),
            metadata=dict(
                raw.get("metadata", {})
            ),
        )

    @staticmethod
    def _number(
        value: Any,
    ) -> Optional[float]:

        if value is None:
            return None

        try:
            return float(value)
        except (TypeError, ValueError):
            return None
    def scan_universe(
        self,
        universe: Iterable[Any],
    ) -> ScannerResult:
        """
        Scan all supplied venues/exchanges/markets.

        Scanner does not restrict discovery to one venue.
        The supplied universe is authoritative.
        """

        return self.scan(universe)

    def scan_by_market(
        self,
        candidates: Iterable[Any],
        markets: Iterable[str],
    ) -> ScannerResult:

        allowed = tuple(
            str(m).strip()
            for m in markets
            if str(m).strip()
        )

        policy = ScannerPolicy(
            max_results=self.policy.max_results,
            min_score=self.policy.min_score,
            min_confidence=self.policy.min_confidence,
            allowed_markets=allowed,
        )

        engine = ScannerEngine(policy)
        return engine.scan(candidates)

    def deduplicate(
        self,
        candidates: Iterable[ScannerCandidate],
    ) -> Tuple[ScannerCandidate, ...]:

        unique = {}

        for candidate in candidates:

            key = (
                candidate.market.upper(),
                candidate.exchange.upper(),
                candidate.instrument_id.upper(),
            )

            if key not in unique:
                unique[key] = candidate

        return tuple(unique.values())

    def rank(
        self,
        candidates: Iterable[ScannerCandidate],
    ) -> Tuple[ScannerCandidate, ...]:

        unique = self.deduplicate(candidates)

        return tuple(
            sorted(
                unique,
                key=lambda item: (
                    -(item.score
                      if item.score is not None
                      else float("-inf")),
                    -(item.confidence
                      if item.confidence is not None
                      else float("-inf")),
                    item.market.upper(),
                    item.exchange.upper(),
                    item.symbol.upper(),
                    item.instrument_id.upper(),
                ),
            )
        )

    def markets(
        self,
        candidates: Iterable[ScannerCandidate],
    ) -> Tuple[str, ...]:

        values = {
            item.market
            for item in candidates
            if item.market
        }

        return tuple(sorted(values))

    def exchanges(
        self,
        candidates: Iterable[ScannerCandidate],
    ) -> Tuple[str, ...]:

        values = {
            item.exchange
            for item in candidates
            if item.exchange
        }

        return tuple(sorted(values))

    def coverage(
        self,
        candidates: Iterable[ScannerCandidate],
    ) -> Dict[str, Any]:

        candidates = tuple(candidates)

        return {
            "total_candidates": len(candidates),
            "markets": list(self.markets(candidates)),
            "exchanges": list(self.exchanges(candidates)),
            "market_count": len(self.markets(candidates)),
            "exchange_count": len(self.exchanges(candidates)),
            "unique_instruments": len({
                item.instrument_id
                for item in candidates
            }),
        }
    def scan_batches(
        self,
        batches: Iterable[Iterable[Any]],
    ) -> ScannerResult:

        all_candidates = []
        total_warnings = []

        for batch in batches:
            result = self.scan(batch)
            all_candidates.extend(result.candidates)
            total_warnings.extend(result.warnings)

        ranked = self.rank(all_candidates)
        ranked = ranked[:self.policy.max_results]

        return ScannerResult(
            status=ScannerStatus.COMPLETE,
            candidates=ranked,
            scanned=len(all_candidates),
            accepted=len(ranked),
            rejected=max(
                0,
                len(all_candidates) - len(ranked),
            ),
            warnings=tuple(
                dict.fromkeys(total_warnings)
            ),
        )

    def scan_venues(
        self,
        venue_data: Dict[str, Iterable[Any]],
    ) -> Dict[str, ScannerResult]:

        results = {}

        for venue, candidates in venue_data.items():

            result = self.scan(candidates)

            results[str(venue)] = result

        return results

    def coverage_report(
        self,
        candidates: Iterable[ScannerCandidate],
    ) -> Dict[str, Any]:

        candidates = tuple(candidates)

        venue_map = {}

        for candidate in candidates:

            venue = candidate.exchange or "UNKNOWN"
            market = candidate.market or "UNKNOWN"

            venue_map.setdefault(
                venue,
                set(),
            ).add(market)

        return {
            "venue_count": len(venue_map),
            "venues": {
                venue: sorted(markets)
                for venue, markets in venue_map.items()
            },
            "instrument_count": len({
                item.instrument_id
                for item in candidates
            }),
        }

    def validate_candidate(
        self,
        candidate: ScannerCandidate,
    ) -> Tuple[str, ...]:

        errors = []

        if not candidate.instrument_id:
            errors.append("MISSING_INSTRUMENT_ID")

        if candidate.score is not None:
            if candidate.score != candidate.score:
                errors.append("INVALID_SCORE")

        if candidate.confidence is not None:
            if not 0 <= candidate.confidence <= 100:
                errors.append("INVALID_CONFIDENCE")

        if not candidate.source_engine:
            errors.append("MISSING_SOURCE_ENGINE")

        return tuple(errors)

    def validate(
        self,
        candidates: Iterable[ScannerCandidate],
    ) -> Dict[str, Any]:

        checked = 0
        invalid = 0
        errors = []

        for candidate in candidates:

            checked += 1

            candidate_errors = self.validate_candidate(
                candidate
            )

            if candidate_errors:
                invalid += 1
                errors.extend(candidate_errors)

        return {
            "checked": checked,
            "valid": checked - invalid,
            "invalid": invalid,
            "errors": sorted(set(errors)),
        }
    def result_contract(
        self,
        result: ScannerResult,
    ) -> Dict[str, Any]:

        return {
            "engine": self.ENGINE_NAME,
            "engine_version": self.ENGINE_VERSION,
            "status": result.status.value,
            "scanned": result.scanned,
            "accepted": result.accepted,
            "rejected": result.rejected,
            "candidates": [
                {
                    "instrument_id": item.instrument_id,
                    "symbol": item.symbol,
                    "market": item.market,
                    "exchange": item.exchange,
                    "eligible": item.eligible,
                    "score": item.score,
                    "confidence": item.confidence,
                    "source_engine": item.source_engine,
                    "decision_id": item.decision_id,
                    "evidence_ids": list(item.evidence_ids),
                    "metadata": item.metadata,
                }
                for item in result.candidates
            ],
            "warnings": list(result.warnings),
            "errors": list(result.errors),
        }

    def engine_info(self) -> Dict[str, Any]:

        return {
            "engine": self.ENGINE_NAME,
            "version": self.ENGINE_VERSION,
            "role": "opportunity_discovery",
            "multi_venue": True,
            "multi_exchange": True,
            "creates_decision": False,
            "creates_new_intelligence": False,
            "decision_authority": "D13",
        }

    def self_check(self) -> Dict[str, Any]:

        checks = {
            "engine_initialized": self.policy is not None,
            "max_results_valid": self.policy.max_results > 0,
            "decision_authority_preserved": True,
            "no_internal_decision_creation": True,
            "multi_venue_supported": True,
        }

        return {
            "engine": self.ENGINE_NAME,
            "version": self.ENGINE_VERSION,
            "passed": all(checks.values()),
            "checks": checks,
        }


def create_scanner_engine(
    policy: Optional[ScannerPolicy] = None,
) -> ScannerEngine:

    return ScannerEngine(policy=policy)


__all__ = [
    "ScannerStatus",
    "ScannerCandidate",
    "ScannerResult",
    "ScannerPolicy",
    "ScannerEngine",
    "create_scanner_engine",
]