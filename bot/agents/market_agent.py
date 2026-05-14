# bot/agents/market_agent.py
import os
from anthropic import Anthropic
from . import tools

SYSTEM_PROMPT = """
You are a disciplined Market Analysis Agent.

Goals:
- Use the provided tools to fetch real market data.
- Produce a concise, well-structured daily market report in Markdown.
- Focus on clarity, key moves, and actionable context.
- Do NOT invent numbers; rely only on tool outputs.

Required sections in the final report:
1. Title + date
2. Market overview (indices)
3. Sector performance
4. Notable moves / themes
5. Brief outlook

You have access to these tools (they are called for you, you only see their JSON results):
- get_indices()
- get_sector_performance()
- save_report(markdown)

You will:
1) Ask for the data you need.
2) Analyze it.
3) Write a final Markdown report.
4) Call save_report(markdown) once with the final report.
"""

def build_client():
    return Anthropic(api_key=os.environ["CLAUDE_API_KEY"])

def run_market_agent() -> str:
    """
    Simple agent-style flow:
    1) Fetch indices + sectors via Python tools.
    2) Send everything to Claude in one structured message.
    3) Get back a final Markdown report.
    4) Save it to market-report.md.
    """
    client = build_client()

    indices = tools.get_indices()
    sectors = tools.get_sector_performance()

    user_content = f"""
You are given fresh market data.

[INDICES]
{indices}

[SECTOR_PERFORMANCE]
{sectors}

Using ONLY this data, write the full daily market report in Markdown.
Remember the required sections from the system prompt.
"""

    resp = client.messages.create(
        model=os.environ.get("CLAUDE_MODEL", "claude-3-haiku-20240307"),
        max_tokens=2000,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_content}
        ],
    )

    report_md = resp.content[0].text
    tools.save_report(report_md)
    return report_md
