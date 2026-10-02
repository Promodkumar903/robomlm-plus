# patch_trade_source_tag.py
# Tags each opened trade with strategy_id so OLD vs DEEPSEEK are separable.
# Backup PEHLE.

import os, sys, shutil
from datetime import datetime

TARGET = r"C:\Users\Administrator\ROBOMLM_PLUS\app\autorobomlm\auto_loop.py"

OLD = '''            entry_source="AUTOROBOMLM",'''

NEW = '''            entry_source=self._entry_source(),'''

METHOD = '''
    def _entry_source(self) -> str:
        """Tag trades by active strategy. OLD keeps legacy tag."""
        sid = str(getattr(self.config, "strategy_id", "OLD") or "OLD").upper()
        if sid == "OLD":
            return "AUTOROBOMLM"
        return f"AUTOROBOMLM_{sid}"
'''


def main():
    if not os.path.isfile(TARGET):
        print(f"ERROR: not found: {TARGET}")
        sys.exit(1)

    with open(TARGET, "r", encoding="utf-8") as f:
        src = f.read()

    if "_entry_source" in src:
        print("ALREADY PATCHED. Skipping.")
        sys.exit(0)

    if OLD not in src:
        print("ERROR: entry_source anchor not found.")
        sys.exit(1)

    # Insert method before _evaluate_symbol
    anchor = "    def _evaluate_symbol("
    if anchor not in src:
        print("ERROR: _evaluate_symbol not found.")
        sys.exit(1)

    src = src.replace(anchor, METHOD + "\n" + anchor, 1)
    src = src.replace(OLD, NEW, 1)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = TARGET + f".bak_{ts}"
    shutil.copy2(TARGET, bak)
    print(f"BACKUP OK: {os.path.basename(bak)}")

    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(src)

    print(f"PATCHED: {TARGET}")
    print(f'Rollback: copy /Y "{bak}" "{TARGET}"')


if __name__ == "__main__":
    main()