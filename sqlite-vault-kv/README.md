# sqlite-vault-kv

Lightweight encrypted key-value store backed by SQLite, PBKDF2, and HMAC authentication.

## Overview

`sqlite-vault-kv` provides a secure, single-file embedded key-value vault. Every entry stored in the database is protected with an independent random 16-byte cryptographic salt, 100,000 iterations of PBKDF2 key derivation, stream encryption, and constant-time HMAC-SHA256 authentication.

It avoids third-party C dependencies by using Python's standard `sqlite3`, `hashlib`, and `hmac` libraries.

## Security Architecture

1. Key Derivation: Master passphrase + unique 16-byte random salt -> PBKDF2-HMAC-SHA256 (100,000 rounds) -> 64 bytes of key material.
   - Bytes 0-31: Encryption key.
   - Bytes 32-63: HMAC integrity key.
2. Stream Keystream: Counter-mode SHA-256 stream cipher XORed with plaintext bytes.
3. Authenticated Integrity: HMAC-SHA256 computed over `salt + ciphertext`. Any modification or incorrect passphrase immediately triggers an integrity failure.

## Features

- Single-File Persistence: Uses local SQLite database files, making backups and synchronization trivial.
- Per-Key Salt Isolation: Each record possesses a unique cryptographic salt, preventing rainbow table attacks.
- Constant-Time Verification: Compares authentication tags using `hmac.compare_digest` to mitigate timing attacks.
- Zero Dependencies: Pure Python standard library implementation.

## Installation

```bash
git clone https://gitlab.com/jk9576/sqlite-vault-kv.git
cd sqlite-vault-kv
pip install -e .
```

## CLI Usage

### Store Secret

```bash
vault-kv --db secrets.vault --passphrase "master-key" set GITHUB_TOKEN "ghp_1234567890abcdef"
```

### Retrieve Secret

```bash
vault-kv --db secrets.vault --passphrase "master-key" get GITHUB_TOKEN
```

### List Keys

```bash
vault-kv --db secrets.vault --passphrase "master-key" list
```

## Python API Usage

```python
from sqlite_vault.vault import EncryptedVault

vault = EncryptedVault("app_secrets.db", "user-master-passphrase")
vault.set("database_url", "postgres://user:pass@localhost:5432/prod")

val = vault.get("database_url")
print(f"Retrieved: {val}")
```

## Running Tests

```bash
python -m unittest discover tests
```

## License

MIT License. See LICENSE for details.
