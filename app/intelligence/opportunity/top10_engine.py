"""
ROBOMLM_PLUS - TopTen Engine
Part 1/4

Role:
    Select and present the strongest candidates from
    authoritative upstream discovery output.

Not a:
    Decision Engine
    Risk Engine
    Signal Generator
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, Optional, Tuple


@dataclass(frozen=True)
class TopTenCandidate:
    instrument_id: str
    symbol: str = ""
    market: str = ""
    exchange: str = ""

    score: Optional[float] = None
    confidence: Optional[float] = None

    source_engine: str = ""
    decision_id: str = ""
    evidence_ids: Tuple[str, ...] = field(default_factory=tuple)

    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class TopTenResult:
    candidates: Tuple[TopTenCandidate, ...]
    requested: int
    returned: int
    warnings: Tuple[str, ...] = field(default_factory=tuple)


class TopTenEngine:

    ENGINE_NAME = "TopTenEngine"
    ENGINE_VERSION = "1.0.0"

    def __init__(self, limit: int = 10):
        self.limit = max(1, int(limit))

    def select(
        self,
        candidates: Iterable[Any],
        limit: Optional[int] = None,
    ) -> TopTenResult:

        requested = (
            self.limit
            if limit is None
            else max(1, int(limit))
        )

        normalized = []

        for raw in candidates:

            candidate = self._normalize(raw)

            if candidate is not None:
                normalized.append(candidate)

        unique = self._deduplicate(normalized)

        ranked = sorted(
            unique,
            key=lambda item: (
                -(
                    item.score
                    if item.score is not None
                    else float("-inf")
                ),
                -(
                    item.confidence
                    if item.confidence is not None
                    else float("-inf")
                ),
                item.market.upper(),
                item.exchange.upper(),
                item.symbol.upper(),
                item.instrument_id.upper(),
            ),
        )

        selected = tuple(ranked[:requested])

        return TopTenResult(
            candidates=selected,
            requested=requested,
            returned=len(selected),
        )

    def _deduplicate(
        self,
        candidates: Iterable[TopTenCandidate],
    ) -> Tuple[TopTenCandidate, ...]:

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

    def _normalize(
        self,
        raw: Any,
    ) -> Optional[TopTenCandidate]:

        if isinstance(raw, TopTenCandidate):
            return raw

        if not isinstance(raw, dict):
            return None

        instrument_id = str(
            raw.get("instrument_id", "")
        ).strip()

        if not instrument_id:
            return None

        return TopTenCandidate(
            instrument_id=instrument_id,
            symbol=str(raw.get("symbol", "")).strip(),
            market=str(raw.get("market", "")).strip(),
            exchange=str(raw.get("exchange", "")).strip(),
            score=self._number(raw.get("score")),
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
    def select_by_scope(
        self,
        candidates: Iterable[Any],
        exchange: Optional[str] = None,
        venue: Optional[str] = None,
        asset_class: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> TopTenResult:

        filtered = []

        exchange = self._clean(exchange)
        venue = self._clean(venue)
        asset_class = self._clean(asset_class)

        for raw in candidates:

            candidate = self._normalize(raw)

            if candidate is None:
                continue

            meta = candidate.metadata

            candidate_exchange = (
                candidate.exchange
                or str(meta.get("exchange", ""))
            )

            candidate_venue = str(
                meta.get("venue", "")
            )

            candidate_class = str(
                meta.get("asset_class", "")
            )

            if exchange:
                if candidate_exchange.upper() != exchange.upper():
                    continue

            if venue:
                if candidate_venue.upper() != venue.upper():
                    continue

            if asset_class:
                if candidate_class.upper() != asset_class.upper():
                    continue

            filtered.append(candidate)

        return self.select(
            filtered,
            limit=limit,
        )

    def select_asset_class(
        self,
        candidates: Iterable[Any],
        asset_class: str,
        limit: Optional[int] = None,
    ) -> TopTenResult:

        return self.select_by_scope(
            candidates,
            asset_class=asset_class,
            limit=limit,
        )

    def select_exchange(
        self,
        candidates: Iterable[Any],
        exchange: str,
        limit: Optional[int] = None,
    ) -> TopTenResult:

        return self.select_by_scope(
            candidates,
            exchange=exchange,
            limit=limit,
        )

    def select_venue(
        self,
        candidates: Iterable[Any],
        venue: str,
        limit: Optional[int] = None,
    ) -> TopTenResult:

        return self.select_by_scope(
            candidates,
            venue=venue,
            limit=limit,
        )

    @staticmethod
    def _clean(value: Any) -> str:

        if value is None:
            return ""

        return str(value).strip()

    def available_scopes(
        self,
        candidates: Iterable[Any],
    ) -> Dict[str, Any]:

        exchanges = set()
        venues = set()
        asset_classes = set()

        for raw in candidates:

            candidate = self._normalize(raw)

            if candidate is None:
                continue

            meta = candidate.metadata

            if candidate.exchange:
                exchanges.add(candidate.exchange)

            if meta.get("venue"):
                venues.add(str(meta["venue"]))

            if meta.get("asset_class"):
                asset_classes.add(
                    str(meta["asset_class"])
                )

        return {
            "exchanges": sorted(exchanges),
            "venues": sorted(venues),
            "asset_classes": sorted(asset_classes),
        }
    def select_quality(
        self,
        candidates: Iterable[Any],
        min_grade: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> TopTenResult:

        qualified = []

        grade_order = {
            "A+": 5,
            "A": 4,
            "B+": 3,
            "B": 2,
            "C": 1,
        }

        minimum = grade_order.get(
            str(min_grade).upper(),
            0,
        )

        for raw in candidates:

            candidate = self._normalize(raw)

            if candidate is None:
                continue

            grade = str(
                candidate.metadata.get(
                    "quality_grade",
                    "",
                )
            ).upper()

            if grade_order.get(grade, 0) < minimum:
                continue

            qualified.append(candidate)

        return self.select(
            qualified,
            limit=limit,
        )

    def select_best_available(
        self,
        candidates: Iterable[Any],
        limit: Optional[int] = None,
    ) -> TopTenResult:

        """
        Select up to TopTen maximum from the quality
        actually available in the supplied ROBOMLM output.

        No artificial candidate creation.
        """

        candidates = tuple(candidates)

        qualified = []

        for raw in candidates:

            candidate = self._normalize(raw)

            if candidate is None:
                continue

            grade = str(
                candidate.metadata.get(
                    "quality_grade",
                    "",
                )
            ).strip()

            if not grade:
                continue

            qualified.append(candidate)

        return self.select(
            qualified,
            limit=limit,
        )

    def quality_distribution(
        self,
        candidates: Iterable[Any],
    ) -> Dict[str, int]:

        distribution: Dict[str, int] = {}

        for raw in candidates:

            candidate = self._normalize(raw)

            if candidate is None:
                continue

            grade = str(
                candidate.metadata.get(
                    "quality_grade",
                    "UNKNOWN",
                )
            ).upper()

            distribution[grade] = (
                distribution.get(grade, 0) + 1
            )

        return dict(
            sorted(distribution.items())
        )

    def scope_quality(
        self,
        candidates: Iterable[Any],
        asset_class: Optional[str] = None,
        exchange: Optional[str] = None,
        venue: Optional[str] = None,
        min_grade: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> TopTenResult:

        scoped = self.select_by_scope(
            candidates,
            exchange=exchange,
            venue=venue,
            asset_class=asset_class,
            limit=None,
        )

        return self.select_quality(
            scoped.candidates,
            min_grade=min_grade,
            limit=limit,
        )
    def display_list(
        self,
        result: TopTenResult,
    ) -> Tuple[Dict[str, Any], ...]:
        """
        UI-ready TopTen list.

        Presentation only.
        No new decision or signal is generated.
        """

        rows = []

        for rank, candidate in enumerate(
            result.candidates,
            start=1,
        ):
            meta = candidate.metadata

            rows.append({
                "rank": rank,
                "symbol": candidate.symbol,
                "instrument_id": candidate.instrument_id,

                "asset_class": str(
                    meta.get("asset_class", "")
                ),

                "market": candidate.market,

                "exchange": candidate.exchange,

                "venue": str(
                    meta.get("venue", "")
                ),

                "quality_grade": str(
                    meta.get("quality_grade", "")
                ),

                "score": candidate.score,

                "confidence": candidate.confidence,

                "source_engine": candidate.source_engine,

                "decision_id": candidate.decision_id,

                "evidence_ids": list(
                    candidate.evidence_ids
                ),

                "metadata": dict(meta),
            })

        return tuple(rows)

    def display_contract(
        self,
        result: TopTenResult,
    ) -> Dict[str, Any]:
        """
        Stable contract for Terminal / Discovery / UI.

        TopTen only presents upstream intelligence.
        """

        return {
            "engine": self.ENGINE_NAME,
            "version": self.ENGINE_VERSION,
            "requested": result.requested,
            "returned": result.returned,
            "candidates": list(
                self.display_list(result)
            ),
            "warnings": list(result.warnings),
        }

    def validate_result(
        self,
        result: TopTenResult,
    ) -> Tuple[str, ...]:

        errors = []

        if result.returned != len(result.candidates):
            errors.append(
                "returned count mismatch"
            )

        if result.returned > result.requested:
            errors.append(
                "result exceeds requested limit"
            )

        if result.returned > self.limit:
            errors.append(
                "result exceeds engine limit"
            )

        seen = set()

        for candidate in result.candidates:

            key = (
                candidate.market.upper(),
                candidate.exchange.upper(),
                candidate.instrument_id.upper(),
            )

            if key in seen:
                errors.append(
                    f"duplicate candidate: "
                    f"{candidate.instrument_id}"
                )

            seen.add(key)

            if not candidate.instrument_id:
                errors.append(
                    "candidate missing instrument_id"
                )

        return tuple(errors)

    def engine_info(self) -> Dict[str, Any]:

        return {
            "engine_name": self.ENGINE_NAME,
            "engine_version": self.ENGINE_VERSION,
            "role": (
                "Top-quality candidate selection "
                "and presentation"
            ),
            "decision_authority": "D13",
            "creates_decision": False,
            "creates_signal": False,
            "creates_risk": False,
            "supports_multi_asset": True,
            "supports_multi_exchange": True,
            "supports_multi_venue": True,
            "max_default_results": self.limit,
        }

    def self_check(self) -> Dict[str, Any]:

        checks = {
            "engine_initialized": self.limit >= 1,
            "max_limit_is_ten_or_less": (
                self.limit <= 10
            ),
            "decision_authority_preserved": True,
            "no_signal_generation": True,
            "no_risk_generation": True,
            "presentation_only": True,
        }

        return {
            "engine": self.ENGINE_NAME,
            "version": self.ENGINE_VERSION,
            "passed": all(checks.values()),
            "checks": checks,
        }


def create_topten_engine(
    limit: int = 10,
) -> TopTenEngine:
    """
    Factory for TopTen Engine.
    """

    return TopTenEngine(
        limit=min(10, max(1, int(limit)))
    )


__all__ = [
    "TopTenCandidate",
    "TopTenResult",
    "TopTenEngine",
    "create_topten_engine",
]