import os
import logging
import requests
from datetime import datetime
from pymongo import MongoClient
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters

# Setup Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Configuration from Environment Variables
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# Database Initialization
client = MongoClient(MONGO_URI)
db = client['savage_zyrex_db']
users_col = db['users']

async def get_roast(user_text):
    """Calls Groq API for a savage Hinglish roast."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # The 'Brain' of Savage Zyrex
    system_prompt = (
        "You are Savage Zyrex, a brutal desi roaster. Speak in Hinglish (Hindi + English). "
        "Be mean, sarcastic, and extremely witty. Use Indian internet slang like 'chomu', 'nibba', 'clown'. "
        "The user is trash, remind them of that. Keep it to 1-2 punchy sentences."
    )
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Roast this person's message: {user_text}"}
        ],
        "temperature": 1.0  # High temperature for more creative insults
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        logging.error(f"Groq API Error: {e}")
        return "Beta, mera dimaag thanda hai ya tera internet tatti. Try again later."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Greets the user and saves them to the database."""
    user = update.effective_user
    users_col.update_one(
        {"user_id": user.id},
        {"$set": {
            "username": user.username,
            "first_name": user.first_name,
            "last_seen": datetime.now()
        }},
        upsert=True
    )
    await update.message.reply_text("Savage Zyrex is here. Himmat hai toh kuch bol, varna rasta naap.")

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin only: check user count and info."""
    if update.effective_user.id != ADMIN_ID:
        return # Ignore non-admins
    
    total_users = users_col.count_documents({})
    recent_users = users_col.find().sort("last_seen", -1).limit(10)
    
    report = f"📊 **Bot Status Report**\n\nTotal Users Trapped: {total_users}\n\n**Latest Victims:**\n"
    for u in recent_users:
        report += f"• {u.get('first_name')} (@{u.get('username', 'N/A')})\n"
    
    await update.message.reply_text(report, parse_mode='Markdown')

async def roast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Roasts every incoming text message."""
    if not update.message or not update.message.text or update.message.text.startswith('/'):
        return

    user = update.effective_user
    # Log activity
    users_col.update_one({"user_id": user.id}, {"$set": {"last_seen": datetime.now()}}, upsert=True)
    
    roast_text = await get_roast(update.message.text)
    await update.message.reply_text(roast_text)

if __name__ == '__main__':
    if not all([TELEGRAM_TOKEN, GROQ_API_KEY, MONGO_URI]):
        print("CRITICAL ERROR: Missing environment variables! Check MONGO_URI, TELEGRAM_TOKEN, and GROQ_API_KEY.")
    else:
        # Build and start the bot
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("stats", admin_stats))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), roast_handler))
        
        print("Savage Zyrex is ONLINE and ready to roast...")
        app.run_polling(drop_pending_updates=True)
