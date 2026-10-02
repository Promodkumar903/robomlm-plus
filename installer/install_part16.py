"""Fix CSS overlap for eyebrow + heading"""
from pathlib import Path
import shutil
from datetime import datetime

CSS = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\autorobomlm\autorobomlm.css")

if not CSS.exists():
    print(f"ERROR: {CSS} not found.")
    raise SystemExit(1)

content = CSS.read_text(encoding="utf-8")

backup = CSS.with_suffix(f".css.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
shutil.copy2(CSS, backup)
print(f"BACKUP: {backup}")

if "OVERLAP FIX" in content:
    print("Already patched. No change.")
    raise SystemExit(0)

OVERRIDES = '''

/* ============================================================
   OVERLAP FIX — eyebrow label + heading stacking
   ============================================================
   The .auto-eyebrow (small label) and h2 (title) were rendering
   on the same line, causing "ACTIVE Running trades" overlap.
   Fix: stack them vertically with proper spacing.
   ============================================================ */

/* Panel header: label above title */
.auto-panel-head,
.auto-panel-head > div,
.auto-panel-head > div:first-child {
  display: flex !important;
  flex-direction: column !important;
  align-items: flex-start !important;
  gap: 4px !important;
}

.auto-panel-head {
  flex-direction: row !important;
  align-items: flex-start !important;
  justify-content: space-between !important;
}

.auto-eyebrow {
  display: block !important;
  position: static !important;
  margin: 0 !important;
  padding: 0 !important;
  font-size: 11px !important;
  line-height: 1.2 !important;
  letter-spacing: 1.2px !important;
  text-transform: uppercase !important;
  opacity: 0.7 !important;
  color: inherit !important;
  white-space: nowrap !important;
}

.auto-panel-head h2,
.auto-panel-head > div > h2,
.auto-header h2 {
  display: block !important;
  position: static !important;
  margin: 0 !important;
  padding: 0 !important;
  font-size: 20px !important;
  line-height: 1.25 !important;
  font-weight: 700 !important;
  letter-spacing: 0 !important;
}

/* Header eyebrow above title */
.auto-header > div:first-child {
  display: flex !important;
  flex-direction: column !important;
  align-items: flex-start !important;
  gap: 4px !important;
}

.auto-header .auto-eyebrow {
  margin: 0 !important;
}

.auto-header h1 {
  margin: 0 !important;
  padding: 0 !important;
  line-height: 1.15 !important;
}

.auto-header .auto-subtitle {
  margin: 6px 0 0 0 !important;
  line-height: 1.4 !important;
}

/* Decision context header: label + title with badge inline */
.auto-panel-head > div > h2 {
  display: flex !important;
  align-items: center !important;
  gap: 10px !important;
}

/* Events/Activity panel */
.auto-panel-head .auto-count {
  align-self: flex-start !important;
  margin-top: 2px !important;
}
'''

content = content.rstrip() + OVERRIDES + "\n"
CSS.write_text(content, encoding="utf-8")
print(f"UPDATED: {CSS}")
print(f"  ({CSS.stat().st_size} bytes)")
print()
print("Next:")
print("  cd C:\\Users\\Administrator\\ROBOMLM_PLUS\\frontend")
print("  npx tsc --noEmit")
print("  (then refresh browser with Ctrl+Shift+R)")