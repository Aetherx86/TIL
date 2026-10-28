import tempfile
from pathlib import Path
import unittest
from md_auditor.auditor import MarkdownLinkAuditor
from md_auditor.graph import DocumentationGraph, TarjanSCC

class TestMarkdownAuditor(unittest.TestCase):
    def test_tarjan_scc_cycle_detection(self):
        graph = DocumentationGraph()
        graph.add_edge("A.md", "B.md")
        graph.add_edge("B.md", "C.md")
        graph.add_edge("C.md", "A.md")  # Cycle A -> B -> C -> A
        graph.add_edge("C.md", "D.md")  # D is non-cyclic leaf

        cycles = graph.find_cycles()
        self.assertEqual(len(cycles), 1)
        self.assertEqual(sorted(cycles[0]), ["A.md", "B.md", "C.md"])

    def test_orphan_detection(self):
        graph = DocumentationGraph()
        graph.add_edge("README.md", "guide.md")
        graph.add_edge("guide.md", "api.md")
        graph.all_nodes.add("orphaned_island.md")

        orphans = graph.find_orphans(["README.md"])
        self.assertEqual(orphans, ["orphaned_island.md"])

    def test_header_slugification(self):
        self.assertEqual(MarkdownLinkAuditor.slugify_header("## Introduction & Quick Start!"), "introduction-quick-start")
        self.assertEqual(MarkdownLinkAuditor.slugify_header("API Reference (v2.0)"), "api-reference-v20")

if __name__ == "__main__":
    unittest.main()
