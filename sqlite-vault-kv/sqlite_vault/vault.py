import hashlib
import hmac
import os
import sqlite3
import time
from typing import Dict, List, Optional, Tuple

class HKDF:
    """
    RFC 5869 HMAC-based Extract-and-Expand Key Derivation Function.
    Derives cryptographically strong pseudorandom keys from master key material.
    """
    @staticmethod
    def extract(salt: bytes, ikm: bytes) -> bytes:
        if not salt:
            salt = bytes(32)
        return hmac.new(salt, ikm, hashlib.sha256).digest()

    @staticmethod
    def expand(prk: bytes, info: bytes, length: int) -> bytes:
        n = (length + 31) // 32
        if n > 255:
            raise ValueError("HKDF expand output length exceeds limit")
        okm = b""
        t = b""
        for i in range(1, n + 1):
            t = hmac.new(prk, t + info + bytes([i]), hashlib.sha256).digest()
            okm += t
        return okm[:length]

    @classmethod
    def derive(cls, ikm: bytes, salt: bytes, info: bytes, length: int) -> bytes:
        prk = cls.extract(salt, ikm)
        return cls.expand(prk, info, length)

class EncryptedVault:
    """
    Zero-dependency transactional SQLite key-value vault.
    Implements RFC 5869 HKDF key derivation, CTR-SHA256 authenticated encryption,
    and atomic passphrase rotation.
    """
    CURRENT_VERSION = 1

    def __init__(self, db_path: str, passphrase: str):
        self.db_path = db_path
        self.passphrase = passphrase.encode("utf-8")
        self._init_db()

    def _derive_keys(self, salt: bytes, key_name: str) -> Tuple[bytes, bytes]:
        # PBKDF2 stretching to prevent brute force
        stretched = hashlib.pbkdf2_hmac("sha256", self.passphrase, salt, iterations=100_000, dklen=32)
        # HKDF domain separation for encryption key and integrity MAC key
        enc_key = HKDF.derive(stretched, salt, key_name.encode("utf-8") + b":enc", 32)
        mac_key = HKDF.derive(stretched, salt, key_name.encode("utf-8") + b":mac", 32)
        return enc_key, mac_key

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("""
                CREATE TABLE IF NOT EXISTS vault (
                    key TEXT PRIMARY KEY,
                    salt BLOB NOT NULL,
                    ciphertext BLOB NOT NULL,
                    tag BLOB NOT NULL,
                    version INT NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)
            conn.commit()

    @staticmethod
    def _keystream_xor(data: bytes, key: bytes, nonce: bytes) -> bytes:
        keystream = b""
        counter = 0
        while len(keystream) < len(data):
            ctr_block = counter.to_bytes(4, "big")
            keystream += hashlib.sha256(key + nonce + ctr_block).digest()
            counter += 1
        return bytes([b ^ k for b, k in zip(data, keystream[:len(data)])])

    def set(self, key: str, value: str):
        salt = os.urandom(16)
        nonce = os.urandom(16)
        enc_key, mac_key = self._derive_keys(salt, key)
        val_bytes = value.encode("utf-8")

        ct = self._keystream_xor(val_bytes, enc_key, nonce)
        payload = nonce + ct
        tag = hmac.new(mac_key, salt + payload, hashlib.sha256).digest()

        now = time.time()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO vault (key, salt, ciphertext, tag, version, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (key, salt, payload, tag, self.CURRENT_VERSION, now),
            )
            conn.commit()

    def get(self, key: str) -> Optional[str]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("SELECT salt, ciphertext, tag FROM vault WHERE key = ?", (key,))
            row = cur.fetchone()
            if not row:
                return None
            salt, payload, tag = row
            if len(payload) < 16:
                raise ValueError("Corrupt vault payload: insufficient length for nonce")
            nonce = payload[:16]
            ct = payload[16:]

            enc_key, mac_key = self._derive_keys(salt, key)
            computed_tag = hmac.new(mac_key, salt + payload, hashlib.sha256).digest()
            if not hmac.compare_digest(tag, computed_tag):
                raise ValueError("Cryptographic verification failed: invalid passphrase or tampered ciphertext")

            decrypted = self._keystream_xor(ct, enc_key, nonce)
            return decrypted.decode("utf-8")

    def rekey(self, new_passphrase: str):
        """Atomically re-encrypts all vault entries under a new master passphrase."""
        keys = self.list_keys()
        items = {}
        for k in keys:
            items[k] = self.get(k)

        # Temporarily switch passphrase and update in single transaction
        self.passphrase = new_passphrase.encode("utf-8")
        with sqlite3.connect(self.db_path) as conn:
            for k, val in items.items():
                if val is not None:
                    salt = os.urandom(16)
                    nonce = os.urandom(16)
                    enc_key, mac_key = self._derive_keys(salt, k)
                    val_bytes = val.encode("utf-8")
                    ct = self._keystream_xor(val_bytes, enc_key, nonce)
                    payload = nonce + ct
                    tag = hmac.new(mac_key, salt + payload, hashlib.sha256).digest()
                    now = time.time()
                    conn.execute(
                        "UPDATE vault SET salt = ?, ciphertext = ?, tag = ?, updated_at = ? WHERE key = ?",
                        (salt, payload, tag, now, k),
                    )
            conn.commit()

    def list_keys(self) -> List[str]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("SELECT key FROM vault ORDER BY key ASC")
            return [r[0] for r in cur.fetchall()]
