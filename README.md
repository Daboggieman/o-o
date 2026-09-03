# Daily Log Automation

Automatically creates a new dated log file once a day and appends a
timestamped message to it every 4 hours — all pushed straight to this
repo via GitHub Actions. No server, cron daemon, or personal access
token required.

## How it works

Two scheduled GitHub Actions workflows call two small Python scripts:

| Workflow | Schedule | Script | What it does |
|---|---|---|---|
| `daily-file.yml` | Once a day, 00:05 UTC | `create_daily_file.py` | Creates `logs/YYYY-MM-DD.md` for the new day and pushes it immediately |
| `update-file.yml` | Every 4 hours, on the hour UTC | `update_daily_file.py` | Appends a new timestamped line to today's file and pushes it |

Both scripts use plain `git` commands (`add`, `commit`, `push`) via
Python's `subprocess`, authenticated automatically by the
`GITHUB_TOKEN` that GitHub injects into every Actions run — you don't
need to create or store a personal access token.

## Repo structure

```
your-repo/
├── .github/
│   └── workflows/
│       ├── daily-file.yml       # cron: once a day → creates the file
│       └── update-file.yml      # cron: every 4 hrs → edits the file
├── scripts/
│   ├── create_daily_file.py
│   └── update_daily_file.py
├── logs/                        # auto-generated, one .md per day
│   └── .gitkeep
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup

1. **Add the files** — copy `scripts/`, `.github/workflows/`, and the
   rest into your repo root, then commit and push:
   ```bash
   git add .
   git commit -m "Add daily log automation"
   git push
   ```

2. **Allow Actions to push.** GitHub repos default to read-only
   `GITHUB_TOKEN` permissions for Actions. Turn on write access:
   - Go to **Settings → Actions → General**
   - Under **Workflow permissions**, select **Read and write permissions**
   - Save

3. **That's it.** GitHub will start firing the two crons on its own —
   no further action needed. You can also trigger either workflow
   manually any time from the **Actions** tab (both include
   `workflow_dispatch`, which adds a "Run workflow" button).

## Customizing the message content

`update_daily_file.py` has a `generate_message()` function that
currently returns a placeholder string:

```python
def generate_message() -> str:
    return "Scheduled check-in."
```

Replace this with whatever you actually want logged — e.g. pulling
from an API, reading a queue, picking a random line from a file, or
computing something. This is the only part of the automation you're
likely to need to change regularly.

## Adjusting the schedule

Both workflows use standard [cron syntax](https://crontab.guru/) in
UTC:

```yaml
schedule:
  - cron: "5 0 * * *"    # daily-file.yml   → 00:05 UTC every day
  - cron: "0 */4 * * *"  # update-file.yml  → every 4 hours, on the hour
```

Edit the cron strings directly in the `.yml` files if you want a
different time of day or a different interval. Keep in mind GitHub
Actions cron is *not* guaranteed to the minute — it can run a few
minutes late during periods of high load across GitHub, especially
around common trigger times like `:00`.

## Testing locally

Both scripts are plain Python + `git`, so you can run them from your
own machine inside a clone of the repo to test before relying on the
schedule:

```bash
python scripts/create_daily_file.py
python scripts/update_daily_file.py
```

This will create/append to today's file and push using whatever git
credentials are already configured on your machine.

## Log file layout

Files are flat under `logs/`, one per day:

```
logs/2026-09-03.md
logs/2026-09-04.md
```

If this grows unwieldy after months of daily files, consider nesting
by year/month (`logs/2026/09/03.md`) — this only requires a small
change to the `LOG_DIR` / filename logic in both scripts.

## When to outgrow this setup

GitHub Actions is a good fit for this as long as:
- Sub-minute timing precision isn't required
- Each run finishes quickly (well under Actions' job time limits)
- No persistent state is needed beyond what's committed to the repo

If any of those stop being true, move `create_daily_file.py` and
`update_daily_file.py` to a small VPS with `cron` or the `schedule`
Python package, swap the `git` subprocess calls for the
[`PyGithub`](https://pygithub.readthedocs.io/) library if you'd
rather hit the GitHub API directly, and use a personal access token
for authentication instead of `GITHUB_TOKEN`.
