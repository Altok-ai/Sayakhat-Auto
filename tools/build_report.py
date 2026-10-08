"""Shymbulak Rent: data/records.csv файлынан out/report.json есебін жасайды."""
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path
 
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "records.csv"
OUT = ROOT / "out" / "report.json"
VARIANT = 1
 
 
def load_rows():
    with open(DATA, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))
 
 
def control_code(rows):
    text = "\n".join("|".join(row.values()) for row in rows)
    digest = hashlib.sha256(f"{VARIANT}\n{text}".encode("utf-8"))
    return digest.hexdigest()[:8].upper()
 
 
def money(value):
    return f"{value:,}".replace(",", " ") + " ₸"
 
 
def build(rows):
    by_item = defaultdict(lambda: [0, 0, 0])
    by_day = defaultdict(lambda: [0, 0])
    for r in rows:
        hours, amount = int(r["hours"]), int(r["amount"])
        item = by_item[r["item"]]
        item[0] += 1
        item[1] += hours
        item[2] += amount
        day = by_day[r["date"]]
        day[0] += 1
        day[1] += amount
    total = sum(int(r["amount"]) for r in rows)
    summary = [
        {"label": "Жалпы түсім", "value": money(total)},
        {"label": "Жалға беру саны", "value": len(rows)},
        {"label": "Жалпы сағат", "value": sum(int(r["hours"]) for r in rows)},
    ]
    items = sorted(by_item.items(), key=lambda kv: -kv[1][2])
    days = sorted(by_day.items(), key=lambda kv: (-kv[1][1], kv[0]))
    tables = [
        {"title": "Жабдық түрлері бойынша түсім",
         "columns": ["Жабдық", "Жалға беру", "Сағат", "Түсім"],
         "rows": [[k, v[0], v[1], money(v[2])] for k, v in items]},
        {"title": "Ең табысты күндер",
         "columns": ["Күн", "Жалға беру", "Түсім"],
         "rows": [[k, v[0], money(v[1])] for k, v in days]},
    ]
    return summary, tables
 
 
def main():
    rows = load_rows()
    summary, tables = build(rows)
    report = {
        "variant": VARIANT,
        "org": "Shymbulak Rent",
        "title": "Шаңғы жабдықтарын жалға беру есебі",
        "records": len(rows),
        "control_code": control_code(rows),
        "summary": summary,
        "tables": tables,
    }
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"out/report.json дайын: {len(rows)} жазба, бақылау коды {report['control_code']}")
 
 
if __name__ == "__main__":
    main()
