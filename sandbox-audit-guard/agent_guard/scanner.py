import json
from typing import Any, Dict, List, Optional
from .rules import Finding, SecurityPolicy, Severity


class TranscriptScanner:
    """Scans agent transcripts and execution logs for security policy violations."""

    def __init__(self, policy: Optional[SecurityPolicy] = None):
        self.policy = policy if policy is not None else SecurityPolicy()

    def scan_text(self, text: str) -> List[Finding]:
        findings: List[Finding] = []
        lines = text.splitlines()

        for line_idx, line in enumerate(lines, start=1):
            for rule in self.policy.rules:
                for match in rule.pattern.finditer(line):
                    snippet = line.strip()
                    if len(snippet) > 120:
                        start = max(0, match.start() - 30)
                        end = min(len(snippet), match.end() + 30)
                        snippet = ("..." if start > 0 else "") + snippet[start:end] + ("..." if end < len(snippet) else "")

                    findings.append(
                        Finding(
                            rule_id=rule.rule_id,
                            severity=rule.severity,
                            title=rule.title,
                            description=rule.description,
                            snippet=snippet,
                            line_number=line_idx,
                            recommendation=rule.recommendation,
                        )
                    )
        return findings

    def scan_jsonl(self, jsonl_content: str) -> List[Finding]:
        findings: List[Finding] = []
        for line_idx, line in enumerate(jsonl_content.strip().splitlines(), start=1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
                # Convert whole object to string representation for pattern matching
                serialized = json.dumps(item)
            except Exception:
                serialized = line

            line_findings = self.scan_text(serialized)
            for f in line_findings:
                f.line_number = line_idx
                findings.append(f)

        return findings

    @staticmethod
    def generate_markdown_report(findings: List[Finding], target_name: str = "Evaluation Transcript") -> str:
        lines = [
            f"# Security Audit Report: {target_name}",
            "",
            f"Total Findings: {len(findings)}",
            "",
        ]

        # Group by severity
        severity_counts = {s: 0 for s in Severity}
        for f in findings:
            severity_counts[f.severity] += 1

        lines.extend([
            "## Summary by Severity",
            "",
            "| Severity | Count |",
            "| :--- | :--- |",
            f"| CRITICAL | {severity_counts[Severity.CRITICAL]} |",
            f"| HIGH | {severity_counts[Severity.HIGH]} |",
            f"| MEDIUM | {severity_counts[Severity.MEDIUM]} |",
            f"| LOW | {severity_counts[Severity.LOW]} |",
            "",
            "## Detailed Findings",
            "",
        ])

        if not findings:
            lines.append("No security policy violations detected.")
            return "\n".join(lines)

        for idx, f in enumerate(findings, start=1):
            lines.extend([
                f"### {idx}. [{f.severity.value}] {f.title} ({f.rule_id})",
                "",
                f"- Line: {f.line_number if f.line_number else 'N/A'}",
                f"- Description: {f.description}",
                f"- Match Snippet: `{f.snippet}`",
                f"- Remediation: {f.recommendation}",
                "",
            ])

        return "\n".join(lines)
