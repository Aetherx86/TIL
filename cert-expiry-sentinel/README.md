# cert-expiry-sentinel

Zero-dependency SSL and TLS certificate expiration monitor and scanner.

## Overview

Expired TLS certificates cause unexpected production downtime, degraded customer trust, and broken API pipelines. `cert-expiry-sentinel` is a lightweight, pure-standard-library Python utility designed to scan network endpoints, inspect X.509 validity windows, and alert system administrators before certificates expire.

It requires no external dependencies (like pyOpenSSL or cryptography), operating strictly through Python's built-in `ssl` and `socket` modules.

## Features

- Zero Runtime Dependencies: Operates exclusively with Python standard libraries.
- Multi-Endpoint Inspection: Scans domains, IP addresses, and custom TCP ports concurrently.
- Expiration Threshold Warning: Configurable days-remaining alert threshold (e.g., 30, 45, or 60 days).
- Automation and CI/CD Friendly: Returns deterministic exit codes (0 for valid, 1 for warnings or expired certificates).
- Diagnostic Error Reporting: Captures handshake timeouts, DNS resolution failures, and untrusted certificate authority errors.

## Installation

```bash
git clone https://gitlab.com/jk9576/cert-expiry-sentinel.git
cd cert-expiry-sentinel
pip install -e .
```

## CLI Usage

### Check Multiple Hosts

```bash
cert-sentinel example.com github.com:443 gitlab.com:443
```

Sample Output:

```
Hostname                       Status       Days Left    Expires At
---------------------------------------------------------------------------
example.com                    OK           78           2027-01-15
github.com                     OK           122          2027-02-28
gitlab.com                     OK           45           2026-12-13
```

### Set Custom Warning Threshold

```bash
cert-sentinel --warn-days 60 api.internal.corp:8443
```

## Python API Usage

```python
from cert_sentinel import CertificateChecker

checker = CertificateChecker(timeout=5.0)
info = checker.check_host("example.com", 443)

if info.is_expired:
    print(f"Alert: Certificate for {info.hostname} expired {abs(info.days_remaining)} days ago!")
elif info.days_remaining < 30:
    print(f"Warning: {info.hostname} certificate expires in {info.days_remaining} days.")
else:
    print(f"{info.hostname} certificate is valid until {info.not_after.isoformat()}.")
```

## Running Tests

Execute the unit test suite:

```bash
python -m unittest discover tests
```

## License

MIT License. See LICENSE for details.
