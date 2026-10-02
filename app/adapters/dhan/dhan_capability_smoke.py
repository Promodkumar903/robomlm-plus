from __future__ import annotations

import csv
import io
import os
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any, Mapping

import requests

from app.adapters.dhan.dhan_client import DhanClient


INSTRUMENT_MASTER_URL = (
    "https://images.dhan.co/api-data/api-scrip-master-detailed.csv"
)


class SmokeStatus:
    PASS = "PASS"
    FAIL = "FAIL"
    NOT_SUPPORTED = "NOT_SUPPORTED"


@dataclass(frozen=True, slots=True)
class SmokeResult:
    capability: str
    status: str
    exchange_segment: str | None = None
    symbol: str | None = None
    security_id: str | None = None
    detail: str | None = None
    api: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "capability": self.capability,
            "status": self.status,
            "exchange_segment": self.exchange_segment,
            "symbol": self.symbol,
            "security_id": self.security_id,
            "detail": self.detail,
            "api": self.api,
        }


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()

    if not value:
        raise RuntimeError(
            f"Missing environment variable: {name}"
        )

    return value


def _download_instrument_master() -> list[dict[str, str]]:
    response = requests.get(
        INSTRUMENT_MASTER_URL,
        timeout=30,
    )

    response.raise_for_status()

    text = response.content.decode(
        "utf-8-sig",
        errors="replace",
    )

    reader = csv.DictReader(
        io.StringIO(text)
    )

    rows: list[dict[str, str]] = []

    for row in reader:
        cleaned = {
            str(key).strip(): (
                str(value).strip()
                if value is not None
                else ""
            )
            for key, value in row.items()
        }

        rows.append(cleaned)

    if not rows:
        raise RuntimeError(
            "Dhan instrument master returned no rows"
        )

    return rows


def _exchange_segment(
    row: Mapping[str, str],
) -> str:
    """
    Convert Dhan instrument-master identity into
    the exchange-segment identifiers expected by
    Dhan marketfeed APIs.
    """

    exchange = (
        row.get("EXCH_ID", "")
        .strip()
        .upper()
    )

    segment = (
        row.get("SEGMENT", "")
        .strip()
        .upper()
    )

    if exchange == "NSE" and segment == "E":
        return "NSE_EQ"

    if exchange == "NSE" and segment == "I":
        return "IDX_I"

    if exchange == "NSE" and segment == "D":
        return "NSE_FNO"

    if exchange == "BSE" and segment == "E":
        return "BSE_EQ"

    if exchange == "BSE" and segment == "I":
        return "IDX_I"

    if exchange == "BSE" and segment == "D":
        return "BSE_FNO"

    if exchange == "MCX":
        return "MCX_COMM"

    if exchange == "NCDEX":
        return "NCDEX_COMM"

    return ""


def _security_id(
    row: Mapping[str, str],
) -> str:
    return (
        row.get("SECURITY_ID", "")
        .strip()
    )


def _symbol(
    row: Mapping[str, str],
) -> str:
    for field in (
        "SYMBOL_NAME",
        "DISPLAY_NAME",
        "UNDERLYING_SYMBOL",
    ):
        value = row.get(field, "").strip()

        if value:
            return value

    return ""


def _underlying_symbol(
    row: Mapping[str, str],
) -> str:
    return (
        row.get("UNDERLYING_SYMBOL", "")
        .strip()
    )


def _instrument_type(
    row: Mapping[str, str],
) -> str:
    return (
        row.get("INSTRUMENT_TYPE", "")
        .strip()
        .upper()
    )


def _option_type(
    row: Mapping[str, str],
) -> str:
    return (
        row.get("OPTION_TYPE", "")
        .strip()
        .upper()
    )


def _expiry_date(
    row: Mapping[str, str],
) -> date | None:
    raw = (
        row.get("SM_EXPIRY_DATE", "")
        .strip()
    )

    if not raw:
        return None

    formats = (
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
    )

    for fmt in formats:
        try:
            return datetime.strptime(
                raw,
                fmt,
            ).date()
        except ValueError:
            continue

    return None


def _is_current_or_future(
    row: Mapping[str, str],
) -> bool:
    expiry = _expiry_date(row)

    if expiry is None:
        return True

    return expiry >= date.today()


def _find_equity(
    instruments: list[dict[str, str]],
) -> dict[str, str] | None:
    requested = os.getenv(
        "DHAN_EQUITY_SYMBOL",
        "RELIANCE",
    ).strip().upper()

    candidates = []

    for row in instruments:
        if _exchange_segment(row) != "NSE_EQ":
            continue

        symbol = (
            row.get("SYMBOL_NAME", "")
            .strip()
            .upper()
        )

        if symbol == requested:
            candidates.append(row)

    return candidates[0] if candidates else None


