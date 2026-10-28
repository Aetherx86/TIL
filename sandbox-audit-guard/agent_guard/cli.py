import argparse
import sys
from pathlib import Path

from .integrity import IntegrityChain
from .scanner import TranscriptScanner


def cmd_scan(args):
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File '{args.file}' not found.", file=sys.stderr)
        sys.exit(1)

    content = file_path.read_text(encoding="utf-8")
    scanner = TranscriptScanner()

    if file_path.suffix.lower() == ".jsonl":
        findings = scanner.scan_jsonl(content)
    else:
        findings = scanner.scan_text(content)

    if args.output:
        report = scanner.generate_markdown_report(findings, target_name=file_path.name)
        Path(args.output).write_text(report, encoding="utf-8")
        print(f"Report written to '{args.output}'.")
    else:
        print(f"=== Scan Results for {file_path.name} ===")
        print(f"Total Policy Findings: {len(findings)}\n")
        for f in findings:
            loc = f"Line {f.line_number}: " if f.line_number else ""
            print(f"[{f.severity.value}] {loc}{f.title} ({f.rule_id})")
            print(f"  Snippet: {f.snippet}")
            print(f"  Remediation: {f.recommendation}\n")

    if any(f.severity.value in ["HIGH", "CRITICAL"] for f in findings):
        sys.exit(2)


def cmd_verify(args):
    file_path = Path(args.file)
    if not file_path.exists():
        print(f"Error: File '{args.file}' not found.", file=sys.stderr)
        sys.exit(1)

    content = file_path.read_text(encoding="utf-8")
    chain = IntegrityChain.load_jsonl(content, secret_key=args.key)
    valid, reason = chain.verify_chain()

    if valid:
        print(f"Integrity Verified: Chain of {len(chain.records)} tool-call records is valid and untampered.")
    else:
        print(f"FAILED: Integrity violation detected! {reason}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="agent-guard",
        description="Agent Sandbox Egress and Tool-Call Integrity Monitor",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # scan command
    p_scan = subparsers.add_parser("scan", help="Scan transcripts or shell logs for covert egress and sandbox escapes")
    p_scan.add_argument("file", help="Path to transcript or log file (.txt, .log, .jsonl)")
    p_scan.add_argument("-o", "--output", help="Path to write Markdown audit report")
    p_scan.set_defaults(func=cmd_scan)

    # verify command
    p_verify = subparsers.add_parser("verify", help="Verify cryptographic integrity of tool-call hash chain")
    p_verify.add_argument("file", help="Path to tool-call record JSONL file")
    p_verify.add_argument("--key", help="HMAC secret key used by supervisory monitor", default=None)
    p_verify.set_defaults(func=cmd_verify)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
