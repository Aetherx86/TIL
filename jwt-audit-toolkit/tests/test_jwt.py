import json
import time
import unittest
from jwt_audit.auditor import JWTAuditor, AuditSeverity

class TestJWTAuditor(unittest.TestCase):
    def _create_token(self, header: dict, payload: dict, secret: bytes = b"secret-key") -> str:
        h_str = JWTAuditor.b64_encode(json.dumps(header).encode("utf-8"))
        p_str = JWTAuditor.b64_encode(json.dumps(payload).encode("utf-8"))
        sig_input = f"{h_str}.{p_str}".encode("ascii")
        alg = header.get("alg", "HS256")
        if alg.lower() == "none":
            return f"{h_str}.{p_str}."
        hash_fn = JWTAuditor.SUPPORTED_HMAC[alg]
        import hmac
        sig = JWTAuditor.b64_encode(hmac.new(secret, sig_input, hash_fn).digest())
        return f"{h_str}.{p_str}.{sig}"

    def test_hs256_verification(self):
        token = self._create_token({"alg": "HS256", "typ": "JWT"}, {"sub": "alice", "exp": time.time() + 3600})
        self.assertTrue(JWTAuditor.verify_hmac(token, b"secret-key"))
        self.assertFalse(JWTAuditor.verify_hmac(token, b"wrong-secret"))

    def test_none_algorithm_detection(self):
        token = self._create_token({"alg": "none"}, {"sub": "attacker"})
        decoded = JWTAuditor.inspect(token)
        self.assertTrue(decoded.is_none_algorithm)
        criticals = [f for f in decoded.findings if f.severity == AuditSeverity.CRITICAL]
        self.assertEqual(len(criticals), 1)

    def test_key_confusion_vulnerability_test(self):
        fake_pub_key = "-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8A\n-----END PUBLIC KEY-----"
        # Attacker signs token using public key as HMAC secret
        token = self._create_token({"alg": "HS256"}, {"sub": "admin"}, secret=fake_pub_key.encode("utf-8"))
        self.assertTrue(JWTAuditor.test_key_confusion(token, fake_pub_key))

if __name__ == "__main__":
    unittest.main()
