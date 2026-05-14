import os
import json
from market_data import fetch_index_snapshot
from prompts import build_market_prompt
import requests

# Example using anthropic-style client; adjust to your actual Claude SDK.
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
#SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")  # optional
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")  # optional

def call_claude(prompt: str) -> str:
    client = Anthropic(api_key=os.environ["CLAUDE_API_KEY"])
    resp = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1200,
        messages=[{"role": "user", "content": prompt}],
    )
    # Adjust depending on SDK response shape
    return resp.content[0].text

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

def save_markdown_report(report: str, path: str = "market-report.md"):
    with open(path, "w", encoding="utf-8") as f:
        f.write(report)

def main():
    market_data = fetch_index_snapshot()
    prompt = build_market_prompt(json.dumps(market_data, indent=2))
    report_md = call_claude(prompt)

    # Save to file (can be committed by the workflow if you want)
    save_markdown_report(report_md)
    # Optional: send to Slack
    #post_to_slack(report_md[:3500])  # Slack message length safety
    # send to discord
    post_to_discord(report_md)

if __name__ == "__main__":
    main()
