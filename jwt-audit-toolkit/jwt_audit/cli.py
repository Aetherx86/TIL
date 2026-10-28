import argparse, json
from .auditor import JWTAuditor

def main():
    parser = argparse.ArgumentParser(prog="jwt-audit")
    parser.add_argument("token")
    args = parser.parse_args()
    jwt = JWTAuditor.inspect(args.token)
    print("=== JWT Header ===")
    print(json.dumps(jwt.header, indent=2))
    print("\n=== JWT Payload ===")
    print(json.dumps(jwt.payload, indent=2))
    print(f"\nExpired: {jwt.is_expired}")
    print(f"None Algorithm Flaw: {jwt.is_none_algorithm}")

if __name__ == "__main__":
    main()
