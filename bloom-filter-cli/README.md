# bloom-filter-cli

Space-efficient probabilistic set filter with binary persistence.

## Overview

A Bloom Filter is a space-efficient probabilistic data structure used to test whether an element is a member of a set. False positive matches are possible, but false negatives are impossible. `bloom-filter-cli` provides an implementation supporting configurable false-positive boundaries and bytearray serialization.

## Mathematical Formulation

Given an expected capacity $n$ and desired false positive probability $p$, optimal bit array size $m$ and hash count $k$ are computed as:

$$m = -\frac{n \ln(p)}{(\ln 2)^2}, \quad k = \frac{m}{n} \ln 2$$

Multi-hashing is implemented using double-hashing (Kirsch-Mitzenmacher optimization):

$$g_i(x) = (h_1(x) + i \cdot h_2(x)) \pmod m$$

Where $h_1(x)$ and $h_2(x)$ are derived from SHA-256 and MD5 digests.

## Features

- Optimal Parameter Derivation: Calculates minimal bit allocation based on capacity and target error rate.
- Kirsch-Mitzenmacher Double-Hashing: Derives $k$ independent hash functions without computing $k$ separate digests.
- Zero Dependencies: Pure Python standard library implementation.

## Installation

```bash
git clone https://gitlab.com/jk9576/bloom-filter-cli.git
cd bloom-filter-cli
pip install -e .
```

## CLI Usage

```bash
bloom-filter demo
```

## Python API Usage

```python
from bloom_filter.filter import BloomFilter

# Create filter for 100,000 items with 1% false positive rate
bf = BloomFilter(capacity=100000, false_positive_rate=0.01)

bf.add("user_session_9481")
bf.add("user_session_9482")

print(bf.contains("user_session_9481"))  # True
print(bf.contains("user_session_9999"))  # False
```

## Running Tests

```bash
python -m unittest discover tests
```

## License

MIT License. See LICENSE for details.
