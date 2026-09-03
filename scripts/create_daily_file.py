#!/usr/bin/env python3
"""
Creates today's log file (if it doesn't already exist) and pushes it
to the repo immediately.

Intended to run once a day, e.g. via a GitHub Actions cron trigger.
"""
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = Path("logs")


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def main() -> None:
    LOG_DIR.mkdir(exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filepath = LOG_DIR / f"{today}.md"

    if filepath.exists():
        print(f"{filepath} already exists, nothing to create.")
        return

    filepath.write_text(f"# Log for {today}\n\n")

    try:
        run(["git", "add", str(filepath)])
        run(["git", "commit", "-m", f"Create log file for {today}"])
        run(["git", "push"])
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Created and pushed {filepath}")


if __name__ == "__main__":
    main()
