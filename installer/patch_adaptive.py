# patch_adaptive.py
# Make confluence check optional (skip if components missing).
# Backup PEHLE.

import os, sys, shutil
from datetime import datetime

TARGET = r"C:\Users\Administrator\ROBOMLM_PLUS\app\strategies\deepseek_strategy\strategy.py"

OLD = '''        # 7. Confluence
        c = data.components or {}
        scores = [
            self._num(c.get("flow")),
            self._num(c.get("derivative")),
            self._num(c.get("volume")),
            self._num(c.get("obstacle")),
            self._num(c.get("context")),
            self._num(c.get("regime")),
        ]
        aligned = sum(1 for s in scores if s >= self.CONFLUENCE_COMPONENT_MIN)
        if aligned < self.MIN_CONFLUENCE:
            return self._reject(f"CONFLUENCE_{aligned}_OF_6")

        # 8. Context minimum
        context = self._num(c.get("context"))
        if context < self.MIN_CONTEXT:
            return self._reject(f"CONTEXT_{context:.1f}")'''

NEW = '''        # 7. Confluence — only if components present in signal
        c = data.components or {}
        has_components = any(
            self._num(c.get(k)) > 0 for k in
            ("flow", "derivative", "volume", "obstacle", "context", "regime")
        )
        scores = [
            self._num(c.get("flow")),
            self._num(c.get("derivative")),
            self._num(c.get("volume")),
            self._num(c.get("obstacle")),
            self._num(c.get("context")),
            self._num(c.get("regime")),
        ]
        aligned = 0
        context = 0.0
        if has_components:
            aligned = sum(1 for s in scores if s >= self.CONFLUENCE_COMPONENT_MIN)
            if aligned < self.MIN_CONFLUENCE:
                return self._reject(f"CONFLUENCE_{aligned}_OF_6")
            context = self._num(c.get("context"))
            if context < self.MIN_CONTEXT:
                return self._reject(f"CONTEXT_{context:.1f}")'''


def main():
    if not os.path.isfile(TARGET):
        print(f"ERROR: {TARGET} not found")
        sys.exit(1)

    with open(TARGET, "r", encoding="utf-8") as f:
        src = f.read()

    if "has_components" in src:
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