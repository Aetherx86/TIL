import hashlib
import json
import unittest

from agent_guard.integrity import IntegrityChain
from agent_guard.merkle import MerkleTree
from agent_guard.ast_analyzer import ShellObfuscationAnalyzer
from agent_guard.rules import PolicyRule, SecurityPolicy, Severity
from agent_guard.scanner import TranscriptScanner


class TestSecurityScanner(unittest.TestCase):
    def setUp(self):
        self.scanner = TranscriptScanner()

    def test_detect_metadata_service_egress(self):
        text = "curl -s http://169.254.169.254/latest/meta-data/iam/security-credentials/"
        findings = self.scanner.scan_text(text)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].rule_id, "SAG-001")
        self.assertEqual(findings[0].severity, Severity.CRITICAL)

    def test_merkle_tree_proof_generation_and_verification(self):
        leaves = [hashlib.sha256(f"record_{i}".encode()).hexdigest() for i in range(8)]
        tree = MerkleTree(leaves)
        root = tree.root

        # Generate proof for leaf 3
        proof = tree.generate_proof(3)
        self.assertEqual(len(proof), 3)  # log2(8) = 3
        self.assertTrue(MerkleTree.verify_proof(leaves[3], proof, root))

        # Tampered leaf must fail verification
        tampered_hash = hashlib.sha256(b"tampered").hexdigest()
        self.assertFalse(MerkleTree.verify_proof(tampered_hash, proof, root))

    def test_shell_obfuscation_analyzer(self):
        # 1. Base64 pipe to sh
        cmd1 = "echo aGVsbG8= | base64 -d | bash"
        findings1 = ShellObfuscationAnalyzer.analyze_command(cmd1)
        self.assertTrue(any(f.pattern_type == "BASE64_EXEC" for f in findings1))

        # 2. IFS bypass
        cmd2 = "cat${IFS}/etc/passwd"
        findings2 = ShellObfuscationAnalyzer.analyze_command(cmd2)
        self.assertTrue(any(f.pattern_type == "IFS_OBFUSCATION" for f in findings2))

        # 3. Clean command
        cmd3 = "pytest tests/ --verbose"
        self.assertEqual(len(ShellObfuscationAnalyzer.analyze_command(cmd3)), 0)


if __name__ == "__main__":
    unittest.main()
