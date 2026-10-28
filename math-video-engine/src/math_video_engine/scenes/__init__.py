"""Registry and catalog of all recreated mathematical video scenes."""

from __future__ import annotations
from typing import Dict, Type, List, Any

from math_video_engine.scenes.base import Scene
from math_video_engine.scenes.linear_algebra import (
    VectorLinearCombinationScene,
    MatrixTransformationScene,
    DeterminantAreaScene,
    EigenvectorTransformationScene,
)
from math_video_engine.scenes.calculus import (
    DerivativeTangentScene,
    RiemannIntegralScene,
    TaylorSeriesScene,
)
from math_video_engine.scenes.fourier import (
    FourierEpicyclesScene,
    FourierWaveDecompositionScene,
)
from math_video_engine.scenes.neural_networks import (
    NeuralNetworkArchitectureScene,
    GradientDescentOptimizationScene,
)
from math_video_engine.scenes.physics_pi import (
    PiCollidingBlocksScene,
    BaselProblemScene,
)
from math_video_engine.scenes.goldbach import (
    StrongGoldbachConjectureScene,
    WeakGoldbachConjectureScene,
)
from math_video_engine.scenes.veritasium import (
    CollatzConjectureScene,
    LogisticMapChaosScene,
    HundredPrisonersRiddleScene,
    OptimalStoppingScene,
    DoubleSlitInterferenceScene,
)

SCENE_REGISTRY: Dict[str, Type[Scene]] = {
    # Linear Algebra
    "VectorLinearCombinationScene": VectorLinearCombinationScene,
    "MatrixTransformationScene": MatrixTransformationScene,
    "DeterminantAreaScene": DeterminantAreaScene,
    "EigenvectorTransformationScene": EigenvectorTransformationScene,
    # Calculus
    "DerivativeTangentScene": DerivativeTangentScene,
    "RiemannIntegralScene": RiemannIntegralScene,
    "TaylorSeriesScene": TaylorSeriesScene,
    # Fourier Analysis
    "FourierEpicyclesScene": FourierEpicyclesScene,
    "FourierWaveDecompositionScene": FourierWaveDecompositionScene,
    # Neural Networks
    "NeuralNetworkArchitectureScene": NeuralNetworkArchitectureScene,
    "GradientDescentOptimizationScene": GradientDescentOptimizationScene,
    # Physics & Pure Mathematics
    "PiCollidingBlocksScene": PiCollidingBlocksScene,
    "BaselProblemScene": BaselProblemScene,
    # Number Theory (Goldbach Conjectures)
    "StrongGoldbachConjectureScene": StrongGoldbachConjectureScene,
    "WeakGoldbachConjectureScene": WeakGoldbachConjectureScene,
    # Veritasium Paradoxes & Phenomena
    "CollatzConjectureScene": CollatzConjectureScene,
    "LogisticMapChaosScene": LogisticMapChaosScene,
    "HundredPrisonersRiddleScene": HundredPrisonersRiddleScene,
    "OptimalStoppingScene": OptimalStoppingScene,
    "DoubleSlitInterferenceScene": DoubleSlitInterferenceScene,
}

