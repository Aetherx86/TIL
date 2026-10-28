# git-squash-helper

Conventional commit formatter and branch squash helper.

## Overview

Feature branches often contain fragmented, messy commit histories ("fix typo", "wip", "testing"). `git-squash-helper` analyzes commit messages, infers conventional commit types (`feat`, `fix`, `docs`, `refactor`, `test`), and formats standardized atomic commit messages for squashed pull requests.

## Features

- Conventional Commit Inference: Automatically detects whether a series of commits represents a feature, bugfix, documentation update, or refactor.
- Bulleted Detail Summarization: Consolidates secondary commits into structured markdown bullet points.
- Clean Branch Integration: Prepares clean summaries for `git merge --squash` or GitHub/GitLab squash-and-merge operations.
- Zero Dependencies: Pure Python standard library implementation.

## Installation

```bash
git clone https://gitlab.com/jk9576/git-squash-helper.git
cd git-squash-helper
pip install -e .
```

## CLI Usage

```bash
git-squash "add user authentication" "fix token expiry bug" "add unit tests for login"
```

Sample Output:

```
=== Suggested Squashed Commit Message ===
feat: add user authentication

- fix token expiry bug
- add unit tests for login
```

## Python API Usage

```python
from git_squash.helper import GitSquashHelper, CommitSummary

messages = ["fix database connection pool leak", "update timeout settings"]
ctype = GitSquashHelper.infer_type_from_messages(messages)
summary = CommitSummary(
    commit_type=ctype,
    scope="db",
    description=messages[0],
    bullet_points=messages[1:],
)
print(summary.format_conventional_commit())
```

## Running Tests

```bash
python -m unittest discover tests
```

## License

MIT License. See LICENSE for details.
