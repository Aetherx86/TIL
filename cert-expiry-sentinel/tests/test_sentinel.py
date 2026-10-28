import datetime
import unittest
from cert_sentinel.asn1 import ASN1Parser, ASN1Tag
from cert_sentinel.checker import CertificateChecker, CertInfo

class TestCertSentinel(unittest.TestCase):
    def test_asn1_length_decoding(self):
        # Short form
        self.assertEqual(ASN1Parser.parse_length(b"\x05data", 0), (5, 1))
        # Long form (2 octets)
        self.assertEqual(ASN1Parser.parse_length(b"\x82\x01\x00rest", 0), (256, 3))

    def test_asn1_oid_decoding(self):
        # OID 2.5.4.3 (commonName): 2*40 + 5 = 85 (0x55), 4 (0x04), 3 (0x03)
        raw_oid = bytes([0x55, 0x04, 0x03])
        self.assertEqual(ASN1Parser.decode_oid(raw_oid), "2.5.4.3")

    def test_asn1_time_decoding(self):
        utc_raw = b"261029120000Z"
        dt = ASN1Parser.decode_time(utc_raw, ASN1Tag.UTC_TIME)
        self.assertEqual(dt.year, 2026)
        self.assertEqual(dt.month, 10)
        self.assertEqual(dt.day, 29)
        self.assertEqual(dt.hour, 12)

    def test_der_san_parser(self):
        # Construct synthetic Subject Alternative Name sequence with DNS entries
        # dNSName is context tag 2: 0x82, len 11, "example.com"
        dns1 = bytes([0x82, 11]) + b"example.com"
        dns2 = bytes([0x82, 15]) + b"api.example.com"
        san_seq = bytes([0x30, len(dns1) + len(dns2)]) + dns1 + dns2
        # Wrap in Octet String
        octet_str = bytes([0x04, len(san_seq)]) + san_seq
        sans = ASN1Parser.parse_san_extension(octet_str)
        self.assertEqual(sans, ["example.com", "api.example.com"])

if __name__ == "__main__":
    unittest.main()
