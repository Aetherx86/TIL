import unittest
from json_schema_infer.infer import TypeLattice, infer_schema


class TestInfer(unittest.TestCase):
    def test_lattice_unification(self):
        self.assertEqual(TypeLattice.unify_types("integer", "number"), "number")
        self.assertEqual(TypeLattice.unify_types("string", "string"), "string")
        self.assertEqual(TypeLattice.unify_types("string", "integer"), "anyOf")

    def test_numeric_bounds_aggregation(self):
        data = [10, 25, 5, 80]
        schema = infer_schema(data)
        self.assertEqual(schema["type"], "array")
        self.assertEqual(schema["items"]["type"], "integer")
        self.assertEqual(schema["items"]["minimum"], 5)
        self.assertEqual(schema["items"]["maximum"], 80)

    def test_uuid_format_inference(self):
        uuid_str = "123e4567-e89b-12d3-a456-426614174000"
        schema = infer_schema(uuid_str)
        self.assertEqual(schema["format"], "uuid")

    def test_polymorphic_array_deduplication(self):
        data = [1, 2, "a", "b", None]
        schema = infer_schema(data, track_bounds=False)
        self.assertIn("anyOf", schema["items"])
        # Distinct types: integer, string, null
        self.assertEqual(len(schema["items"]["anyOf"]), 3)


if __name__ == "__main__":
    unittest.main()
