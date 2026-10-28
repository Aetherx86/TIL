# ip-cidr-trie

High-performance binary Radix Trie for IPv4 CIDR matching and egress routing.

## Overview

Evaluating IP addresses against thousands of CIDR blocks using sequential loops introduces significant latency. `ip-cidr-trie` implements a binary Radix Trie (prefix tree) operating on 32-bit integer representations of IPv4 addresses.

It achieves $O(W)$ lookup time where $W = 32$ bits, independent of the number of registered CIDR rules, making it ideal for firewall policies, sandbox egress controls, and IP geolocation routing.

## Features

- Constant-Time $O(32)$ Matching: Lookup performance scales independently of routing table rule size.
- Longest-Prefix Matching (LPM): Accurately resolves overlapping subnets (e.g., matching `10.1.2.0/24` over `10.0.0.0/8`).
- Arbitrary Payload Binding: Attach arbitrary strings, objects, or actions to matched prefixes.
- Zero Dependencies: Built with Python's standard `struct` and `socket` modules.

## Installation

```bash
git clone https://gitlab.com/jk9576/ip-cidr-trie.git
cd ip-cidr-trie
pip install -e .
```

## CLI Usage

```bash
cidr-trie --rule 10.0.0.0/8=PRIVATE_NET --rule 169.254.0.0/16=METADATA_BLOCKED 169.254.169.254
```

Output:

```
169.254.169.254 -> METADATA_BLOCKED
```

## Python API Usage

```python
from ip_cidr_trie.trie import RadixTrie

trie = RadixTrie()
trie.insert("10.0.0.0/8", "INTERNAL_CORP")
trie.insert("10.50.0.0/16", "HIGH_SECURITY_ZONE")

action = trie.find_longest_prefix("10.50.12.4")
print(action)  # "HIGH_SECURITY_ZONE"
```

## Running Tests

```bash
python -m unittest discover tests
```

## License

MIT License. See LICENSE for details.
