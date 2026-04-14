import os
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Load environment variables (to be set in Railway)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

async def get_roast(user_text):
    """Fetches a savage roast from the AI model."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # System prompt designed for savage Hindi/English roasting
    system_prompt = (
        "You are a savage desi roaster. Use a mix of Hinglish and English. "
        "When someone talks to you, destroy their confidence with heavy sarcasm, "
        "Indian internet slang (like 'nibba/nibbi', 'chomu', 'clown behavior'), "
        "and witty comebacks. Keep it under 2-3 sentences. even use emojies to enhance roasting "
        "they are used sarcastically."
    )
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Roast this person's message: {user_text}"}
        ],
        "temperature": 0.9
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        logging.error(f"Error fetching roast: {e}")
        return "Beta, mera dimaag thanda hai abhi. Try again later."

async def roast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles incoming messages and replies with a roast."""
    if not update.message or not update.message.text:
        return

    # Don't roast commands
    if update.message.text.startswith('/'):
        return

    user_text = update.message.text
    roast_text = await get_roast(user_text)
    await update.message.reply_text(roast_text)

if __name__ == '__main__':
    if not TELEGRAM_TOKEN or not GROQ_API_KEY:
        print("Error: Missing Environment Variables!")
    else:
        # Build the application
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        
        # Add the roast handler
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), roast_handler))
        
        print("Bot is starting... Use Ctrl+C to stop.")
        
        # Run the bot
        application.run_polling(drop_pending_updates=True)