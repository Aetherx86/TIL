import tempfile
from pathlib import Path
import unittest
from csv_sql.executor import CSVSQLExecutor, QueryOptimizer, SchemaInferrer

class TestCSVSQL(unittest.TestCase):
    def test_schema_inference(self):
        self.assertEqual(SchemaInferrer.infer_type(["1", "24", "1005"]), "INTEGER")
        self.assertEqual(SchemaInferrer.infer_type(["3.14", "2.718", "10"]), "REAL")
        self.assertEqual(SchemaInferrer.infer_type(["apple", "banana"]), "TEXT")

    def test_auto_indexing_and_execution(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv") as f:
            f.write("user_id,username,score\n1,alice,95.5\n2,bob,88.0\n3,charlie,92.3\n")
            csv_path = f.name

        try:
            engine = CSVSQLExecutor()
            engine.load_csv(csv_path, "users")
            headers, rows = engine.query("SELECT username, score FROM users WHERE user_id = 2")
            self.assertEqual(headers, ["username", "score"])
            self.assertEqual(rows, [("bob", 88.0)])

            # Verify index generation
            plan = engine.explain("SELECT username FROM users WHERE user_id = 2")
            plan_str = " ".join([str(p) for p in plan])
            self.assertIn("idx_users_user_id", plan_str)
        finally:
            Path(csv_path).unlink()

if __name__ == "__main__":
    unittest.main()
