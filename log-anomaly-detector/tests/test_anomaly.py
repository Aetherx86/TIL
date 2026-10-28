import unittest
from log_anomaly.detector import EWMAControlChart, LogAnomalyDetector, PageHinkleyCUSUM

class TestLogAnomaly(unittest.TestCase):
    def test_log_template_abstraction(self):
        line = "Connection established from 192.168.1.104:443 with session 0x7ffd12 for user 4021"
        tpl = LogAnomalyDetector.extract_template(line)
        self.assertEqual(tpl, "Connection established from <IP>:<NUM> with session <HEX> for user <NUM>")

    def test_ewma_control_chart(self):
        detector = LogAnomalyDetector(ewma_alpha=0.3, l_sigma=3.0)
        # Stationary baseline of 100 requests per minute
        stream = [100 + (i % 5) for i in range(50)]
        # Inject sudden spike
        stream.extend([450, 500, 520])
        results = detector.analyze_stream(stream, baseline_window=30)
        # Anomaly should be triggered on the spike
        spike_pt = results[-1]
        self.assertTrue(spike_pt.is_ewma_anomaly or spike_pt.is_cusum_anomaly)

    def test_cusum_changepoint(self):
        cusum = PageHinkleyCUSUM(delta=1.0, threshold=10.0)
        for _ in range(30):
            self.assertFalse(cusum.step(10.0))
        # Sudden sustained jump
        detected = False
        for _ in range(15):
            if cusum.step(50.0):
                detected = True
                break
        self.assertTrue(detected)

if __name__ == "__main__":
    unittest.main()
