import math
import re
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple

class ComplexityClass(Enum):
    SAFE_LINEAR = "O(N) Linear"
    POLYNOMIAL = "O(N^k) Polynomial Backtracking"
    EXPONENTIAL = "O(2^N) Catastrophic Exponential Backtracking"

@dataclass
class FuzzResult:
    pattern: str
    complexity: ComplexityClass
    growth_ratio: float
    max_duration_sec: float
    timing_points: List[Tuple[int, float]]
    vulnerable: bool

class ReDoSFuzzer:
    """
    Regex algorithmic complexity fuzzer.
    Synthesizes progressive pump strings to empirically measure backtracking growth,
    distinguishing linear, polynomial, and catastrophic exponential curves via regression.
    """
    def __init__(self, timeout_threshold: float = 0.5):
        self.timeout_threshold = timeout_threshold

    @staticmethod
    def _fit_growth_ratio(timings: List[Tuple[int, float]]) -> float:
        """Measures average multiplicative factor between successive powers of N."""
        ratios = []
        for i in range(1, len(timings)):
            t_prev = max(timings[i - 1][1], 1e-6)
            t_curr = max(timings[i][1], 1e-6)
            ratios.append(t_curr / t_prev)
        return sum(ratios) / len(ratios) if ratios else 1.0

    def test_pattern(self, pattern_str: str, max_n: int = 24) -> FuzzResult:
        compiled = re.compile(pattern_str)
        # Pump tokens
        candidates = ["a", "1", " ", "ab"]
        worst_r = 1.0
        worst_timings: List[Tuple[int, float]] = []
        worst_max_dur = 0.0

        for char in candidates:
            timings: List[Tuple[int, float]] = []
            for n in range(12, max_n + 1, 3):
                payload = (char * n) + "!"
                t0 = time.perf_counter()
                compiled.search(payload)
                dur = time.perf_counter() - t0
                timings.append((n, dur))
                if dur > worst_max_dur:
                    worst_max_dur = dur
                if dur >= self.timeout_threshold:
                    break

            ratio = self._fit_growth_ratio(timings)
            if ratio > worst_r:
                worst_r = ratio
                worst_timings = timings

        # Classification based on empirical growth ratio across steps of +3 in input size
        # If doubling step multiplier exceeds 1.8^3 ≈ 5.8, exponential backtracking is evident
        if worst_r >= 4.0 or worst_max_dur >= self.timeout_threshold:
            complexity = ComplexityClass.EXPONENTIAL
            vulnerable = True
        elif worst_r >= 1.8:
            complexity = ComplexityClass.POLYNOMIAL
            vulnerable = True
        else:
            complexity = ComplexityClass.SAFE_LINEAR
            vulnerable = False

        return FuzzResult(
            pattern=pattern_str,
            complexity=complexity,
            growth_ratio=round(worst_r, 3),
            max_duration_sec=worst_max_dur,
            timing_points=worst_timings,
            vulnerable=vulnerable,
        )
