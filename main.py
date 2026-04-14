import os
import logging
import requests
import certifi
from datetime import datetime
from pymongo import MongoClient
from telegram import Update
from telegram.constants import ParseMode
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

# Database Initialization with SSL Fix (certifi)
try:
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client['savage_zyrex_db']
    users_col = db['users']
    client.admin.command('ping')
    logging.info("MongoDB Connection Successful")
except Exception as e:
    logging.error(f"MongoDB Connection Failed: {e}")

async def get_roast(user_text):
    """Calls Groq API for a savage Hinglish roast."""
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    system_prompt = (
        "You are Savage Zyrex, a brutal desi roaster. Speak in Hinglish (Hindi + English). "
        "Be mean, sarcastic, and witty. Use Indian slang like 'chomu', 'nibba', 'clown'. "
        "The user is trash, remind them of that. Keep it to 1-2 punchy sentences."
    )
    
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Roast this person's message: {user_text}"}
        ],
        "temperature": 1.0
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        logging.error(f"Groq API Error: {e}")
        return "Beta, dimaag thanda rakh. AI thak gaya hai teri baatein sun ke."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Saves user details on /start."""
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
    await update.message.reply_text("Savage Zyrex is ONLINE. Kuch likh, taaki main teri bezatti kar sakun.")

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin only: check user count and info."""
    if update.effective_user.id != ADMIN_ID:
        return
    
    total_users = users_col.count_documents({})
    recent_users = users_col.find().sort("last_seen", -1).limit(10)
    
    report = f"📊 **Savage Stats**\n\nTotal Victims: {total_users}\n\n**Recent Targets:**\n"
    for u in recent_users:
        name = u.get('first_name') or "Unknown"
        username = f"(@{u.get('username')})" if u.get('username') else "(No Username)"
        report += f"• {name} {username}\n"
    
    await update.message.reply_text(report, parse_mode=ParseMode.MARKDOWN)

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Admin only: Broadcast message to all users."""
    if update.effective_user.id != ADMIN_ID:
        return

    if not context.args:
        await update.message.reply_text("Usage: /broadcast [Your message]")
        return

    broadcast_msg = " ".join(context.args)
    all_users = users_col.find({}, {"user_id": 1})
    
    success, fail = 0, 0
    await update.message.reply_text("📢 Starting Broadcast...")

    for user in all_users:
        try:
            await context.bot.send_message(chat_id=user['user_id'], text=broadcast_msg)
            success += 1
        except Exception:
            fail += 1

    await update.message.reply_text(
        f"✅ Broadcast Sent: {success}\n❌ Failed: {fail} (Blocked/Inactive)"
    )

async def roast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Roasts incoming text and UPDATES user info to prevent 'None' in stats."""
    if not update.message or not update.message.text or update.message.text.startswith('/'):
        return

    user = update.effective_user
    # Force update user info every time they speak to ensure stats are accurate
    users_col.update_one(
        {"user_id": user.id},
        {"$set": {
            "first_name": user.first_name,
            "username": user.username,
            "last_seen": datetime.now()
        }},
        upsert=True
    )
    
    roast_text = await get_roast(update.message.text)
    await update.message.reply_text(roast_text)

if __name__ == '__main__':
    if not all([TELEGRAM_TOKEN, GROQ_API_KEY, MONGO_URI]):
        print("MISSING CONFIG: Please check your environment variables.")
    else:
        app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("stats", admin_stats))
        app.add_handler(CommandHandler("broadcast", broadcast))
        app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), roast_handler))
        
        print("Savage Zyrex V4 is UP and ROASTING...")
        app.run_polling(drop_pending_updates=True)
