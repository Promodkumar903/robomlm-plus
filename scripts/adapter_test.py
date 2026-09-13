# ============================================================
# ROBOMLM_PLUS
# scripts/adapter_test.py
# ============================================================
# PART 1 — ADAPTER TEST FOUNDATION
# ============================================================
#
# Purpose:
#   Establish the deterministic foundation for adapter validation.
#
# Blueprint boundary:
#   Adapter
#       ↓
#   Canonical Market Snapshot
#
# Adapter MUST NOT produce:
#   BUY
#   SELL
#   TOP 10
#   VERDICT
#
# Adapter MAY use:
#   - broker/exchange SDK
#   - HTTP client
#   - adapter configuration
#   - canonical market schemas
#
# ============================================================

from __future__ import annotations

import importlib
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ============================================================
# 1. PROJECT ROOT
# ============================================================

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# 2. TEST IDENTITY
# ============================================================

TEST_NAME = "adapter_test"
TEST_VERSION = "1.0.0"

TEST_PHASE = "PHASE_07"
TEST_GATE = "GATE-04"

CANONICAL_OUTPUT = "Canonical Market Snapshot"


# ============================================================
# 3. BLUEPRINT ADAPTER BOUNDARY
# ============================================================

FORBIDDEN_ADAPTER_OUTPUTS: Tuple[str, ...] = (
    "BUY",
    "SELL",
    "TOP 10",
    "VERDICT",
)

ALLOWED_ADAPTER_RESPONSIBILITIES: Tuple[str, ...] = (
    "market_data_access",
    "source_connection",
    "raw_data_retrieval",
    "canonical_normalization_input",
    "canonical_snapshot_production",
)


# ============================================================
# 4. KNOWN ADAPTER FAMILIES
# ============================================================

ADAPTER_FAMILIES: Tuple[str, ...] = (
    "dhan",
    "kotak",
    "binance",
    "bybit",
    "forex",
    "commodity",
)


# ============================================================
# 5. TEST STATUS
# ============================================================

PASS = "PASS"
FAIL = "FAIL"
WARN = "WARN"
SKIP = "SKIP"


# ============================================================
# 6. TEST RESULT
# ============================================================

@dataclass(frozen=True)
class AdapterTestResult:
    test_id: str
    adapter: str
    status: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)


# ============================================================
# 7. TEST REPORT
# ============================================================

@dataclass
class AdapterTestReport:
    results: List[AdapterTestResult] = field(default_factory=list)

    def add(
        self,
        test_id: str,
        adapter: str,
        status: str,
        message: str,
        **details: Any,
    ) -> None:
        self.results.append(
            AdapterTestResult(
                test_id=test_id,
                adapter=adapter,
                status=status,
                message=message,
                details=details,
            )
        )

    @property
    def passed(self) -> int:
        return sum(result.status == PASS for result in self.results)

    @property
    def failed(self) -> int:
        return sum(result.status == FAIL for result in self.results)

    @property
    def warnings(self) -> int:
        return sum(result.status == WARN for result in self.results)

    @property
    def skipped(self) -> int:
        return sum(result.status == SKIP for result in self.results)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def status(self) -> str:
        if self.failed:
            return FAIL
        if self.warnings:
            return WARN
        return PASS


# ============================================================
# 8. MODULE IMPORT TEST
# ============================================================

def test_module_import(
    module_name: str,
    adapter_name: str,
    report: AdapterTestReport,
) -> Optional[Any]:
    """
    Verify that an adapter module can be imported.

    This test does NOT instantiate the adapter and does NOT
    connect to a live exchange.
    """

    test_id = "ADAPTER-IMPORT"

    try:
        module = importlib.import_module(module_name)

        report.add(
            test_id=test_id,
            adapter=adapter_name,
            status=PASS,
            message="Adapter module imported successfully.",
            module=module_name,
        )

        return module

    except Exception as exc:
        report.add(
            test_id=test_id,
            adapter=adapter_name,
            status=FAIL,
            message="Adapter module import failed.",
            module=module_name,
            error=f"{type(exc).__name__}: {exc}",
        )

        return None


# ============================================================
# 9. MODULE DISCOVERY
# ============================================================

def discover_adapter_modules() -> Dict[str, str]:
    """
    Discover adapter modules already present in the project.

    No adapter module is created by this test.
    """

    adapters_root = PROJECT_ROOT / "adapters"

    discovered: Dict[str, str] = {}

    if not adapters_root.exists():
        return discovered

    for family in ADAPTER_FAMILIES:
        family_dir = adapters_root / family

        if not family_dir.exists():
            continue

        for py_file in family_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue

            relative = py_file.relative_to(PROJECT_ROOT)
            module_name = ".".join(relative.with_suffix("").parts)

            discovered[family] = module_name
            break

    return discovered


# ============================================================
# 10. ADAPTER FILE EXISTENCE TEST
# ============================================================

def test_adapter_discovery(
    report: AdapterTestReport,
) -> Dict[str, str]:
    """
    Check which blueprint adapter families currently exist.

    Missing adapters are reported as SKIP here.
    They are NOT treated as import/code failures.
    """

    discovered = discover_adapter_modules()

    for family in ADAPTER_FAMILIES:

        if family in discovered:
            report.add(
                test_id="ADAPTER-DISCOVERY",
                adapter=family,
                status=PASS,
                message="Adapter family discovered.",
                module=discovered[family],
            )

        else:
            report.add(
                test_id="ADAPTER-DISCOVERY",
                adapter=family,
                status=SKIP,
                message="Adapter family is not currently present.",
            )

    return discovered


# ============================================================
# 11. CANONICAL OUTPUT NAME TEST
# ============================================================

