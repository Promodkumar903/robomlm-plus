# patch_deepseek_v1_1.py
# Tune DeepSeek strategy: allow B grade with higher bar.
# Rule: backup PEHLE.

import os, sys, shutil
from datetime import datetime

TARGET = r"C:\Users\Administrator\ROBOMLM_PLUS\app\strategies\deepseek_strategy\strategy.py"

OLD = '    ALLOWED_GRADES = {"A+", "A", "B+"}'
NEW = '''    # Grade B allowed only if other quality bars are met.
    ALLOWED_GRADES = {"A+", "A", "B+", "B"}
    B_GRADE_MIN_STRENGTH = 55.0
    B_GRADE_MIN_CONFIDENCE = 60.0'''

OLD2 = '''        # 5. Strength gate
        if data.strength < self.MIN_STRENGTH:
            return self._reject(f"STRENGTH_{data.strength:.1f}")

        # 6. Confidence gate
        if data.confidence < self.MIN_CONFIDENCE:
            return self._reject(f"CONFIDENCE_{data.confidence:.1f}")'''

NEW2 = '''        # 5. Strength gate
        min_strength = self.MIN_STRENGTH
        min_confidence = self.MIN_CONFIDENCE

        # Grade B — stricter bar
        if data.trade_quality == "B":
            min_strength = self.B_GRADE_MIN_STRENGTH
            min_confidence = self.B_GRADE_MIN_CONFIDENCE

        if data.strength < min_strength:
            return self._reject(f"STRENGTH_{data.strength:.1f}")

        # 6. Confidence gate
        if data.confidence < min_confidence:
            return self._reject(f"CONFIDENCE_{data.confidence:.1f}")'''


def main():
    if not os.path.isfile(TARGET):
        print(f"ERROR: {TARGET} not found")
        sys.exit(1)

    with open(TARGET, "r", encoding="utf-8") as f:
        src = f.read()

    if "B_GRADE_MIN_STRENGTH" in src:
        print("ALREADY PATCHED v1.1")
        sys.exit(0)

    if OLD not in src:
        print("ERROR: ALLOWED_GRADES anchor not found")
        sys.exit(1)
    if OLD2 not in src:
        print("ERROR: strength/confidence anchor not found")
        sys.exit(1)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = TARGET + f".bak_{ts}"
    shutil.copy2(TARGET, bak)
    print(f"BACKUP OK: {os.path.basename(bak)}")

    new_src = src.replace(OLD, NEW, 1).replace(OLD2, NEW2, 1)

    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(new_src)

    print(f"PATCHED: {TARGET}")


if __name__ == "__main__":
    main()