import argparse, sys
from .vault import EncryptedVault

def main():
    parser = argparse.ArgumentParser(prog="vault-kv")
    parser.add_argument("--db", default="secrets.vault")
    parser.add_argument("--passphrase", required=True)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_set = sub.add_parser("set")
    p_set.add_argument("key")
    p_set.add_argument("value")
    p_get = sub.add_parser("get")
    p_get.add_argument("key")
    p_list = sub.add_parser("list")

    args = parser.parse_args()
    v = EncryptedVault(args.db, args.passphrase)
    if args.cmd == "set":
        v.set(args.key, args.value)
        print(f"Stored key '{args.key}'.")
    elif args.cmd == "get":
        val = v.get(args.key)
        if val is None:
            print("Key not found.", file=sys.stderr)
            sys.exit(1)
        print(val)
    elif args.cmd == "list":
        for k in v.list_keys():
            print(k)

if __name__ == "__main__":
    main()
