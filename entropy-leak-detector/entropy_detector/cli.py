import argparse, sys
from pathlib import Path
from .detector import EntropyScanner

def main():
    parser = argparse.ArgumentParser(prog="entropy-detect")
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--threshold", type=float, default=3.8)
    args = parser.parse_args()
    scanner = EntropyScanner(threshold=args.threshold)
    count = 0
    for p in args.paths:
        f = Path(p)
        if f.is_file():
            res = scanner.scan_text(f.read_text(encoding="utf-8", errors="ignore"))
            count += len(res)
            for r in res:
                print(f"Line {r.line_number} (Entropy {r.entropy:.2f}): {r.token}")
    if count > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
