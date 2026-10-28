import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

class AuditSeverity(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

@dataclass
class AuditFinding:
    severity: AuditSeverity
    title: str
    description: str

@dataclass
class DecodedJWT:
    header: Dict[str, Any]
    payload: Dict[str, Any]
    signature_bytes: bytes
    signing_input: bytes
    raw_token: str
    is_expired: bool
    is_none_algorithm: bool
    findings: List[AuditFinding] = field(default_factory=list)

class JWTAuditor:
    """
    Security auditor for JSON Web Tokens (RFC 7519).
    Audits cryptographic signature algorithms (HS256/384/512),
    CVE-2015-9235 key confusion, 'none' algorithm bypass,
    and temporal validity with clock skew compensation.
    """
    SUPPORTED_HMAC = {
        "HS256": hashlib.sha256,
        "HS384": hashlib.sha384,
        "HS512": hashlib.sha512,
    }

    @staticmethod
    def b64_decode(segment: str) -> bytes:
        rem = len(segment) % 4
        if rem > 0:
            segment += "=" * (4 - rem)
        return base64.urlsafe_b64decode(segment.encode("ascii"))

    @staticmethod
    def b64_encode(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")

    @classmethod
    def inspect(cls, token: str, clock_skew_sec: float = 0.0) -> DecodedJWT:
        parts = token.strip().split(".")
        if len(parts) != 3:
            raise ValueError(f"Invalid JWT format: expected 3 dot-delimited segments, got {len(parts)}")

        header_bytes = cls.b64_decode(parts[0])
        payload_bytes = cls.b64_decode(parts[1])
        sig_bytes = cls.b64_decode(parts[2])
        signing_input = f"{parts[0]}.{parts[1]}".encode("ascii")

        header = json.loads(header_bytes.decode("utf-8"))
        payload = json.loads(payload_bytes.decode("utf-8"))

        findings: List[AuditFinding] = []
        alg = header.get("alg", "")
        is_none = str(alg).lower() == "none"

        if is_none:
            findings.append(AuditFinding(
                severity=AuditSeverity.CRITICAL,
                title="Unsigned Token (alg: none)",
                description="Token specifies 'none' algorithm; no cryptographic authentication is enforced.",
            ))

        now = time.time()
        is_expired = False
        if "exp" in payload:
            exp_val = float(payload["exp"])
            if (now - clock_skew_sec) > exp_val:
                is_expired = True
                findings.append(AuditFinding(
                    severity=AuditSeverity.HIGH,
                    title="Token Expired",
                    description=f"Expiration timestamp {exp_val} is in the past (current: {now:.1f}).",
                ))

        if "nbf" in payload:
            nbf_val = float(payload["nbf"])
            if (now + clock_skew_sec) < nbf_val:
                findings.append(AuditFinding(
                    severity=AuditSeverity.MEDIUM,
                    title="Token Not Yet Valid",
                    description=f"Not-before timestamp {nbf_val} is in the future.",
                ))

        return DecodedJWT(
            header=header,
            payload=payload,
            signature_bytes=sig_bytes,
            signing_input=signing_input,
            raw_token=token,
            is_expired=is_expired,
            is_none_algorithm=is_none,
            findings=findings,
        )

    @classmethod
    def verify_hmac(cls, token: str, secret: bytes) -> bool:
        """Verifies HMAC signature in constant time against timing attacks."""
        decoded = cls.inspect(token)
        alg = decoded.header.get("alg", "")
        if alg not in cls.SUPPORTED_HMAC:
            return False
        hash_fn = cls.SUPPORTED_HMAC[alg]
        expected_sig = hmac.new(secret, decoded.signing_input, hash_fn).digest()
        return hmac.compare_digest(decoded.signature_bytes, expected_sig)

    @classmethod
    def test_key_confusion(cls, token: str, public_key_pem: str) -> bool:
        """
        Tests CVE-2015-9235: verifies if a token signed with HMAC accepts
        the server's public key (PEM) as an HMAC shared secret.
        """
        return cls.verify_hmac(token, public_key_pem.encode("utf-8"))
