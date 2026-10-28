import os
import shutil
import time
from typing import Dict, List, Optional
from .stream_stats import PageHinkleyDetector, WelfordAccumulator

class MetricCollector:
    """
    Real-time system telemetry collector with online EWMA smoothing,
    streaming variance estimators, and Page-Hinkley saturation detection.
    """
    def __init__(self, ewma_alpha: float = 0.3):
        self.ewma_alpha = ewma_alpha
        self.load_welford = WelfordAccumulator()
        self.saturation_detector = PageHinkleyDetector(delta=0.1, threshold=5.0)
        self.smoothed_load1: Optional[float] = None

    def get_disk_metrics(self, path: str = "/") -> Dict[str, float]:
        usage = shutil.disk_usage(path)
        return {
            "node_disk_bytes_total": float(usage.total),
            "node_disk_bytes_used": float(usage.used),
            "node_disk_bytes_free": float(usage.free),
            "node_disk_utilization_ratio": usage.used / usage.total if usage.total > 0 else 0.0,
        }

    def get_load_metrics(self) -> Dict[str, float]:
        load1, load5, load15 = os.getloadavg()
        # EWMA filter update
        if self.smoothed_load1 is None:
            self.smoothed_load1 = load1
        else:
            self.smoothed_load1 = self.ewma_alpha * load1 + (1.0 - self.ewma_alpha) * self.smoothed_load1

        self.load_welford.update(load1)
        anomaly_flag = 1.0 if self.saturation_detector.add(load1) else 0.0

        return {
            "node_load1": float(load1),
            "node_load5": float(load5),
            "node_load15": float(load15),
            "node_load1_ewma": float(self.smoothed_load1),
            "node_load1_variance": float(self.load_welford.variance()),
            "node_load_anomaly_flag": anomaly_flag,
        }

    def collect_prometheus_format(self) -> str:
        lines = []
        metrics = {}
        metrics.update(self.get_disk_metrics())
        metrics.update(self.get_load_metrics())

        for name, val in metrics.items():
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name} {val:.4f}")
        return "\n".join(lines) + "\n"
