"""Sayakhat Auto: data/records.csv файлынан out/report.json есебін жасайды."""
import csv
import hashlib
import json
from collections import defaultdict
from datetime import date
from pathlib import Path
 
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "records.csv"
OUT = ROOT / "out" / "report.json"
VARIANT = 9
 
 
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
    by_service = defaultdict(lambda: [0, 0, 0])
    for r in rows:
        days = (date.fromisoformat(r["closed"]) - date.fromisoformat(r["opened"])).days
        s = by_service[r["service"]]
        s[0] += 1
        s[1] += int(r["cost"])
        s[2] += days
    total = sum(v[1] for v in by_service.values())
    all_days = sum(v[2] for v in by_service.values())
    summary = [
        {"label": "Жалпы түсім", "value": money(total)},
        {"label": "Тапсырыс саны", "value": len(rows)},
        {"label": "Жөндеудің орташа ұзақтығы", "value": f"{all_days / len(rows):.1f} күн"},
    ]
    services = sorted(by_service.items(), key=lambda kv: -kv[1][1])
    slow = sorted(by_service.items(), key=lambda kv: (-kv[1][2] / kv[1][0], kv[0]))
    tables = [
        {"title": "Жұмыс түрлері бойынша түсім",
         "columns": ["Жұмыс түрі", "Тапсырыс", "Түсім"],
         "rows": [[k, v[0], money(v[1])] for k, v in services]},
        {"title": "Жөндеудің орташа ұзақтығы",
         "columns": ["Жұмыс түрі", "Орташа күн"],
         "rows": [[k, round(v[2] / v[0], 1)] for k, v in slow]},
    ]
    return summary, tables
 
 
def main():
    rows = load_rows()
    summary, tables = build(rows)
    report = {
        "variant": VARIANT,
        "org": "Sayakhat Auto",
        "title": "Автосервистің тапсырыс-нарядтары",
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
