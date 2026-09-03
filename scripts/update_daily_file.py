#!/usr/bin/env python3
"""
Appends a new timestamped message to today's log file and pushes it.

Intended to run every 4 hours, e.g. via a GitHub Actions cron trigger.
"""
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = Path("logs")


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def generate_message() -> str:
    """
    Replace this with whatever content you actually want logged —
    pull from an API, a queue, sensor data, a random quote, etc.
    """
    return "Scheduled check-in."


def main() -> None:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filepath = LOG_DIR / f"{today}.md"

    if not filepath.exists():
        LOG_DIR.mkdir(exist_ok=True)
        filepath.write_text(f"# Log for {today}\n\n")

    timestamp = datetime.now(timezone.utc).strftime("%H:%M UTC")
    message = generate_message()

    with filepath.open("a") as f:
        f.write(f"- **{timestamp}** — {message}\n")

    try:
        run(["git", "add", str(filepath)])
        run(["git", "commit", "-m", f"Update log for {today} at {timestamp}"])
        run(["git", "push"])
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Updated and pushed {filepath}")


if __name__ == "__main__":
    main()
