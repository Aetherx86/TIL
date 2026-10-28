import unittest
from git_squash.helper import CommitNode, GitSquashHelper

class TestGitSquash(unittest.TestCase):
    def test_conventional_type_inference(self):
        messages = ["Fix memory leak in parser", "Bug fix for socket timeout", "Cleanup tests"]
        ctype = GitSquashHelper.infer_type(messages)
        self.assertEqual(ctype, "fix")

    def test_synthesize_squash_commit(self):
        commits = [
            CommitNode("hash1", "feat: add user authentication", ["auth/login.py", "auth/models.py"]),
            CommitNode("hash2", "fix token expiration boundary", ["auth/login.py"]),
            CommitNode("hash3", "add auth unit tests", ["auth/test_auth.py"]),
        ]
        summary = GitSquashHelper.synthesize_squash(commits)
        self.assertEqual(summary.scope, "auth")
        formatted = summary.format_commit()
        self.assertIn("auth", formatted)
        self.assertIn("- Add user authentication", formatted)

if __name__ == "__main__":
    unittest.main()
