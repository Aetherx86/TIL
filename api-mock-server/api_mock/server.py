import json
import random
import re
import time
from dataclasses import dataclass, field
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Callable, Dict, List, Optional, Tuple

@dataclass
class RouteMatch:
    handler: Dict[str, Any]
    path_params: Dict[str, str]

class DynamicRouter:
    """
    Regex-compiled dynamic URL route matching with typed path parameters.
    Supports routes like '/api/v1/users/{id:[0-9]+}/items/{slug:[a-z-]+}'.
    """
    PARAM_REGEX = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)(?::([^}]+))?\}")

    def __init__(self):
        self.routes: List[Tuple[re.Pattern, List[str], Dict[str, Any]]] = []

    def add_route(self, pattern_str: str, spec: Dict[str, Any]):
        param_names: List[str] = []

        def replacer(match):
            name = match.group(1)
            custom_re = match.group(2) or "[^/]+"
            param_names.append(name)
            return f"({custom_re})"

        regex_pattern = f"^{self.PARAM_REGEX.sub(replacer, pattern_str)}$"
        compiled = re.compile(regex_pattern)
        self.routes.append((compiled, param_names, spec))

    def resolve(self, path: str) -> Optional[RouteMatch]:
        clean_path = path.split("?")[0]
        for pattern, param_names, spec in self.routes:
            m = pattern.match(clean_path)
            if m:
                extracted = dict(zip(param_names, m.groups()))
                return RouteMatch(handler=spec, path_params=extracted)
        return None

class MockServer:
    """
    High-fidelity API Mock Server with dynamic parameter routing,
    stochastic latency injection, and chaos engineering fault simulation.
    """
    def __init__(
        self,
        routes: Dict[str, Dict[str, Any]],
        port: int = 8080,
        latency_mean_ms: float = 0.0,
        chaos_fail_rate: float = 0.0,
    ):
        self.router = DynamicRouter()
        for route_path, spec in routes.items():
            self.router.add_route(route_path, spec)
        self.port = port
        self.latency_mean_ms = latency_mean_ms
        self.chaos_fail_rate = chaos_fail_rate
        self.server: Optional[HTTPServer] = None

    def create_handler_class(self):
        router_ref = self.router
        lat_ms = self.latency_mean_ms
        chaos_p = self.chaos_fail_rate

        class Handler(BaseHTTPRequestHandler):
            def _handle_request(self, method: str):
                if lat_ms > 0:
                    time.sleep(lat_ms / 1000.0)

                if chaos_p > 0 and random.random() < chaos_p:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(b'{"error": "Chaos engineering injected 500 error"}')
                    return

                matched = router_ref.resolve(self.path)
                if matched:
                    spec = matched.handler
                    status = spec.get("status", 200)
                    body_data = spec.get("body", {})
                    # Interpolate path params if template
                    body_json = json.dumps(body_data).encode("utf-8")
                    self.send_response(status)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(body_json)
                else:
                    self.send_response(404)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(b'{"error": "Route not found"}')

            def do_GET(self):
                self._handle_request("GET")

            def do_POST(self):
                self._handle_request("POST")

            def log_message(self, format, *args):
                pass

        return Handler

    def create_server(self) -> HTTPServer:
        handler_cls = self.create_handler_class()
        self.server = HTTPServer(("127.0.0.1", self.port), handler_cls)
        return self.server
