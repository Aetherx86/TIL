import math
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

@dataclass
class AnomalyPoint:
    index: int
    count: int
    ewma: float
    ucl: float
    lcl: float
    is_ewma_anomaly: bool
    is_cusum_anomaly: bool

class EWMAControlChart:
    """
    Statistical process control chart with adaptive Upper/Lower Control Limits.
    UCL_t = mu + L * sigma * sqrt( (alpha / (2 - alpha)) * (1 - (1 - alpha)^(2t)) )
    """
    def __init__(self, alpha: float = 0.2, l_sigma: float = 3.0):
        self.alpha = alpha
        self.l_sigma = l_sigma
        self.mean: Optional[float] = None
        self.variance: float = 1.0
        self.ewma: Optional[float] = None
        self.t: int = 0

    def fit_baseline(self, baseline: List[float]):
        if not baseline:
            return
        self.mean = sum(baseline) / len(baseline)
        var = sum((x - self.mean) ** 2 for x in baseline) / len(baseline)
        self.variance = var if var > 1e-6 else 1.0
        self.ewma = self.mean
        self.t = 0

    def step(self, x: float) -> Tuple[float, float, float, bool]:
        self.t += 1
        if self.mean is None:
            self.mean = x
            self.ewma = x
        self.ewma = self.alpha * x + (1.0 - self.alpha) * self.ewma
        sigma = math.sqrt(self.variance)
        factor = math.sqrt((self.alpha / (2.0 - self.alpha)) * (1.0 - (1.0 - self.alpha) ** (2 * self.t)))
        margin = self.l_sigma * sigma * factor
        ucl = self.mean + margin
        lcl = max(0.0, self.mean - margin)
        is_anomaly = self.ewma > ucl or self.ewma < lcl
        return self.ewma, ucl, lcl, is_anomaly

class PageHinkleyCUSUM:
    """Sequential CUSUM changepoint detector for abrupt log frequency surges."""
    def __init__(self, delta: float = 1.0, threshold: float = 20.0, alpha: float = 0.95):
        self.delta = delta
        self.threshold = threshold
        self.alpha = alpha
        self.mean = 0.0
        self.cumsum = 0.0
        self.min_cumsum = 0.0
        self.t = 0

    def step(self, x: float) -> bool:
        self.t += 1
        if self.t == 1:
            self.mean = x
        else:
            self.mean = self.alpha * self.mean + (1.0 - self.alpha) * x
        self.cumsum += (x - self.mean - self.delta)
        if self.cumsum < self.min_cumsum:
            self.min_cumsum = self.cumsum
        return (self.cumsum - self.min_cumsum) > self.threshold

class LogAnomalyDetector:
    """
    Detects log volume and distributional anomalies using EWMA control charts,
    Page-Hinkley CUSUM changepoint detection, and invariant template abstraction.
    """
    IP_REGEX = re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b")
    HEX_REGEX = re.compile(r"\b0x[0-9a-fA-F]+\b")
    NUM_REGEX = re.compile(r"\b[0-9]+\b")

    def __init__(self, ewma_alpha: float = 0.2, l_sigma: float = 3.0, cusum_threshold: float = 15.0):
        self.ewma_chart = EWMAControlChart(alpha=ewma_alpha, l_sigma=l_sigma)
        self.cusum = PageHinkleyCUSUM(threshold=cusum_threshold)

    @classmethod
    def extract_template(cls, log_line: str) -> str:
        s = cls.IP_REGEX.sub("<IP>", log_line.strip())
        s = cls.HEX_REGEX.sub("<HEX>", s)
        s = cls.NUM_REGEX.sub("<NUM>", s)
        return s

    def analyze_stream(self, series: List[int], baseline_window: int = 30) -> List[AnomalyPoint]:
        if len(series) < baseline_window:
            baseline = [float(x) for x in series]
        else:
            baseline = [float(x) for x in series[:baseline_window]]
        self.ewma_chart.fit_baseline(baseline)

        points = []
        for idx, count in enumerate(series):
            ewma_val, ucl, lcl, is_ewma = self.ewma_chart.step(float(count))
            is_cusum = self.cusum.step(float(count))
            points.append(AnomalyPoint(
                index=idx,
                count=count,
                ewma=ewma_val,
                ucl=ucl,
                lcl=lcl,
                is_ewma_anomaly=is_ewma,
                is_cusum_anomaly=is_cusum,
            ))
        return points
