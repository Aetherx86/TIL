import hashlib
import math
from typing import List, Tuple

class CountingBloomFilter:
    """
    Counting Bloom Filter with 4-bit nibble counters supporting deletion,
    Kirsch-Mitzenmacher double-hashing, and saturation protection at 15.
    """
    def __init__(self, capacity: int = 10_000, false_positive_rate: float = 0.01):
        self.capacity = capacity
        self.fp_rate = false_positive_rate
        # Optimal counter count m = -(n * ln(p)) / (ln(2)^2)
        self.m = max(64, int(-1.0 * (capacity * math.log(false_positive_rate)) / (math.log(2) ** 2)))
        # Optimal hash count k = (m/n) * ln(2)
        self.k = max(1, int((self.m / capacity) * math.log(2)))
        # 4-bit counters: 2 counters per byte
        self.byte_count = (self.m + 1) // 2
        self.storage = bytearray(self.byte_count)
        self.count = 0

    def _get_counter(self, idx: int) -> int:
        byte_idx = idx // 2
        is_high = (idx % 2 == 1)
        b = self.storage[byte_idx]
        return (b >> 4) & 0x0F if is_high else (b & 0x0F)

    def _set_counter(self, idx: int, val: int):
        byte_idx = idx // 2
        is_high = (idx % 2 == 1)
        val = min(15, max(0, val))
        b = self.storage[byte_idx]
        if is_high:
            self.storage[byte_idx] = (b & 0x0F) | (val << 4)
        else:
            self.storage[byte_idx] = (b & 0xF0) | val

    def _hash_indices(self, item: str) -> List[int]:
        # Kirsch-Mitzenmacher optimization: g_i(x) = h1(x) + i * h2(x) mod m
        raw = item.encode("utf-8")
        h = hashlib.sha256(raw).digest()
        h1 = int.from_bytes(h[:8], "big")
        h2 = int.from_bytes(h[8:16], "big") | 1  # ensure non-zero
        return [(h1 + i * h2) % self.m for i in range(self.k)]

    def add(self, item: str):
        indices = self._hash_indices(item)
        for idx in indices:
            c = self._get_counter(idx)
            if c < 15:  # Saturate at 15
                self._set_counter(idx, c + 1)
        self.count += 1

    def contains(self, item: str) -> bool:
        indices = self._hash_indices(item)
        for idx in indices:
            if self._get_counter(idx) == 0:
                return False
        return True

    def remove(self, item: str) -> bool:
        """Removes an item by decrementing its counters."""
        if not self.contains(item):
            return False
        indices = self._hash_indices(item)
        for idx in indices:
            c = self._get_counter(idx)
            if 0 < c < 15:  # Do not decrement saturated counters
                self._set_counter(idx, c - 1)
        self.count = max(0, self.count - 1)
        return True

    def theoretical_fp_rate(self) -> float:
        """Computes instantaneous false positive probability based on current occupancy."""
        if self.count == 0:
            return 0.0
        exponent = -1.0 * (self.k * self.count) / self.m
        return (1.0 - math.exp(exponent)) ** self.k
