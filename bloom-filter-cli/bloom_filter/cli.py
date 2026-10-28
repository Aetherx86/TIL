import argparse
from .filter import BloomFilter

def main():
    parser = argparse.ArgumentParser(prog="bloom-filter")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_demo = sub.add_parser("demo")
    args = parser.parse_args()
    bf = BloomFilter(capacity=1000, false_positive_rate=0.01)
    bf.add("test-item")
    print("Contains 'test-item':", bf.contains("test-item"))
    print("Contains 'unknown':", bf.contains("unknown"))

if __name__ == "__main__":
    main()
