# Roast Bot

![npm version](https://img.shields.io/npm/v/roast-bot)
![npm downloads](https://img.shields.io/npm/dt/roast-bot)
![license](https://img.shields.io/npm/l/roast-bot)

An unfiltered roast bot. Chat for fun in the terminal, completely unfiltered. Powered by the Groq API.

## Usage

You can run Roast Bot instantly without installing anything globally:

```bash
npx roast-bot
```

Or, install it globally:

```bash
npm install -g roast-bot
roast-bot
```

### First-Time Setup
On your first run, you will be prompted to paste your Groq API Key (get one for free at [console.groq.com](https://console.groq.com)). The key will be securely saved in your local configuration (`~/.roast-bot-rc`) so you only have to do this once.

To update or reset your key later, run:
```bash
npx roast-bot --set-key
```

## Features
- **Savage Personality**: Brutal, arrogant, Hinglish, emojis, Indian slang.
- **Terminal Aesthetics**: Colored chat loop with a sleek startup banner.
- **Smart Context**: Remembers the last few messages for contextual roasting.
- **No Heavy Dependencies**: Lightweight and fast.
- **Model Fallbacks**: Automatically falls back if the primary model is busy.

## License
MIT
