"""Strategy comparison logger.

Appends one record per strategy decision to data/strategy_decisions.jsonl.
Never raises — logging failures must not break the trading loop.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

LOG_DIR = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\data")
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "strategy_decisions.jsonl"


def log_strategy_decision(
    *,
    symbol: str,
    signal: Mapping[str, Any],
    allowed: bool,
    reason: str,
    strategy_id: str,
) -> None:
    """Append one decision record. Never raises."""
    try:
        rec = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "strategy_id": str(strategy_id or "UNKNOWN"),
            "symbol": symbol,
            "allowed": bool(allowed),
            "reason": str(reason or ""),
            "direction": signal.get("direction"),
            "action": signal.get("action"),
            "strength": signal.get("strength") or signal.get("decision_score"),
            "confidence": signal.get("confidence"),
            "trade_quality": signal.get("trade_quality") or signal.get("grade"),
            "risk_level": signal.get("risk_level"),
        }
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, default=str) + "\n")
    except Exception:
        # Never break the loop for logging.
        pass