def test_canonical_output_definition(
    report: AdapterTestReport,
) -> None:
    """
    Verify the test's canonical output contract.

    The adapter layer must terminate at canonical market data,
    not at intelligence or decision output.
    """

    if CANONICAL_OUTPUT == "Canonical Market Snapshot":

        report.add(
            test_id="ADAPTER-CONTRACT",
            adapter="ALL",
            status=PASS,
            message="Canonical adapter output contract is defined.",
            output=CANONICAL_OUTPUT,
        )

    else:

        report.add(
            test_id="ADAPTER-CONTRACT",
            adapter="ALL",
            status=FAIL,
            message="Invalid canonical adapter output contract.",
            output=CANONICAL_OUTPUT,
        )


# ============================================================
# 12. FORBIDDEN OUTPUT CONTRACT TEST
# ============================================================

def test_forbidden_outputs(
    report: AdapterTestReport,
) -> None:
    """
    Verify that adapter-level testing explicitly rejects
    intelligence/decision outputs.
    """

    required_forbidden = {
        "BUY",
        "SELL",
        "TOP 10",
        "VERDICT",
    }

    configured_forbidden = set(FORBIDDEN_ADAPTER_OUTPUTS)

    missing = sorted(required_forbidden - configured_forbidden)

    if missing:

        report.add(
            test_id="ADAPTER-BOUNDARY",
            adapter="ALL",
            status=FAIL,
            message="Adapter boundary is incomplete.",
            missing_forbidden_outputs=missing,
        )

    else:

        report.add(
            test_id="ADAPTER-BOUNDARY",
            adapter="ALL",
            status=PASS,
            message="Adapter intelligence boundary is defined correctly.",
            forbidden_outputs=list(FORBIDDEN_ADAPTER_OUTPUTS),
        )


# ============================================================
# 13. ADAPTER RESPONSIBILITY TEST
# ============================================================

def test_adapter_responsibilities(
    report: AdapterTestReport,
) -> None:
    """
    Verify the foundational responsibility set for adapters.
    """

    required = {
        "market_data_access",
        "source_connection",
        "raw_data_retrieval",
        "canonical_snapshot_production",
    }

    configured = set(ALLOWED_ADAPTER_RESPONSIBILITIES)

    missing = sorted(required - configured)

    if missing:

        report.add(
            test_id="ADAPTER-RESPONSIBILITY",
            adapter="ALL",
            status=FAIL,
            message="Required adapter responsibilities are missing.",
            missing=missing,
        )

    else:

        report.add(
            test_id="ADAPTER-RESPONSIBILITY",
            adapter="ALL",
            status=PASS,
            message="Adapter responsibility boundary is defined.",
            responsibilities=list(
                ALLOWED_ADAPTER_RESPONSIBILITIES
            ),
        )


# ============================================================
# 14. FOUNDATION TEST RUNNER
# ============================================================

def run_part1() -> AdapterTestReport:
    """
    Execute Part 1 foundation tests only.

    Live API connectivity is intentionally NOT performed here.
    """

    report = AdapterTestReport()

    test_canonical_output_definition(report)
    test_forbidden_outputs(report)
    test_adapter_responsibilities(report)

    discovered = test_adapter_discovery(report)

    for adapter_name, module_name in discovered.items():
        test_module_import(
            module_name=module_name,
            adapter_name=adapter_name,
            report=report,
        )

    return report


# ============================================================
# 15. REPORT PRINTER
# ============================================================

def print_report(report: AdapterTestReport) -> None:

    print("=" * 72)
    print("ROBOMLM_PLUS ADAPTER TEST")
    print("=" * 72)

    print(f"Test       : {TEST_NAME}")
    print(f"Version    : {TEST_VERSION}")
    print(f"Phase      : {TEST_PHASE}")
    print(f"Gate       : {TEST_GATE}")
    print(f"Status     : {report.status}")
    print("-" * 72)

    for result in report.results:

        print(
            f"[{result.status:<4}] "
            f"{result.test_id:<24} "
            f"{result.adapter:<12} "
            f"{result.message}"
        )

    print("-" * 72)

    print(f"Total      : {report.total}")
    print(f"PASS       : {report.passed}")
    print(f"FAIL       : {report.failed}")
    print(f"WARN       : {report.warnings}")
    print(f"SKIP       : {report.skipped}")

    print("=" * 72)


# ============================================================
# 16. EXIT CODE
# ============================================================

def get_exit_code(report: AdapterTestReport) -> int:

    if report.failed:
        return 1

    return 0


# ============================================================
# 17. MAIN
# ============================================================

def main() -> int:

    report = run_part1()

    print_report(report)

    return get_exit_code(report)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    raise SystemExit(main())
# ============================================================
# PART 2 — EXISTING ADAPTER LOCATION AUDIT
# ============================================================
#
# Purpose:
#   Locate adapter implementations that may exist outside the
#   expected adapters/<family>/ structure.
#
# Important:
#   This part ONLY discovers and audits existing files.
#   It does NOT create adapters.
#   It does NOT modify adapters.
#   It does NOT connect to live APIs.
#   It does NOT generate BUY / SELL / TOP 10 / VERDICT.
#
# Blueprint boundary:
#
#   Existing Adapter Code
#          ↓
#   Location Discovery
#          ↓
#   Structural Audit
#
# ============================================================


# ============================================================
# 18. ADAPTER SEARCH ROOTS
# ============================================================

ADAPTER_SEARCH_ROOTS: Tuple[str, ...] = (
    "app",
    "adapters",
    "core",
    "services",
    "data",
    "market",
    "market_data",
    "integration",
    "integrations",
)


# ============================================================
# 19. ADAPTER FILE NAME HINTS
# ============================================================

ADAPTER_FILE_HINTS: Tuple[str, ...] = (
    "adapter",
    "market_data",
    "broker",
    "exchange",
)


# ============================================================
# 20. ADAPTER FAMILY NAME HINTS
# ============================================================

