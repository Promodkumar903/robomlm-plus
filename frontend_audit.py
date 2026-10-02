from pathlib import Path
import re

ROOT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\frontend")

print("=" * 90)
print("ROBOMLM_PLUS FRONTEND ACTIVE-WIRING AUDIT")
print("=" * 90)
print("ROOT:", ROOT)

# ------------------------------------------------------------
# 1. ACTIVE SOURCE FILES
# ------------------------------------------------------------
print("\n[1] ACTIVE TS / TSX / JS / JSX FILES")

active_files = []

for p in ROOT.rglob("*"):
    if not p.is_file():
        continue

    rel = p.relative_to(ROOT)
    name = p.name.lower()

    if "node_modules" in rel.parts:
        continue
    if "dist" in rel.parts:
        continue
    if ".bak" in name:
        continue
    if ".broken" in name:
        continue
    if ".v1" in name or ".v2" in name or ".v3" in name:
        continue
    if "broken" in name:
        continue

    if p.suffix.lower() in {".ts", ".tsx", ".js", ".jsx"}:
        active_files.append(p)

for p in sorted(active_files):
    print(" ", p.relative_to(ROOT))


# ------------------------------------------------------------
# 2. APP.TSX ROUTES
# ------------------------------------------------------------
print("\n[2] ROUTES FROM src/App.tsx")

APP = ROOT / "src" / "App.tsx"

if not APP.exists():
    print("  ERROR: src/App.tsx NOT FOUND")
else:
    app_text = APP.read_text(encoding="utf-8", errors="ignore")

    route_pattern = re.compile(
        r'<Route\s+path=["\']([^"\']+)["\']\s+element=\{<([A-Za-z0-9_]+)'
    )

    routes = route_pattern.findall(app_text)

    if not routes:
        print("  No routes detected.")
    else:
        for path, component in routes:
            print(f"  {path:25} -> {component}")


# ------------------------------------------------------------
# 3. IMPORTS IN APP.TSX
# ------------------------------------------------------------
print("\n[3] IMPORTS FROM src/App.tsx")

if APP.exists():
    import_pattern = re.compile(
        r'import\s+([A-Za-z0-9_]+)\s+from\s+["\']([^"\']+)["\']'
    )

    imports = import_pattern.findall(app_text)

    for component, source in imports:
        print(f"  {component:25} <- {source}")


# ------------------------------------------------------------
# 4. NAVRAIL
# ------------------------------------------------------------
print("\n[4] NAVIGATION ITEMS")

NAV = ROOT / "src" / "NavRail.tsx"

nav_routes = []

if not NAV.exists():
    print("  ERROR: src/NavRail.tsx NOT FOUND")
else:
    nav_text = NAV.read_text(encoding="utf-8", errors="ignore")

    nav_pattern = re.compile(
        r'to:\s*["\']([^"\']+)["\']\s*,\s*label:\s*["\']([^"\']+)'
    )

    nav_routes = nav_pattern.findall(nav_text)

    for path, label in nav_routes:
        print(f"  {label:20} -> {path}")


# ------------------------------------------------------------
# 5. ROUTE / NAV CONSISTENCY
# ------------------------------------------------------------
print("\n[5] ROUTE / NAV CONSISTENCY")

route_paths = {x[0] for x in routes} if APP.exists() else set()
nav_paths = {x[0] for x in nav_routes}

print("  Routes without Nav:")
for x in sorted(route_paths - nav_paths):
    print("   ", x)

print("  Nav items without Route:")
for x in sorted(nav_paths - route_paths):
    print("   ", x)


# ------------------------------------------------------------
# 6. PAGE FILES AND API REFERENCES
# ------------------------------------------------------------
print("\n[6] PAGE API / NETWORK REFERENCES")

patterns = [
    "fetch(",
    "axios",
    "/api/",
    "http://",
    "https://",
    "WebSocket",
    "EventSource",
    "XMLHttpRequest",
]

