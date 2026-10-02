# patch_flip_fix_v2.py
# Correct anchor for auto_loop.py D13_FLIP fix.
# Backup PEHLE.

import os, sys, shutil
from datetime import datetime

TARGET = r"C:\Users\Administrator\ROBOMLM_PLUS\app\autorobomlm\auto_loop.py"

OLD = '''            if signal_side != position.direction.value:
                self._close(position.position_id, "D13_FLIP", summary)
                continue'''

NEW = '''            if signal_side != position.direction.value:
                # MIN HOLD: 5 min (noise filter)
                hold_ok = False
                try:
                    from datetime import datetime as _dt, timezone as _tz
                    opened_str = str(getattr(position, "opened_at", "") or "")
                    if opened_str:
                        opened = _dt.fromisoformat(
                            opened_str.replace("Z", "+00:00")
                        )
                        age_sec = (
                            _dt.now(_tz.utc) - opened
                        ).total_seconds()
                        hold_ok = age_sec >= 300.0
                except Exception:
                    hold_ok = True

                if not hold_ok:
                    continue

                # STRENGTH filter: only strong flip
                try:
                    flip_strength = float(
                        signal.get("strength")
                        or signal.get("decision_score")
                        or 0.0
                    )
                except (TypeError, ValueError):
                    flip_strength = 0.0

                if flip_strength < 55.0:
                    continue

                self._close(position.position_id, "D13_FLIP", summary)
                continue'''


def main():
    if not os.path.isfile(TARGET):
        print(f"ERROR: not found: {TARGET}")
        sys.exit(1)

    with open(TARGET, "r", encoding="utf-8") as f:
        src = f.read()

    if "MIN HOLD: 5 min (noise filter)" in src:
        print("ALREADY PATCHED. Skipping.")
        sys.exit(0)

    if OLD not in src:
        print("ERROR: anchor not found.")
        sys.exit(1)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = TARGET + f".bak_{ts}"
    shutil.copy2(TARGET, bak)
    print(f"BACKUP OK: {os.path.basename(bak)}")

    src = src.replace(OLD, NEW, 1)

    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(src)

    print(f"PATCHED: {TARGET}")
    print()
    print("Rollback:")
    print(f'  copy /Y "{bak}" "{TARGET}"')


if __name__ == "__main__":
    main()