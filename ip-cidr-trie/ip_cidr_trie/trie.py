import socket
import struct
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

@dataclass
class PatriciaNode:
    bit_prefix: str  # Compressed binary bitstring (e.g. "1100000010101000")
    value: Optional[Any] = None
    is_terminal: bool = False
    children: Dict[str, "PatriciaNode"] = None

    def __post_init__(self):
        if self.children is None:
            self.children = {}

class PatriciaTrie:
    """
    Practical Algorithm to Retrieve Information Coded in Alphanumeric (Patricia Trie).
    Implements radix path compression for high-throughput longest prefix matching (LPM)
    across both IPv4 (32-bit) and IPv6 (128-bit) routing tables,
    plus route aggregation (CIDR supernetting).
    """
    def __init__(self):
        self.root = PatriciaNode(bit_prefix="")

    @staticmethod
    def ip_to_bitstring(ip_str: str) -> Tuple[str, int]:
        """Converts an IPv4 or IPv6 address to its full bit representation."""
        if ":" in ip_str:
            raw = socket.inet_pton(socket.AF_INET6, ip_str)
            bits = "".join(f"{b:08b}" for b in raw)
            return bits, 128
        else:
            raw = socket.inet_pton(socket.AF_INET, ip_str)
            bits = "".join(f"{b:08b}" for b in raw)
            return bits, 32

    def insert(self, cidr: str, value: Any = True):
        if "/" in cidr:
            ip_str, p_len_str = cidr.split("/", 1)
            p_len = int(p_len_str)
        else:
            ip_str = cidr
            p_len = 128 if ":" in cidr else 32

        full_bits, max_bits = self.ip_to_bitstring(ip_str)
        prefix_bits = full_bits[:p_len]
        self._insert_bits(self.root, prefix_bits, value)

    def _insert_bits(self, node: PatriciaNode, bits: str, value: Any):
        if not bits:
            node.value = value
            node.is_terminal = True
            return

        first_bit = bits[0]
        if first_bit not in node.children:
            node.children[first_bit] = PatriciaNode(bit_prefix=bits, value=value, is_terminal=True)
            return

        child = node.children[first_bit]
        # Calculate common prefix length between child.bit_prefix and bits
        common_len = 0
        min_len = min(len(child.bit_prefix), len(bits))
        while common_len < min_len and child.bit_prefix[common_len] == bits[common_len]:
            common_len += 1

        if common_len == len(child.bit_prefix):
            # Recurse into child
            self._insert_bits(child, bits[common_len:], value)
        else:
            # Split child node
            split_prefix = child.bit_prefix[:common_len]
            child_remaining_prefix = child.bit_prefix[common_len:]
            new_remaining_bits = bits[common_len:]

            split_node = PatriciaNode(bit_prefix=split_prefix)
            node.children[first_bit] = split_node

            # Re-attach child under split_node
            child.bit_prefix = child_remaining_prefix
            split_node.children[child_remaining_prefix[0]] = child

            if new_remaining_bits:
                split_node.children[new_remaining_bits[0]] = PatriciaNode(
                    bit_prefix=new_remaining_bits, value=value, is_terminal=True
                )
            else:
                split_node.value = value
                split_node.is_terminal = True

    def find_longest_prefix(self, ip_str: str) -> Optional[Any]:
        full_bits, _ = self.ip_to_bitstring(ip_str)
        curr = self.root
        last_match = curr.value if curr.is_terminal else None
        offset = 0

        while offset < len(full_bits):
            bit = full_bits[offset]
            if bit not in curr.children:
                break
            child = curr.children[bit]
            edge_len = len(child.bit_prefix)
            if full_bits[offset:offset + edge_len] != child.bit_prefix:
                break
            offset += edge_len
            curr = child
            if curr.is_terminal:
                last_match = curr.value

        return last_match

    @classmethod
    def aggregate_routes(cls, cidrs: List[str]) -> List[str]:
        """Performs route summarization / supernetting across adjacent subnets."""
        import ipaddress
        nets = [ipaddress.ip_network(c, strict=False) for c in cidrs]
        collapsed = ipaddress.collapse_addresses(nets)
        return [str(net) for net in collapsed]
