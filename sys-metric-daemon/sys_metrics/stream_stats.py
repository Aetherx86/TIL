import math
from typing import Optional, Tuple

class WelfordAccumulator:
    """
    Welford's algorithm for numerically stable, single-pass computation
    of sample variance, standard deviation, skewness, and kurtosis.
    """
    def __init__(self):
        self.count = 0
        self.mean = 0.0
        self.M2 = 0.0
        self.M3 = 0.0
        self.M4 = 0.0

    def update(self, x: float):
        self.count += 1
        n = self.count
        delta = x - self.mean
        delta_n = delta / n
        delta_n2 = delta_n * delta_n
        term1 = delta * delta_n * (n - 1)

        self.mean += delta_n
        self.M4 += term1 * delta_n2 * (n * n - 3 * n + 3) + 6 * delta_n2 * self.M2 - 4 * delta_n * self.M3
        self.M3 += term1 * delta_n * (n - 2) - 3 * delta_n * self.M2
        self.M2 += term1

    def variance(self) -> float:
        return self.M2 / (self.count - 1) if self.count > 1 else 0.0

    def std_dev(self) -> float:
        return math.sqrt(self.variance())

class PageHinkleyDetector:
    """
    Sequential Page-Hinkley cumulative sum (CUSUM) test for detecting
    abrupt changepoints and mean shifts in system telemetry streams.
    """
    def __init__(self, delta: float = 0.05, threshold: float = 15.0, alpha: float = 0.99):
        self.delta = delta
        self.threshold = threshold
        self.alpha = alpha
        self.mean = 0.0
        self.cumsum = 0.0
        self.min_cumsum = 0.0
        self.n = 0

    def add(self, x: float) -> bool:
        self.n += 1
        if self.n == 1:
            self.mean = x
        else:
            self.mean = self.alpha * self.mean + (1.0 - self.alpha) * x
        self.cumsum += (x - self.mean - self.delta)
        if self.cumsum < self.min_cumsum:
            self.min_cumsum = self.cumsum
        return (self.cumsum - self.min_cumsum) > self.threshold
