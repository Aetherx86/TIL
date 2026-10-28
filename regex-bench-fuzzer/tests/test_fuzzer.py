import unittest
from regex_fuzzer.fuzzer import ComplexityClass, ReDoSFuzzer

class TestRegexFuzzer(unittest.TestCase):
    def test_safe_linear_pattern(self):
        fuzzer = ReDoSFuzzer(timeout_threshold=0.2)
        res = fuzzer.test_pattern(r"^[a-zA-Z0-9]+$")
        self.assertEqual(res.complexity, ComplexityClass.SAFE_LINEAR)
        self.assertFalse(res.vulnerable)

    def test_catastrophic_backtracking_pattern(self):
        fuzzer = ReDoSFuzzer(timeout_threshold=0.1)
        # Classic evil regex: (a+)+$
        res = fuzzer.test_pattern(r"^(a+)+$", max_n=22)
        self.assertEqual(res.complexity, ComplexityClass.EXPONENTIAL)
        self.assertTrue(res.vulnerable)

if __name__ == "__main__":
    unittest.main()
