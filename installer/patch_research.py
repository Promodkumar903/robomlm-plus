# patch_research.py
# Fix Research page: 422 error
# Reason: /api/terminal/frontend requires "symbol" query param
#         but research.ts doesn't send it.
#
# Rule: backup PEHLE, phir edit. Kuch delete nahi.

import os
import sys
import shutil
from datetime import datetime

TARGET = r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\src\api\research.ts"

OLD_SIG = '''export async function getResearch(
  signal?: AbortSignal,
): Promise<ResearchApiState> {
  let response: Response;

  try {
    response = await fetch(
      RESEARCH_ENDPOINT,
      {'''

NEW_SIG = '''const DEFAULT_RESEARCH_SYMBOL = "BTCUSDT";

export async function getResearch(
  signal?: AbortSignal,
  symbol: string = DEFAULT_RESEARCH_SYMBOL,
): Promise<ResearchApiState> {
  let response: Response;

  const safeSymbol =
    (symbol && symbol.trim()) || DEFAULT_RESEARCH_SYMBOL;

  const requestUrl =
    `${RESEARCH_ENDPOINT}?symbol=${encodeURIComponent(safeSymbol)}`;

  try {
    response = await fetch(
      requestUrl,
      {'''


def main():
    if not os.path.isfile(TARGET):
        print(f"ERROR: not found: {TARGET}")
        sys.exit(1)

    with open(TARGET, "r", encoding="utf-8") as f:
        src = f.read()

    if "DEFAULT_RESEARCH_SYMBOL" in src:
        print("ALREADY PATCHED. Skipping.")
        sys.exit(0)

    if OLD_SIG not in src:
        print("ERROR: signature block not found. File changed? Abort.")
        sys.exit(1)

    # ---- Backup FIRST ----
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = TARGET + f".bak_{ts}"
    try:
        shutil.copy2(TARGET, backup)
    except Exception as e:
        print(f"ERROR: backup failed -> {e}")
        print("Backup ke bina edit nahi hoga. Abort.")
        sys.exit(1)

    if not os.path.isfile(backup):
        print("ERROR: backup not verified. Abort.")
        sys.exit(1)

    print(f"BACKUP OK: {backup}")

    # ---- Patch ----
    new_src = src.replace(OLD_SIG, NEW_SIG, 1)

    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(new_src)

    print(f"PATCHED: {TARGET}")
    print()
    print("Rollback (agar zaroorat pade):")
    print(f'  copy /Y "{backup}" "{TARGET}"')


if __name__ == "__main__":
    main()