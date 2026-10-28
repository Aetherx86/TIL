# regex-bench-fuzzer

Regular expression backtracking fuzzer and ReDoS vulnerability scanner.

## Overview

Regular Expression Denial of Service (ReDoS) occurs when an unanchored or nested regular expression experiences catastrophic polynomial or exponential backtracking when presented with adversarial input. `regex-bench-fuzzer` evaluates regular expressions against targeted repetition strings, measuring execution duration to flag vulnerable expressions.

## Features

- Catastrophic Backtracking Detection: Generates pathological prefixes and suffix mismatch strings to trigger worst-case backtracking.
- Execution Duration Benchmark: Measures search latency using high-resolution performance counters.
- Safe Threshold Interruption: Flags patterns exceeding configurable execution timeouts.
- Zero Dependencies: Pure Python standard library implementation.

## Installation

```bash
git clone https://gitlab.com/jk9576/regex-bench-fuzzer.git
cd regex-bench-fuzzer
pip install -e .
```

## CLI Usage

```bash
regex-fuzz "(a+)+$"
```

Sample Output:

```
Pattern: (a+)+$
Catastrophic Backtracking Detected: True
Max Search Duration: 0.6421s
```

## Python API Usage

```python
from regex_fuzzer.fuzzer import ReDoSFuzzer

fuzzer = ReDoSFuzzer(timeout_threshold=0.5)
result = fuzzer.test_pattern(r"^([a-zA-Z0-9]+)*$")
if result.is_vulnerable:
    print(f"Warning: ReDoS vulnerability detected in pattern! Execution took {result.max_duration_sec:.2f}s")
```

## Running Tests

```bash
python -m unittest discover tests
```

## License

MIT License. See LICENSE for details.
