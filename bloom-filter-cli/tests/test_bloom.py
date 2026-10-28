import unittest
from bloom_filter.filter import CountingBloomFilter

class TestCountingBloomFilter(unittest.TestCase):
    def test_add_contains_remove(self):
        cbf = CountingBloomFilter(capacity=1000, false_positive_rate=0.01)
        self.assertFalse(cbf.contains("apple"))
        cbf.add("apple")
        self.assertTrue(cbf.contains("apple"))
        self.assertTrue(cbf.remove("apple"))
        self.assertFalse(cbf.contains("apple"))

    def test_saturation_protection(self):
        cbf = CountingBloomFilter(capacity=100, false_positive_rate=0.05)
        for _ in range(20):
            cbf.add("item")
        idx0 = cbf._hash_indices("item")[0]
        # Counter should saturate at 15
        self.assertEqual(cbf._get_counter(idx0), 15)

    def test_theoretical_fp_rate(self):
        cbf = CountingBloomFilter(capacity=1000, false_positive_rate=0.01)
        for i in range(100):
            cbf.add(f"key_{i}")
        fp = cbf.theoretical_fp_rate()
        self.assertTrue(0.0 <= fp <= 0.01)

if __name__ == "__main__":
    unittest.main()
