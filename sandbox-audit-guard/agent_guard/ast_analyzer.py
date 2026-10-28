import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ObfuscationFinding:
    pattern_type: str
    token: str
    description: str


class ShellObfuscationAnalyzer:
    """
    Syntactic analyzer identifying shell evasion and command obfuscation patterns:
    - Base64 payload decoding piped into shells
    - Hexadecimal / octal byte encodings ($'\x41', \0101)
    - Variable concatenation / IFS splitting tricks (${IFS}, $u$r$l)
    - Subshell backtick and command substitution nesting
    """

    PATTERNS = [
        ("BASE64_EXEC", re.compile(r"base64\s+(-d|--decode)[^|;&]*\|\s*(sh|bash|zsh|python|perl)", re.IGNORECASE),
         "Base64 encoded string piped directly into command interpreter"),
        ("HEX_OCTAL_ESCAPE", re.compile(r"(\$'\[0-9xX][0-9a-fA-F]+'|\[0-7]{3})"),
         "Hexadecimal or octal escape sequence used to obfuscate binary execution"),
        ("IFS_OBFUSCATION", re.compile(r"\$\{IFS\}|\$IFS"),
         "Internal Field Separator manipulation used to bypass whitespace keyword filters"),
        ("CONCAT_VARIABLE_TRICK", re.compile(r"(\$[a-zA-Z0-9_]+){3,}"),
         "Chained environment variable expansion used to reconstruct blocked command names"),
        ("NESTED_CMD_SUBSTITUTION", re.compile(r"`[^`]*`|\$\([^\)]*\$\([^\)]*\)[^\)]*\)"),
         "Deeply nested command substitution subshells concealing execution payloads"),
    ]

    @classmethod
    def analyze_command(cls, command_str: str) -> List[ObfuscationFinding]:
        findings = []
        for ptype, regex, desc in cls.PATTERNS:
            for m in regex.finditer(command_str):
                findings.append(ObfuscationFinding(
                    pattern_type=ptype,
                    token=m.group(0),
                    description=desc,
                ))
        return findings
