"""Shymbulak Rent: деректердің бизнес-ережелерін тексеретін тесттер."""
import csv
import json
import unittest
from pathlib import Path
 
ROOT = Path(__file__).resolve().parent.parent
with open(ROOT / "data" / "records.csv", encoding="utf-8-sig", newline="") as f:
    ROWS = list(csv.DictReader(f))
 
COLUMNS = ["rental_id", "date", "client", "item", "hours", "tariff", "amount"]
TARIFF = {"ski": 3000, "snowboard": 3500, "boots": 1200, "helmet": 800, "goggles": 600}
 
 
class DataRulesTest(unittest.TestCase):
    def test_columns(self):
        self.assertEqual(list(ROWS[0].keys()), COLUMNS)
 
    def test_own_records_added(self):
        self.assertGreaterEqual(len(ROWS), 35, "records.csv соңына өз 5 жазбаңызды қосыңыз")
 
    def test_report_created(self):
        report = json.loads((ROOT / "out" / "report.json").read_text(encoding="utf-8"))
        self.assertEqual(report["records"], len(ROWS))
        self.assertEqual(len(report["control_code"]), 8)
 
    def test_tariff_from_price_list(self):
        for line, r in enumerate(ROWS, start=2):
            with self.subTest(line=line):
                self.assertIn(r["item"], TARIFF)
                self.assertEqual(int(r["tariff"]), TARIFF[r["item"]])
 
    def test_hours_between_1_and_10(self):
        for line, r in enumerate(ROWS, start=2):
            with self.subTest(line=line):
                self.assertTrue(1 <= int(r["hours"]) <= 10)
 
    def test_amount_is_hours_times_tariff(self):
        for line, r in enumerate(ROWS, start=2):
            with self.subTest(line=line):
                self.assertEqual(int(r["amount"]), int(r["hours"]) * int(r["tariff"]))
 
 
if __name__ == "__main__":
    unittest.main()
