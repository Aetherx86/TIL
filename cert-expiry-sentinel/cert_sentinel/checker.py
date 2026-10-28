import datetime
import socket
import ssl
from dataclasses import dataclass, field
from typing import List, Optional
from .asn1 import ASN1Parser, ASN1Tag, KNOWN_OIDS

@dataclass
class CertInfo:
    hostname: str
    port: int
    common_name: str
    organization: str
    san_list: List[str]
    not_before: datetime.datetime
    not_after: datetime.datetime
    days_remaining: int
    is_expired: bool
    clock_skew_warning: bool = False
    error: Optional[str] = None

class CertificateChecker:
    """
    Audits X.509 TLS/SSL certificates with ASN.1 DER stream inspection,
    validating temporal windows, SAN coverage, and expiration thresholds.
    """
    def __init__(self, timeout: float = 5.0, skew_tolerance_hours: float = 24.0):
        self.timeout = timeout
        self.skew_tolerance_hours = skew_tolerance_hours
        self.context = ssl.create_default_context()

    def parse_der_cert(self, der_bytes: bytes, hostname: str = "local", port: int = 0) -> CertInfo:
        try:
            # Certificate is SEQUENCE { tbsCertificate TBSCertificate, signatureAlgorithm ..., signatureValue ... }
            tag, cert_body, _ = ASN1Parser.parse_tlv(der_bytes, 0)
            tag, tbs_body, _ = ASN1Parser.parse_tlv(cert_body, 0)

            offset = 0
            # [0] version?
            tag, val, offset = ASN1Parser.parse_tlv(tbs_body, offset)
            if (tag & 0xC0) == 0x80:  # Context-specific tag 0
                tag, val, offset = ASN1Parser.parse_tlv(tbs_body, offset)  # SerialNumber

            # signature AlgId
            tag, val, offset = ASN1Parser.parse_tlv(tbs_body, offset)

            # issuer Name (SEQUENCE of SETs)
            tag, issuer_raw, offset = ASN1Parser.parse_tlv(tbs_body, offset)

            # validity (SEQUENCE of two times: notBefore, notAfter)
            tag, validity_raw, offset = ASN1Parser.parse_tlv(tbs_body, offset)
            v_offset = 0
            tag_nb, val_nb, v_offset = ASN1Parser.parse_tlv(validity_raw, v_offset)
            not_before = ASN1Parser.decode_time(val_nb, tag_nb)
            tag_na, val_na, v_offset = ASN1Parser.parse_tlv(validity_raw, v_offset)
            not_after = ASN1Parser.decode_time(val_na, tag_na)

            # subject Name
            tag, subject_raw, offset = ASN1Parser.parse_tlv(tbs_body, offset)
            cn = ""
            org = ""
            s_offset = 0
            while s_offset < len(subject_raw):
                tag_set, set_raw, s_offset = ASN1Parser.parse_tlv(subject_raw, s_offset)
                _, atv_raw, _ = ASN1Parser.parse_tlv(set_raw, 0)
                _, oid_raw, atv_off = ASN1Parser.parse_tlv(atv_raw, 0)
                oid_str = ASN1Parser.decode_oid(oid_raw)
                _, val_str_raw, _ = ASN1Parser.parse_tlv(atv_raw, atv_off)
                val_text = val_str_raw.decode("utf-8", errors="ignore")
                if KNOWN_OIDS.get(oid_str) == "commonName":
                    cn = val_text
                elif KNOWN_OIDS.get(oid_str) == "organizationName":
                    org = val_text

            # Subject Public Key Info
            tag, spki_raw, offset = ASN1Parser.parse_tlv(tbs_body, offset)

            # Extensions (optional context tag [3])
            san_list: List[str] = []
            while offset < len(tbs_body):
                tag_ext, ext_raw, offset = ASN1Parser.parse_tlv(tbs_body, offset)
                if (tag_ext & 0x1F) == 3:  # [3] Extensions
                    _, ext_seq, _ = ASN1Parser.parse_tlv(ext_raw, 0)
                    e_off = 0
                    while e_off < len(ext_seq):
                        _, single_ext, e_off = ASN1Parser.parse_tlv(ext_seq, e_off)
                        _, oid_ext_raw, se_off = ASN1Parser.parse_tlv(single_ext, 0)
                        ext_oid = ASN1Parser.decode_oid(oid_ext_raw)
                        # Check if critical boolean follows
                        next_tag, next_val, se_off2 = ASN1Parser.parse_tlv(single_ext, se_off)
                        if next_tag == ASN1Tag.BOOLEAN:
                            _, next_val, se_off2 = ASN1Parser.parse_tlv(single_ext, se_off2)
                        if ext_oid == "2.5.29.17":  # subjectAltName
                            san_list = ASN1Parser.parse_san_extension(next_val)

            now = datetime.datetime.now(datetime.timezone.utc)
            days_rem = (not_after - now).days
            is_expired = now > not_after
            skew_warn = now < (not_before - datetime.timedelta(hours=self.skew_tolerance_hours))

            return CertInfo(
                hostname=hostname,
                port=port,
                common_name=cn,
                organization=org,
                san_list=san_list,
                not_before=not_before,
                not_after=not_after,
                days_remaining=days_rem,
                is_expired=is_expired,
                clock_skew_warning=skew_warn,
            )
        except Exception as e:
            return CertInfo(
                hostname=hostname,
                port=port,
                common_name="",
                organization="",
                san_list=[],
                not_before=datetime.datetime.min.replace(tzinfo=datetime.timezone.utc),
                not_after=datetime.datetime.min.replace(tzinfo=datetime.timezone.utc),
                days_remaining=-9999,
                is_expired=True,
                error=f"ASN.1 parse error: {str(e)}",
            )

    def check_host(self, hostname: str, port: int = 443) -> CertInfo:
        try:
            with socket.create_connection((hostname, port), timeout=self.timeout) as sock:
                with self.context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    der_cert = ssock.getpeercert(binary_form=True)
                    if not der_cert:
                        raise ValueError("Peer did not provide a binary DER certificate")
                    return self.parse_der_cert(der_cert, hostname=hostname, port=port)
        except Exception as e:
            return CertInfo(
                hostname=hostname,
                port=port,
                common_name="",
                organization="",
                san_list=[],
                not_before=datetime.datetime.min.replace(tzinfo=datetime.timezone.utc),
                not_after=datetime.datetime.min.replace(tzinfo=datetime.timezone.utc),
                days_remaining=-9999,
                is_expired=True,
                error=str(e),
            )
