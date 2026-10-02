# ROBOMLM+ Trading Philosophy

**Locked decisions — do not violate without 48h data evidence.**

---

## 1. TP hit is the goal, NOT "avoid SL"

Wrong: "Design so SL doesn't hit."
Right: "Design so TP hits."

If system only tries to avoid loss, it will trade rarely, timidly, badly.

---

## 2. Signal stability > signal snapshot

A signal is NOT the current second's direction.
A signal is a **stable direction** that persists across:
- Multiple consecutive ticks (low flip rate)
- Multiple timeframes agreeing (5m, 15m, 1h)

**Rule:**
- STABLE signal → eligible for trade
- MIXED / UNSTABLE → skip, wait

Current system does NOT enforce this. Pending.

---

## 3. Candle is BYPRODUCT, not input

Real market:

If you trade on candle → you trade on result → you miss cause.

**Primary inputs:**
- Order flow (tape, DOM)
- Derivatives (basis, OI, funding)
- Obstacles (FVG, BOS, OB, VWAP, Pivots)
- Volume (delta, whale, ROC)

Candle used only for:
- Level extraction (already done)
- Absorption detection (vol vs range)

---

## 4. Raw data > indicators

Indicators (EMA, RSI, MACD) are derivative of price — lagging.
Real edge:
- Raw tape
- Live DOM
- OI changes
- Funding flow
- Whale trades

**Existing engines already collect this.** Preserve. Extend.

---

## 5. No hardcoded values

Every number must be:
- Fetched from provider, OR
- Computed from fetched data

Never invented.

**Enforcement:** Every output has `provenance` field.

---

## 6. Data before decisions

Before changing any threshold, any weight, any filter:
- Log signal
- Log outcome
- Log context (stability, TF agreement)
- Wait 24-48h
- Then decide with evidence

**No guessing.** 3 rebuilds already lost to guessing.

---

## 7. HOLD is not a loss

HOLD means "no trade taken". It is NOT correct or wrong.
Only BUY / SELL counted in accuracy.

Recorder enforces this (SKIPPED outcome).

---

## 8. One change at a time

- One file at a time
- Backup before patch
- Test after
- Verify with data
- Then next

Never "fix 5 things at once".

---

## 9. When signal flips → system missed

If signal was BEARISH at entry, and 30 sec later it's BULLISH:
- The entry was wrong (not the SL)
- Signal was unstable at entry
- Fix = stability filter, NOT tighter SL

---

## 10. Multi-market is future, not now

Crypto (Bybit, Binance) — working.
Equity (Massive), India (Dhan), Forex — provider layer ready, engines not yet.

**Do not mix until crypto is proven.**

---

## What is measured

Accuracy % = wins / resolved actionable signals.

Wins = TP_HIT + CORRECT
Losses = SL_HIT + WRONG
Pending = OPEN
Not counted = SKIPPED (HOLD)

Report source: `app/intelligence/real/signal_recorder.py`

---

## Do not touch (working)

- 13 engines in `app/intelligence/real/`
- Provider registry (`app/providers/`)
- Adapters (`app/adapters/binance`, `massive`, `bybit`)
- `universe_seed.py` (line 580 wired)

---

## Pending critical

- `auto_loop.py` — ATR-based SL/TP (should use signal SL/TP)
- Signal stability filter in `unified_signal`
- TP Runner (multi-target shift)
- Defense Score (live level strength)

---

**Version:** 1.0 — 2026-09-24
**Next review:** After 48h data