from app.v6_bridge.v6_bridge import V6Bridge


def check(name, condition):
    if condition:
        print(f"[PASS] {name}")
        return True
    print(f"[FAIL] {name}")
    return False


def main():
    print("=" * 90)
    print("V6 BRIDGE - CORRECTED 12 RUNTIME CONTRACT TESTS")
    print("=" * 90)

    passed = 0
    failed = 0

    bridge = V6Bridge()

    # 01 - valid payload translation
    try:
        payload = {
            "event_type": "MARKET_UPDATE",
            "action": "ANALYZE",
            "symbol": "BTCUSDT",
            "price": 100000,
        }

        result = bridge.translate(payload)

        ok = (
            result.success is True
            and isinstance(result.translated, dict)
            and result.translated.get("event_type") == "MARKET_UPDATE"
            and result.translated.get("action") == "ANALYZE"
        )

        if check("01 - valid payload translation", ok):
            passed += 1
        else:
            failed += 1

    except Exception as e:
        print(f"[FAIL] 01 - valid payload translation :: {type(e).__name__}: {e}")
        failed += 1

    # 02 - missing event_type rejected
    try:
        bridge.translate({
            "action": "ANALYZE",
            "symbol": "BTCUSDT",
        })
        print("[FAIL] 02 - missing event_type rejected")
        failed += 1
    except Exception:
        print("[PASS] 02 - missing event_type rejected")
        passed += 1

    # 03 - missing action rejected
    try:
        bridge.translate({
            "event_type": "MARKET_UPDATE",
            "symbol": "BTCUSDT",
        })
        print("[FAIL] 03 - missing action rejected")
        failed += 1
    except Exception:
        print("[PASS] 03 - missing action rejected")
        passed += 1

    # 04 - disabled bridge blocks translation
    try:
        bridge.set_enabled(False)

        try:
            bridge.translate({
                "event_type": "MARKET_UPDATE",
                "action": "ANALYZE",
            })
            print("[FAIL] 04 - disabled bridge blocks translation")
            failed += 1
        except Exception:
            print("[PASS] 04 - disabled bridge blocks translation")
            passed += 1

        bridge.set_enabled(True)

    except Exception as e:
        print(f"[FAIL] 04 - disabled bridge blocks translation :: {type(e).__name__}: {e}")
        failed += 1
        bridge.set_enabled(True)

    # 05 - unknown-field preservation
    try:
        payload = {
            "event_type": "MARKET_UPDATE",
            "action": "ANALYZE",
            "custom_test_field": "PRESERVE_ME",
        }

        result = bridge.translate(payload)

        ok = (
            result.translated.get("unknown_fields", {}).get("custom_test_field")
            == "PRESERVE_ME"
            and "custom_test_field" in result.preserved_fields
        )

        if check("05 - unknown-field preservation", ok):
            passed += 1
        else:
            failed += 1

    except Exception as e:
        print(f"[FAIL] 05 - unknown-field preservation :: {type(e).__name__}: {e}")
        failed += 1

    # 06 - original payload preservation
    try:
        payload = {
            "event_type": "MARKET_UPDATE",
            "action": "ANALYZE",
            "custom_original": 123,
        }

        result = bridge.translate(payload)

        ok = (
            result.original == payload
            and result.translated.get("original_payload") == payload
        )

        if check("06 - original payload preservation", ok):
            passed += 1
        else:
            failed += 1

    except Exception as e:
        print(f"[FAIL] 06 - original payload preservation :: {type(e).__name__}: {e}")
        failed += 1

    # 07 - input immutability / handler mutation isolation
    try:
        payload = {
            "event_type": "MARKET_UPDATE",
            "action": "ANALYZE",
            "value": 100,
        }

        original = dict(payload)

        def mutating_handler(data):
            data["value"] = 999999
            return data

        bridge.set_translation_handler(mutating_handler)

        bridge.translate(payload)

        bridge.set_translation_handler(None)

        ok = payload == original

        if check("07 - handler mutation isolation", ok):
            passed += 1
        else:
            failed += 1

    except Exception as e:
        print(f"[FAIL] 07 - handler mutation isolation :: {type(e).__name__}: {e}")
        failed += 1
        bridge.set_translation_handler(None)

    # 08 - handler exception propagates
    try:
        def failing_handler(data):
            raise RuntimeError("TEST_HANDLER_FAILURE")

        bridge.set_translation_handler(failing_handler)

        try:
            bridge.translate({
                "event_type": "MARKET_UPDATE",
                "action": "ANALYZE",
            })
            print("[FAIL] 08 - handler exception propagates")
            failed += 1
        except RuntimeError:
            print("[PASS] 08 - handler exception propagates")
            passed += 1

        bridge.set_translation_handler(None)

    except Exception as e:
        print(f"[FAIL] 08 - handler exception propagates :: {type(e).__name__}: {e}")
        failed += 1
        bridge.set_translation_handler(None)

    # 09 - dispatch without handler
    try:
        bridge.set_translation_handler(None)

        result = bridge.dispatch({
            "event_type": "MARKET_UPDATE",
            "action": "ANALYZE",
        })

        ok = result.success is True

        if check("09 - dispatch without handler", ok):
            passed += 1
        else:
            failed += 1

    except Exception as e:
        print(f"[FAIL] 09 - dispatch without handler :: {type(e).__name__}: {e}")
        failed += 1

    # 10 - set_enabled False/True behavior
    try:
        bridge.set_enabled(False)
        first = bridge.enabled is False

        bridge.set_enabled(True)
        second = bridge.enabled is True

        ok = first and second

        if check("10 - set_enabled False/True behavior", ok):
            passed += 1
        else:
            failed += 1

    except Exception as e:
        print(f"[FAIL] 10 - set_enabled False/True behavior :: {type(e).__name__}: {e}")
        failed += 1

    # 11 - translate_many
    try:
        payloads = [
            {
                "event_type": "MARKET_UPDATE",
                "action": "ANALYZE",
                "symbol": "BTCUSDT",
            },
            {
                "event_type": "MARKET_UPDATE",
                "action": "ANALYZE",
                "symbol": "ETHUSDT",
            },
        ]

        results = bridge.translate_many(payloads)

        ok = (
            isinstance(results, list)
            and len(results) == 2
            and all(r.success is True for r in results)
        )

        if check("11 - translate_many", ok):
            passed += 1
        else:
            failed += 1

    except Exception as e:
        print(f"[FAIL] 11 - translate_many :: {type(e).__name__}: {e}")
        failed += 1

    # 12 - no execution / broker methods exposed
    try:
        forbidden = [
            "execute",
            "place_order",
            "submit_order",
            "cancel_order",
            "broker",
        ]

        public_names = [
            name
            for name in dir(bridge)
            if not name.startswith("_")
        ]

        found = [name for name in forbidden if name in public_names]

        ok = len(found) == 0

        if check("12 - no execution/broker methods exposed", ok):
            passed += 1
        else:
            print(f"      Forbidden public names found: {found}")
            failed += 1

    except Exception as e:
        print(f"[FAIL] 12 - no execution/broker methods exposed :: {type(e).__name__}: {e}")
        failed += 1

    print("=" * 90)
    print(f"RESULT: PASS={passed} FAIL={failed} TOTAL={passed + failed}")
    print("=" * 90)


if __name__ == "__main__":
    main()