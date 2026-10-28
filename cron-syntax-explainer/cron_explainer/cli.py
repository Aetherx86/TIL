import argparse
from .explainer import explain_cron

def main():
    parser = argparse.ArgumentParser(prog="cron-explain")
    parser.add_argument("cron_expr", help="5-field cron string")
    args = parser.parse_args()
    print(explain_cron(args.cron_expr))

if __name__ == "__main__":
    main()
