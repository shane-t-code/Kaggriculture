"""Dump an x-ray notebook's cell outputs as plain text.
Usage: python tools/xray_dump.py <notebook.ipynb> [max_chars_per_output]
"""
import json, sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
path = sys.argv[1]
cap = int(sys.argv[2]) if len(sys.argv) > 2 else 1200
nb = json.load(open(path, encoding="utf-8"))
for i, cell in enumerate(nb.get("cells", [])):
    src = "".join(cell.get("source", []))
    # print markdown headers and short code hints for orientation
    if cell.get("cell_type") == "markdown":
        head = [l for l in src.splitlines() if l.strip().startswith("#")]
        if head:
            print("\n" + " / ".join(h.strip() for h in head[:2]))
        continue
    outs = []
    for o in cell.get("outputs", []):
        if o.get("output_type") == "stream":
            outs.append("".join(o.get("text", [])))
        elif o.get("output_type") in ("execute_result", "display_data"):
            d = o.get("data", {})
            if "text/plain" in d:
                outs.append("".join(d["text/plain"]))
    txt = "\n".join(outs).strip()
    if txt:
        first = src.splitlines()[0][:80] if src else ""
        print(f"\n--- cell {i} [{first}] ---")
        print(txt[:cap])