ADAPTER_FAMILY_HINTS: Dict[str, Tuple[str, ...]] = {
    "dhan": (
        "dhan",
    ),
    "kotak": (
        "kotak",
        "neo",
    ),
    "binance": (
        "binance",
    ),
    "bybit": (
        "bybit",
    ),
    "forex": (
        "forex",
        "fx",
    ),
    "commodity": (
        "commodity",
        "commodities",
    ),
}


# ============================================================
# 21. EXCLUDED DIRECTORIES
# ============================================================

ADAPTER_AUDIT_EXCLUDED_DIRS: Tuple[str, ...] = (
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "env",
    "node_modules",
    ".pytest_cache",
)


# ============================================================
# 22. DISCOVERED FILE RECORD
# ============================================================

@dataclass(frozen=True)
class AdapterFileRecord:
    path: str
    relative_path: str
    family: str
    name_match: bool
    family_match: bool


# ============================================================
# 23. ADAPTER FILE DISCOVERY
# ============================================================

def discover_existing_adapter_files() -> List[AdapterFileRecord]:
    """
    Search existing project Python files for likely adapter files.

    This is a discovery operation only.

    No files are imported.
    No files are executed.
    No files are modified.
    """

    records: List[AdapterFileRecord] = []
    seen_paths: set[str] = set()

    for root_name in ADAPTER_SEARCH_ROOTS:

        root = PROJECT_ROOT / root_name

        if not root.exists() or not root.is_dir():
            continue

        for py_file in root.rglob("*.py"):

            if py_file.name == "__init__.py":
                continue

            if any(
                excluded in py_file.parts
                for excluded in ADAPTER_AUDIT_EXCLUDED_DIRS
            ):
                continue

            normalized_path = str(py_file.resolve()).lower()

            if normalized_path in seen_paths:
                continue

            seen_paths.add(normalized_path)

            filename_lower = py_file.stem.lower()

            name_match = any(
                hint in filename_lower
                for hint in ADAPTER_FILE_HINTS
            )

            family = "unknown"
            family_match = False

            for family_name, hints in ADAPTER_FAMILY_HINTS.items():

                if any(
                    hint in filename_lower
                    for hint in hints
                ):
                    family = family_name
                    family_match = True
                    break

                path_lower = str(py_file).lower()

                if any(
                    f"{root_name}\\{family_name}\\" in path_lower
                    for _ in (0,)
                ):
                    family = family_name
                    family_match = True
                    break

            if name_match or family_match:

                relative_path = str(
                    py_file.relative_to(PROJECT_ROOT)
                )

                records.append(
                    AdapterFileRecord(
                        path=str(py_file),
                        relative_path=relative_path,
                        family=family,
                        name_match=name_match,
                        family_match=family_match,
                    )
                )

    return sorted(
        records,
        key=lambda record: (
            record.family,
            record.relative_path.lower(),
        ),
    )


# ============================================================
# 24. EXISTING ADAPTER LOCATION TEST
# ============================================================

def test_existing_adapter_locations(
    report: AdapterTestReport,
) -> List[AdapterFileRecord]:
    """
    Determine whether adapter-like Python files already exist
    anywhere inside the known project source roots.
    """

    records = discover_existing_adapter_files()

    if records:

        report.add(
            test_id="ADAPTER-LOCATION",
            adapter="ALL",
            status=PASS,
            message="Existing adapter-like Python files discovered.",
            count=len(records),
        )

    else:

        report.add(
            test_id="ADAPTER-LOCATION",
            adapter="ALL",
            status=WARN,
            message="No existing adapter-like Python files discovered.",
            count=0,
        )

    return records


# ============================================================
# 25. FAMILY LOCATION AUDIT
# ============================================================

def test_family_locations(
    report: AdapterTestReport,
    records: List[AdapterFileRecord],
) -> None:
    """
    Map discovered adapter-like files to blueprint adapter families.
    """

    for family in ADAPTER_FAMILIES:

        family_records = [
            record
            for record in records
            if record.family == family
        ]

        if family_records:

            report.add(
                test_id="ADAPTER-FAMILY-LOCATION",
                adapter=family,
                status=PASS,
                message="Existing adapter implementation candidate found.",
                files=[
                    record.relative_path
                    for record in family_records
                ],
            )

        else:

            report.add(
                test_id="ADAPTER-FAMILY-LOCATION",
                adapter=family,
                status=SKIP,
                message="No existing implementation candidate found.",
            )


# ============================================================
# 26. DUPLICATE FAMILY LOCATION TEST
# ============================================================

def test_duplicate_family_locations(
    report: AdapterTestReport,
    records: List[AdapterFileRecord],
) -> None:
    """
    Detect multiple candidate files for the same adapter family.

    This does NOT declare them wrong.

    It only reports them for architectural review because
    duplicate adapter implementations can create ambiguity.
    """

    for family in ADAPTER_FAMILIES:

        family_records = [
            record
            for record in records
            if record.family == family
        ]

        if len(family_records) <= 1:
            continue

        report.add(
            test_id="ADAPTER-DUPLICATE-CANDIDATE",
            adapter=family,
            status=WARN,
            message="Multiple adapter implementation candidates found.",
            files=[
                record.relative_path
                for record in family_records
            ],
        )


# ============================================================
# 27. UNKNOWN ADAPTER CANDIDATE TEST
# ============================================================

def test_unknown_adapter_candidates(
    report: AdapterTestReport,
    records: List[AdapterFileRecord],
) -> None:
    """
    Report adapter-like files whose family could not be mapped.

    Unknown does not mean invalid.
    It means the file requires manual architectural mapping.
    """

    unknown_records = [
        record
        for record in records
        if record.family == "unknown"
    ]

    if not unknown_records:
        return

    report.add(
        test_id="ADAPTER-UNKNOWN-CANDIDATE",
        adapter="UNKNOWN",
        status=WARN,
        message="Adapter-like files require family mapping.",
        files=[
            record.relative_path
            for record in unknown_records
        ],
    )


