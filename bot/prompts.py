def build_market_prompt(market_data: dict) -> str:
    return f"""
You are a professional macro and market analyst.

Here is current index data in JSON:

{market_data}

Tasks:
1. Summarize overall market tone (risk-on / risk-off).
2. Comment on each index (S&P 500, Nasdaq, Dow, Russell 2000, VIX).
3. Highlight notable divergences or risk signals.
4. Provide a concise TL;DR (3 sentences max) at the top.

Format your answer in Markdown.
"""
