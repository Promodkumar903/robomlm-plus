"""AutoROBOMLM installer part 9 - auto-register router in main.py"""
from pathlib import Path
import re
import shutil
from datetime import datetime

MAIN = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\main.py")
API_FILE = Path(
    r"C:\Users\Administrator\ROBOMLM_PLUS\app\api\v1\autorobomlm_api.py"
)

# Sanity checks
if not MAIN.exists():
    print(f"ERROR: {MAIN} not found.")
    raise SystemExit(1)

if not API_FILE.exists():
    print(f"ERROR: {API_FILE} not found.")
    print("Did you run install_part8.py first?")
    raise SystemExit(1)

# Read
content = MAIN.read_text(encoding="utf-8")

# Already registered?
if "autorobomlm_router" in content:
    print("ALREADY REGISTERED. main.py already includes autorobomlm_router.")
    print("No changes made.")
    raise SystemExit(0)

# Backup
backup = MAIN.with_suffix(
    f".py.bak_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
)
shutil.copy2(MAIN, backup)
print(f"BACKUP: {backup}")

# Find 'app = FastAPI(' line
match = re.search(r"^app\s*=\s*FastAPI\s*\(", content, re.MULTILINE)

if not match:
    print("ERROR: could not find 'app = FastAPI(' in main.py.")
    print("Please add these lines manually:")
    print()
    print("    from app.api.v1.autorobomlm_api import router as autorobomlm_router")
    print("    app.include_router(autorobomlm_router)")
    raise SystemExit(1)

# Find the end of FastAPI(...) call (next line starting with non-space)
# Strategy: find the closing parenthesis of the FastAPI( call
start_idx = match.start()
# Find matching close paren
depth = 0
end_idx = None
for i in range(match.end() - 1, len(content)):
    ch = content[i]
    if ch == "(":
        depth += 1
    elif ch == ")":
        depth -= 1
        if depth == 0:
            end_idx = i
            break

if end_idx is None:
    print("ERROR: could not locate end of FastAPI(...) block.")
    raise SystemExit(1)

# Find the line end after end_idx
after = content[end_idx + 1:]
line_end_match = re.search(r"\n", after)
if line_end_match:
    insert_pos = end_idx + 1 + line_end_match.end()
else:
    insert_pos = len(content)

# Import block: find first 'app.include_router' or place imports near top
import_line = (
    "from app.api.v1.autorobomlm_api import "
    "router as autorobomlm_router\n"
)
register_line = "app.include_router(autorobomlm_router)\n"

# Check if import already exists anywhere
if import_line not in content:
    # Insert import after the FastAPI creation line for simplicity
    # (Python allows imports anywhere at module level)
    inject = (
        "\n# AutoROBOMLM router\n"
        + import_line
        + register_line
    )
else:
    inject = "\n# AutoROBOMLM router\n" + register_line

new_content = content[:insert_pos] + inject + content[insert_pos:]

MAIN.write_text(new_content, encoding="utf-8")

print(f"UPDATED: {MAIN}")
print()
print("Injected lines:")
print("    " + import_line.strip())
print("    " + register_line.strip())
print()
print("Verify with:")
print("  findstr /N /C:\"autorobomlm\" main.py")
print()
print("Then restart backend and test:")
print("  curl http://127.0.0.1:8000/api/autorobomlm/health")