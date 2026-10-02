# patch_default_config_v2.py
# Fix _build_default_config — correct anchor.
# Backup PEHLE.

import os, sys, shutil
from datetime import datetime

TARGET = r"C:\Users\Administrator\ROBOMLM_PLUS\app\api\v1\autorobomlm_api.py"

OLD = """        sl_atr_multiplier=1.5,
        tp_atr_multiplier=3.0,
        loop_interval_sec=60,
    )
    cfg.validate()
    return cfg"""

NEW = """        sl_atr_multiplier=2.0,
        tp_atr_multiplier=4.0,
        loop_interval_sec=60,
    )
    cfg.validate()
    return cfg"""


def main():
    if not os.path.isfile(TARGET):
        print(f"ERROR: not found: {TARGET}")
        sys.exit(1)

    with open(TARGET, "r", encoding="utf-8") as f:
        src = f.read()

    if "sl_atr_multiplier=2.0" in src and "tp_atr_multiplier=4.0" in src:
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


if __name__ == "__main__":
    main()