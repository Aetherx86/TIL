import argparse
from .detector import LogAnomalyDetector

def main():
    parser = argparse.ArgumentParser(prog="log-anomaly")
    parser.add_argument("counts", nargs="+", type=int, help="Event counts per sliding time bucket")
    args = parser.parse_args()
    res = LogAnomalyDetector().evaluate_counts(args.counts)
    for w in res:
        mark = " [!] ANOMALY" if w.is_anomaly else ""
        print(f"Window {w.window_index:<4} Count: {w.event_count:<6} Z-Score: {w.z_score:>6.2f}{mark}")

if __name__ == "__main__":
    main()
