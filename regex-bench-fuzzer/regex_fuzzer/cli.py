import argparse
from .fuzzer import ReDoSFuzzer

def main():
    parser = argparse.ArgumentParser(prog="regex-fuzz")
    parser.add_argument("pattern")
    args = parser.parse_args()
    res = ReDoSFuzzer().test_pattern(args.pattern)
    print(f"Pattern: {res.pattern}")
    print(f"Catastrophic Backtracking Detected: {res.is_vulnerable}")
    print(f"Max Search Duration: {res.max_duration_sec:.4f}s")

if __name__ == "__main__":
    main()
