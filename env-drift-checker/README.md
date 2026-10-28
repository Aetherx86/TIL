# env-drift-checker

Environment variable drift detector for CI/CD and deployment configuration.

## Overview

When software applications evolve, new configuration keys are added to runtime `.env` files while `.env.example` templates fall out of sync. `env-drift-checker` parses environment templates and target configurations, flagging missing variables, empty values, and undocumented keys.

## Features

- Bi-directional Drift Detection: Identifies parameters present in template but absent in deployment, as well as undocumented deployment keys.
- Empty Value Warning: Flags mandatory configuration keys left blank in target environments.
- Quote and Comment Handling: Accurately strips comments, leading/trailing whitespace, and single/double quotation marks.
- Automated Gatekeeping: Returns non-zero exit codes when missing configurations are detected.

## Installation

```bash
git clone https://gitlab.com/jk9576/env-drift-checker.git
cd env-drift-checker
pip install -e .
```

## CLI Usage

```bash
env-drift --example .env.example --target .env
```

Sample Output:

```
Missing in target (2): DATABASE_URL, REDIS_PORT
Empty in target (1): STRIPE_PUBLIC_KEY
Undocumented in template (1): DEBUG_VERBOSE_LOGS
```

## Python API Usage

```python
from pathlib import Path
from env_drift.checker import EnvDriftChecker

report = EnvDriftChecker.compare(Path(".env.example"), Path(".env"))
if report.missing_in_target:
    print(f"Missing required configs: {report.missing_in_target}")
```

## Running Tests

```bash
python -m unittest discover tests
```

## License

MIT License. See LICENSE for details.
