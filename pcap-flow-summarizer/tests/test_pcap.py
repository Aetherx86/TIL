import os
import socket
import struct
import tempfile
import unittest
from pcap_flow.parser import FlowKey, FlowSummarizer, TCPState


class TestPcap(unittest.TestCase):
    def test_canonical_flow(self):
        k1 = FlowKey("192.168.1.1", "10.0.0.1", 443, 52100, "TCP")
        k2 = FlowKey("10.0.0.1", "192.168.1.1", 52100, 443, "TCP")
        self.assertEqual(k1.canonical(), k2.canonical())

    def _create_pcap_with_two_packets(self) -> bytes:
        gh = struct.pack("<IHHiIII", 0xa1b2c3d4, 2, 4, 0, 0, 65535, 1)

        eth = b"\x00" * 12 + struct.pack("!H", 0x0800)
        src_ip = socket.inet_aton("10.0.0.2")
        dst_ip = socket.inet_aton("10.0.0.1")
        ipv4 = struct.pack("!BBHHHBBH", 0x45, 0, 40, 1, 0, 64, 6, 0) + src_ip + dst_ip

        # Packet 1: SYN (flags=2)
        tcp1 = struct.pack("!HHIIBBHHH", 50000, 80, 1000, 0, (5 << 4), 2, 65535, 0, 0)
        payload1 = eth + ipv4 + tcp1
        ph1 = struct.pack("<IIII", 1600000000, 0, len(payload1), len(payload1))

        # Packet 2: SYN-ACK (flags=18) after 0.05s
        ipv4_rev = struct.pack("!BBHHHBBH", 0x45, 0, 40, 2, 0, 64, 6, 0) + dst_ip + src_ip
        tcp2 = struct.pack("!HHIIBBHHH", 80, 50000, 2000, 1001, (5 << 4), 18, 65535, 0, 0)
        payload2 = eth + ipv4_rev + tcp2
        ph2 = struct.pack("<IIII", 1600000000, 50000, len(payload2), len(payload2))

        return gh + ph1 + payload1 + ph2 + payload2

    def test_flow_fsm_and_iat_moments(self):
        raw = self._create_pcap_with_two_packets()
        with tempfile.NamedTemporaryFile("wb", delete=False, suffix=".pcap") as f:
            f.write(raw)
            pcap_path = f.name
        try:
            flows = FlowSummarizer.summarize(pcap_path)
            self.assertEqual(len(flows), 1)
            st = list(flows.values())[0]
            self.assertEqual(st.packet_count, 2)
            self.assertAlmostEqual(st.mean_iat(), 0.05, places=3)
            self.assertEqual(st.tcp_state, TCPState.SYN_RECEIVED)
        finally:
            os.remove(pcap_path)


if __name__ == "__main__":
    unittest.main()
