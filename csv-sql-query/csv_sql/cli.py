import argparse
from .executor import CSVSQLExecutor

def main():
    parser = argparse.ArgumentParser(prog="csv-sql")
    parser.add_argument("--table", action="append", help="Load table format: file.csv=tbl_name")
    parser.add_argument("query", help="SQL query to execute")
    args = parser.parse_args()

    exec = CSVSQLExecutor()
    if args.table:
        for t in args.table:
            f, name = t.split("=")
            exec.load_csv(f, name)

    headers, rows = exec.query(args.query)
    print(" | ".join(headers))
    print("-" * 50)
    for r in rows:
        print(" | ".join(str(x) for x in r))

if __name__ == "__main__":
    main()