for p in sorted(active_files):
    if p.name in {"App.tsx", "main.tsx"}:
        continue

    text = p.read_text(encoding="utf-8", errors="ignore")

    matches = [x for x in patterns if x in text]

    if matches:
        print(f"  {p.relative_to(ROOT)}")
        print("      ->", ", ".join(matches))


# ------------------------------------------------------------
# 7. PAGES WITH NO OBVIOUS API REFERENCE
# ------------------------------------------------------------
print("\n[7] FILES WITH NO OBVIOUS API / NETWORK REFERENCE")

for p in sorted(active_files):
    if p.name in {"App.tsx", "main.tsx"}:
        continue

    text = p.read_text(encoding="utf-8", errors="ignore")

    if not any(x in text for x in patterns):
        print(" ", p.relative_to(ROOT))


# ------------------------------------------------------------
# 8. API DIRECTORY
# ------------------------------------------------------------
print("\n[8] ACTIVE API CLIENT FILES")

API = ROOT / "src" / "api"

if API.exists():
    found = False

    for p in sorted(API.rglob("*")):
        if not p.is_file():
            continue

        name = p.name.lower()

        if ".bak" in name or ".v1" in name or ".v2" in name or ".v3" in name:
            continue

        found = True
        print(" ", p.relative_to(ROOT))

    if not found:
        print("  No active API files found.")
else:
    print("  src/api directory NOT FOUND")


# ------------------------------------------------------------
# 9. OLD / BACKUP FILES
# ------------------------------------------------------------
print("\n[9] BACKUP / OLD / VERSION FILES")

old_files = []

for p in ROOT.rglob("*"):
    if not p.is_file():
        continue

    if "node_modules" in p.parts:
        continue

    name = p.name.lower()

    if (
        ".bak" in name
        or ".broken" in name
        or ".v1" in name
        or ".v2" in name
        or ".v3" in name
        or "broken" in name
    ):
        old_files.append(p)

for p in sorted(old_files):
    print(" ", p.relative_to(ROOT))


# ------------------------------------------------------------
# 10. IMPORTANT BUILD FILES
# ------------------------------------------------------------
print("\n[10] BUILD / PROJECT FILES")

for name in [
    "package.json",
    "index.html",
    "vite.config.ts",
    "vite.config.js",
    "vite.config.mjs",
    "tsconfig.json",
]:
    p = ROOT / name

    print(
        f"  {name:20} -> "
        + ("FOUND" if p.exists() else "MISSING")
    )


# ------------------------------------------------------------
# 11. IMPORTANT CURRENT FILE STATUS
# ------------------------------------------------------------
print("\n[11] CORE STATUS")

core = [
    ROOT / "src" / "main.tsx",
    ROOT / "src" / "App.tsx",
    ROOT / "src" / "NavRail.tsx",
    ROOT / "src" / "components" / "AppShell.tsx",
]

for p in core:
    print(
        f"  {p.relative_to(ROOT):45} -> "
        + ("FOUND" if p.exists() else "MISSING")
    )


# ------------------------------------------------------------
# 12. BUSINESS / TRADING UI TERMS
# ------------------------------------------------------------
print("\n[12] IMPORTANT UI / TRADING TERMS")

terms = [
    "Active Trades",
    "NEXT BEST",
    "Next Best",
    "Equity",
    "Unrealized",
    "Realized",
    "BUY",
    "SELL",
    "HOLD",
    "P&L",
    "Position",
    "Opportunity",
    "Decision",
    "Signal",
]

for term in terms:
    found = []

    for p in active_files:
        text = p.read_text(encoding="utf-8", errors="ignore")

        if term.lower() in text.lower():
            found.append(str(p.relative_to(ROOT)))

    if found:
        print(f"\n  [{term}]")
        for x in found:
            print("    ", x)
    else:
        print(f"  [{term}] -> NOT FOUND")


print("\n" + "=" * 90)
print("AUDIT COMPLETE")
print("=" * 90)