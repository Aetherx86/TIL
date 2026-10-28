import argparse
from .helper import GitSquashHelper, CommitSummary

def main():
    parser = argparse.ArgumentParser(prog="git-squash")
    parser.add_argument("messages", nargs="+", help="Commit messages to combine")
    args = parser.parse_args()
    ctype = GitSquashHelper.infer_type_from_messages(args.messages)
    summary = CommitSummary(
        commit_type=ctype,
        scope="",
        description=args.messages[0],
        bullet_points=args.messages[1:],
    )
    print("=== Suggested Squashed Commit Message ===")
    print(summary.format_conventional_commit())

if __name__ == "__main__":
    main()