# ============================================================
# 28. PART 2 RUNNER
# ============================================================

def run_part2(
    report: AdapterTestReport,
) -> None:
    """
    Execute Part 2 existing-adapter location audit.

    Part 1 remains untouched.
    """

    records = test_existing_adapter_locations(report)

    test_family_locations(
        report=report,
        records=records,
    )

    test_duplicate_family_locations(
        report=report,
        records=records,
    )

    test_unknown_adapter_candidates(
        report=report,
        records=records,
    )


# ============================================================
# 29. EXTENDED MAIN
# ============================================================
#
# NOTE:
#   Part 1 main() is intentionally NOT modified.
#
#   This separate function runs Part 1 + Part 2.
#
# ============================================================

def main_part2() -> int:

    report = run_part1()

    run_part2(report)

    print_report(report)

    return get_exit_code(report)


# ============================================================
# PART 2 ENTRY POINT
# ============================================================

if __name__ == "__main__":
    raise SystemExit(main_part2())
# ============================================================
# PART 3 — ADAPTER SOURCE STRUCTURAL AUDIT
# ============================================================
#
# Purpose:
#   Audit discovered adapter source files against the
#   ROBOMLM_PLUS adapter architectural boundary.
#
# This part:
#   - READS existing adapter source files
#   - DOES NOT execute adapter code
#   - DOES NOT connect to exchanges
#   - DOES NOT modify source files
#   - DOES NOT create adapter implementations
#
# Blueprint boundary:
#
#   External Market Source
#          ↓
#   Adapter
#          ↓
#   Canonical Market Snapshot
#          ↓
#   Evidence / Intelligence
#
# Adapter MUST NOT become:
#   Decision Engine
#   Signal Generator
#   Opportunity Ranker
#   BUY/SELL Generator
#
# ============================================================


# ============================================================
# 30. STRUCTURAL AUDIT CONSTANTS
# ============================================================

ADAPTER_FORBIDDEN_SOURCE_TERMS: Tuple[str, ...] = (
    "BUY",
    "SELL",
    "TOP 10",
    "VERDICT",
)


ADAPTER_CANONICAL_TERMS: Tuple[str, ...] = (
    "Canonical Market Snapshot",
    "canonical_market_snapshot",
    "MarketSnapshot",
    "MarketData",
    "market_snapshot",
)


ADAPTER_CONNECTION_TERMS: Tuple[str, ...] = (
    "requests",
    "httpx",
    "urllib",
    "websocket",
    "WebSocket",
    "sdk",
    "client",
    "api",
)


ADAPTER_INTELLIGENCE_TERMS: Tuple[str, ...] = (
    "signal",
    "opportunity",
    "ranking",
    "rank",
    "decision",
    "verdict",
    "recommendation",
    "score",
    "trade",
)


# ============================================================
# 31. SOURCE AUDIT RECORD
# ============================================================

@dataclass(frozen=True)
class AdapterSourceAudit:
    relative_path: str
    family: str
    line_count: int
    forbidden_terms: Tuple[str, ...]
    canonical_terms: Tuple[str, ...]
    connection_terms: Tuple[str, ...]
    intelligence_terms: Tuple[str, ...]


# ============================================================
# 32. SAFE SOURCE READER
# ============================================================

def read_adapter_source(
    record: AdapterFileRecord,
) -> Optional[str]:
    """
    Read adapter source as plain text.

    The source is NEVER imported or executed.
    """

    try:

        source_path = Path(record.path)

        if not source_path.exists():
            return None

        return source_path.read_text(
            encoding="utf-8",
            errors="replace",
        )

    except Exception:
        return None


# ============================================================
# 33. TERM DETECTOR
# ============================================================

def detect_source_terms(
    source: str,
    terms: Tuple[str, ...],
) -> Tuple[str, ...]:
    """
    Detect configured architectural terms in source text.

    Detection is case-insensitive.
    """

    source_lower = source.lower()

    detected = []

    for term in terms:

        if term.lower() in source_lower:
            detected.append(term)

    return tuple(sorted(set(detected)))


# ============================================================
# 34. SINGLE ADAPTER SOURCE AUDIT
# ============================================================

def audit_adapter_source(
    record: AdapterFileRecord,
) -> Optional[AdapterSourceAudit]:
    """
    Perform non-executing structural inspection of one
    adapter candidate.
    """

    source = read_adapter_source(record)

    if source is None:
        return None

    return AdapterSourceAudit(
        relative_path=record.relative_path,
        family=record.family,
        line_count=len(source.splitlines()),
        forbidden_terms=detect_source_terms(
            source,
            ADAPTER_FORBIDDEN_SOURCE_TERMS,
        ),
        canonical_terms=detect_source_terms(
            source,
            ADAPTER_CANONICAL_TERMS,
        ),
        connection_terms=detect_source_terms(
            source,
            ADAPTER_CONNECTION_TERMS,
        ),
        intelligence_terms=detect_source_terms(
            source,
            ADAPTER_INTELLIGENCE_TERMS,
        ),
    )


# ============================================================
# 35. SOURCE READ TEST
# ============================================================

def test_adapter_source_readability(
    report: AdapterTestReport,
    records: List[AdapterFileRecord],
) -> List[AdapterSourceAudit]:
    """
    Verify that discovered adapter candidate source files can
    be read safely as text.
    """

    audits: List[AdapterSourceAudit] = []

    for record in records:

        audit = audit_adapter_source(record)

        if audit is None:

            report.add(
                test_id="ADAPTER-SOURCE-READ",
                adapter=record.family,
                status=FAIL,
                message="Adapter source could not be read.",
                file=record.relative_path,
            )

            continue

        audits.append(audit)

        report.add(
            test_id="ADAPTER-SOURCE-READ",
            adapter=record.family,
            status=PASS,
            message="Adapter source read successfully.",
            file=record.relative_path,
            lines=audit.line_count,
        )

    return audits


