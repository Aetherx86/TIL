# cron-syntax-explainer

Translates standard UNIX cron expressions into plain English human descriptions.

## Overview

UNIX cron syntax (e.g., `*/15 9-17 * * 1-5`) is compact but prone to misinterpretation by developers and operations teams. `cron-syntax-explainer` decomposes 5-field cron strings and translates them into unambiguous English sentences.

## Features

- 5-Field Parsing: Decomposes minute, hour, day-of-month, month, and day-of-week fields.
- Step Values: Explains step intervals (e.g., `*/10` -> `every 10 minutes`).
- Ranges and Lists: Accurately articulates ranges (`9-17` -> `from hour 9 through 17`) and comma-separated lists.
- Zero Dependencies: Pure Python standard library implementation.

## Installation

```bash
git clone https://gitlab.com/jk9576/cron-syntax-explainer.git
cd cron-syntax-explainer
pip install -e .
```

## CLI Usage

```bash
cron-explain "*/15 9-17 * * 1-5"
```

Output:

```
Runs every 15 minutes, from hour 9 through 17, on every day-of-month, in every month, and from day-of-week 1 through 5.
```

## Python API Usage

```python
from cron_explainer.explainer import explain_cron

description = explain_cron("0 0 1 * *")
print(description)  # "Runs at minute 0, at hour 0, on day-of-month 1, in every month, and on every day-of-week."
```

## Running Tests

```bash
python -m unittest discover tests
```

## License

MIT License. See LICENSE for details.
