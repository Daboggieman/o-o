#!/usr/bin/env python3
"""
Checks whether it's time for the next update yet, and if so, appends
a random motivational quote to today's log file and pushes it.

Runs hourly on weekdays (see .github/workflows/update-file.yml), but
only actually posts an update when the random 1-5 hour gap since the
last one has elapsed — this is what produces a "somewhere between 1
and 5 hours" cadence instead of a fixed interval.
"""
import random
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

LOG_DIR = Path("logs")
STATE_FILE = LOG_DIR / ".next_update_at.txt"
QUOTES_API_URL = "https://dummyjson.com/quotes/random"
MIN_GAP_HOURS = 1
MAX_GAP_HOURS = 5

# Used if the API call fails for any reason — keeps the automation
# working even when the network/API is unavailable.
FALLBACK_QUOTES = [
    ("The only way to do great work is to love what you do.", "Steve Jobs"),
    ("Success is not final, failure is not fatal: it is the courage to continue that counts.", "Winston Churchill"),
    ("Believe you can and you're halfway there.", "Theodore Roosevelt"),
    ("It always seems impossible until it's done.", "Nelson Mandela"),
    ("Start where you are. Use what you have. Do what you can.", "Arthur Ashe"),
    ("The future belongs to those who believe in the beauty of their dreams.", "Eleanor Roosevelt"),
    ("Don't watch the clock; do what it does. Keep going.", "Sam Levenson"),
    ("Your limitation—it's only your imagination.", "Unknown"),
    ("Great things never come from comfort zones.", "Unknown"),
    ("Dream it. Wish it. Do it.", "Unknown"),
]


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def generate_message() -> str:
    """
    Returns a random motivational quote, formatted as: "Quote" — Author

    Tries the DummyJSON quotes API first; falls back to a small local
    list if the request fails for any reason (network issue, timeout,
    API downtime, rate limit, etc.), so the automation never breaks.
    """
    try:
        response = requests.get(QUOTES_API_URL, timeout=10)
        response.raise_for_status()
        data = response.json()
        quote, author = data["quote"], data["author"]
    except (requests.RequestException, KeyError, ValueError):
        quote, author = random.choice(FALLBACK_QUOTES)

    return f'"{quote}" — {author}'


def read_next_update_at():
    if not STATE_FILE.exists():
        return None
    try:
        return datetime.fromisoformat(STATE_FILE.read_text().strip())
    except ValueError:
        return None


def write_next_update_at(when: datetime) -> None:
    LOG_DIR.mkdir(exist_ok=True)
    STATE_FILE.write_text(when.isoformat())


def main() -> None:
    now = datetime.now(timezone.utc)
    next_update_at = read_next_update_at()

    if next_update_at is not None and now < next_update_at:
        print(f"Not due yet — next update at {next_update_at.isoformat()}.")
        return

    today = now.strftime("%Y-%m-%d")
    filepath = LOG_DIR / f"{today}.md"

    if not filepath.exists():
        LOG_DIR.mkdir(exist_ok=True)
        filepath.write_text(f"# Log for {today}\n\n")

    timestamp = now.strftime("%H:%M UTC")
    message = generate_message()

    with filepath.open("a") as f:
        f.write(f"- **{timestamp}** — {message}\n")

    gap_hours = random.randint(MIN_GAP_HOURS, MAX_GAP_HOURS)
    write_next_update_at(now + timedelta(hours=gap_hours))
    print(f"Next update scheduled in {gap_hours}h.")

    try:
        run(["git", "add", str(filepath), str(STATE_FILE)])
        run(["git", "commit", "-m", f"Update log for {today} at {timestamp}"])
        run(["git", "push"])
    except subprocess.CalledProcessError as e:
        print(f"Git command failed: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Updated and pushed {filepath}")


if __name__ == "__main__":
    main()