SCENE_METADATA: Dict[str, Dict[str, Any]] = {
    "VectorLinearCombinationScene": {
        "category": "Linear Algebra",
        "description": "Basis vectors, scalar multiples, and parallelogram vector addition",
    },
    "MatrixTransformationScene": {
        "category": "Linear Algebra",
        "description": "2D linear transformation warping the coordinate grid while preserving linearity",
    },
    "DeterminantAreaScene": {
        "category": "Linear Algebra",
        "description": "Geometric meaning of determinant as signed area scaling factor",
    },
    "EigenvectorTransformationScene": {
        "category": "Linear Algebra",
        "description": "Eigenvectors maintaining invariant directional spans under linear maps",
    },
    "DerivativeTangentScene": {
        "category": "Calculus",
        "description": "Secant slope line converging to instantaneous tangent line as delta x approaches zero",
    },
    "RiemannIntegralScene": {
        "category": "Calculus",
        "description": "Convergence of stepped rectangular Riemann partitions to exact definite integral",
    },
    "TaylorSeriesScene": {
        "category": "Calculus",
        "description": "Successive polynomial approximations converging to sin(x)",
    },
    "FourierEpicyclesScene": {
        "category": "Fourier Analysis",
        "description": "Rotating tip-to-tail complex phase vectors tracing periodic trajectories",
    },
    "FourierWaveDecompositionScene": {
        "category": "Fourier Analysis",
        "description": "Decomposition of a square wave into its fundamental and odd harmonic series",
    },
    "NeuralNetworkArchitectureScene": {
        "category": "Neural Networks",
        "description": "Multi-layer feedforward neural network structure with signal activation flow",
    },
    "GradientDescentOptimizationScene": {
        "category": "Neural Networks",
        "description": "2D loss landscape contour optimization trajectory down gradient slope",
    },
    "PiCollidingBlocksScene": {
        "category": "Physics & Geometry",
        "description": "Galperin billiard block collision method calculating digits of Pi",
    },
    "BaselProblemScene": {
        "category": "Pure Mathematics",
        "description": "Euler solution to sum of inverse squares connecting to pi squared over six",
    },
    "StrongGoldbachConjectureScene": {
        "category": "Number Theory",
        "description": "Even integers as sums of two primes, Goldbach pairs, and Goldbach comet asymptotic growth",
    },
    "WeakGoldbachConjectureScene": {
        "category": "Number Theory",
        "description": "Odd integers as ternary sums of three primes and Helfgott 2013 unconditional proof",
    },
    "CollatzConjectureScene": {
        "category": "Veritasium Paradoxes",
        "description": "Veritasium 3x+1 problem hailstone sequences collapsing into the 4-2-1 loop",
    },
    "LogisticMapChaosScene": {
        "category": "Veritasium Paradoxes",
        "description": "Veritasium equation of chaos with period doubling cascade and Feigenbaum constant",
    },
    "HundredPrisonersRiddleScene": {
        "category": "Veritasium Paradoxes",
        "description": "Veritasium 100 prisoners permutation cycle loop strategy beating impossible odds",
    },
    "OptimalStoppingScene": {
        "category": "Veritasium Paradoxes",
        "description": "Veritasium 37% rule secretary problem balancing exploration vs selection",
    },
    "DoubleSlitInterferenceScene": {
        "category": "Veritasium Paradoxes",
        "description": "Veritasium wave-particle quantum interference pattern from dual coherent slits",
    },
}


def get_scene_class(name: str) -> Type[Scene]:
    """Retrieve scene class by case-insensitive name."""
    name_clean = name.strip().lower()
    for registered_name, cls in SCENE_REGISTRY.items():
        if registered_name.lower() == name_clean:
            return cls
    raise KeyError(f"Scene '{name}' not found. Available scenes: {list(SCENE_REGISTRY.keys())}")


def list_available_scenes() -> List[Dict[str, Any]]:
    """Return catalog of all available scenes with metadata."""
    catalog = []
    for name, cls in SCENE_REGISTRY.items():
        meta = SCENE_METADATA.get(name, {})
        catalog.append({
            "name": name,
            "category": meta.get("category", "General"),
            "description": meta.get("description", ""),
        })
    return catalog


__all__ = [
    "Scene",
    "SCENE_REGISTRY",
    "SCENE_METADATA",
    "get_scene_class",
    "list_available_scenes",
    "VectorLinearCombinationScene",
    "MatrixTransformationScene",
    "DeterminantAreaScene",
    "EigenvectorTransformationScene",
    "DerivativeTangentScene",
    "RiemannIntegralScene",
    "TaylorSeriesScene",
    "FourierEpicyclesScene",
    "FourierWaveDecompositionScene",
    "NeuralNetworkArchitectureScene",
    "GradientDescentOptimizationScene",
    "PiCollidingBlocksScene",
    "BaselProblemScene",
    "StrongGoldbachConjectureScene",
    "WeakGoldbachConjectureScene",
    "CollatzConjectureScene",
    "LogisticMapChaosScene",
    "HundredPrisonersRiddleScene",
    "OptimalStoppingScene",
    "DoubleSlitInterferenceScene",
]
