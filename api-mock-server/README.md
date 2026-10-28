# api-mock-server

Declarative zero-config HTTP mock server driven by JSON route schemas.

## Overview

When developing microservices, frontend applications, or agentic workflows, external APIs may be unavailable, rate-limited, or unstable. `api-mock-server` runs a local HTTP mock server driven by a declarative JSON routing specification.

## Features

- Pure Standard Library: Built on Python's `http.server` without external frameworks (like Flask or FastAPI).
- JSON Declarative Routing: Define status codes, response headers, and JSON response bodies in a single file.
- Fast Local Mocking: Binds instantly to localhost ports for automated integration testing.

## Installation

```bash
git clone https://gitlab.com/jk9576/api-mock-server.git
cd api-mock-server
pip install -e .
```

## CLI Usage

```bash
api-mock --port 8080 --routes '{"/api/v1/health": {"status": 200, "body": {"status": "healthy"}}}'
```

Query the endpoint in another terminal:

```bash
curl http://127.0.0.1:8080/api/v1/health
```

Output:

```json
{"status": "healthy"}
```

## Python API Usage

```python
from api_mock.server import MockServer

routes = {
    "/v1/users": {
        "status": 200,
        "body": [{"id": 1, "username": "alice"}, {"id": 2, "username": "bob"}]
    }
}

server = MockServer(routes, port=9000)
# server.run()
```

## Running Tests

```bash
python -m unittest discover tests
```

## License

MIT License. See LICENSE for details.
