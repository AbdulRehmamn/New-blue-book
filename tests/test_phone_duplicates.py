import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from storage import Store, FIELDS
from extractor import phones

class PhoneSelectionTests(unittest.TestCase):
    def test_priority_shared_numbers_fallback_and_dedup(self):
        def row(company, number, name="", title="", kind="Phone"):
            r = dict.fromkeys(FIELDS, "")
            r.update({"Company Name":company, "Phone Number":number, "Contact Name":name, "Title":title, "Phone Type":kind})
            return r
        raw = [row("A", "+18056403050"), row("A", "805-640-3050", "Owner A", "Owner"),
               row("A", "+18056403007", "Owner A", "Owner"), row("A", "+18056403008", kind="Mobile"),
               row("B", "+18056403009"), row("B", "+18056403010", "Sales B", kind="Mobile"),
               row("C", "+18056403011"), row("C", "+18056403012", "Sales C", "Estimator"),
               row("D", "1 (805) 640-3011"), row("E", "+18056403013", kind="Fax")]
        with tempfile.TemporaryDirectory() as folder:
            store = Store(folder)
            store._raw_rows = lambda: iter(raw)
            rows = list(store.rows())
            self.assertEqual(len(rows), 4)
            numbered = {r["Phone Number"]:r for r in rows if r["Phone Number"]}
            self.assertEqual(set(numbered), {"+18056403007", "+18056403010", "+18056403011"})
            self.assertEqual(numbered["+18056403007"]["Contact Name"], "Owner A")
            self.assertIn("D", numbered["+18056403011"]["Company Name"])
            self.assertTrue(all(not r["Company Phone"] for r in rows))
            self.assertEqual(list(store.rows()), rows)
            store.close()

    def test_mobile_requires_explicit_label(self):
        self.assertEqual(phones("Cell: (619) 555-0120")[0]["kind"], "Mobile")
        self.assertEqual(phones("(619) 555-0120")[0]["kind"], "Phone")
        self.assertEqual(phones("Fax: (619) 555-0120")[0]["kind"], "Fax")
