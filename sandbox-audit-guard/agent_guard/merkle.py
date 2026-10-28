import hashlib
from typing import List, Optional, Tuple


class MerkleTree:
    """
    Cryptographic Merkle Tree for verifiable, tamper-evident audit logs.
    Enables logarithmic O(log N) inclusion proofs for tool-call records.
    """

    def __init__(self, leaf_hashes: List[str]):
        if not leaf_hashes:
            raise ValueError("Cannot construct Merkle tree with empty leaves.")
        self.leaves = [bytes.fromhex(h) if len(h) == 64 else hashlib.sha256(h.encode()).digest() for h in leaf_hashes]
        self.levels = [self.leaves]
        self._build_tree()

    @staticmethod
    def _hash_pair(left: bytes, right: bytes) -> bytes:
        return hashlib.sha256(left + right).digest()

    def _build_tree(self):
        current = self.leaves
        while len(current) > 1:
            next_level = []
            for i in range(0, len(current), 2):
                left = current[i]
                right = current[i + 1] if i + 1 < len(current) else current[i]  # Duplicate odd leaf
                next_level.append(self._hash_pair(left, right))
            self.levels.append(next_level)
            current = next_level

    @property
    def root(self) -> str:
        return self.levels[-1][0].hex()

    def generate_proof(self, leaf_index: int) -> List[Tuple[str, str]]:
        """Generates audit path for leaf at leaf_index. Returns list of (direction, hash_hex)."""
        if leaf_index < 0 or leaf_index >= len(self.leaves):
            raise IndexError("Leaf index out of bounds.")
        proof = []
        idx = leaf_index
        for level in self.levels[:-1]:
            is_right = (idx % 2 == 1)
            sibling_idx = idx - 1 if is_right else (idx + 1 if idx + 1 < len(level) else idx)
            direction = "left" if is_right else "right"
            proof.append((direction, level[sibling_idx].hex()))
            idx //= 2
        return proof

    @classmethod
    def verify_proof(cls, leaf_hash_hex: str, proof: List[Tuple[str, str]], expected_root_hex: str) -> bool:
        curr = bytes.fromhex(leaf_hash_hex)
        for direction, sibling_hex in proof:
            sibling = bytes.fromhex(sibling_hex)
            if direction == "left":
                curr = cls._hash_pair(sibling, curr)
            else:
                curr = cls._hash_pair(curr, sibling)
        return curr.hex() == expected_root_hex
