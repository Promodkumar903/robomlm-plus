# patch_research_v4b.py
import os, sys, shutil
from datetime import datetime

TARGET = r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\src\api\research.ts"

OLD = """      evidence: {
        ...evidenceResult,
        state: first(evidenceResult.status, evidenceResult.state),
        status: evidenceResult.status,
      },"""

NEW = """      evidence: (() => {
        const norm = record(evidenceResult.normalized);
        const conf = record(evidenceResult.conflict_result);
        const rel = record(evidenceResult.reliability_results);
        const pkg = record(evidenceResult.package);
        const supporting = numberOrNull(norm.normalized_count);
        const conflicting = numberOrNull(conf.conflict_count);
        const relKeys = Object.keys(rel);
        const provenance = relKeys.length > 0 ? relKeys.join(", ") : undefined;
        const temporal = stringOrUndefined(pkg.created_at);
        return {
          ...evidenceResult,
          state: first(evidenceResult.status, evidenceResult.state),
          status: evidenceResult.status,
          supportingCount: supporting ?? undefined,
          conflictingCount: conflicting ?? undefined,
          acceptedCount: numberOrNull(evidenceResult.accepted_count) ?? undefined,
          rejectedCount: numberOrNull(evidenceResult.rejected_count) ?? undefined,
          provenance,
          temporal,
        };
      })(),"""


def main():
    if not os.path.isfile(TARGET):
        print("ERROR: target not found")
        sys.exit(1)

    with open(TARGET, "r", encoding="utf-8") as f:
        src = f.read()

    if "evidence: (() => {" in src:
        print("ALREADY PATCHED v4b")
        sys.exit(0)

    if OLD not in src:
        print("ERROR: anchor not found")
        print("Searching for 'evidence: {' ...")
        idx = src.find("evidence: {")
        if idx >= 0:
            print("Found at char", idx, ":")
            print(repr(src[idx:idx+250]))
        sys.exit(1)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = TARGET + f".bak_{ts}"
    shutil.copy2(TARGET, backup)
    print("BACKUP OK:", backup)

    new_src = src.replace(OLD, NEW, 1)
    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(new_src)

    print("PATCHED:", TARGET)
    print("Rollback:")
    print(f'  copy /Y "{backup}" "{TARGET}"')


if __name__ == "__main__":
    main()