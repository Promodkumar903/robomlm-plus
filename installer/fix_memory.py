import ast
import re
from pathlib import Path

p = Path(r"C:\Users\Administrator\ROBOMLM_PLUS\app\intelligence\memory\__init__.py")
src = p.read_text(encoding="utf-8")
pkg_dir = p.parent

pattern = re.compile(r'from \.([a-z_]+) import \(([^)]+)\)', re.DOTALL)


def get_names_from_file(path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        elif isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    names.add(t.id)
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                names.add(alias.asname or alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.asname or alias.name.split('.')[0])
    return names


def fix(m):
    sub = m.group(1)
    names = [
        n.strip().rstrip(',')
        for n in m.group(2).split("\n")
        if n.strip() and not n.strip().startswith('#')
    ]
    subpath = pkg_dir / f"{sub}.py"
    if not subpath.exists():
        print(f'[{sub}] FILE_MISSING - keeping all')
        return m.group(0)
    try:
        existing = get_names_from_file(subpath)
    except Exception as e:
        print(f'[{sub}] PARSE_ERROR: {e} - keeping all')
        return m.group(0)

    keep = [n for n in names if n and n in existing]
    dropped = [n for n in names if n and n not in existing]

    print(f'[{sub}] keep={len(keep)} dropped={len(dropped)}')
    for d in dropped:
        print('   - ' + d)

    if keep:
        body = ',\n    '.join(keep)
        return f'from .{sub} import (\n    {body},\n)'
    return ''


new_src = pattern.sub(fix, src)
p.write_text(new_src, encoding="utf-8")
print('DONE')