# ============================================================
# 36. FORBIDDEN DECISION LOGIC TEST
# ============================================================

def test_adapter_forbidden_source_terms(
    report: AdapterTestReport,
    audits: List[AdapterSourceAudit],
) -> None:
    """
    Detect explicit adapter source references to forbidden
    decision outputs.

    Presence is reported for architectural review.

    This test does NOT claim that every occurrence is business
    logic; comments/docstrings may also contain these words.
    """

    for audit in audits:

        if not audit.forbidden_terms:

            report.add(
                test_id="ADAPTER-FORBIDDEN-SOURCE",
                adapter=audit.family,
                status=PASS,
                message="No forbidden decision-output terms detected.",
                file=audit.relative_path,
            )

            continue

        report.add(
            test_id="ADAPTER-FORBIDDEN-SOURCE",
            adapter=audit.family,
            status=FAIL,
            message="Forbidden decision-output terms detected in adapter source.",
            file=audit.relative_path,
            terms=list(audit.forbidden_terms),
        )


# ============================================================
# 37. CANONICAL OUTPUT INDICATOR TEST
# ============================================================

def test_adapter_canonical_indicators(
    report: AdapterTestReport,
    audits: List[AdapterSourceAudit],
) -> None:
    """
    Check whether adapter candidates contain at least one
    canonical market-data related implementation indicator.
    """

    for audit in audits:

        if audit.canonical_terms:

            report.add(
                test_id="ADAPTER-CANONICAL-INDICATOR",
                adapter=audit.family,
                status=PASS,
                message="Canonical market-data indicator detected.",
                file=audit.relative_path,
                terms=list(audit.canonical_terms),
            )

        else:

            report.add(
                test_id="ADAPTER-CANONICAL-INDICATOR",
                adapter=audit.family,
                status=WARN,
                message="No canonical market-data indicator detected.",
                file=audit.relative_path,
            )


# ============================================================
# 38. CONNECTION IMPLEMENTATION TEST
# ============================================================

def test_adapter_connection_indicators(
    report: AdapterTestReport,
    audits: List[AdapterSourceAudit],
) -> None:
    """
    Detect external connection implementation indicators.

    This is only a structural inspection.
    """

    for audit in audits:

        if audit.connection_terms:

            report.add(
                test_id="ADAPTER-CONNECTION-INDICATOR",
                adapter=audit.family,
                status=PASS,
                message="External connection indicator detected.",
                file=audit.relative_path,
                terms=list(audit.connection_terms),
            )

        else:

            report.add(
                test_id="ADAPTER-CONNECTION-INDICATOR",
                adapter=audit.family,
                status=WARN,
                message="No external connection indicator detected.",
                file=audit.relative_path,
            )


# ============================================================
# 39. INTELLIGENCE CONTAMINATION TEST
# ============================================================

def test_adapter_intelligence_contamination(
    report: AdapterTestReport,
    audits: List[AdapterSourceAudit],
) -> None:
    """
    Detect possible intelligence-layer terminology inside
    adapter source.

    This is deliberately a WARN-level structural audit.

    It does NOT automatically declare the adapter invalid because
    terms such as 'score' or 'trade' may appear in comments,
    provider payload names, documentation, or raw market fields.
    """

    for audit in audits:

        if not audit.intelligence_terms:

            report.add(
                test_id="ADAPTER-INTELLIGENCE-CONTAMINATION",
                adapter=audit.family,
                status=PASS,
                message="No intelligence-layer terminology detected.",
                file=audit.relative_path,
            )

            continue

        report.add(
            test_id="ADAPTER-INTELLIGENCE-CONTAMINATION",
            adapter=audit.family,
            status=WARN,
            message="Possible intelligence-layer terminology detected; manual review required.",
            file=audit.relative_path,
            terms=list(audit.intelligence_terms),
        )


# ============================================================
# 40. SOURCE AUDIT SUMMARY
# ============================================================

def print_part3_summary(
    audits: List[AdapterSourceAudit],
) -> None:
    """
    Print a dedicated Part 3 source audit summary.
    """

    print("")
    print("=" * 72)
    print("PART 3 — ADAPTER SOURCE STRUCTURAL AUDIT")
    print("=" * 72)

    if not audits:

        print("No adapter source candidates available for audit.")
        print("=" * 72)
        return

    for audit in audits:

        print("")
        print(f"Adapter : {audit.family}")
        print(f"File    : {audit.relative_path}")
        print(f"Lines   : {audit.line_count}")

        print(
            "Forbidden decision terms : "
            + (
                ", ".join(audit.forbidden_terms)
                if audit.forbidden_terms
                else "NONE"
            )
        )

        print(
            "Canonical indicators     : "
            + (
                ", ".join(audit.canonical_terms)
                if audit.canonical_terms
                else "NONE"
            )
        )

        print(
            "Connection indicators    : "
            + (
                ", ".join(audit.connection_terms)
                if audit.connection_terms
                else "NONE"
            )
        )

        print(
            "Intelligence indicators  : "
            + (
                ", ".join(audit.intelligence_terms)
                if audit.intelligence_terms
                else "NONE"
            )
        )

    print("")
    print("=" * 72)


# ============================================================
# 41. PART 3 RUNNER
# ============================================================

