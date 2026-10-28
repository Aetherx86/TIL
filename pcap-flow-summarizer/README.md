# pcap-flow-summarizer

High-Precision TCP Finite-State Machine Tracking and Flow Inter-Arrival Time Moments.

## Overview

Network forensics and security monitoring require behavioral conversation telemetry beyond raw packet counts. `pcap-flow-summarizer` implements pure-Python packet parsing, Layer 4 protocol state-machine tracking, and statistical moment analysis for packet inter-arrival times (IAT).

## Mathematical Formulation: Inter-Arrival Time Moments

For packet arrival timestamps $t_1, t_2, \dots, t_N$, the inter-arrival times are $\Delta t_i = t_{i} - t_{i-1}$:

$$\mu_{\text{IAT}} = \frac{1}{N-1} \sum_{i=2}^{N} \Delta t_i$$

$$\sigma^2_{\text{IAT}} = \frac{1}{N-2} \sum_{i=2}^{N} (\Delta t_i - \mu_{\text{IAT}})^2$$

## Features

- TCP Finite-State Machine: Tracks connection lifecycles (`LISTEN`, `SYN_SENT`, `SYN_RECEIVED`, `ESTABLISHED`, `FIN_WAIT`, `CLOSED`).
- High-Resolution IAT Statistics: Computes sample means and variances for jitter analysis.
- Zero Dependencies: Pure Python standard library implementation.

## Installation

```bash
git clone https://gitlab.com/jk9576/pcap-flow-summarizer.git
cd pcap-flow-summarizer
pip install -e .
```

## Running Tests

```bash
python -m unittest discover tests
```

## License

MIT License. See LICENSE for details.
