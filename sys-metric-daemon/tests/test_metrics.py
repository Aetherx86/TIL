import unittest
from sys_metrics.collector import MetricCollector
from sys_metrics.stream_stats import PageHinkleyDetector, WelfordAccumulator

class TestSysMetrics(unittest.TestCase):
    def test_welford_variance_computation(self):
        w = WelfordAccumulator()
        data = [10.0, 12.0, 23.0, 23.0, 16.0, 23.0, 21.0, 16.0]
        for x in data:
            w.update(x)
        # Sample mean = 18.0, sample variance = 27.42857
        self.assertAlmostEqual(w.mean, 18.0, places=4)
        self.assertAlmostEqual(w.variance(), 27.42857, places=4)

    def test_page_hinkley_changepoint(self):
        ph = PageHinkleyDetector(delta=0.05, threshold=5.0)
        # Baseline normal values
        for _ in range(50):
            self.assertFalse(ph.add(1.0))
        # Sudden shift / spike
        detected = False
        for _ in range(30):
            if ph.add(10.0):
                detected = True
                break
        self.assertTrue(detected)

    def test_collector_prometheus_output(self):
        c = MetricCollector()
        out = c.collect_prometheus_format()
        self.assertIn("node_disk_bytes_total", out)
        self.assertIn("node_load1_ewma", out)
        self.assertIn("node_load1_variance", out)

if __name__ == "__main__":
    unittest.main()