def run_part3(
    report: AdapterTestReport,
    records: List[AdapterFileRecord],
) -> None:
    """
    Execute Part 3 structural source audit.
    """

    audits = test_adapter_source_readability(
        report=report,
        records=records,
    )

    test_adapter_forbidden_source_terms(
        report=report,
        audits=audits,
    )

    test_adapter_canonical_indicators(
        report=report,
        audits=audits,
    )

    test_adapter_connection_indicators(
        report=report,
        audits=audits,
    )

    test_adapter_intelligence_contamination(
        report=report,
        audits=audits,
    )

    print_part3_summary(audits)


# ============================================================
# 42. PART 3 COMPLETE RUNNER
# ============================================================

def main_part3() -> int:
    """
    Execute Part 1 + Part 2 + Part 3.

    Existing Part 1 and Part 2 functions remain untouched.
    """

    report = run_part1()

    records = discover_existing_adapter_files()

    run_part2(report)

    run_part3(
        report=report,
        records=records,
    )

    print_report(report)

    return get_exit_code(report)


# ============================================================
# END OF PART 3
# ============================================================
# ============================================================
# PART 4 — SINGLE FILE EXECUTION DISPATCHER
# ============================================================

def main_full_adapter_test() -> int:
    """
    Execute all completed adapter-test parts from this
    single adapter_test.py file.
    """

    report = AdapterTestReport()

    # Part 1
    test_canonical_output_definition(report)
    test_forbidden_outputs(report)
    test_adapter_responsibilities(report)

    discovered = test_adapter_discovery(report)

    for adapter_name, module_name in discovered.items():
        test_module_import(
            module_name=module_name,
            adapter_name=adapter_name,
            report=report,
        )

    # Part 2
    records = discover_existing_adapter_files()

    test_existing_adapter_locations(
        report=report,
    )

    test_family_locations(
        report=report,
        records=records,
    )

    test_duplicate_family_locations(
        report=report,
        records=records,
    )

    test_unknown_adapter_candidates(
        report=report,
        records=records,
    )

    # Part 3
    run_part3(
        report=report,
        records=records,
    )

    print_report(report)

    return get_exit_code(report)


# ============================================================
# SINGLE FILE FINAL ENTRY POINT
# ============================================================

main = main_full_adapter_test

if __name__ == "__main__":
    raise SystemExit(main_full_adapter_test())
# ============================================================
# PART 4 — ADAPTER SOURCE TRUTH AUDIT
# ============================================================
#
# Purpose:
#   Establish the physical truth of discovered adapter files
#   before making any architectural conclusion from Part 3.
#
# This part:
#   - DOES NOT modify adapter source
#   - DOES NOT execute adapter source
#   - DOES NOT connect to live APIs
#   - DOES NOT create adapter implementations
#   - DOES NOT generate BUY / SELL / TOP 10 / VERDICT
#
# Core question:
#
#   Does the discovered file actually contain source code?
#
# ============================================================


# ============================================================
# 43. PART 4 FILE ROLE DEFINITIONS
# ============================================================

ADAPTER_FILE_ROLE_HINTS: Dict[str, Tuple[str, ...]] = {
    "market_data": (
        "market_data",
        "marketdata",
    ),
    "client": (
        "client",
    ),
    "orders": (
        "order",
        "orders",
    ),
    "positions": (
        "position",
        "positions",
    ),
    "base": (
        "adapter_base",
        "base_adapter",
    ),
}


# ============================================================
# 44. PART 4 EXCLUDED NON-ADAPTER PATHS
# ============================================================

ADAPTER_NON_IMPLEMENTATION_PATH_HINTS: Tuple[str, ...] = (
    "\\ui\\",
    "/ui/",
    "\\scanner",
    "/scanner",
    "\\scanners\\",
    "/scanners/",
    "\\tests\\",
    "/tests/",
    "\\test\\",
    "/test/",
)


# ============================================================
# 45. PART 4 TRUTH RECORD
# ============================================================

@dataclass(frozen=True)
class AdapterSourceTruth:
    relative_path: str
    family: str
    file_exists: bool
    file_size_bytes: int
    raw_byte_count: int
    readable_text: bool
    encoding: str
    line_count: int
    non_whitespace_characters: int
    role: str
    likely_non_adapter: bool
    first_bytes_hex: str
    source_preview: str


# ============================================================
# 46. FILE ROLE CLASSIFIER
# ============================================================

def classify_adapter_file_role(
    record: AdapterFileRecord,
) -> str:
    """
    Classify an adapter candidate by structural filename role.

    This is classification only.
    No source execution occurs.
    """

    filename = Path(record.path).stem.lower()

    for role, hints in ADAPTER_FILE_ROLE_HINTS.items():

        if any(
            hint in filename
            for hint in hints
        ):
            return role

    return "unknown"


# ============================================================
# 47. NON-ADAPTER PATH DETECTOR
# ============================================================

def is_likely_non_adapter_file(
    record: AdapterFileRecord,
) -> bool:
    """
    Detect files located in known UI/scanner/test areas.

    Such files may contain adapter-like terminology but are
    not treated as adapter implementations by this audit.
    """

    normalized = str(
        Path(record.path)
    ).replace("\\", "/").lower()

    for hint in ADAPTER_NON_IMPLEMENTATION_PATH_HINTS:

        normalized_hint = hint.replace("\\", "/").lower()

        if normalized_hint in normalized:
            return True

    return False


# ============================================================
# 48. ENCODING-AWARE SOURCE READER
# ============================================================

def read_source_with_encoding_detection(
    path: Path,
) -> Tuple[Optional[str], str, bytes]:
    """
    Read raw bytes first.

    Then attempt safe text decoding.

    No source execution occurs.
    """

    try:

        raw = path.read_bytes()

    except Exception:
        return None, "READ_ERROR", b""

    if not raw:
        return "", "EMPTY_FILE", raw

    encodings = (
        "utf-8",
        "utf-8-sig",
        "cp1252",
        "latin-1",
    )

    for encoding in encodings:

        try:

            return (
                raw.decode(encoding),
                encoding,
                raw,
            )

        except UnicodeDecodeError:
            continue

    return None, "UNKNOWN_ENCODING", raw


