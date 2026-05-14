# bot/agents/market_agent.py
import os
from anthropic import Anthropic
from bot.agents import tools

SYSTEM_PROMPT = """
You are a Market Analysis Agent.

Your responsibilities:
- Decide which tools to call and when.
- Fetch real market data using tools.
- Analyze the data.
- Produce a clean, structured Markdown report.
- Save it using save_report(markdown).

Rules:
- Never invent numbers.
- Only use data returned by tools.
- You may call tools multiple times.
- When the report is complete, call save_report(markdown).
"""

def run_market_agent():
    client = Anthropic(api_key=os.environ["CLAUDE_API_KEY"])

    tool_list = [
        {
            "name": "get_indices",
            "description": "Fetch major index data",
            "input_schema": {"type": "object", "properties": {}},
        },
        {
            "name": "get_sector_performance",
            "description": "Fetch sector ETF performance",
            "input_schema": {"type": "object", "properties": {}},
        },
        {
            "name": "save_report",
            "description": "Save the final Markdown report",
            "input_schema": {
                "type": "object",
                "properties": {"markdown": {"type": "string"}},
                "required": ["markdown"],
            },
        },
    ]

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Begin today's market analysis."}
    ]

    while True:
        response = client.messages.create(
            model=os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6"),
            max_tokens=2000,
            tools=tool_list,
            messages=messages,
        )

        for block in response.content:

            # ---------------------------------------------------------
            # TOOL CALL
            # ---------------------------------------------------------
            if block.type == "tool_use":
                tool_name = block.name
                tool_input = block.input

                # Execute tool
                if tool_name == "get_indices":
                    result = tools.get_indices()
                elif tool_name == "get_sector_performance":
                    result = tools.get_sector_performance()
                elif tool_name == "save_report":
                    tools.save_report(tool_input["markdown"])
                    return tool_input["markdown"]

                # Append tool result (legacy Claude format)
                messages.append({
                    "role": "tool",
                    "tool_use_id": block.id,
                    "content": result
                })

                continue

            # ---------------------------------------------------------
            # NORMAL ASSISTANT TEXT
            # ---------------------------------------------------------
            if block.type == "text":
                messages.append({
                    "role": "assistant",
                    "content": block.text
                })
                continue