def _find_index(
    instruments: list[dict[str, str]],
) -> dict[str, str] | None:
    requested = os.getenv(
        "DHAN_INDEX_SYMBOL",
        "NIFTY",
    ).strip().upper()

    candidates = []

    for row in instruments:
        if _exchange_segment(row) != "IDX_I":
            continue

        values = {
            row.get("SYMBOL_NAME", "")
            .strip()
            .upper(),
            row.get("UNDERLYING_SYMBOL", "")
            .strip()
            .upper(),
            row.get("DISPLAY_NAME", "")
            .strip()
            .upper(),
        }

        if requested in values:
            candidates.append(row)

    return candidates[0] if candidates else None


def _find_future(
    instruments: list[dict[str, str]],
    underlying: str,
    *,
    commodity: bool = False,
) -> dict[str, str] | None:
    target_segment = (
        "MCX_COMM"
        if commodity
        else "NSE_FNO"
    )

    allowed_types = (
        {"FUTCOM"}
        if commodity
        else {"FUTIDX", "FUTSTK"}
    )

    requested = underlying.strip().upper()

    candidates = []

    for row in instruments:
        if _exchange_segment(row) != target_segment:
            continue

        if _instrument_type(row) not in allowed_types:
            continue

        if not _is_current_or_future(row):
            continue

        values = {
            row.get("UNDERLYING_SYMBOL", "")
            .strip()
            .upper(),
            row.get("SYMBOL_NAME", "")
            .strip()
            .upper(),
        }

        if requested not in values:
            continue

        candidates.append(row)

    candidates.sort(
        key=lambda row: (
            _expiry_date(row)
            or date.max,
            _security_id(row),
        )
    )

    return candidates[0] if candidates else None


def _find_option(
    instruments: list[dict[str, str]],
    underlying: str,
    option_type: str,
) -> dict[str, str] | None:
    requested_segment = os.getenv(
        "DHAN_OPTION_SEGMENT",
        "NSE_FNO",
    ).strip().upper()

    requested = underlying.strip().upper()
    requested_option = option_type.strip().upper()

    candidates = []

    for row in instruments:
        if _exchange_segment(row) != requested_segment:
            continue

        if _instrument_type(row) not in {
            "OPTIDX",
            "OPTSTK",
        }:
            continue

        if _option_type(row) != requested_option:
            continue

        if not _is_current_or_future(row):
            continue

        values = {
            row.get("UNDERLYING_SYMBOL", "")
            .strip()
            .upper(),
            row.get("SYMBOL_NAME", "")
            .strip()
            .upper(),
        }

        if requested not in values:
            continue

        candidates.append(row)

    candidates.sort(
        key=lambda row: (
            _expiry_date(row)
            or date.max,
            _security_id(row),
        )
    )

    return candidates[0] if candidates else None


def _instrument_label(
    row: Mapping[str, str],
) -> tuple[str, str, str]:
    return (
        _exchange_segment(row),
        _symbol(row),
        _security_id(row),
    )


def _quote_test(
    client: DhanClient,
    *,
    capability: str,
    row: Mapping[str, str],
) -> SmokeResult:
    segment, symbol, security_id = (
        _instrument_label(row)
    )

    if not segment:
        return SmokeResult(
            capability=capability,
            status=SmokeStatus.FAIL,
            symbol=symbol or None,
            security_id=security_id or None,
            detail=(
                "Could not map instrument-master "
                "EXCH_ID/SEGMENT to Dhan marketfeed segment"
            ),
        )

    if not security_id:
        return SmokeResult(
            capability=capability,
            status=SmokeStatus.FAIL,
            exchange_segment=segment,
            symbol=symbol or None,
            detail="Missing SECURITY_ID",
        )

    try:
        response = client.post(
            "/marketfeed/quote",
            payload={
                segment: [int(security_id)],
            },
        )
    except Exception as exc:
        return SmokeResult(
            capability=capability,
            status=SmokeStatus.FAIL,
            exchange_segment=segment,
            symbol=symbol or None,
            security_id=security_id,
            detail=str(exc),
            api="/marketfeed/quote",
        )

    if not isinstance(response, Mapping):
        return SmokeResult(
            capability=capability,
            status=SmokeStatus.FAIL,
            exchange_segment=segment,
            symbol=symbol or None,
            security_id=security_id,
            detail="Dhan response is not a JSON object",
            api="/marketfeed/quote",
        )

    data = response.get("data")

    if not isinstance(data, Mapping):
        return SmokeResult(
            capability=capability,
            status=SmokeStatus.FAIL,
            exchange_segment=segment,
            symbol=symbol or None,
            security_id=security_id,
            detail="Missing data object",
            api="/marketfeed/quote",
        )

    segment_data = data.get(segment)

    if not isinstance(segment_data, Mapping):
        return SmokeResult(
            capability=capability,
            status=SmokeStatus.NOT_SUPPORTED,
            exchange_segment=segment,
            symbol=symbol or None,
            security_id=security_id,
            detail=(
                f"Real response did not contain "
                f"segment {segment}"
            ),
            api="/marketfeed/quote",
        )

    instrument = segment_data.get(
        str(security_id)
    )

    if not isinstance(instrument, Mapping):
        return SmokeResult(
            capability=capability,
            status=SmokeStatus.FAIL,
            exchange_segment=segment,
            symbol=symbol or None,
            security_id=security_id,
            detail=(
                "Real response did not contain "
                "requested security"
            ),
            api="/marketfeed/quote",
        )

    if "last_price" not in instrument:
        return SmokeResult(
            capability=capability,
            status=SmokeStatus.FAIL,
            exchange_segment=segment,
            symbol=symbol or None,
            security_id=security_id,
            detail=(
                "Real response received but "
                "last_price is missing"
            ),
            api="/marketfeed/quote",
        )

    return SmokeResult(
        capability=capability,
        status=SmokeStatus.PASS,
        exchange_segment=segment,
        symbol=symbol or None,
        security_id=security_id,
        detail="Real Dhan quote response validated",
        api="/marketfeed/quote",
    )


