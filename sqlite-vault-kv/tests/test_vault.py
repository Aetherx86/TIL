import os
import tempfile
import unittest
from sqlite_vault.vault import EncryptedVault, HKDF

class TestVault(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
        self.tmp.close()
        self.db_path = self.tmp.name

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_hkdf_rfc5869_vectors(self):
        ikm = bytes.fromhex("0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b")
        salt = bytes.fromhex("000102030405060708090a0b0c")
        info = bytes.fromhex("f0f1f2f3f4f5f6f7f8f9")
        okm = HKDF.derive(ikm, salt, info, 42)
        expected = bytes.fromhex("3cb25f25faacd57a90434f64d0362f2a2d2d0a90cf1a5a4c5db02d56ecc4c5bf34007208d5b887185865")
        self.assertEqual(okm, expected)

    def test_vault_encryption_roundtrip(self):
        v = EncryptedVault(self.db_path, "super-secret-password-123")
        v.set("api_key", "sk-live-9876543210")
        self.assertEqual(v.get("api_key"), "sk-live-9876543210")

    def test_tamper_detection(self):
        v = EncryptedVault(self.db_path, "correct-pass")
        v.set("k1", "v1")
        v_wrong = EncryptedVault(self.db_path, "wrong-pass")
        with self.assertRaises(ValueError):
            v_wrong.get("k1")

    def test_atomic_rekey(self):
        v = EncryptedVault(self.db_path, "old-pass")
        v.set("secret", "confidential-data")
        v.rekey("new-stronger-pass")
        self.assertEqual(v.get("secret"), "confidential-data")
        # Ensure old pass no longer decrypts
        v_old = EncryptedVault(self.db_path, "old-pass")
        with self.assertRaises(ValueError):
            v_old.get("secret")

if __name__ == "__main__":
    unittest.main()
