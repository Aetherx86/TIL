import unittest
from api_mock.server import DynamicRouter, MockServer

class TestMockServer(unittest.TestCase):
    def test_dynamic_route_parameter_extraction(self):
        router = DynamicRouter()
        router.add_route("/api/v1/users/{id:[0-9]+}/orders/{code:[A-Z]+}", {"status": 200, "body": {"ok": True}})

        match1 = router.resolve("/api/v1/users/42/orders/ABC")
        self.assertIsNotNone(match1)
        self.assertEqual(match1.path_params, {"id": "42", "code": "ABC"})

        match_fail = router.resolve("/api/v1/users/alice/orders/ABC")  # id not numeric
        self.assertIsNone(match_fail)

    def test_mock_server_instantiation(self):
        server = MockServer({"/ping": {"status": 200, "body": {"pong": True}}}, port=0)
        http_srv = server.create_server()
        try:
            self.assertIsNotNone(http_srv)
        finally:
            http_srv.server_close()

if __name__ == "__main__":
    unittest.main()
