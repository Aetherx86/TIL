import argparse
from .tracker import DNSTracker

def main():
    parser = argparse.ArgumentParser(prog="dns-track")
    parser.add_argument("domain")
    args = parser.parse_args()
    tracker = DNSTracker()
    for name, ip in tracker.RESOLVERS.items():
        ok, res = tracker.query_resolver(args.domain, ip)
        print(f"{name:<12} ({ip:<15}): {'OK' if ok else 'FAIL'} - {res}")

if __name__ == "__main__":
    main()