# ============================================================
# 49. SINGLE FILE SOURCE TRUTH AUDIT
# ============================================================

def audit_source_truth(
    record: AdapterFileRecord,
) -> AdapterSourceTruth:

    source_path = Path(record.path)

    if not source_path.exists():

        return AdapterSourceTruth(
            relative_path=record.relative_path,
            family=record.family,
            file_exists=False,
            file_size_bytes=0,
            raw_byte_count=0,
            readable_text=False,
            encoding="MISSING",
            line_count=0,
            non_whitespace_characters=0,
            role=classify_adapter_file_role(record),
            likely_non_adapter=is_likely_non_adapter_file(record),
            first_bytes_hex="",
            source_preview="",
        )

    try:

        file_size = source_path.stat().st_size

    except Exception:

        file_size = 0

    source, encoding, raw = read_source_with_encoding_detection(
        source_path
    )

    if source is None:

        return AdapterSourceTruth(
            relative_path=record.relative_path,
            family=record.family,
            file_exists=True,
            file_size_bytes=file_size,
            raw_byte_count=len(raw),
            readable_text=False,
            encoding=encoding,
            line_count=0,
            non_whitespace_characters=0,
            role=classify_adapter_file_role(record),
            likely_non_adapter=is_likely_non_adapter_file(record),
            first_bytes_hex=raw[:32].hex(" "),
            source_preview="",
        )

    line_count = len(source.splitlines())

    non_whitespace = sum(
        1
        for char in source
        if not char.isspace()
    )

    preview_source = source.replace(
        "\x00",
        "\\x00",
    )

    preview_source = preview_source[:240]

    return AdapterSourceTruth(
        relative_path=record.relative_path,
        family=record.family,
        file_exists=True,
        file_size_bytes=file_size,
        raw_byte_count=len(raw),
        readable_text=True,
        encoding=encoding,
        line_count=line_count,
        non_whitespace_characters=non_whitespace,
        role=classify_adapter_file_role(record),
        likely_non_adapter=is_likely_non_adapter_file(record),
        first_bytes_hex=raw[:32].hex(" "),
        source_preview=preview_source,
    )


# ============================================================
# 50. SOURCE TRUTH TEST
# ============================================================

def test_adapter_source_truth(
    report: AdapterTestReport,
    records: List[AdapterFileRecord],
) -> List[AdapterSourceTruth]:

    truths: List[AdapterSourceTruth] = []

    for record in records:

        truth = audit_source_truth(record)

        truths.append(truth)

        if not truth.file_exists:

            report.add(
                test_id="ADAPTER-SOURCE-TRUTH",
                adapter=truth.family,
                status=FAIL,
                message="Adapter candidate file does not exist.",
                file=truth.relative_path,
            )

            continue

        if truth.file_size_bytes == 0:

            report.add(
                test_id="ADAPTER-SOURCE-TRUTH",
                adapter=truth.family,
                status=WARN,
                message="Adapter candidate is a zero-byte file.",
                file=truth.relative_path,
                size_bytes=truth.file_size_bytes,
                role=truth.role,
            )

            continue

        if not truth.readable_text:

            report.add(
                test_id="ADAPTER-SOURCE-TRUTH",
                adapter=truth.family,
                status=FAIL,
                message="Adapter candidate contains bytes but could not be decoded as text.",
                file=truth.relative_path,
                size_bytes=truth.file_size_bytes,
                encoding=truth.encoding,
            )

            continue

        if truth.non_whitespace_characters == 0:

            report.add(
                test_id="ADAPTER-SOURCE-TRUTH",
                adapter=truth.family,
                status=WARN,
                message="Adapter candidate contains only whitespace.",
                file=truth.relative_path,
                size_bytes=truth.file_size_bytes,
                lines=truth.line_count,
                role=truth.role,
            )

            continue

        report.add(
            test_id="ADAPTER-SOURCE-TRUTH",
            adapter=truth.family,
            status=PASS,
            message="Adapter source file contains readable source content.",
            file=truth.relative_path,
            size_bytes=truth.file_size_bytes,
            raw_bytes=truth.raw_byte_count,
            encoding=truth.encoding,
            lines=truth.line_count,
            non_whitespace_characters=truth.non_whitespace_characters,
            role=truth.role,
        )

    return truths


# ============================================================
# 51. NON-ADAPTER CLASSIFICATION TEST
# ============================================================

def test_non_adapter_classification(
    report: AdapterTestReport,
    truths: List[AdapterSourceTruth],
) -> None:
    """
    Report files that were discovered as adapter candidates but
    structurally appear to belong to UI/scanner/test areas.
    """

    for truth in truths:

        if not truth.likely_non_adapter:
            continue

        report.add(
            test_id="ADAPTER-NON-IMPLEMENTATION",
            adapter=truth.family,
            status=WARN,
            message="Candidate appears to be outside the adapter implementation boundary.",
            file=truth.relative_path,
            role=truth.role,
        )


# ============================================================
# 52. ADAPTER ROLE AUDIT
# ============================================================

def test_adapter_roles(
    report: AdapterTestReport,
    truths: List[AdapterSourceTruth],
) -> None:
    """
    Report the structural role of every discovered candidate.
    """

    for truth in truths:

        if truth.likely_non_adapter:
            continue

        if truth.role == "market_data":

            report.add(
                test_id="ADAPTER-ROLE",
                adapter=truth.family,
                status=PASS,
                message="Market-data adapter role identified.",
                file=truth.relative_path,
                role=truth.role,
            )

        elif truth.role in (
            "client",
            "orders",
            "positions",
            "base",
        ):

            report.add(
                test_id="ADAPTER-ROLE",
                adapter=truth.family,
                status=PASS,
                message="Supporting adapter role identified.",
                file=truth.relative_path,
                role=truth.role,
            )

        else:

            report.add(
                test_id="ADAPTER-ROLE",
                adapter=truth.family,
                status=WARN,
                message="Adapter candidate role requires architectural mapping.",
                file=truth.relative_path,
                role=truth.role,
            )


