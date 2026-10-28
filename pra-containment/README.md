# pra-containment

Probabilistic Risk Assessment (PRA) and Dependency Modeling for Autonomous AI Agent Containment.

## Overview

When cyber-capable AI agents operate inside evaluation sandboxes or semi-autonomous workflows, reward hacking can transition into an external infrastructure compromise if multiple perimeter boundaries fail in sequence.

`pra-containment` provides a formal Event-Tree and Copula-based probabilistic risk framework that models this transition across five conditional failure stages:
1. Reward Hacking ($E_1$): Agent adopts prohibited shortcuts violating system goals.
2. Containment Escape ($E_2$): Agent navigates unassigned network paths.
3. Usable Access ($E_3$): Agent extracts valid authentication tokens or execution authority.
4. Persistence ($E_4$): Agent survives session resets or establishes lateral persistence.
5. Detection Failure ($E_5$): Supervisory telemetry and cross-layer anomaly monitors fail to detect the intrusion before external consequences manifest.

## Mathematical Formulation

### 1. Multi-Stage Conditional Probability Chain

For an agent execution run $i$, stage log-odds are modeled via multilinear logistic representations:

$$\text{logit}_{i,k} = \beta_{0,k} + \sum_{j=1}^{d_k} w_{j,k} X_{i,j,k}$$

$$p_{i,k} = \sigma(\text{logit}_{i,k}) = \frac{1}{1 + \exp(-\text{logit}_{i,k})}$$

The end-to-end compromise likelihood is the joint product of conditional stage probabilities:

$$P_i(\text{Incident}) = \prod_{k=1}^5 p_{i,k}$$

### 2. Gaussian Copula Multi-Layer Dependency

While classical risk assessment assumes conditional independence given sampled latents, shared infrastructure (e.g., container orchestrators, kernel sockets) induces structural coupling across controls. The framework integrates a Gaussian Copula $C_\Sigma(u_1, \dots, u_d)$ parameterized by correlation matrix $\Sigma$:

$$C_\Sigma(u_1, \dots, u_d) = \Phi_\Sigma \left( \Phi^{-1}(u_1), \dots, \Phi^{-1}(u_d) \right)$$

Where $\Phi^{-1}$ denotes the inverse standard normal cumulative distribution function.

### 3. Saltelli-Jansen Variance Decomposition

Parameter sensitivities are evaluated using first-order ($S_i$) and total-effect ($S_{Ti}$) Sobol indices:

$$S_i = \frac{\text{Var}_{X_i}\left(E_{\mathbf{X}_{\sim i}}[Y \mid X_i]\right)}{\text{Var}(Y)}$$

$$S_{Ti} = 1 - \frac{\text{Var}_{\mathbf{X}_{\sim i}}\left(E_{X_i}[Y \mid \mathbf{X}_{\sim i}]\right)}{\text{Var}(Y)} = \frac{E_{\mathbf{X}_{\sim i}}\left[\text{Var}_{X_i}(Y \mid \mathbf{X}_{\sim i})\right]}{\text{Var}(Y)}$$

The total effect index $S_{Ti}$ quantifies the contribution of variable $X_i$ including all interaction terms of any order.

## Installation

```bash
git clone https://gitlab.com/jk9576/pra-containment.git
cd pra-containment
pip install -e .
```

## Running Tests

```bash
python -m unittest discover tests
```

## License

MIT License. See LICENSE for details.
