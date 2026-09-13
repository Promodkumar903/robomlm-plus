import importlib


ENUM_CLASSES = {
    "market_data_acknowledgement_stat": "MarketDataAcknowledgementStatus",
    "market_data_channel_message_status": "MarketDataChannelMessageStatus",
    "market_data_channel_message_type": "MarketDataChannelMessageType",
    "market_data_channel_status": "MarketDataChannelStatus",
    "market_data_channel_type": "MarketDataChannelType",
    "market_data_subscription_status": "MarketDataSubscriptionStatus",
}


def test_market_enum_like_classes_are_available():
    failures = []

    for module_name, class_name in ENUM_CLASSES.items():
        try:
            module = importlib.import_module(f"schemas.market.{module_name}")
            cls = getattr(module, class_name)

            if not callable(cls):
                failures.append(
                    f"{module_name}.{class_name}: class is not callable"
                )

            if not hasattr(cls, "__dict__"):
                failures.append(
                    f"{module_name}.{class_name}: class dictionary unavailable"
                )

        except Exception as exc:
            failures.append(
                f"{module_name}.{class_name}: "
                f"{type(exc).__name__}: {exc}"
            )

    assert not failures, (
        "Market enum-like vocabulary failures:\n"
        + "\n".join(failures)
    )


def test_market_cashflow_type_is_vocabulary_class():
    module = importlib.import_module(
        "schemas.market.market_cashflow_type"
    )
    cls = getattr(module, "MarketCashflowType")

    assert callable(cls)
    assert hasattr(cls, "__dict__")

    # MarketCashflowType is a controlled vocabulary/constants class.
    # It must not be treated as CashflowTypeDefinition.
    assert cls.__name__ == "MarketCashflowType"