"""Unit tests for Goldbach number theory algorithms and Veritasium paradox models."""

import math
import pytest
from math_video_engine.scenes.goldbach import (
    is_prime, get_primes_up_to, goldbach_pairs, ternary_goldbach_triplets
)


def test_is_prime():
    primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    for p in primes:
        assert is_prime(p) is True

    composites = [-5, 0, 1, 4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 25, 27]
    for c in composites:
        assert is_prime(c) is False


def test_goldbach_pairs():
    # 4 = 2 + 2
    assert (2, 2) in goldbach_pairs(4)
    # 10 = 3 + 7 = 5 + 5
    pairs_10 = goldbach_pairs(10)
    assert (3, 7) in pairs_10
    assert (5, 5) in pairs_10
    # Every even number from 4 to 100 has at least one Goldbach pair
    for even_n in range(4, 102, 2):
        pairs = goldbach_pairs(even_n)
        assert len(pairs) >= 1
        for p1, p2 in pairs:
            assert is_prime(p1)
            assert is_prime(p2)
            assert p1 + p2 == even_n


def test_ternary_goldbach_triplets():
    # 7 = 2 + 2 + 3
    assert (2, 2, 3) in ternary_goldbach_triplets(7)
    # 27 = 3 + 5 + 19 = 7 + 7 + 13
    triplets_27 = ternary_goldbach_triplets(27)
    assert len(triplets_27) >= 1
    for p1, p2, p3 in triplets_27:
        assert is_prime(p1)
        assert is_prime(p2)
        assert is_prime(p3)
        assert p1 + p2 + p3 == 27


def test_optimal_stopping_maximum():
    # P(r) = -r * ln(r) has maximum at r = 1/e
    r_opt = 1.0 / math.e
    p_opt = -r_opt * math.log(r_opt)
    assert pytest.approx(p_opt, abs=1e-5) == 1.0 / math.e
    assert pytest.approx(p_opt, abs=1e-3) == 0.368
