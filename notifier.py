"""Scrapes every category that has at least one Telegram subscriber,
diffs the results against the previous snapshot, and messages
subscribers about newly-posted jobs.

Meant to run on a schedule (see .github/workflows/notify.yml). The first
time a category is scraped there's no previous snapshot to diff against,
so that run just establishes a baseline — nobody gets spammed with every
job currently listed.
"""
import json
import sys
from pathlib import Path

import requests

from bot import BOT_TOKEN, API_URL, SUBSCRIBERS_FILE
from scraper import CATEGORIES, scrape_category

DATA_DIR = Path(__file__).parent / "data"
SNAPSHOTS_DIR = DATA_DIR / "snapshots"


def load_subscribers():
    if not SUBSCRIBERS_FILE.exists():
        return {}
    with open(SUBSCRIBERS_FILE, encoding="utf-8") as f:
        return json.load(f).get("subscribers", {})


def snapshot_path(category_index):
    return SNAPSHOTS_DIR / f"category_{category_index}.json"


def load_snapshot(category_index):
    path = snapshot_path(category_index)
    if not path.exists():
        return None  # no baseline yet, distinct from an empty {} snapshot
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_snapshot(category_index, jobs):
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(snapshot_path(category_index), "w", encoding="utf-8") as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)


def send_message(chat_id, text):
    try:
        requests.post(
            f"{API_URL}/sendMessage",
            json={"chat_id": chat_id, "text": text, "disable_web_page_preview": True},
            timeout=15,
        )
    except requests.RequestException as e:
        print(f"failed to send message to {chat_id}: {e}")


def format_job(job):
    lines = [job.get("job_position", "Untitled"), job.get("job_company", "")]
    if job.get("job_url"):
        lines.append(job["job_url"])
    return "\n".join(line for line in lines if line)


def main():
    if not BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN is not set", file=sys.stderr)
        sys.exit(1)

    subscribers = load_subscribers()

    # invert chat_id -> [categories] into category -> [chat_ids] so each
    # category is scraped once no matter how many people subscribe to it
    subscribed_categories = {}
    for chat_id, prefs in subscribers.items():
        for cat in prefs.get("categories", []):
            subscribed_categories.setdefault(cat, []).append(chat_id)

    if not subscribed_categories:
        print("no active subscriptions, nothing to do")
        return

    for cat_index, chat_ids in subscribed_categories.items():
        name = CATEGORIES[cat_index]["name"]
        print(f"category {cat_index} ({name}): {len(chat_ids)} subscriber(s)")

        jobs = scrape_category(cat_index)
        previous = load_snapshot(cat_index)

        if previous is None:
            print("no previous snapshot, establishing baseline (no notifications sent)")
        else:
            new_urls = set(jobs) - set(previous)
            print(f"{len(new_urls)} new job(s)")
            for url in new_urls:
                text = f"New job posting ({name}):\n\n{format_job(jobs[url])}"
                for chat_id in chat_ids:
                    send_message(chat_id, text)

        save_snapshot(cat_index, jobs)


if __name__ == "__main__":
    main()
