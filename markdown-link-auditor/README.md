# markdown-link-auditor

Local Markdown anchor and dead file link auditor.

## Overview

Large documentation repositories accumulate broken cross-references, missing anchor slugs, and dead relative file paths over time. `markdown-link-auditor` scans Markdown documentation trees, discovers local reference links and section anchors, and verifies their integrity.

## Features

- Local File Target Verification: Resolves relative file links (e.g., `[Guide](../guides/setup.md)`) and verifies file presence on disk.
- Header Slug Anchor Validation: Slugs Markdown headers (e.g., `# Getting Started` -> `#getting-started`) and flags broken anchor links.
- Recursive Directory Traversal: Audits single files or entire documentation suites.
- CI/CD Exit Codes: Returns exit code 1 if broken links are discovered, enabling automated pull request gating.
- Zero Dependencies: Uses Python standard library regular expressions and filesystem utilities.

## Installation

```bash
git clone https://gitlab.com/jk9576/markdown-link-auditor.git
cd markdown-link-auditor
pip install -e .
```

## CLI Usage

```bash
md-audit docs/
```

Sample Output:

```
docs/index.md:24 -> #quickstart (Anchor #quickstart not found)
docs/api.md:58 -> ../guides/auth.md (Local target file does not exist)

Total broken links: 2
```

## Python API Usage

```python
from pathlib import Path
from md_auditor.auditor import MarkdownLinkAuditor

auditor = MarkdownLinkAuditor()
findings = auditor.audit_file(Path("docs/README.md"))

for item in findings:
    print(f"Line {item.line_number}: {item.target_link} - {item.reason}")
```

## Running Tests

```bash
python -m unittest discover tests
```

## License

MIT License. See LICENSE for details.
