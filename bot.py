"""Telegram bot: lets users subscribe to job categories.

Meant to run as a short-lived process on a schedule (see
.github/workflows/telegram-bot.yml) — each run polls Telegram once for
any messages sent since the last run, processes commands, persists
subscriber state to data/subscribers.json, and exits.

Commands:
    /start, /help        show usage
    /categories           list all job categories with their index
    /subscribe <n>         subscribe to category n
    /unsubscribe <n>       unsubscribe from category n
    /mysubs                list your current subscriptions
"""
import json
import os
import sys
from pathlib import Path

import requests

from scraper import CATEGORIES

DATA_DIR = Path(__file__).parent / "data"
SUBSCRIBERS_FILE = DATA_DIR / "subscribers.json"

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


def load_state():
    if SUBSCRIBERS_FILE.exists():
        with open(SUBSCRIBERS_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"last_update_id": 0, "subscribers": {}}


def save_state(state):
    DATA_DIR.mkdir(exist_ok=True)
    with open(SUBSCRIBERS_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def send_message(chat_id, text):
    try:
        requests.post(
            f"{API_URL}/sendMessage",
            json={"chat_id": chat_id, "text": text},
            timeout=15,
        )
    except requests.RequestException as e:
        print(f"failed to send message to {chat_id}: {e}")


def categories_text():
    return "\n".join(f"{i} - {c['name']}" for i, c in enumerate(CATEGORIES))


def handle_command(state, chat_id, text):
    chat_id = str(chat_id)
    parts = text.strip().split(maxsplit=1)
    cmd = parts[0].lower().split("@")[0]  # strip /cmd@BotName form
    arg = parts[1].strip() if len(parts) > 1 else ""

    subs = state["subscribers"].setdefault(chat_id, {"categories": []})

    if cmd in ("/start", "/help"):
        send_message(
            chat_id,
            "Welcome to JobsGeScraper bot!\n\n"
            "Commands:\n"
            "/categories - list job categories\n"
            "/subscribe <n> - subscribe to a category\n"
            "/unsubscribe <n> - unsubscribe from a category\n"
            "/mysubs - show your subscriptions\n\n"
            "You'll get a message whenever a new job is posted in a "
            "category you're subscribed to.",
        )

    elif cmd == "/categories":
        send_message(chat_id, categories_text())

    elif cmd == "/subscribe":
        if not arg.isdigit() or not (0 <= int(arg) < len(CATEGORIES)):
            send_message(chat_id, f"Usage: /subscribe <n>\n\n{categories_text()}")
            return
        n = int(arg)
        if n not in subs["categories"]:
            subs["categories"].append(n)
        send_message(chat_id, f"Subscribed to: {CATEGORIES[n]['name']}")

    elif cmd == "/unsubscribe":
        if not arg.isdigit() or not (0 <= int(arg) < len(CATEGORIES)):
            send_message(chat_id, f"Usage: /unsubscribe <n>\n\n{categories_text()}")
            return
        n = int(arg)
        if n in subs["categories"]:
            subs["categories"].remove(n)
            send_message(chat_id, f"Unsubscribed from: {CATEGORIES[n]['name']}")
        else:
            send_message(chat_id, f"You weren't subscribed to: {CATEGORIES[n]['name']}")

    elif cmd == "/mysubs":
        if not subs["categories"]:
            send_message(
                chat_id, "You have no subscriptions yet. Use /categories then /subscribe <n>."
            )
        else:
            names = "\n".join(f"{i} - {CATEGORIES[i]['name']}" for i in sorted(subs["categories"]))
            send_message(chat_id, f"Your subscriptions:\n{names}")

    else:
        send_message(chat_id, "Unknown command. Try /help")


def main():
    if not BOT_TOKEN:
        print("TELEGRAM_BOT_TOKEN is not set", file=sys.stderr)
        sys.exit(1)

    state = load_state()
    resp = requests.get(
        f"{API_URL}/getUpdates",
        params={"offset": state["last_update_id"] + 1, "timeout": 0},
        timeout=30,
    )
    resp.raise_for_status()
    updates = resp.json().get("result", [])

    for update in updates:
        state["last_update_id"] = update["update_id"]
        message = update.get("message")
        if not message or "text" not in message:
            continue
        handle_command(state, message["chat"]["id"], message["text"])

    save_state(state)
    print(f"processed {len(updates)} update(s)")


if __name__ == "__main__":
    main()
