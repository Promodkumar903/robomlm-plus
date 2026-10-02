"""Fix __init__.py to include AutoRobomlmAPI"""
from pathlib import Path

ROOT = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\autorobomlm")
init_file = ROOT / "__init__.py"

content = init_file.read_text(encoding="utf-8")

# Add API import + __all__ entry if missing
if "AutoRobomlmAPI" not in content:
    # Add import
    content = content.replace(
        "from app.autorobomlm.auto_loop import (\n"
        "    AutoRobomlmLoop,\n"
        "    LoopState,\n"
        "    TickSummary,\n"
        ")",
        "from app.autorobomlm.auto_loop import (\n"
        "    AutoRobomlmLoop,\n"
        "    LoopState,\n"
        "    TickSummary,\n"
        ")\n\n"
        "from app.autorobomlm.autorobomlm_api import (\n"
        "    AutoRobomlmAPI,\n"
        ")"
    )
    # Add __all__ entry
    content = content.replace(
        '    "AutoRobomlmLoop", "LoopState", "TickSummary",\n]',
        '    "AutoRobomlmLoop", "LoopState", "TickSummary",\n\n'
        '    # api\n'
        '    "AutoRobomlmAPI",\n]'
    )
    init_file.write_text(content, encoding="utf-8")
    print(f"FIXED: {init_file}")
else:
    print("Already has AutoRobomlmAPI - no change needed.")

print()
print("Verify with:")
print('python -c "from app.autorobomlm import AutoRobomlmAPI; print(\'API IMPORT OK\')"')