from pathlib import Path
import tempfile
import unittest
from env_drift.checker import EnvDriftChecker
from env_drift.types import SemanticType, TypeLattice

class TestEnvDrift(unittest.TestCase):
    def test_type_lattice_inference(self):
        self.assertEqual(TypeLattice.infer("true"), SemanticType.BOOLEAN)
        self.assertEqual(TypeLattice.infer("8080"), SemanticType.PORT)
        self.assertEqual(TypeLattice.infer("999999"), SemanticType.INTEGER)
        self.assertEqual(TypeLattice.infer("https://api.domain.internal/v1"), SemanticType.URL)
        self.assertEqual(TypeLattice.infer("192.168.1.1/24"), SemanticType.IPV4)
        self.assertEqual(TypeLattice.infer("xK9_mQp01-aZ98Ywe1924Lksd_"), SemanticType.HIGH_ENTROPY_TOKEN)

    def test_dependency_constraint_enforcement(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as tpl, tempfile.NamedTemporaryFile("w", delete=False) as tgt:
            tpl.write("DB_SSL=true\nDB_CERT=/path/to/cert\n")
            tgt.write("DB_SSL=true\n")
            tpl_path = Path(tpl.name)
            tgt_path = Path(tgt.name)

        try:
            report = EnvDriftChecker.compare(
                tpl_path,
                tgt_path,
                dependencies={"DB_SSL": ["DB_CERT"]},
            )
            self.assertEqual(len(report.dependency_violations), 1)
            self.assertIn("DB_CERT", report.dependency_violations[0])
        finally:
            tpl_path.unlink()
            tgt_path.unlink()

if __name__ == "__main__":
    unittest.main()
