import unittest
from entropy_detector.detector import EntropyScanner


class TestEntropyDetector(unittest.TestCase):
    def setUp(self):
        self.scanner = EntropyScanner(threshold=3.5, min_length=16)

    def test_shannon_entropy_constant(self):
        self.assertEqual(EntropyScanner.calculate_shannon_entropy(""), 0.0)
        self.assertEqual(EntropyScanner.calculate_shannon_entropy("AAAAAAAAAAAAAAAA"), 0.0)

    def test_renyi_entropy(self):
        token = "9bF!q2#Lz9$vX1*mQ4@z"
        h_shannon = EntropyScanner.calculate_shannon_entropy(token)
        h_renyi = EntropyScanner.calculate_renyi_entropy(token, alpha=2.0)
        # Mathematical property: H_alpha <= H_shannon for alpha > 1
        self.assertLessEqual(h_renyi, h_shannon + 1e-6)

    def test_kolmogorov_compression_distance(self):
        repeated = "ABCDEF" * 50
        random_str = "aK9#zL1$mQ8!vX2@pT7&wR3%bF0^yU6*jN5~"
        ratio_rep = EntropyScanner.calculate_normalized_compression_distance(repeated)
        ratio_rand = EntropyScanner.calculate_normalized_compression_distance(random_str)
        # Random high-entropy strings have much higher compression overhead/ratio
        self.assertGreater(ratio_rand, ratio_rep)

    def test_scan_text_detection(self):
        sample = "aws_secret_key = 'dGhpcy1pcy1hLXZlcnktaGlnaC1lbnRyb3B5LXNlY3JldC1rZXk='"
        findings = self.scanner.scan_text(sample)
        self.assertEqual(len(findings), 1)
        self.assertGreaterEqual(findings[0].shannon_entropy, 3.5)
        self.assertGreaterEqual(findings[0].renyi_entropy, 2.5)


if __name__ == "__main__":
    unittest.main()
