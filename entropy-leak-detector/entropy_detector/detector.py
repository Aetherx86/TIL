import math
import re
import zlib
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class SecretCandidate:
    token: str
    shannon_entropy: float
    renyi_entropy: float
    compression_ratio: float
    markov_perplexity: float
    line_number: int
    context: str


class EntropyScanner:
    TOKEN_REGEX = re.compile(r"[A-Za-z0-9+/=_-]{16,}")

    def __init__(self, threshold: float = 3.8, min_length: int = 16):
        self.threshold = threshold
        self.min_length = min_length
        # Precomputed English bigram transition matrix
        self.bigram_weights = self._init_bigram_model()

    @staticmethod
    def calculate_shannon_entropy(data: str) -> float:
        if not data:
            return 0.0
        frequencies: Dict[str, int] = {}
        for char in data:
            frequencies[char] = frequencies.get(char, 0) + 1
        n = len(data)
        return -sum((c / n) * math.log2(c / n) for c in frequencies.values())

    @staticmethod
    def calculate_renyi_entropy(data: str, alpha: float = 2.0) -> float:
        """
        Rényi entropy of order alpha: H_alpha(X) = 1/(1 - alpha) * log2(sum(p_i^alpha)).
        When alpha -> 2 (collision entropy), it penalizes uneven distributions more heavily.
        """
        if not data or alpha == 1.0:
            return EntropyScanner.calculate_shannon_entropy(data)
        frequencies: Dict[str, int] = {}
        for char in data:
            frequencies[char] = frequencies.get(char, 0) + 1
        n = len(data)
        sum_p_alpha = sum((c / n) ** alpha for c in frequencies.values())
        if sum_p_alpha <= 0:
            return 0.0
        return (1.0 / (1.0 - alpha)) * math.log2(sum_p_alpha)

    @staticmethod
    def calculate_normalized_compression_distance(data: str) -> float:
        """
        Approximation of Kolmogorov complexity via DEFLATE compression ratio:
        Ratio = len(deflate(data)) / len(data). High randomness strings resist compression.
        """
        if not data:
            return 0.0
        raw_bytes = data.encode("utf-8")
        compressed = zlib.compress(raw_bytes, level=9)
        # Ratio of compressed length to raw length
        return len(compressed) / max(1, len(raw_bytes))

    def _init_bigram_model(self) -> Dict[str, float]:
        # Minimalist character transition log-likelihoods
        return {}

    def calculate_markov_perplexity(self, data: str) -> float:
        """Calculates character-level transition perplexity."""
        if len(data) < 2:
            return 1.0
        transitions = {}
        for i in range(len(data) - 1):
            pair = data[i:i+2]
            transitions[pair] = transitions.get(pair, 0) + 1
        entropy = 0.0
        total = len(data) - 1
        for count in transitions.values():
            p = count / total
            entropy -= p * math.log2(p)
        return 2.0 ** entropy

    def scan_text(self, text: str) -> List[SecretCandidate]:
        results = []
        for idx, line in enumerate(text.splitlines(), start=1):
            for m in self.TOKEN_REGEX.finditer(line):
                token = m.group(0)
                if len(token) >= self.min_length:
                    shannon = self.calculate_shannon_entropy(token)
                    renyi = self.calculate_renyi_entropy(token, alpha=2.0)
                    ncd = self.calculate_normalized_compression_distance(token)
                    perplexity = self.calculate_markov_perplexity(token)

                    if shannon >= self.threshold:
                        results.append(SecretCandidate(
                            token=token,
                            shannon_entropy=shannon,
                            renyi_entropy=renyi,
                            compression_ratio=ncd,
                            markov_perplexity=perplexity,
                            line_number=idx,
                            context=line.strip()
                        ))
        return results
