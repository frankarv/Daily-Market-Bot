# 📈 Daily Market Intelligence Bot

The **Daily Market Intelligence Bot** is an automated GitHub Actions workflow that generates a concise, AI‑powered market summary every weekday morning. It fetches live market data, sends it to Claude for analysis, and posts the final report to your preferred channel (Discord or Slack).

The bot runs **Monday–Friday at 6:00 AM MST** using GitHub Actions’ scheduled workflows.

---

## 🚀 Features

- Fetches daily market data (indices, sectors, volatility, macro events)
- Generates a structured market summary using **Claude (Anthropic API)**
- Posts the report to **Discord** or **Slack** via webhook
- Optionally commits the generated `market-report.md` back to the repo
- Fully automated — no servers, no cron jobs, no manual steps

---

## 🧠 How It Works

1. GitHub Actions starts the workflow on a schedule or manual trigger  
2. Python environment is created and dependencies are installed  
3. The bot gathers market data  
4. A prompt is sent to Claude using the Anthropic API  
5. Claude returns a formatted market summary  
6. The bot posts the summary to Discord/Slack  
7. (Optional) The report is committed to the repository

---

## 🔧 Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/Daily-Market-Bot
```

### 2. Add your secrets in GitHub
Go to:

**Settings → Secrets and variables → Actions**

Add:

- `CLAUDE_API_KEY` — your Anthropic API key  
- `DISCORD_WEBHOOK_URL` or `SLACK_WEBHOOK_URL`  

### 3. Install dependencies locally (optional)
```bash
pip install -r bot/requirements.txt
```

### 4. Run the bot locally (optional)
```bash
python bot/main.py
```

---

## 🕒 Schedule

The workflow runs automatically:

```
0 13 * * 1-5
```

This corresponds to **13:00 UTC**, which is **6:00 AM MST**, Monday through Friday.

You can also run it manually from the **Actions** tab.

---

## 📄 Generated Output

Each run produces:

- A Discord/Slack message  
- A `market-report.md` file (optional commit)

Example sections include:

- Market overview  
- Sector performance  
- Macro events  
- AI‑generated insights  

---

## 🛠️ File Structure

```
Daily-Market-Bot/
├── bot/
│   ├── main.py
│   ├── requirements.txt
│   └── utils/
├── market-report.md (generated)
└── .github/
    └── workflows/
        └── daily-market.yml
```

---

## 🤝 Contributing

Pull requests are welcome!  
Feel free to open issues for improvements, new data sources, or additional output formats.
