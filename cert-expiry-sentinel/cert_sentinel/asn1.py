import datetime
from typing import Any, List, Optional, Tuple

class ASN1Tag:
    BOOLEAN = 0x01
    INTEGER = 0x02
    BIT_STRING = 0x03
    OCTET_STRING = 0x04
    NULL = 0x05
    OBJECT_IDENTIFIER = 0x06
    UTF8_STRING = 0x0C
    PRINTABLE_STRING = 0x13
    TELETEX_STRING = 0x14
    IA5_STRING = 0x16
    UTC_TIME = 0x17
    GENERALIZED_TIME = 0x18
    SEQUENCE = 0x30
    SET = 0x31
    CONTEXT_0 = 0xA0
    CONTEXT_3 = 0xA3

KNOWN_OIDS = {
    "2.5.4.3": "commonName",
    "2.5.4.6": "countryName",
    "2.5.4.7": "localityName",
    "2.5.4.8": "stateOrProvinceName",
    "2.5.4.10": "organizationName",
    "2.5.4.11": "organizationalUnitName",
    "2.5.29.17": "subjectAltName",
    "2.5.29.19": "basicConstraints",
    "2.5.29.15": "keyUsage",
    "1.2.840.113549.1.1.1": "rsaEncryption",
    "1.2.840.10045.2.1": "ecPublicKey",
}

class ASN1Parser:
    """
    Zero-dependency pure Python ASN.1 DER parser.
    Decodes X.509 TLV (Type-Length-Value) hierarchical structures,
    OIDs, GeneralizedTime/UTCTime, and Subject Alternative Names (SANs).
    """

    @staticmethod
    def parse_length(data: bytes, offset: int) -> Tuple[int, int]:
        initial = data[offset]
        if initial < 0x80:
            return initial, offset + 1
        num_octets = initial & 0x7F
        if num_octets == 0 or offset + 1 + num_octets > len(data):
            raise ValueError("Corrupt or unsupported indefinite ASN.1 length")
        length = int.from_bytes(data[offset + 1:offset + 1 + num_octets], "big")
        return length, offset + 1 + num_octets

    @classmethod
    def parse_tlv(cls, data: bytes, offset: int = 0) -> Tuple[int, bytes, int]:
        if offset >= len(data):
            raise IndexError("Offset out of bounds in ASN.1 DER stream")
        tag = data[offset]
        length, val_start = cls.parse_length(data, offset + 1)
        val_end = val_start + length
        if val_end > len(data):
            raise ValueError(f"TLV payload overflow: length {length} exceeds buffer size {len(data) - val_start}")
        return tag, data[val_start:val_end], val_end

    @staticmethod
    def decode_oid(raw: bytes) -> str:
        """Decodes raw DER bytes of an Object Identifier into dotted notation."""
        if not raw:
            return ""
        first = raw[0]
        nodes = [str(first // 40), str(first % 40)]
        val = 0
        for b in raw[1:]:
            val = (val << 7) | (b & 0x7F)
            if not (b & 0x80):
                nodes.append(str(val))
                val = 0
        return ".".join(nodes)

    @staticmethod
    def decode_time(raw: bytes, tag: int) -> datetime.datetime:
        """Decodes UTCTime (0x17) or GeneralizedTime (0x18) into datetime object."""
        s = raw.decode("ascii", errors="ignore")
        if tag == ASN1Tag.UTC_TIME:
            year = int(s[0:2])
            year += 2000 if year < 50 else 1900
            month = int(s[2:4])
            day = int(s[4:6])
            hour = int(s[6:8])
            minute = int(s[8:10])
            second = int(s[10:12]) if len(s) >= 12 and s[10:12].isdigit() else 0
            return datetime.datetime(year, month, day, hour, minute, second, tzinfo=datetime.timezone.utc)
        elif tag == ASN1Tag.GENERALIZED_TIME:
            year = int(s[0:4])
            month = int(s[4:6])
            day = int(s[6:8])
            hour = int(s[8:10])
            minute = int(s[10:12])
            second = int(s[12:14]) if len(s) >= 14 and s[12:14].isdigit() else 0
            return datetime.datetime(year, month, day, hour, minute, second, tzinfo=datetime.timezone.utc)
        raise ValueError(f"Unsupported ASN.1 time tag: {tag}")

    @classmethod
    def parse_san_extension(cls, raw: bytes) -> List[str]:
        """Parses raw GeneralNames sequence inside Subject Alternative Name (SAN) extension."""
        names: List[str] = []
        try:
            cur = raw
            # If wrapped in OCTET STRING or SEQUENCE, unwrap
            while cur and (cur[0] == ASN1Tag.OCTET_STRING or cur[0] == ASN1Tag.SEQUENCE):
                _, cur, _ = cls.parse_tlv(cur, 0)
            offset = 0
            while offset < len(cur):
                tag, val, offset = cls.parse_tlv(cur, offset)
                tag_no = tag & 0x1F
                if tag_no == 2:  # dNSName
                    names.append(val.decode("ascii", errors="ignore"))
                elif tag_no == 7:  # iPAddress
                    if len(val) == 4:
                        names.append(".".join(str(b) for b in val))
        except Exception:
            pass
        return names
