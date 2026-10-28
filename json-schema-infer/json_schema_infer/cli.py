import argparse, json, sys
from .infer import infer_schema

def main():
    parser = argparse.ArgumentParser(prog="json-schema-infer")
    parser.add_argument("file", help="JSON file to infer schema from")
    args = parser.parse_args()
    with open(args.file, "r", encoding="utf-8") as f:
        data = json.load(f)
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        **infer_schema(data)
    }
    print(json.dumps(schema, indent=2))

if __name__ == "__main__":
    main()
