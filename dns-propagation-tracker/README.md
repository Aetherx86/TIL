# dns-propagation-tracker

Cross-resolver DNS lookup and propagation diagnostic tool.

## Overview

When DNS records are updated, changes propagate across global recursive resolvers at varying rates due to TTL caching and upstream synchronizations. `dns-propagation-tracker` queries multiple global public anycast DNS resolvers (Cloudflare, Google, Quad9, OpenDNS) directly via raw UDP socket datagrams (RFC 1035) to measure propagation status.

## Features

- Raw RFC 1035 Datagram Construction: Formats binary DNS query packets without third-party libraries (such as dnspython).
- Multi-Resolver Validation: Simultaneously inspects responses from Cloudflare (`1.1.1.1`), Google (`8.8.8.8`), Quad9 (`9.9.9.9`), and OpenDNS (`208.67.222.222`).
- Discrepancy Flagging: Identifies split-horizon anomalies and resolution failures.
- Zero Dependencies: Uses standard `socket` and `struct` modules.

## Installation

```bash
git clone https://gitlab.com/jk9576/dns-propagation-tracker.git
cd dns-propagation-tracker
pip install -e .
```

## CLI Usage

```bash
dns-track example.com
```

Sample Output:

```
Cloudflare   (1.1.1.1        ): OK - Answer Count: 1
Google       (8.8.8.8        ): OK - Answer Count: 1
Quad9        (9.9.9.9        ): OK - Answer Count: 1
OpenDNS      (208.67.222.222 ): OK - Answer Count: 1
```

## Python API Usage

```python
from dns_tracker.tracker import DNSTracker

tracker = DNSTracker()
ok, result = tracker.query_resolver("example.com", "1.1.1.1")
print(f"Cloudflare resolution: {result}")
```

## Running Tests

```bash
python -m unittest discover tests
```

## License

MIT License. See LICENSE for details.
