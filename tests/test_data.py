"""Sayakhat Auto: деректердің бизнес-ережелерін тексеретін тесттер."""
import csv
import json
import unittest
import re
from datetime import date
from pathlib import Path
 
ROOT = Path(__file__).resolve().parent.parent
with open(ROOT / "data" / "records.csv", encoding="utf-8-sig", newline="") as f:
    ROWS = list(csv.DictReader(f))
 
COLUMNS = ["order_id", "plate", "service", "opened", "closed", "cost"]
PLATE = re.compile(r"^[0-9]{3}[A-Z]{3}02$")
 
 
class DataRulesTest(unittest.TestCase):
    def test_columns(self):
        self.assertEqual(list(ROWS[0].keys()), COLUMNS)
 
    def test_own_records_added(self):
        self.assertGreaterEqual(len(ROWS), 35, "records.csv соңына өз 5 жазбаңызды қосыңыз")
 
    def test_report_created(self):
        report = json.loads((ROOT / "out" / "report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["records"], len(ROWS))
        self.assertEqual(len(report["control_code"]), 8)
 
    def test_plate_format(self):
        for line, r in enumerate(ROWS, start=2):
            with self.subTest(line=line, plate=r["plate"]):
                self.assertRegex(r["plate"], PLATE)
 
    def test_closed_not_before_opened(self):
        for line, r in enumerate(ROWS, start=2):
            with self.subTest(line=line):
                self.assertGreaterEqual(date.fromisoformat(r["closed"]),
                                        date.fromisoformat(r["opened"]))
 
    def test_cost_positive(self):
        for line, r in enumerate(ROWS, start=2):
            with self.subTest(line=line):
                self.assertGreater(int(r["cost"]), 0)
 
 
if __name__ == "__main__":
    unittest.main()
