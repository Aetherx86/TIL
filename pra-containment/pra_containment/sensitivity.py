import math
import random
from typing import Dict, List, Tuple
from pra_containment.model import ControlConfiguration, RiskModel

def pearson_correlation(x: List[float], y: List[float]) -> float:
    n = len(x)
    if n == 0:
        return 0.0
    mx = sum(x) / n
    my = sum(y) / n
    cov = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    vx = sum((xi - mx) ** 2 for xi in x)
    vy = sum((yi - my) ** 2 for yi in y)
    if vx <= 1e-15 or vy <= 1e-15:
        return 0.0
    return cov / math.sqrt(vx * vy)

def compute_correlations(inputs: Dict[str, List[float]], target: List[float]) -> Dict[str, float]:
    return {k: pearson_correlation(v, target) for k, v in inputs.items()}

def compute_quantiles_table(data: List[float], percentiles: List[float] = [5.0, 25.0, 50.0, 75.0, 95.0]) -> Dict[float, float]:
    sorted_d = sorted(data)
    n = len(sorted_d)
    if n == 0:
        return {p: 0.0 for p in percentiles}
    res = {}
    for p in percentiles:
        idx = int(round((p / 100.0) * (n - 1)))
        idx = max(0, min(n - 1, idx))
        res[p] = sorted_d[idx]
    return res

def sobol_sensitivity(
    model: RiskModel,
    control_config: ControlConfiguration,
    n_samples: int = 2_000,
    seed: int = 42,
) -> Dict[str, Dict[str, float]]:
    """
    Variance-based global sensitivity analysis using Saltelli-Jansen Monte Carlo estimator.
    Computes first-order indices S_i and total-effect indices S_Ti without external dependencies.
    """
    rng_a = random.Random(seed)
    rng_b = random.Random(seed + 100_007)

    inputs_a = model.sample_inputs(n_samples, control_config, rng_a)
    inputs_b = model.sample_inputs(n_samples, control_config, rng_b)
    param_names = sorted(list(inputs_a.keys()))

    def eval_chain(inputs: Dict[str, List[float]], idx: int) -> float:
        row = {k: inputs[k][idx] for k in inputs}
        prod = 1.0
        for stage in model.stages:
            prod *= stage.evaluate_prob(row)
        return prod

    ya = [eval_chain(inputs_a, i) for i in range(n_samples)]
    yb = [eval_chain(inputs_b, i) for i in range(n_samples)]

    mean_y = sum(ya + yb) / (2 * n_samples)
    var_y = sum((y - mean_y) ** 2 for y in ya + yb) / (2 * n_samples - 1)
    if var_y <= 1e-14:
        return {p: {"first_order": 0.0, "total_effect": 0.0} for p in param_names}

    results: Dict[str, Dict[str, float]] = {}

    for i, p in enumerate(param_names):
        # Construct A_B(i): matrix A with column p from matrix B
        y_ab_i = []
        for row_idx in range(n_samples):
            row = {k: inputs_a[k][row_idx] for k in param_names}
            row[p] = inputs_b[p][row_idx]
            prod = 1.0
            for stage in model.stages:
                prod *= stage.evaluate_prob(row)
            y_ab_i.append(prod)

        # Saltelli (2010) first-order estimator: S_i = (1/N * sum(y_b * (y_ab_i - y_a))) / Var(Y)
        num_s_i = sum(yb[j] * (y_ab_i[j] - ya[j]) for j in range(n_samples)) / n_samples
        s_i = max(0.0, min(1.0, num_s_i / var_y))

        # Jansen (1999) total-effect estimator: S_Ti = (1 / (2*N) * sum((y_a - y_ab_i)^2)) / Var(Y)
        num_s_ti = sum((ya[j] - y_ab_i[j]) ** 2 for j in range(n_samples)) / (2.0 * n_samples)
        s_ti = max(s_i, min(1.0, num_s_ti / var_y))

        results[p] = {
            "first_order": round(s_i, 5),
            "total_effect": round(s_ti, 5),
        }

    return results
