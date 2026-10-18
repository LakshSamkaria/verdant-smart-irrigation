import unittest
from algorithms.greedy import run_greedy
from algorithms.dynamic_programming import run_dp
from services.irrigation_service import validate_payload, enrich_fields

FIELDS = [
    {"id": 1, "name": "A", "crop": "Wheat", "area": 1, "moisture": 20, "target_moisture": 60, "demand": 50, "priority": 5, "max_allocation": 50},
    {"id": 2, "name": "B", "crop": "Tomato", "area": 1, "moisture": 40, "target_moisture": 60, "demand": 40, "priority": 3, "max_allocation": 40},
]

class AlgorithmTests(unittest.TestCase):
    def setUp(self):
        self.fields = enrich_fields(FIELDS)

    def test_allocation_respects_budget(self):
        for result in (run_greedy(self.fields, 30, 10), run_dp(self.fields, 30, 10)):
            self.assertLessEqual(result["total_water_used"], 30)
            self.assertGreaterEqual(result["remaining_water"], 0)

    def test_zero_water(self):
        for result in (run_greedy(self.fields, 0, 10), run_dp(self.fields, 0, 10)):
            self.assertEqual(result["total_water_used"], 0)
            self.assertEqual(result["remaining_water"], 0)

    def test_sufficient_budget(self):
        result = run_dp(self.fields, 200, 10)
        self.assertLessEqual(result["total_water_used"], 200)

    def test_invalid_negative_budget(self):
        self.assertIsNotNone(validate_payload({"available_water": -1, "unit_size": 10, "fields": FIELDS}))

    def test_empty_fields_valid_for_service(self):
        self.assertIsNone(validate_payload({"available_water": 0, "unit_size": 10, "fields": []}))

if __name__ == "__main__":
    unittest.main()
