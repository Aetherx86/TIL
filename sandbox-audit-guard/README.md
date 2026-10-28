# sandbox-audit-guard

Agent Sandbox Egress and Merkle-Verified Tool-Call Integrity Monitor.

## Overview

Autonomous tool-using AI agents require robust operational containment and verifiable telemetry. When executing commands within evaluation sandboxes or deployment containers, agents may attempt:
1. Covert Egress: Querying link-local Cloud Metadata endpoints (IMDSv1/v2), mounting Docker sockets, or opening reverse shells.
2. Shell Obfuscation: Evading signature filters through base64 pipes, IFS splitting, and octal byte escapes.
3. Transcript Tampering: Manipulating execution logs, exit codes, or tool return payloads post-hoc.

`sandbox-audit-guard` provides real-time detection, syntactic shell obfuscation analysis, and Merkle-tree authenticated audit paths.

## Cryptographic Merkle Tree Architecture

Tool executions form an authenticated Merkle tree $T$:
- Leaves: $H_i = \text{SHA-256}(\text{CanonicalPayload}_i)$
- Intermediate nodes: $H_{parent} = \text{SHA-256}(H_{left} \parallel H_{right})$
- Root: Top-level hash representing the complete immutable session history.

Audit proofs allow any individual tool invocation to be verified in $O(\log N)$ time and space without transmitting the full trajectory:

$$\text{VerifyProof}(H_i, \pi_i, \text{Root}) = \text{True}$$

## Features

- Syntactic Shell Obfuscation Detection: Dissects command strings for `$IFS` substitutions, chained variable expansions, and hex/octal escapes.
- Cryptographic Inclusion Proofs: Generates logarithmic Merkle proofs for external third-party verifiers.
- Zero External Dependencies: Pure Python standard library implementation.

## Installation

```bash
git clone https://gitlab.com/jk9576/sandbox-audit-guard.git
cd sandbox-audit-guard
pip install -e .
```

## Running Tests

```bash
python -m unittest discover tests
```

## License

MIT License. See LICENSE for details.
