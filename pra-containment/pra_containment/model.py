import math
import random
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

@dataclass
class Stage:
    name: str
    intercept: float
    weights: Dict[str, float]
    description: str = ""

    def evaluate_logit(self, row: Dict[str, float]) -> float:
        val = self.intercept
        for var_name, weight in self.weights.items():
            if var_name not in row:
                raise KeyError(f"Variable '{var_name}' required by stage '{self.name}' not found.")
            val += weight * row[var_name]
        return val

    def evaluate_prob(self, row: Dict[str, float]) -> float:
        logit = self.evaluate_logit(row)
        if logit >= 0:
            return 1.0 / (1.0 + math.exp(-logit))
        else:
            exp_l = math.exp(logit)
            return exp_l / (1.0 + exp_l)

@dataclass
class ControlConfiguration:
    name: str
    strengths: Dict[str, Tuple[float, float]]
    description: str = ""

@dataclass
class SimulationResult:
    configuration_name: str
    n_runs: int
    n_incidents: int
    incident_rate: float
    ci_95: Tuple[float, float]
    mean_exact_prob: float
    exact_probs: List[float]
    bernoulli_incidents: List[bool]
    sampled_inputs: Dict[str, List[float]]
    stage_probs: Dict[str, List[float]]

class RiskModel:
    """
    Probabilistic Risk Assessment (PRA) event-tree simulation engine.
    Supports Common-Cause Failure (CCF) modeling, coefficient perturbation,
    and exact likelihood evaluation without third-party dependencies.
    """
    def __init__(
        self,
        stages: Optional[List[Stage]] = None,
        ccf_beta: float = 0.0,
    ):
        self.stages = stages if stages is not None else self.default_stages()
        self.ccf_beta = float(ccf_beta)

    @classmethod
    def default_stages(cls) -> List[Stage]:
        return [
            Stage(
                name="reward_hacking",
                intercept=-3.0,
                weights={"capability": 1.7, "reward_pressure": 1.3, "task_difficulty": 1.1},
                description="Agent exploits objective shortcut over intended policy",
            ),
            Stage(
                name="containment_escape",
                intercept=-2.2,
                weights={"capability": 2.1, "isolation_weakness": 1.4},
                description="Agent establishes communication outside assigned boundary",
            ),
            Stage(
                name="usable_access",
                intercept=-2.5,
                weights={"capability": 1.7, "credential_weakness": 1.8},
                description="Agent harvests credentials or gains executable privilege",
            ),
            Stage(
                name="persistence",
                intercept=-2.4,
                weights={"capability": 1.4, "monitoring_weakness": 1.1},
                description="Agent maintains execution context or establishes foothold",
            ),
            Stage(
                name="detection_failure",
                intercept=-1.4,
                weights={"monitoring_weakness": 2.3, "authorization_weakness": 1.2},
                description="Evasion of cross-layer telemetry and human oversight",
            ),
        ]

    def sample_inputs(
        self,
        n_runs: int,
        control_config: ControlConfiguration,
        rng: random.Random,
        cap_params: Tuple[float, float] = (5.0, 3.0),
        rew_params: Tuple[float, float] = (4.0, 3.0),
        diff_params: Tuple[float, float] = (4.0, 3.0),
    ) -> Dict[str, List[float]]:
        inputs: Dict[str, List[float]] = {
            "capability": [rng.betavariate(*cap_params) for _ in range(n_runs)],
            "reward_pressure": [rng.betavariate(*rew_params) for _ in range(n_runs)],
            "task_difficulty": [rng.betavariate(*diff_params) for _ in range(n_runs)],
        }
        for control_name, (a, b) in control_config.strengths.items():
            weakness_name = f"{control_name}_weakness"
            weaknesses = [1.0 - rng.betavariate(a, b) for _ in range(n_runs)]
            if self.ccf_beta > 0.0:
                for idx in range(n_runs):
                    if rng.random() < self.ccf_beta:
                        shock = rng.betavariate(5.0, 1.0)
                        if shock > weaknesses[idx]:
                            weaknesses[idx] = shock
            inputs[weakness_name] = weaknesses
        return inputs

    def simulate(
        self,
        control_config: ControlConfiguration,
        n_runs: int = 10_000,
        seed: Optional[int] = 260903,
    ) -> SimulationResult:
        rng = random.Random(seed)
        inputs = self.sample_inputs(n_runs, control_config, rng)
        stage_probs: Dict[str, List[float]] = {s.name: [] for s in self.stages}
        exact_probs: List[float] = []
        bernoulli_incidents: List[bool] = []

        for i in range(n_runs):
            row = {k: inputs[k][i] for k in inputs}
            chain_success = True
            chain_prob = 1.0
            for stage in self.stages:
                p = stage.evaluate_prob(row)
                stage_probs[stage.name].append(p)
                chain_prob *= p
                if chain_success:
                    if rng.random() >= p:
                        chain_success = False
            exact_probs.append(chain_prob)
            bernoulli_incidents.append(chain_success)

        n_incidents = sum(bernoulli_incidents)
        rate = n_incidents / n_runs
        se = math.sqrt(max(rate * (1.0 - rate) / n_runs, 1e-12))
        ci_95 = (max(0.0, rate - 1.96 * se), min(1.0, rate + 1.96 * se))

        return SimulationResult(
            configuration_name=control_config.name,
            n_runs=n_runs,
            n_incidents=n_incidents,
            incident_rate=rate,
            ci_95=ci_95,
            mean_exact_prob=sum(exact_probs) / n_runs,
            exact_probs=exact_probs,
            bernoulli_incidents=bernoulli_incidents,
            sampled_inputs=inputs,
            stage_probs=stage_probs,
        )

    def perturb(self, factor_range: Tuple[float, float] = (0.75, 1.25), rng: Optional[random.Random] = None) -> "RiskModel":
        if rng is None:
            rng = random.Random()
        perturbed = []
        for stage in self.stages:
            p_intercept = stage.intercept * rng.uniform(*factor_range)
            p_weights = {k: v * rng.uniform(*factor_range) for k, v in stage.weights.items()}
            perturbed.append(Stage(name=stage.name, intercept=p_intercept, weights=p_weights, description=stage.description))
        return RiskModel(stages=perturbed, ccf_beta=self.ccf_beta)
