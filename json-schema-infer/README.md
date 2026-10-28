# json-schema-infer

Lattice-Based JSON Schema Draft-07 Synthesis and Numeric Bound Inference.

## Overview

Infers structural JSON Schema specifications from JSON instances using a formal type-lattice unification framework. It synthesizes structural typing, aggregates numeric interval bounds $[\min, \max]$, and infers semantic string formats (RFC 4122 UUID, RFC 3986 URI, RFC 5322 Email).

## Type Lattice

```
         any (Top)
       /   |   \
    string number object
           |     \
        integer   array
           \     /
          never (Bottom)
```

## Features

- Formal Lattice Join: Resolves numeric promotions (e.g., $\text{integer} \sqcup \text{number} = \text{number}$).
- Compact Schema Minimization: Deduplicates union variants within `anyOf` arrays.
- Zero External Dependencies: Pure standard library implementation.

## Installation

```bash
git clone https://gitlab.com/jk9576/json-schema-infer.git
cd json-schema-infer
pip install -e .
```

## Running Tests

```bash
python -m unittest discover tests
```

## License

MIT License. See LICENSE for details.
