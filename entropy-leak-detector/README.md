# entropy-leak-detector

Multi-Metric Information-Theoretic Secret Scanner (Shannon, Rényi, Kolmogorov Approximation).

## Overview

Standard regex filters struggle to distinguish high-entropy cryptographic keys from legitimate code tokens (e.g., camelCase identifiers or static hashes). `entropy-leak-detector` combines three complementary information-theoretic metrics:
1. Shannon Entropy ($H$): Quantifies expected information content.
2. Rényi Collision Entropy ($H_2$): Evaluates collision resistance and probability mass concentration.
3. Normalized Compression Ratio (NCD): Uses DEFLATE algorithmic compressibility as an empirical proxy for Kolmogorov complexity.

## Mathematical Formulation

### 1. Rényi Entropy
Generalized entropy of order $\alpha \ge 0$:

$$H_\alpha(X) = \frac{1}{1 - \alpha} \log_2 \left( \sum_{i=1}^{n} p_i^\alpha \right)$$

For $\alpha = 2$, Rényi entropy yields collision entropy $H_2(X) = -\log_2 \sum p_i^2$, providing a stricter lower bound than Shannon entropy.

### 2. Algorithmic Information Proxy
Let $C(x)$ denote the DEFLATE compressed size of string $x$. The compressibility ratio:

$$R(x) = \frac{C(x)}{|x|}$$

Random cryptographic tokens exhibit $R(x) \ge 1.0$ due to compression header overhead and lack of repeating substrings, while repetitive code tokens exhibit $R(x) \ll 0.5$.

## Installation

```bash
git clone https://gitlab.com/jk9576/entropy-leak-detector.git
cd entropy-leak-detector
pip install -e .
```

## Running Tests

```bash
python -m unittest discover tests
```

## License

MIT License. See LICENSE for details.
