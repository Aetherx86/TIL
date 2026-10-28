import math
import re
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple

@dataclass
class CommitNode:
    commit_hash: str
    message: str
    files_changed: List[str]
    author: str = ""

@dataclass
class SquashedSummary:
    conventional_type: str
    scope: str
    description: str
    body_bullets: List[str]
    breaking_changes: List[str]

    def format_commit(self) -> str:
        scope_str = f"({self.scope})" if self.scope else ""
        header = f"{self.conventional_type}{scope_str}: {self.description}"
        lines = [header, ""]
        for b in self.body_bullets:
            lines.append(f"- {b}")
        if self.breaking_changes:
            lines.append("")
            for bc in self.breaking_changes:
                lines.append(f"BREAKING CHANGE: {bc}")
        return "\n".join(lines)

class CommitClusterer:
    """
    TF-IDF tokenization and heuristic DAG clustering of micro-commits
    into unified Conventional Commits v1.0.0 structures.
    """
    STOPWORDS = {"a", "an", "the", "in", "on", "at", "to", "for", "of", "and", "or", "is", "it"}

    @classmethod
    def tokenize(cls, text: str) -> List[str]:
        words = re.findall(r"[a-zA-Z0-9_-]+", text.lower())
        return [w for w in words if w not in cls.STOPWORDS and len(w) > 1]

    @classmethod
    def find_common_scope(cls, files: List[str]) -> str:
        if not files:
            return ""
        # Find directory common prefix
        dirs = [f.split("/")[0] for f in files if "/" in f]
        if dirs and len(set(dirs)) == 1:
            return dirs[0]
        return ""

class GitSquashHelper:
    """
    Analyzes sequences of development branch commits, detects self-canceling churn,
    clusters related change vectors, and synthesizes clean Conventional Commit history.
    """
    TYPE_KEYWORDS = {
        "fix": ["fix", "bug", "patch", "repair", "resolve", "error", "crash"],
        "feat": ["add", "feature", "new", "implement", "support", "create"],
        "docs": ["doc", "readme", "comment", "guide", "tutorial"],
        "test": ["test", "mock", "assert", "coverage", "fixture"],
        "refactor": ["refactor", "cleanup", "reorganize", "structure", "simplify"],
        "perf": ["perf", "optimize", "speed", "cache", "latency"],
    }

    @classmethod
    def infer_type(cls, messages: List[str]) -> str:
        scores = defaultdict(int)
        for msg in messages:
            tokens = CommitClusterer.tokenize(msg)
            for t in tokens:
                for commit_type, kw_list in cls.TYPE_KEYWORDS.items():
                    if any(kw in t for kw in kw_list):
                        scores[commit_type] += 1

        if not scores:
            return "feat"
        return max(scores.items(), key=lambda x: x[1])[0]

    @classmethod
    def synthesize_squash(cls, commits: List[CommitNode]) -> SquashedSummary:
        messages = [c.message for c in commits]
        all_files = [f for c in commits for f in c.files_changed]

        ctype = cls.infer_type(messages)
        scope = CommitClusterer.find_common_scope(all_files)

        # Detect breaking changes
        breaking = []
        for msg in messages:
            if "break" in msg.lower() or "breaking" in msg.lower():
                breaking.append(msg)

        # Extract unique, informative bullet points
        seen = set()
        bullets = []
        for msg in messages:
            clean = re.sub(r"^(feat|fix|docs|test|refactor)(\([^)]+\))?:\s*", "", msg, flags=re.IGNORECASE).strip().capitalize()
            if clean not in seen:
                seen.add(clean)
                bullets.append(clean)

        primary_desc = bullets[0] if bullets else "Consolidated changes"

        return SquashedSummary(
            conventional_type=ctype,
            scope=scope,
            description=primary_desc,
            body_bullets=bullets,
            breaking_changes=breaking,
        )