# ============================================================
# 53. MARKET DATA ADAPTER INVENTORY
# ============================================================

def test_market_data_adapter_inventory(
    report: AdapterTestReport,
    truths: List[AdapterSourceTruth],
) -> None:
    """
    Establish the actual market-data adapter inventory.

    UI scanners and supporting adapter files are excluded.
    """

    for family in ADAPTER_FAMILIES:

        market_data_files = [
            truth.relative_path
            for truth in truths
            if truth.family == family
            and truth.role == "market_data"
            and not truth.likely_non_adapter
        ]

        if market_data_files:

            report.add(
                test_id="ADAPTER-MARKET-DATA-INVENTORY",
                adapter=family,
                status=PASS,
                message="Market-data adapter implementation file identified.",
                files=market_data_files,
            )

        else:

            report.add(
                test_id="ADAPTER-MARKET-DATA-INVENTORY",
                adapter=family,
                status=WARN,
                message="No dedicated market-data adapter file identified.",
            )


# ============================================================
# 54. BASE ADAPTER INVENTORY
# ============================================================

def test_base_adapter_inventory(
    report: AdapterTestReport,
    truths: List[AdapterSourceTruth],
) -> None:
    """
    Identify the shared adapter base/contract layer.
    """

    base_files = [
        truth.relative_path
        for truth in truths
        if truth.role == "base"
    ]

    if base_files:

        report.add(
            test_id="ADAPTER-BASE-INVENTORY",
            adapter="ALL",
            status=PASS,
            message="Shared adapter base/contract candidate identified.",
            files=base_files,
        )

    else:

        report.add(
            test_id="ADAPTER-BASE-INVENTORY",
            adapter="ALL",
            status=WARN,
            message="No shared adapter base candidate identified.",
        )


# ============================================================
# 55. PART 4 SUMMARY
# ============================================================

def print_part4_summary(
    truths: List[AdapterSourceTruth],
) -> None:

    print("")
    print("=" * 72)
    print("PART 4 — ADAPTER SOURCE TRUTH AUDIT")
    print("=" * 72)

    if not truths:

        print("No adapter candidates available.")
        print("=" * 72)
        return

    for truth in truths:

        print("")
        print(f"Adapter      : {truth.family}")
        print(f"File         : {truth.relative_path}")
        print(f"Exists       : {truth.file_exists}")
        print(f"Size bytes   : {truth.file_size_bytes}")
        print(f"Raw bytes    : {truth.raw_byte_count}")
        print(f"Readable     : {truth.readable_text}")
        print(f"Encoding     : {truth.encoding}")
        print(f"Lines        : {truth.line_count}")
        print(
            f"Non-whitespace chars : "
            f"{truth.non_whitespace_characters}"
        )
        print(f"Role         : {truth.role}")
        print(
            f"Non-adapter  : "
            f"{truth.likely_non_adapter}"
        )

        print(
            "First bytes  : "
            + (
                truth.first_bytes_hex
                if truth.first_bytes_hex
                else "NONE"
            )
        )

        if truth.source_preview:

            preview = truth.source_preview.replace(
                "\n",
                "\\n",
            )

            print(
                "Preview      : "
                + preview
            )

        else:

            print("Preview      : NONE")

    print("")
    print("=" * 72)


# ============================================================
# 56. PART 4 RUNNER
# ============================================================

def run_part4(
    report: AdapterTestReport,
    records: List[AdapterFileRecord],
) -> None:

    truths = test_adapter_source_truth(
        report=report,
        records=records,
    )

    test_non_adapter_classification(
        report=report,
        truths=truths,
    )

    test_adapter_roles(
        report=report,
        truths=truths,
    )

    test_market_data_adapter_inventory(
        report=report,
        truths=truths,
    )

    test_base_adapter_inventory(
        report=report,
        truths=truths,
    )

    print_part4_summary(truths)


# ============================================================
# 57. FULL AUDIT RUNNER — PART 1 TO PART 4
# ============================================================

def main_full_adapter_test_part4() -> int:
    """
    Execute the complete adapter audit through Part 4.

    Earlier parts remain untouched.
    """

    report = AdapterTestReport()

    # --------------------------------------------------------
    # PART 1
    # --------------------------------------------------------

    test_canonical_output_definition(report)

    test_forbidden_outputs(report)

    test_adapter_responsibilities(report)

    discovered = test_adapter_discovery(report)

    for adapter_name, module_name in discovered.items():

        test_module_import(
            module_name=module_name,
            adapter_name=adapter_name,
            report=report,
        )

    # --------------------------------------------------------
    # PART 2
    # --------------------------------------------------------

    records = discover_existing_adapter_files()

    test_existing_adapter_locations(
        report=report,
    )

    test_family_locations(
        report=report,
        records=records,
    )

    test_duplicate_family_locations(
        report=report,
        records=records,
    )

    test_unknown_adapter_candidates(
        report=report,
        records=records,
    )

    # --------------------------------------------------------
    # PART 3
    # --------------------------------------------------------

    run_part3(
        report=report,
        records=records,
    )

    # --------------------------------------------------------
    # PART 4
    # --------------------------------------------------------

    run_part4(
        report=report,
        records=records,
    )

    # --------------------------------------------------------
    # FINAL REPORT
    # --------------------------------------------------------

    print_report(report)

    return get_exit_code(report)


# ============================================================
# END OF PART 4
# ============================================================
