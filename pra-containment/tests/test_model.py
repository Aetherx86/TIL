import random
import unittest

from pra_containment.model import ControlConfiguration, RiskModel, Stage
from pra_containment.copula import GaussianCopula
from pra_containment.sensitivity import pearson_correlation, compute_quantiles_table, sobol_sensitivity

class TestRiskModel(unittest.TestCase):
    def setUp(self):
        self.model = RiskModel()
        self.config_weak = ControlConfiguration(
            name="Weak",
            strengths={"isolation": (2.0, 5.0), "credential": (2.0, 5.0), "monitoring": (2.0, 5.0), "authorization": (2.0, 5.0)},
        )
        self.config_layered = ControlConfiguration(
            name="Layered",
            strengths={"isolation": (8.0, 2.0), "credential": (8.0, 2.0), "monitoring": (8.0, 2.0), "authorization": (8.0, 2.0)},
        )

    def test_copula_correlation_structure(self):
        cop = GaussianCopula.exchangeable(dim=4, rho=0.5)
        samples = cop.sample_uniforms(5_000, random.Random(42))
        self.assertEqual(len(samples), 5_000)
        self.assertEqual(len(samples[0]), 4)
        for row in samples:
            for val in row:
                self.assertTrue(0.0 <= val <= 1.0)
        col0 = [r[0] for r in samples]
        col1 = [r[1] for r in samples]
        corr = pearson_correlation(col0, col1)
        self.assertAlmostEqual(corr, 0.48, delta=0.08)

    def test_saltelli_jansen_sobol_indices(self):
        indices = sobol_sensitivity(self.model, self.config_weak, n_samples=1_500, seed=7)
        for var, idx in indices.items():
            self.assertIn("first_order", idx)
            self.assertIn("total_effect", idx)
            self.assertGreaterEqual(idx["total_effect"] + 1e-5, idx["first_order"])

    def test_common_cause_failure(self):
        m_base = RiskModel(ccf_beta=0.0)
        m_ccf = RiskModel(ccf_beta=0.30)
        res_b = m_base.simulate(self.config_layered, n_runs=8_000, seed=123)
        res_c = m_ccf.simulate(self.config_layered, n_runs=8_000, seed=123)
        self.assertGreater(res_c.incident_rate, res_b.incident_rate)

if __name__ == "__main__":
    unittest.main()
