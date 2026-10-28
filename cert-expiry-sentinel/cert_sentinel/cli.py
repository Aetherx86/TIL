import argparse
import sys
from .checker import CertificateChecker

def main():
    parser = argparse.ArgumentParser(
        prog="cert-expiry-sentinel",
        description="X.509 TLS certificate sentinel with ASN.1 DER parser",
    )
    parser.add_argument("hosts", nargs="+", help="Hostnames to check (e.g., example.com:443 or google.com)")
    parser.add_argument("--warn-days", type=int, default=30, help="Days threshold for expiry warning (default: 30)")
    parser.add_argument("--timeout", type=float, default=5.0, help="Connection timeout in seconds")

    args = parser.parse_args()
    checker = CertificateChecker(timeout=args.timeout)

    print(f"{'Host':<30} {'Status':<10} {'Days Left':<12} {'Common Name':<25} {'Expires On'}")
    print("-" * 95)

    has_warnings = False
    for item in args.hosts:
        if ":" in item:
            host, port_str = item.split(":", 1)
            port = int(port_str)
        else:
            host, port = item, 443

        info = checker.check_host(host, port)
        if info.error:
            print(f"{host + ':' + str(port):<30} {'ERROR':<10} {'N/A':<12} {'N/A':<25} {info.error}")
            has_warnings = True
            continue

        status = "EXPIRED" if info.is_expired else ("WARN" if info.days_remaining <= args.warn_days else "OK")
        if status in ("EXPIRED", "WARN"):
            has_warnings = True

        exp_str = info.not_after.strftime("%Y-%m-%d %H:%M UTC")
        print(f"{host + ':' + str(port):<30} {status:<10} {str(info.days_remaining) + 'd':<12} {info.common_name[:24]:<25} {exp_str}")

    sys.exit(1 if has_warnings else 0)

if __name__ == "__main__":
    main()
