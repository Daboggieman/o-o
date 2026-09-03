#!/usr/bin/env python3
"""
Creates today's log file (if it doesn't already exist), seeds a fresh
random 1-5 hour countdown for the first update of the day, and pushes
both to the repo immediately.

Intended to run once a day on weekdays, e.g. via a GitHub Actions
cron trigger (see .github/workflows/daily-file.yml).
"""
import random
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

LOG_DIR = Path("logs")
STATE_FILE = LOG_DIR / ".next_update_at.txt"
MIN_GAP_HOURS = 1
MAX_GAP_HOURS = 5


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def main() -> None:
    LOG_DIR.mkdir(exist_ok=True)
    now = datetime.now(timezone.utc)
    today = now.strftime("%Y-%m-%d")
    filepath = LOG_DIR / f"{today}.md"

    if filepath.exists():
        print(f"{filepath} already exists, nothing to create.")
        return

    filepath.write_text(f"# Log for {today}\n\n")

    # Seed a fresh random countdown so today's first update also lands
    # somewhere between 1 and 5 hours out, not immediately.
    gap_hours = random.randint(MIN_GAP_HOURS, MAX_GAP_HOURS)
    STATE_FILE.write_text((now + timedelta(hours=gap_hours)).isoformat())

    try:
        run(["git", "add", str(filepath), str(STATE_FILE)])
        run(["git", "commit", "-m", f"Create log file for {today}"])
        run(["git", "push"])
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Created and pushed {filepath} (first update in {gap_hours}h)")


if __name__ == "__main__":
    main()