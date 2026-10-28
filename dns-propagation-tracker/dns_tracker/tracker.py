import socket
import struct
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

@dataclass
class DNSRecord:
    name: str
    record_type: str
    ttl: int
    data: str

@dataclass
class DNSResponse:
    rcode: int
    answers: List[DNSRecord] = field(default_factory=list)
    authorities: List[DNSRecord] = field(default_factory=list)
    additionals: List[DNSRecord] = field(default_factory=list)

class RFC1035Dissector:
    """
    Pure Python RFC 1035 wire-format DNS dissector.
    Handles message compression pointer chasing (0xC0),
    Type A (IPv4), AAAA (IPv6), CNAME, and TXT records.
    """
    TYPE_NAMES = {1: "A", 2: "NS", 5: "CNAME", 6: "SOA", 15: "MX", 16: "TXT", 28: "AAAA"}

    @classmethod
    def decode_name(cls, buffer: bytes, offset: int) -> Tuple[str, int]:
        labels = []
        jumped = False
        initial_offset = offset
        consumed = 0

        while True:
            if offset >= len(buffer):
                break
            length = buffer[offset]
            if length == 0:
                if not jumped:
                    consumed = offset + 1 - initial_offset
                break
            elif (length & 0xC0) == 0xC0:
                # Compression pointer
                pointer = struct.unpack("!H", buffer[offset:offset + 2])[0] & 0x3FFF
                if not jumped:
                    consumed = offset + 2 - initial_offset
                    jumped = True
                offset = pointer
            else:
                offset += 1
                labels.append(buffer[offset:offset + length].decode("ascii", errors="ignore"))
                offset += length

        name = ".".join(labels)
        return name, (consumed if jumped else (offset + 1 - initial_offset))

    @classmethod
    def parse_packet(cls, packet: bytes) -> DNSResponse:
        if len(packet) < 12:
            raise ValueError("DNS packet too short for 12-byte header")
        _, flags, qdcount, ancount, nscount, arcount = struct.unpack("!HHHHHH", packet[:12])
        rcode = flags & 0x0F

        offset = 12
        # Skip questions
        for _ in range(qdcount):
            _, consumed = cls.decode_name(packet, offset)
            offset += consumed + 4  # QTYPE (2) + QCLASS (2)

        def parse_rr_section(count: int) -> List[DNSRecord]:
            nonlocal offset
            records = []
            for _ in range(count):
                if offset >= len(packet):
                    break
                name, consumed = cls.decode_name(packet, offset)
                offset += consumed
                rtype, rclass, ttl, rdlength = struct.unpack("!HHIH", packet[offset:offset + 10])
                offset += 10
                rdata_raw = packet[offset:offset + rdlength]
                offset += rdlength

                type_str = cls.TYPE_NAMES.get(rtype, f"TYPE_{rtype}")
                data_str = ""
                if rtype == 1 and len(rdata_raw) == 4:  # A
                    data_str = socket.inet_ntoa(rdata_raw)
                elif rtype == 28 and len(rdata_raw) == 16:  # AAAA
                    data_str = socket.inet_ntop(socket.AF_INET6, rdata_raw)
                elif rtype == 5:  # CNAME
                    data_str, _ = cls.decode_name(packet, offset - rdlength)
                else:
                    data_str = rdata_raw.hex()

                records.append(DNSRecord(name=name, record_type=type_str, ttl=ttl, data=data_str))
            return records

        answers = parse_rr_section(ancount)
        auths = parse_rr_section(nscount)
        adds = parse_rr_section(arcount)

        return DNSResponse(rcode=rcode, answers=answers, authorities=auths, additionals=adds)

class DNSTracker:
    RESOLVERS = {
        "Cloudflare": "1.1.1.1",
        "Google": "8.8.8.8",
        "Quad9": "9.9.9.9",
        "OpenDNS": "208.67.222.222",
    }

    @staticmethod
    def build_a_query(hostname: str) -> bytes:
        header = struct.pack("!HHHHHH", 0x1234, 0x0100, 1, 0, 0, 0)
        qname = b""
        for label in hostname.split("."):
            qname += bytes([len(label)]) + label.encode("ascii")
        qname += bytes([0])
        question = qname + struct.pack("!HH", 1, 1)
        return header + question
