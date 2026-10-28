import argparse, sys
from pathlib import Path
from .auditor import MarkdownLinkAuditor

def main():
    parser = argparse.ArgumentParser(prog="md-audit")
    parser.add_argument("path", help="Markdown file or directory to audit")
    args = parser.parse_args()
    auditor = MarkdownLinkAuditor()
    p = Path(args.path)
    files = [p] if p.is_file() else list(p.rglob("*.md"))
    total_broken = 0
    for f in files:
        findings = auditor.audit_file(f)
        for item in findings:
            total_broken += 1
            print(f"{item.source_file}:{item.line_number} -> {item.target_link} ({item.reason})")
    if total_broken > 0:
        print(f"Total broken links: {total_broken}")
        sys.exit(1)
    print("All internal links and anchors valid.")

if __name__ == "__main__":
    main()
