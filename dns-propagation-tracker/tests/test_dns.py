import struct
import unittest
from dns_tracker.tracker import RFC1035Dissector

class TestDNSTracker(unittest.TestCase):
    def test_dns_pointer_decompression(self):
        # Header (12 bytes)
        hdr = struct.pack("!HHHHHH", 0x1234, 0x8180, 1, 1, 0, 0)
        # Question: example.com (offset 12)
        qname = b"\x07example\x03com\x00"
        q_tail = struct.pack("!HH", 1, 1)

        # Answer with pointer to example.com (0xC00C -> offset 12)
        ans_name = bytes([0xC0, 12])
        ans_rr = ans_name + struct.pack("!HHIH", 1, 1, 300, 4) + bytes([93, 184, 216, 34])

        packet = hdr + qname + q_tail + ans_rr
        resp = RFC1035Dissector.parse_packet(packet)
        self.assertEqual(resp.rcode, 0)
        self.assertEqual(len(resp.answers), 1)
        self.assertEqual(resp.answers[0].name, "example.com")
        self.assertEqual(resp.answers[0].data, "93.184.216.34")
        self.assertEqual(resp.answers[0].ttl, 300)

if __name__ == "__main__":
    unittest.main()
