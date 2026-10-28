import math
import socket
import struct
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


class TCPState(Enum):
    LISTEN = "LISTEN"
    SYN_SENT = "SYN_SENT"
    SYN_RECEIVED = "SYN_RECEIVED"
    ESTABLISHED = "ESTABLISHED"
    FIN_WAIT = "FIN_WAIT"
    CLOSED = "CLOSED"


@dataclass
class FlowKey:
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    protocol: str

    def canonical(self) -> Tuple[str, str, int, int, str]:
        endpoint_a = (self.src_ip, self.src_port)
        endpoint_b = (self.dst_ip, self.dst_port)
        if endpoint_a <= endpoint_b:
            return (self.src_ip, self.dst_ip, self.src_port, self.dst_port, self.protocol)
        return (self.dst_ip, self.src_ip, self.dst_port, self.src_port, self.protocol)


@dataclass
class FlowStats:
    packet_count: int = 0
    total_bytes: int = 0
    start_ts: float = 0.0
    end_ts: float = 0.0
    tcp_state: TCPState = TCPState.LISTEN
    packet_sizes: List[int] = field(default_factory=list)
    inter_arrival_times: List[float] = field(default_factory=list)

    def mean_iat(self) -> float:
        if not self.inter_arrival_times:
            return 0.0
        return sum(self.inter_arrival_times) / len(self.inter_arrival_times)

    def variance_iat(self) -> float:
        if len(self.inter_arrival_times) < 2:
            return 0.0
        mean = self.mean_iat()
        return sum((x - mean) ** 2 for x in self.inter_arrival_times) / (len(self.inter_arrival_times) - 1)


class PcapReader:
    def __init__(self, filename: str):
        self.filename = filename

    def parse_packets(self):
        with open(self.filename, "rb") as f:
            global_header = f.read(24)
            if len(global_header) < 24:
                return
            magic = struct.unpack("<I", global_header[:4])[0]
            endian = "<" if magic == 0xa1b2c3d4 else ">"

            while True:
                p_header = f.read(16)
                if len(p_header) < 16:
                    break
                ts_sec, ts_usec, incl_len, _ = struct.unpack(endian + "IIII", p_header)
                data = f.read(incl_len)
                if len(data) < incl_len:
                    break
                ts = ts_sec + ts_usec / 1_000_000.0
                yield ts, data


class FlowSummarizer:
    @staticmethod
    def dissect_ipv4_packet(data: bytes) -> Optional[Tuple[FlowKey, int]]:
        if len(data) < 34:
            return None
        eth_type = struct.unpack("!H", data[12:14])[0]
        if eth_type != 0x0800:
            return None
        ip_header = data[14:34]
        proto = ip_header[9]
        src_ip = socket.inet_ntoa(ip_header[12:16])
        dst_ip = socket.inet_ntoa(ip_header[16:20])

        proto_name = "OTHER"
        src_port, dst_port = 0, 0
        tcp_flags = 0
        if proto == 6 and len(data) >= 54:
            proto_name = "TCP"
            src_port, dst_port = struct.unpack("!HH", data[34:38])
            tcp_flags = data[47]
        elif proto == 17 and len(data) >= 42:
            proto_name = "UDP"
            src_port, dst_port = struct.unpack("!HH", data[34:38])

        return FlowKey(src_ip, dst_ip, src_port, dst_port, proto_name), tcp_flags

    @classmethod
    def summarize(cls, pcap_path: str) -> Dict[Tuple, FlowStats]:
        reader = PcapReader(pcap_path)
        flows: Dict[Tuple, FlowStats] = {}
        for ts, packet_data in reader.parse_packets():
            dissected = cls.dissect_ipv4_packet(packet_data)
            if dissected is None:
                continue
            flow_key, flags = dissected
            canonical_key = flow_key.canonical()
            pkt_len = len(packet_data)

            if canonical_key not in flows:
                st = FlowStats(packet_count=1, total_bytes=pkt_len, start_ts=ts, end_ts=ts)
                st.packet_sizes.append(pkt_len)
                flows[canonical_key] = st
            else:
                st = flows[canonical_key]
                st.packet_count += 1
                st.total_bytes += pkt_len
                st.inter_arrival_times.append(max(0.0, ts - st.end_ts))
                st.end_ts = ts
                st.packet_sizes.append(pkt_len)

            # Update TCP State Machine if TCP
            if flow_key.protocol == "TCP":
                st = flows[canonical_key]
                if flags & 0x02:  # SYN
                    st.tcp_state = TCPState.SYN_SENT if not (flags & 0x10) else TCPState.SYN_RECEIVED
                elif flags & 0x10 and st.tcp_state in [TCPState.SYN_RECEIVED, TCPState.SYN_SENT]:
                    st.tcp_state = TCPState.ESTABLISHED
                elif flags & 0x01:  # FIN
                    st.tcp_state = TCPState.FIN_WAIT
                elif flags & 0x04:  # RST
                    st.tcp_state = TCPState.CLOSED

        return flows
