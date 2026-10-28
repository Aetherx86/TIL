import argparse
from .collector import MetricCollector

def main():
    parser = argparse.ArgumentParser(prog="sys-metrics")
    parser.add_argument("--once", action="store_true", default=True)
    args = parser.parse_args()
    print(MetricCollector().collect_prometheus_format())

if __name__ == "__main__":
    main()
