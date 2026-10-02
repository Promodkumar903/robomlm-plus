"""Fix heading + empty state + market display"""
from pathlib import Path
import shutil
from datetime import datetime

FILE = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\frontend\autorobomlm\index.tsx")

if not FILE.exists():
    print(f"ERROR: {FILE} not found.")
    raise SystemExit(1)

content = FILE.read_text(encoding="utf-8")
backup = FILE.with_suffix(f".tsx.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
shutil.copy2(FILE, backup)
print(f"BACKUP: {backup}")

applied = []
skipped = []

# ----------------------------------------------------------------
# FIX 1: Change "Running trades" -> "Active trades"
# ----------------------------------------------------------------
if "<h2>Active trades</h2>" in content:
    skipped.append("1: already Active trades")
elif "<h2>Running trades</h2>" in content:
    content = content.replace(
        "<h2>Running trades</h2>",
        "<h2>Active trades</h2>",
        1,
    )
    applied.append("1: heading renamed to Active trades")
else:
    skipped.append("1: heading not found")

# ----------------------------------------------------------------
# FIX 2: Better empty state for Active trades
# ----------------------------------------------------------------
old_empty = '''              Automation is scanning for opportunities. When a signal is
              confirmed, trades will appear here with entry, SL, TP and live
              P&L.'''

new_empty = '''              Click <strong>Tick</strong> above to run one scan now, or
              press <strong>Start</strong> to scan automatically. Trades will
              appear here when a signal passes grade and all gates.'''

if old_empty in content:
    content = content.replace(old_empty, new_empty, 1)
    applied.append("2: empty state text improved")
else:
    skipped.append("2: empty state text not found")

# ----------------------------------------------------------------
# FIX 3: Better empty state for Opportunities
# ----------------------------------------------------------------
old_opp_empty = '''              The scanner has not produced candidates for the {market} market
              yet.'''

new_opp_empty = '''              No candidates returned by the scanner for the {market} market.
              If this looks wrong, the discovery endpoint may ignore the
              market filter — check backend <code>/api/discovery</code>.'''

if old_opp_empty in content:
    content = content.replace(old_opp_empty, new_opp_empty, 1)
    applied.append("3: opportunities empty text improved")
else:
    skipped.append("3: opp empty text not found")

# ----------------------------------------------------------------
# FIX 4: Filter opportunities by market if data looks mismatched
# (Frontend guard - backend may ignore market param)
# ----------------------------------------------------------------
# Find where opportunities are set
old_set = '''      const opps = extractOpportunities(discRes.value).sort(sortOpportunities);
      setOpportunities(opps);'''

new_set = '''      const allOpps = extractOpportunities(discRes.value).sort(sortOpportunities);

      // Frontend guard: if backend ignored market filter, filter locally.
      // Crypto symbols typically contain "/" with USDT/BTC/USD quotes.
      const cryptoQuotes = ["USDT", "USDC", "BUSD", "BTC", "ETH"];
      const isCrypto = (sym: string) =>
        cryptoQuotes.some((q) => sym.toUpperCase().endsWith(q) || sym.toUpperCase().includes(q + "/"));

      const filtered =
        market === "CRYPTO"
          ? allOpps.filter((o) => isCrypto(o.symbol))
          : allOpps;

      // If filter left nothing but backend returned data, keep original
      // so the page is never silently empty due to filter mismatch.
      const opps = filtered.length > 0 ? filtered : allOpps;

      setOpportunities(opps);'''

if "Frontend guard" in content:
    skipped.append("4: filter already applied")
elif old_set in content:
    content = content.replace(old_set, new_set, 1)
    applied.append("4: frontend market guard added")
else:
    skipped.append("4: set opportunities line not found")

FILE.write_text(content, encoding="utf-8")

print()
print("APPLIED:")
for a in applied:
    print(f"  + {a}")
print("SKIPPED:")
for s in skipped:
    print(f"  - {s}")
print()
print(f"UPDATED: {FILE}")
print()
print("Next:")
print("  cd C:\\Users\\Administrator\\ROBOMLM_PLUS\\frontend")
print("  npx tsc --noEmit")
print("  (then refresh browser with Ctrl+Shift+R)")