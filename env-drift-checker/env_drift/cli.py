import argparse, sys
from pathlib import Path
from .checker import EnvDriftChecker

def main():
    parser = argparse.ArgumentParser(prog="env-drift")
    parser.add_argument("--example", required=True)
    parser.add_argument("--target", required=True)
    args = parser.parse_args()
    rep = EnvDriftChecker.compare(Path(args.example), Path(args.target))
    has_drift = False
    if rep.missing_in_target:
        has_drift = True
        print(f"Missing in target ({len(rep.missing_in_target)}): {', '.join(rep.missing_in_target)}")
    if rep.empty_in_target:
        has_drift = True
        print(f"Empty in target ({len(rep.empty_in_target)}): {', '.join(rep.empty_in_target)}")
    if rep.undocumented_in_target:
        print(f"Undocumented in template ({len(rep.undocumented_in_target)}): {', '.join(rep.undocumented_in_target)}")
    if has_drift:
        sys.exit(1)
    print("Environment variables in sync.")

if __name__ == "__main__":
    main()
