import math
import re
from enum import Enum
from typing import Dict, List, Optional, Set

class SemanticType(Enum):
    BOOLEAN = "BOOLEAN"
    INTEGER = "INTEGER"
    PORT = "PORT"
    FLOAT = "FLOAT"
    URL = "URL"
    IPV4 = "IPV4"
    EMAIL = "EMAIL"
    HIGH_ENTROPY_TOKEN = "HIGH_ENTROPY_TOKEN"
    JSON = "JSON"
    STRING = "STRING"

class TypeLattice:
    """
    Formal type inference lattice for environment configuration variables.
    Determines fine-grained semantic signatures and cryptographic entropy metrics.
    """
    BOOL_REGEX = re.compile(r"^(true|false|1|0|yes|no|on|off)$", re.IGNORECASE)
    INT_REGEX = re.compile(r"^[+-]?[0-9]+$")
    FLOAT_REGEX = re.compile(r"^[+-]?[0-9]+\.[0-9]+$")
    URL_REGEX = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*://[^\s/$.?#].[^\s]*$")
    IPV4_REGEX = re.compile(r"^([0-9]{1,3}\.){3}[0-9]{1,3}(/[0-9]{1,2})?$")
    EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    @staticmethod
    def shannon_entropy(s: str) -> float:
        if not s:
            return 0.0
        counts: Dict[str, int] = {}
        for c in s:
            counts[c] = counts.get(c, 0) + 1
        n = len(s)
        return -sum((cnt / n) * math.log2(cnt / n) for cnt in counts.values())

    @classmethod
    def infer(cls, val: str) -> SemanticType:
        v = val.strip()
        if not v:
            return SemanticType.STRING
        if cls.BOOL_REGEX.match(v):
            return SemanticType.BOOLEAN
        if cls.INT_REGEX.match(v):
            num = int(v)
            if 1 <= num <= 65535:
                return SemanticType.PORT
            return SemanticType.INTEGER
        if cls.FLOAT_REGEX.match(v):
            return SemanticType.FLOAT
        if cls.URL_REGEX.match(v):
            return SemanticType.URL
        if cls.IPV4_REGEX.match(v):
            return SemanticType.IPV4
        if cls.EMAIL_REGEX.match(v):
            return SemanticType.EMAIL
        if len(v) >= 16 and cls.shannon_entropy(v) >= 3.7:
            return SemanticType.HIGH_ENTROPY_TOKEN
        if (v.startswith("{") and v.endswith("}")) or (v.startswith("[") and v.endswith("]")):
            return SemanticType.JSON
        return SemanticType.STRING
