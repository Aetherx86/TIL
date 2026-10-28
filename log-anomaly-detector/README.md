# log-anomaly-detector

Sliding-window event rate and error-spike anomaly detector for server logs.

## Overview

Sudden surges or drops in application event volumes frequently indicate security intrusions, denial of service attacks, or upstream service failures. `log-anomaly-detector` implements statistical sliding-window evaluation, computing rolling z-scores across discrete time buckets to flag anomalous behavior.

## Mathematical Formulation

For a sequence of event counts $X = [x_1, x_2, \dots, x_n]$, the z-score $Z_i$ for window $i$ is defined as:

$$Z_i = \frac{x_i - \mu}{\sigma}$$

Where $\mu$ is the mean event rate and $\sigma$ is the standard deviation. A window is marked anomalous when $|Z_i| \ge \tau$ (default threshold $\tau = 2.5$).

## Features

- Statistical Z-Score Detection: Pinpoints distribution outliers across discrete time intervals.
- Configurable Sensitivity: Adjustable threshold parameter for tuning false positive rates.
- Batch and Streaming Capability: Analyzes static log arrays or streaming pipeline counts.
- Zero Dependencies: Pure standard-library Python math implementation.

## Installation

```bash
git clone https://gitlab.com/jk9576/log-anomaly-detector.git
cd log-anomaly-detector
pip install -e .
```

## CLI Usage

```bash
log-anomaly 12 15 14 13 16 14 15 280 14 13
```

Sample Output:

```
Window 0    Count: 12     Z-Score:  -0.37
Window 1    Count: 15     Z-Score:  -0.33
Window 6    Count: 15     Z-Score:  -0.33
Window 7    Count: 280    Z-Score:   3.12 [!] ANOMALY
Window 8    Count: 14     Z-Score:  -0.34
```

## Python API Usage

```python
from log_anomaly.detector import LogAnomalyDetector

detector = LogAnomalyDetector(z_threshold=2.5)
data = [100, 105, 98, 102, 101, 850, 99]
windows = detector.evaluate_counts(data)

anomalies = [w for w in windows if w.is_anomaly]
print(f"Discovered {len(anomalies)} anomalous windows.")
```

## Running Tests

```bash
python -m unittest discover tests
```

## License

MIT License. See LICENSE for details.
