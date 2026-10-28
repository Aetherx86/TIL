import math
import random
from typing import List, Tuple

def cholesky(A: List[List[float]]) -> List[List[float]]:
    """Cholesky-Banachiewicz decomposition of a symmetric positive-definite matrix A = L * L^T."""
    n = len(A)
    L = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s = sum(L[i][k] * L[j][k] for k in range(j))
            if i == j:
                val = A[i][i] - s
                if val <= 0:
                    raise ValueError(f"Matrix is not positive definite: principal minor non-positive at index {i}.")
                L[i][j] = math.sqrt(val)
            else:
                L[i][j] = (A[i][j] - s) / L[j][j]
    return L

def std_normal_cdf(z: float) -> float:
    """Standard normal CDF: Phi(z) = 0.5 * (1 + erf(z / sqrt(2)))."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))

class GaussianCopula:
    """
    Gaussian Copula for modeling correlated multivariate dependency across risk stages.
    Transforms independent Gaussian draws via Cholesky factor L, then maps to uniform
    marginals through the standard normal CDF.
    """
    def __init__(self, corr_matrix: List[List[float]]):
        self.corr_matrix = corr_matrix
        self.dim = len(corr_matrix)
        self.cholesky_l = cholesky(self.corr_matrix)

    @classmethod
    def exchangeable(cls, dim: int, rho: float) -> "GaussianCopula":
        if not (-1.0 / (dim - 1) < rho < 1.0):
            raise ValueError(f"Correlation rho={rho} must satisfy -1/(dim-1) < rho < 1 for positive definiteness.")
        corr = [[rho if i != j else 1.0 for j in range(dim)] for i in range(dim)]
        return cls(corr)

    def sample_uniforms(self, n_samples: int, rng: random.Random) -> List[List[float]]:
        """Generates n_samples realizations of dim-dimensional correlated uniform random variables."""
        results: List[List[float]] = []
        for _ in range(n_samples):
            # Draw independent standard normals
            z_indep = [rng.gauss(0.0, 1.0) for _ in range(self.dim)]
            # Multiply L * z_indep
            z_corr = [
                sum(self.cholesky_l[i][k] * z_indep[k] for k in range(i + 1))
                for i in range(self.dim)
            ]
            # Map through normal CDF to uniform marginals
            u = [min(max(std_normal_cdf(zc), 1e-12), 1.0 - 1e-12) for zc in z_corr]
            results.append(u)
        return results
