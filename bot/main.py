import os
import json
import requests

from anthropic import Anthropic
from bot.market_data import fetch_index_snapshot
from bot.prompts import build_market_prompt
from bot.agents.market_agent import run_market_agent

CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


def post_to_discord(content: str):
    webhook = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook:
        print("No Discord webhook set.")
        return
    payload = {"content": content[:1900]}  # Discord limit safety
    r = requests.post(webhook, json=payload)
    r.raise_for_status()


def post_to_slack(text: str):
    if not SLACK_WEBHOOK_URL:
        print("No SLACK_WEBHOOK_URL set; skipping Slack.")
        return
    payload = {"text": text}
    r = requests.post(SLACK_WEBHOOK_URL, json=payload)
    r.raise_for_status()


def main():
    report = run_market_agent()
    post_to_discord(report)
    print("Generated report:\n")
    print(report)


if __name__ == "__main__":
    main()
