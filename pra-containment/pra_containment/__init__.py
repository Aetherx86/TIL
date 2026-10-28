"""
pra-containment: Probabilistic Risk Assessment for AI Agent Containment.
"""

from .model import (
    ControlConfiguration,
    RiskModel,
    SimulationResult,
    Stage,
)
from .sensitivity import compute_quantiles_table, sobol_sensitivity

__version__ = "0.1.0"
__all__ = [
    "Stage",
    "ControlConfiguration",
    "RiskModel",
    "SimulationResult",
    "compute_quantiles_table",
    "sobol_sensitivity",
]
