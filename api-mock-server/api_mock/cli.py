import argparse, json
from .server import MockServer

def main():
    parser = argparse.ArgumentParser(prog="api-mock")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--routes", default='{"/health": {"status": 200, "body": {"status": "ok"}}}')
    args = parser.parse_args()
    routes = json.loads(args.routes)
    print(f"Serving mock on http://127.0.0.1:{args.port}")
    MockServer(routes, args.port)

if __name__ == "__main__":
    main()
