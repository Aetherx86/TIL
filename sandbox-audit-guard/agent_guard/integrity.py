import hashlib
import hmac
import json
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class ToolCallRecord:
    index: int
    tool_name: str
    arguments: Dict[str, Any]
    output: str
    exit_code: int
    timestamp: float
    previous_hash: str
    record_hash: str = ""

    def canonical_payload(self) -> bytes:
        """Produces deterministic JSON bytes for cryptographic hashing."""
        data = {
            "index": self.index,
            "tool_name": self.tool_name,
            "arguments": self.arguments,
            "output": self.output,
            "exit_code": self.exit_code,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
        }
        return json.dumps(data, sort_keys=True, separators=(",", ":")).encode("utf-8")


class IntegrityChain:
    """
    Append-only tamper-evident hash chain for recording agent tool executions.
    Can be signed with an HMAC secret key known only to the supervisory kernel.
    """

    GENESIS_HASH = "0" * 64

    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key.encode("utf-8") if secret_key else None
        self.records: List[ToolCallRecord] = []

    def _compute_hash(self, payload: bytes) -> str:
        if self.secret_key:
            return hmac.new(self.secret_key, payload, hashlib.sha256).hexdigest()
        return hashlib.sha256(payload).hexdigest()

    def append(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        output: str,
        exit_code: int = 0,
        timestamp: Optional[float] = None,
    ) -> ToolCallRecord:
        idx = len(self.records)
        prev_hash = self.records[-1].record_hash if idx > 0 else self.GENESIS_HASH
        ts = timestamp if timestamp is not None else time.time()

        rec = ToolCallRecord(
            index=idx,
            tool_name=tool_name,
            arguments=arguments,
            output=output,
            exit_code=exit_code,
            timestamp=ts,
            previous_hash=prev_hash,
        )
        rec.record_hash = self._compute_hash(rec.canonical_payload())
        self.records.append(rec)
        return rec

    def verify_chain(self) -> Tuple[bool, Optional[str]]:
        """Verifies the integrity of the entire record chain."""
        expected_prev = self.GENESIS_HASH
        for i, rec in enumerate(self.records):
            if rec.index != i:
                return False, f"Index mismatch at position {i}: record says {rec.index}"
            if rec.previous_hash != expected_prev:
                return False, f"Hash link broken at record {i}: expected previous {expected_prev}, got {rec.previous_hash}"
            
            calculated_hash = self._compute_hash(rec.canonical_payload())
            if rec.record_hash != calculated_hash:
                return False, f"Tampered record at index {i}: hash {rec.record_hash} does not match payload {calculated_hash}"
            
            expected_prev = rec.record_hash

        return True, None

    def export_jsonl(self) -> str:
        lines = [json.dumps(asdict(r)) for r in self.records]
        return "\n".join(lines)

    @classmethod
    def load_jsonl(cls, content: str, secret_key: Optional[str] = None) -> "IntegrityChain":
        chain = cls(secret_key=secret_key)
        for line in content.strip().split("\n"):
            if not line.strip():
                continue
            data = json.loads(line)
            rec = ToolCallRecord(**data)
            chain.records.append(rec)
        return chain
