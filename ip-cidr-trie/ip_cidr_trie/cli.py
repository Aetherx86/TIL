import argparse
from .trie import RadixTrie

def main():
    parser = argparse.ArgumentParser(prog="cidr-trie")
    parser.add_argument("--rule", action="append", required=True, help="CIDR rule e.g. 10.0.0.0/8=PRIVATE")
    parser.add_argument("ip", help="IP address to lookup")
    args = parser.parse_args()

    trie = RadixTrie()
    for r in args.rule:
        parts = r.split("=")
        val = parts[1] if len(parts) > 1 else True
        trie.insert(parts[0], val)

    match = trie.find_longest_prefix(args.ip)
    print(f"{args.ip} -> {match}")

if __name__ == "__main__":
    main()
