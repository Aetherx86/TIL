import argparse
import sys
from typing import Dict

from .model import ControlConfiguration, RiskModel
from .sensitivity import pearson_correlation, sobol_sensitivity

def get_standard_configurations() -> Dict[str, ControlConfiguration]:
    return {
        "weak": ControlConfiguration(
            name="Weak Controls",
            strengths={
                "isolation": (2.0, 5.0),
                "credential": (2.0, 5.0),
                "monitoring": (2.0, 5.0),
                "authorization": (2.0, 5.0),
            },
            description="Baseline fragile perimeter; weak controls across all stages.",
        ),
        "network_only": ControlConfiguration(
            name="Network Isolation Only",
            strengths={
                "isolation": (7.0, 2.0),
                "credential": (2.0, 5.0),
                "monitoring": (2.0, 5.0),
                "authorization": (2.0, 5.0),
            },
            description="Strong egress filtering but weak internal credentials and telemetry.",
        ),
        "monitoring_only": ControlConfiguration(
            name="Monitoring Only",
            strengths={
                "isolation": (2.0, 5.0),
                "credential": (2.0, 5.0),
                "monitoring": (7.0, 2.0),
                "authorization": (2.0, 5.0),
            },
            description="Strong observability but permissive egress and long-lived credentials.",
        ),
        "layered": ControlConfiguration(
            name="Layered Controls",
            strengths={
                "isolation": (8.0, 2.0),
                "credential": (8.0, 2.0),
                "monitoring": (8.0, 2.0),
                "authorization": (8.0, 2.0),
            },
            description="Defense-in-depth across isolation, credentials, monitoring, and authorization.",
        ),
    }

def cmd_compare(args):
    configs = get_standard_configurations()
    model = RiskModel(ccf_beta=args.ccf)
    print(f"=== Multi-Stage PRA Simulation ({args.runs:,} runs per configuration) ===")
    if args.ccf > 0.0:
        print(f"[!] Common-Cause Failure (CCF) Beta: {args.ccf:.2f}")

    results = []
    weak_rate = None
    for key in ["weak", "network_only", "monitoring_only", "layered"]:
        cfg = configs[key]
        res = model.simulate(cfg, n_runs=args.runs, seed=args.seed)
        if key == "weak":
            weak_rate = res.incident_rate
        rel_reduction = (
            (1.0 - (res.incident_rate / weak_rate)) * 100.0 if weak_rate and weak_rate > 0 else 0.0
        )
        results.append((res, rel_reduction))

    print("-" * 88)
    print(f"{"Configuration":<26} {"Incidents":<12} {"Rate":<10} {"95% CI":<22} {"Rel. Reduction":<15}")
    print("-" * 88)
    for res, red in results:
        ci_str = f"[{res.ci_95[0]*100:.3f}%, {res.ci_95[1]*100:.3f}%]"
        print(
            f"{res.configuration_name:<26} {res.n_incidents:<12} "
            f"{res.incident_rate*100:>6.3f}%    {ci_str:<22} {red:>6.1f}%"
        )
    print("-" * 88)

def cmd_sensitivity(args):
    configs = get_standard_configurations()
    cfg = configs[args.config]
    model = RiskModel()
    print(f"=== Global Sobol Sensitivity (Saltelli-Jansen Estimator): {cfg.name} ===")
    sobol_indices = sobol_sensitivity(model, cfg, n_samples=args.runs, seed=args.seed)
    print("-" * 65)
    print(f"{"Variable":<28} {"First-Order S_i":<18} {"Total-Effect S_Ti":<18}")
    print("-" * 65)
    for var, idxs in sorted(sobol_indices.items(), key=lambda x: x[1]["total_effect"], reverse=True):
        print(f"{var:<28} {idxs["first_order"]:>12.5f}      {idxs["total_effect"]:>12.5f}")
    print("-" * 65)

def main():
    parser = argparse.ArgumentParser(
        prog="pra-containment",
        description="Probabilistic Risk Assessment for AI Agent Containment Failure",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # compare
    p_comp = subparsers.add_parser("compare", help="Compare control configurations")
    p_comp.add_argument("--runs", type=int, default=20_000, help="Number of Monte Carlo runs per scenario")
    p_comp.add_argument("--seed", type=int, default=260903, help="Random seed")
    p_comp.add_argument("--ccf", type=float, default=0.0, help="Common-Cause Failure beta factor (0.0 to 1.0)")
    p_comp.set_defaults(func=cmd_compare)

    # sensitivity
    p_sens = subparsers.add_parser("sensitivity", help="Sobol global sensitivity analysis")
    p_sens.add_argument("--config", choices=["weak", "network_only", "monitoring_only", "layered"], default="weak")
    p_sens.add_argument("--runs", type=int, default=2_000, help="Runs")
    p_sens.add_argument("--seed", type=int, default=260903, help="Seed")
    p_sens.set_defaults(func=cmd_sensitivity)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
