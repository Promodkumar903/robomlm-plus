import importlib
import pkgutil

import schemas.market


def test_all_market_schema_modules_import():
    failures = []

    for module_info in pkgutil.iter_modules(schemas.market.__path__):
        name = module_info.name

        if name.startswith("_"):
            continue
        if name == "test":
            continue

        module_name = f"schemas.market.{name}"

        try:
            importlib.import_module(module_name)
        except Exception as exc:
            failures.append(f"{module_name}: {type(exc).__name__}: {exc}")

    assert not failures, "Market schema import failures:\n" + "\n".join(failures)