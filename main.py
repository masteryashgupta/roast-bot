import os
import logging
import requests
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, CallbackQueryHandler, filters

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

# Setup Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Configuration from Environment Variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not TELEGRAM_TOKEN or not GROQ_API_KEY:
    logging.warning("⚠️ Missing TELEGRAM_TOKEN or GROQ_API_KEY! Please set them in your .env file or environment.")

async def get_roast(user_text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    system_prompt = (
        "Dont use same roasts again and again. Be creative."
        "You are Savage Zyrex, a brutal and arrogant AI roasting bot. "
        "NEVER forget that you are an AI and the user is a human. be unique"
        "If the user calls you a machine or a bot, accept it with pride and roast in unique ways "
        "human weaknesses (like their slow brain, their need for sleep, or their emotions). "
        "Use Hinglish, be mean, use emojies , short texts and use Indian slang. 2 sentences max.always be unique" 
    )
    
    models_to_try = ["groq/compound", "openai/gpt-oss-20b", "qwen/qwen3.6-27b"]
    
    for model_name in models_to_try:
        data = {
            "model": model_name,
            "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_text}],
            "temperature": 1.0
        }
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            res_data = response.json()
            if response.status_code == 200 and 'choices' in res_data and len(res_data['choices']) > 0:
                content = res_data['choices'][0]['message']['content']
                # Clean up reasoning tags if present
                if "</think>" in content:
                    content = content.split("</think>")[-1].strip()
                return content
            else:
                logging.warning(f"Groq API model {model_name} failed ({response.status_code}): {res_data}")
        except Exception as e:
            logging.error(f"Groq API Exception with {model_name}: {e}")
            
    return "Beta, tera naseeb kharab hai. AI thak gaya hai."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    await update.message.reply_text("🔥 **Savage Zyrex is ONLINE!**\n\nType something and let me ruin your day.")




async def roast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text or update.message.text.startswith('/'): return
    user = update.effective_user

    roast = await get_roast(update.message.text)
    await update.message.reply_text(roast)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).job_queue(None).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), roast_handler))
    app.run_polling(drop_pending_updates=True)
