# jwt-audit-toolkit

Offline JSON Web Token (JWT) debugger and security vulnerability scanner.

## Overview

JSON Web Tokens are widely used for API authentication and microservice authorization. However, flawed implementations frequently suffer from algorithm confusion vulnerabilities (e.g., accepting `alg: none`), expired token acceptance, or signature verification bypasses.

`jwt-audit-toolkit` inspects tokens locally without network calls, decoding headers and claims while flagging known vulnerability patterns.

## Features

- Algorithm Confusion Detection: Flags insecure `none` algorithm declarations and weak signature schemes.
- Expiration Claim Analysis: Computes validity windows against current timestamps (`exp`, `nbf`, `iat`).
- Offline Parsing: Decodes and formats headers and payload bodies without sending sensitive tokens over the network.
- Zero Dependencies: Uses standard `base64` and `json` modules.

## Installation

```bash
git clone https://gitlab.com/jk9576/jwt-audit-toolkit.git
cd jwt-audit-toolkit
pip install -e .
```

## CLI Usage

```bash
jwt-audit eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkFsaWNlIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

Sample Output:

```
=== JWT Header ===
{
  "alg": "HS256",
  "typ": "JWT"
}

=== JWT Payload ===
{
  "sub": "1234567890",
  "name": "Alice",
  "iat": 1516239022
}

Expired: False
None Algorithm Flaw: False
```

## Python API Usage

```python
from jwt_audit.auditor import JWTAuditor

token_info = JWTAuditor.inspect("eyJhbGciOiAibm9uZSIgfQ.eyJzdWIiOiAidGVzdCJ9.")
if token_info.is_none_algorithm:
    print("Security Alert: Token uses 'none' algorithm!")
```

## Running Tests

```bash
python -m unittest discover tests
```

## License

MIT License. See LICENSE for details.
