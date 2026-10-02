# patch_account_link_v2.py
# Ensures _ensure_state() is called before reading portfolio.
# Backup PEHLE.

import os, sys, shutil
from datetime import datetime

TARGET = r"C:\Users\Administrator\ROBOMLM_PLUS\app\api\account_routes.py"

OLD = '''    try:
        from app.api.v1.autorobomlm_api import _state
        port = _state.get("portfolio") if isinstance(_state, dict) else None
        if port is not None:'''

NEW = '''    try:
        from app.api.v1.autorobomlm_api import _ensure_state, _state
        _ensure_state()
        port = _state.get("portfolio") if isinstance(_state, dict) else None
        if port is not None:'''

OLD2 = '''    try:
        from app.api.v1.autorobomlm_api import _state
        loop = _state.get("loop") if isinstance(_state, dict) else None
        if loop is not None:'''

NEW2 = '''    try:
        from app.api.v1.autorobomlm_api import _ensure_state, _state
        _ensure_state()
        loop = _state.get("loop") if isinstance(_state, dict) else None
        if loop is not None:'''


def main():
    if not os.path.isfile(TARGET):
        print(f"ERROR: not found: {TARGET}")
        sys.exit(1)

    with open(TARGET, "r", encoding="utf-8") as f:
        src = f.read()

    if "_ensure_state, _state" in src:
        print("ALREADY PATCHED v2. Skipping.")
        sys.exit(0)

    if OLD not in src:
        print("ERROR: anchor1 not found.")
        sys.exit(1)
    if OLD2 not in src:
        print("ERROR: anchor2 not found.")
        sys.exit(1)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    bak = TARGET + f".bak_{ts}"
    shutil.copy2(TARGET, bak)
    print(f"BACKUP OK: {os.path.basename(bak)}")

    src = src.replace(OLD, NEW, 1).replace(OLD2, NEW2, 1)

    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(src)

    print(f"PATCHED: {TARGET}")
    print(f'Rollback: copy /Y "{bak}" "{TARGET}"')


if __name__ == "__main__":
    main()