def _not_found(
    capability: str,
    detail: str,
) -> SmokeResult:
    return SmokeResult(
        capability=capability,
        status=SmokeStatus.NOT_SUPPORTED,
        detail=detail,
    )


def _run() -> list[SmokeResult]:
    client_id = _required_env(
        "DHAN_CLIENT_ID"
    )

    access_token = _required_env(
        "DHAN_ACCESS_TOKEN"
    )

    client = DhanClient(
        client_id=client_id,
        access_token=access_token,
    )

    instruments = _download_instrument_master()

    results: list[SmokeResult] = []

    try:
        equity = _find_equity(
            instruments
        )

        if equity is None:
            results.append(
                _not_found(
                    "EQUITY_SPOT",
                    (
                        "No current NSE equity "
                        "instrument found"
                    ),
                )
            )
        else:
            results.append(
                _quote_test(
                    client,
                    capability="EQUITY_SPOT",
                    row=equity,
                )
            )

        index = _find_index(
            instruments
        )

        if index is None:
            results.append(
                _not_found(
                    "INDEX",
                    (
                        "No current index instrument "
                        "found"
                    ),
                )
            )
        else:
            results.append(
                _quote_test(
                    client,
                    capability="INDEX",
                    row=index,
                )
            )

        future = _find_future(
            instruments,
            os.getenv(
                "DHAN_FUTURE_UNDERLYING",
                "NIFTY",
            ),
        )

        if future is None:
            results.append(
                _not_found(
                    "FUTURES",
                    (
                        "No current NSE index/stock "
                        "future found"
                    ),
                )
            )
        else:
            results.append(
                _quote_test(
                    client,
                    capability="FUTURES",
                    row=future,
                )
            )

        option_underlying = os.getenv(
            "DHAN_OPTION_UNDERLYING",
            "NIFTY",
        )

        for option_type, capability in (
            ("CE", "CE"),
            ("PE", "PE"),
        ):
            option = _find_option(
                instruments,
                option_underlying,
                option_type,
            )

            if option is None:
                results.append(
                    _not_found(
                        capability,
                        (
                            f"No current {option_underlying} "
                            f"{option_type} found"
                        ),
                    )
                )
            else:
                results.append(
                    _quote_test(
                        client,
                        capability=capability,
                        row=option,
                    )
                )

        commodities = {
            "GOLD": "GOLD",
            "SILVER": "SILVER",
            "CRUDE_OIL": "CRUDEOIL",
            "NATURAL_GAS": "NATURALGAS",
        }

        for capability, underlying in commodities.items():
            commodity = _find_future(
                instruments,
                underlying,
                commodity=True,
            )

            if commodity is None:
                results.append(
                    _not_found(
                        capability,
                        (
                            f"No current MCX "
                            f"{underlying} future found"
                        ),
                    )
                )
            else:
                results.append(
                    _quote_test(
                        client,
                        capability=capability,
                        row=commodity,
                    )
                )

    finally:
        client.close()

    return results


def main() -> None:
    results = _run()

    print()
    print("DHAN CAPABILITY SMOKE TEST")
    print("===========================")

    for result in results:
        print(
            f"{result.status:15} "
            f"{result.capability:15} "
            f"{result.exchange_segment or '-':10} "
            f"{result.symbol or '-':30} "
            f"{result.security_id or '-':12}"
        )

        if result.detail:
            print(
                f"                 {result.detail}"
            )

    print()
    print("SUMMARY")
    print("-------")

    counts = {
        SmokeStatus.PASS: 0,
        SmokeStatus.FAIL: 0,
        SmokeStatus.NOT_SUPPORTED: 0,
    }

    for result in results:
        counts[result.status] += 1

    for status, count in counts.items():
        print(
            f"{status}: {count}"
        )


if __name__ == "__main__":
    main()