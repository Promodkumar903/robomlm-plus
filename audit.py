import os

root = r"C:\Users\Administrator\ROBOMLM_PLUS\app"
output = r"C:\Users\Administrator\ROBOMLM_PLUS\app_audit_full.txt"

with open(output, "w", encoding="utf-8") as out:
    for dirpath, dirnames, filenames in os.walk(root):
        for filename in filenames:
            if filename.endswith(".py"):
                fullpath = os.path.join(dirpath, filename)
                out.write("\n" + "="*80 + "\n")
                out.write(f"FILE: {fullpath}\n")
                out.write("="*80 + "\n")
                try:
                    with open(fullpath, "r", encoding="utf-8") as f:
                        out.write(f.read())
                except Exception as e:
                    out.write(f"[ERROR reading file: {e}]\n")

print("Done! File created at:", output)