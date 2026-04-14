# Savage Roast Telegram Bot

A Telegram bot that roasts users in Hindi/English using Llama 3 via Groq.

## Deployment Instructions

### 1. Get API Keys
- **Telegram:** Create a bot via @BotFather and get the token.
- **AI Brain:** Go to [Groq Cloud](https://console.groq.com/) and create a free API Key.

### 2. GitHub Upload
- Create a new repository on GitHub.
- Upload these files (`main.py`, `requirements.txt`, `Procfile`).

### 3. Railway Deployment
- Connect your GitHub repo to Railway.app.
- In the **Variables** tab, add:
  - `TELEGRAM_TOKEN`: (Your Bot Token)
  - `GROQ_API_KEY`: (Your Groq API Key)
- Railway will automatically detect the `requirements.txt` and `Procfile` and start the bot.
