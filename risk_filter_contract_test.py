from datetime import datetime, timezone, timedelta

from app.intelligence.opportunity.risk_filter import (
    RiskFilter,
    RiskPolicy,
    RiskStatus,
    RiskCondition,
)


def run_test(name, fn, failures):
    try:
        result = fn()
        print(f"[PASS] {name}: {result}")
        return result
    except Exception as exc:
        failures.append((name, f"{type(exc).__name__}: {exc}"))
        print(f"[FAIL] {name}: {type(exc).__name__}: {exc}")
        return None


def main():
    print("=== RISK FILTER END-TO-END CONTRACT TEST ===")

    now = datetime.now(timezone.utc)

    policy = RiskPolicy(
        minimum_liquidity_score=50,
        review_liquidity_score=60,
        maximum_volatility_pct=10,
        review_volatility_pct=8,
        maximum_spread_bps=50,
        review_spread_bps=30,
        minimum_risk_score=50,
        review_risk_score=60,
        require_market_match=True,
        reject_future_data=True,
    )

    engine = RiskFilter(
        policy,
        expected_market_id="TEST",
    )

    failures = []
    results = {}

    # ------------------------------------------------------------
    # NORMALIZE
    # ------------------------------------------------------------

    results["normalize_mapping"] = run_test(
        "normalize_mapping",
        lambda: engine.normalize(
            {
                "instrument_id": "I1",
                "symbol": "ABC",
                "market_id": "TEST",
                "timestamp": now,
                "liquidity_score": 75,
                "volatility_pct": 5,
                "spread_bps": 10,
                "risk_score": 75,
            }
        ),
        failures,
    )

    results["normalize_aliases"] = run_test(
        "normalize_aliases",
        lambda: engine.normalize(
            {
                "id": "I2",
                "ticker": "XYZ",
                "marketId": "TEST",
                "time": now.isoformat(),
                "lqs": 70,
                "vol_pct": 5,
            }
        ),
        failures,
    )

    # ------------------------------------------------------------
    # CONDITION
    # ------------------------------------------------------------

    safe_snapshot = engine.normalize(
        {
            "instrument_id": "I3",
            "symbol": "SAFE",
            "market_id": "TEST",
            "liquidity_score": 80,
            "volatility_pct": 3,
            "spread_bps": 5,
            "risk_score": 80,
        }
    )

    risky_snapshot = engine.normalize(
        {
            "instrument_id": "I4",
            "symbol": "RISKY",
            "market_id": "TEST",
            "liquidity_score": 40,
            "volatility_pct": 15,
            "spread_bps": 80,
            "risk_score": 20,
        }
    )

    results["_condition_safe"] = run_test(
        "_condition_safe",
        lambda: engine._condition(safe_snapshot),
        failures,
    )

    results["_condition_risky"] = run_test(
        "_condition_risky",
        lambda: engine._condition(risky_snapshot),
        failures,
    )

    # ------------------------------------------------------------
    # OBSERVABLE RISK
    # ------------------------------------------------------------

    no_risk_snapshot = engine.normalize(
        {
            "instrument_id": "I5",
            "symbol": "NONE",
            "market_id": "TEST",
        }
    )

    observable_snapshot = engine.normalize(
        {
            "instrument_id": "I6",
            "symbol": "OBS",
            "market_id": "TEST",
            "risk_score": 70,
        }
    )

    results["_has_observable_risk_false"] = run_test(
        "_has_observable_risk_false",
        lambda: engine._has_observable_risk(no_risk_snapshot),
        failures,
    )

    results["_has_observable_risk_true"] = run_test(
        "_has_observable_risk_true",
        lambda: engine._has_observable_risk(observable_snapshot),
        failures,
    )

    # ------------------------------------------------------------
    # DECISION
    # ------------------------------------------------------------

    decision_snapshot = engine.normalize(
        {
            "instrument_id": "I7",
            "symbol": "DEC",
            "market_id": "TEST",
            "risk_score": 70,
        }
    )

    results["_decision"] = run_test(
        "_decision",
        lambda: engine._decision(
            decision_snapshot,
            RiskStatus.PASS,
            RiskCondition.MODERATE,
            ["test reason"],
            ["test warning"],
        ),
        failures,
    )

    # ------------------------------------------------------------
    # FOUR PRIMARY PATHS
    # ------------------------------------------------------------

    results["PASS_path"] = run_test(
        "PASS_path",
        lambda: engine.evaluate(
            {
                "instrument_id": "P",
                "symbol": "PASS",
                "market_id": "TEST",
                "liquidity_score": 80,
                "volatility_pct": 5,
                "spread_bps": 10,
                "risk_score": 80,
            }
        ).status,
        failures,
    )

    results["REVIEW_path"] = run_test(
        "REVIEW_path",
        lambda: engine.evaluate(
            {
                "instrument_id": "R",
                "symbol": "REVIEW",
                "market_id": "TEST",
                "liquidity_score": 55,
                "volatility_pct": 9,
                "spread_bps": 20,
                "risk_score": 70,
            }
        ).status,
        failures,
    )

    results["REJECT_path"] = run_test(
        "REJECT_path",
        lambda: engine.evaluate(
            {
                "instrument_id": "X",
                "symbol": "REJECT",
                "market_id": "TEST",
                "liquidity_score": 20,
                "volatility_pct": 5,
                "risk_score": 80,
            }
        ).status,
        failures,
    )

    results["UNKNOWN_path"] = run_test(
        "UNKNOWN_path",
        lambda: engine.evaluate(
            {
                "instrument_id": "U",
                "symbol": "UNKNOWN",
                "market_id": "TEST",
            }
        ).status,
        failures,
    )

    # ------------------------------------------------------------
    # _BUILD_RESULT
    # ------------------------------------------------------------

    decisions = [
        engine.evaluate(
            {
                "instrument_id": "I8",
                "symbol": "PASS2",
                "market_id": "TEST",
                "risk_score": 80,
            }
        ),
        engine.evaluate(
            {
                "instrument_id": "I9",
                "symbol": "REJECT2",
                "market_id": "TEST",
                "risk_score": 40,
            }
        ),
        engine.evaluate(
            {
                "instrument_id": "I10",
                "symbol": "REVIEW2",
                "market_id": "TEST",
                "risk_score": 55,
            }
        ),
        engine.evaluate(
            {
                "instrument_id": "I11",
                "symbol": "UNKNOWN2",
                "market_id": "TEST",
            }
        ),
    ]

    results["_build_result"] = run_test(
        "_build_result",
        lambda: engine._build_result(decisions),
        failures,
    )

    # ------------------------------------------------------------
    # PROTECTION PATHS
    # ------------------------------------------------------------

    results["missing_market_reject"] = run_test(
        "missing_market_reject",
        lambda: engine.evaluate(
            {
                "instrument_id": "M",
                "symbol": "MISS",
                "risk_score": 80,
            }
        ).status,
        failures,
    )

    results["market_mismatch_reject"] = run_test(
        "market_mismatch_reject",
        lambda: engine.evaluate(
            {
                "instrument_id": "MM",
                "symbol": "MISMATCH",
                "market_id": "OTHER",
                "risk_score": 80,
            }
        ).status,
        failures,
    )

    results["future_timestamp_reject"] = run_test(
        "future_timestamp_reject",
        lambda: engine.evaluate(
            {
                "instrument_id": "FT",
                "symbol": "FUTURE",
                "market_id": "TEST",
                "timestamp": now + timedelta(minutes=5),
                "risk_score": 80,
            },
            now=now,
        ).status,
        failures,
    )

    results["invalid_numeric_reject"] = run_test(
        "invalid_numeric_reject",
        lambda: engine.evaluate(
            {
                "instrument_id": "INV",
                "symbol": "INVALID",
                "market_id": "TEST",
                "risk_score": "bad",
            }
        ).status,
        failures,
    )

    # ------------------------------------------------------------
    # EXPECTED STATUS ASSERTIONS
    # ------------------------------------------------------------

    expected = {
        "PASS_path": RiskStatus.PASS,
        "REVIEW_path": RiskStatus.REVIEW,
        "REJECT_path": RiskStatus.REJECT,
        "UNKNOWN_path": RiskStatus.UNKNOWN,
        "missing_market_reject": RiskStatus.REJECT,
        "market_mismatch_reject": RiskStatus.REJECT,
        "future_timestamp_reject": RiskStatus.REJECT,
        "invalid_numeric_reject": RiskStatus.REJECT,
    }

    status_failures = []

    for name, expected_status in expected.items():
        actual = results.get(name)

        if actual != expected_status:
            status_failures.append(
                (name, expected_status, actual)
            )

    print()
    print("=== EXPECTED STATUS CHECK ===")

    if status_failures:
        for item in status_failures:
            print("[FAIL]", item)
    else:
        print("[PASS] All expected status paths")

    print()
    print("=== _BUILD_RESULT CONTENT CHECK ===")

    build_result = results.get("_build_result")

    if build_result is not None:
        print("total:", build_result.total)
        print("passed:", len(build_result.passed))
        print("review:", len(build_result.review))
        print("rejected:", len(build_result.rejected))
        print("unknown:", len(build_result.unknown))

        if build_result.total == 4:
            print("[PASS] _build_result total")
        else:
            print("[FAIL] _build_result total")
            failures.append(
                (
                    "_build_result total",
                    f"expected 4, got {build_result.total}",
                )
            )

    print()
    print("=== FINAL CONTRACT RESULT ===")

    print("TESTS:", len(results))
    print("EXCEPTION_FAILURES:", len(failures))
    print("STATUS_FAILURES:", len(status_failures))

    total_failures = len(failures) + len(status_failures)

    print("TOTAL_FAILURES:", total_failures)

    if total_failures == 0:
        print("=== RISK FILTER CONTRACT TEST: PASS ===")
        return 0

    print("=== RISK FILTER CONTRACT TEST: FAIL ===")

    if failures:
        print()
        print("FAILURE DETAILS:")
        for item in failures:
            print(item)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())