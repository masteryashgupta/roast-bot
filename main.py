import os
import logging
import requests
import certifi
from datetime import datetime
from pymongo import MongoClient
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, CallbackQueryHandler, filters

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
CHANNEL_ID = os.getenv("CHANNEL_ID") # e.g., @SavageZyrexAnnouncements

# Database Initialization
try:
    client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
    db = client['savage_zyrex_db']
    users_col = db['users']
    client.admin.command('ping')
    logging.info("MongoDB Connection Successful")
except Exception as e:
    logging.error(f"MongoDB Connection Failed: {e}")

async def is_subscribed(bot, user_id):
    """Checks if the user is a member of the required channel."""
    if not CHANNEL_ID:
        return True
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['creator', 'administrator', 'member']
    except Exception as e:
        logging.error(f"Subscription check error: {e}")
        return False

def get_join_keyboard():
    """Creates a professional join button keyboard."""
    channel_url = f"https://t.me/{CHANNEL_ID.replace('@', '')}"
    keyboard = [
        [InlineKeyboardButton("📢 Join Channel", url=channel_url)],
        [InlineKeyboardButton("✅ I have joined!", callback_data="check_join")]
    ]
    return InlineKeyboardMarkup(keyboard)

async def get_roast(user_text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    system_prompt = (
        "You are Savage Zyrex, a brutal and arrogant AI roasting bot. "
        "NEVER forget that you are an AI and the user is a human. "
        "If the user calls you a machine or a bot, accept it with pride and roast their "
        "human weaknesses (like their slow brain, their need for sleep, or their emotions). "
        "Use Hinglish, be mean, use emojies , short texts and use Indian slang. 2 sentences max." 
    )
    data = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_text}],
        "temperature": 1.0
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)
        return response.json()['choices'][0]['message']['content']
    except:
        return "Beta, tera naseeb kharab hai. AI thak gaya hai."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Force Subscribe Check
    if not await is_subscribed(context.bot, user.id):
        await update.message.reply_text(
            f"✋ **Wait a minute, Chomu!**\n\nYou must join our official channel to unlock Savage Zyrex.",
            reply_markup=get_join_keyboard(),
            parse_mode=ParseMode.MARKDOWN
        )
        return

    # Update User Info
    users_col.update_one(
        {"user_id": user.id},
        {"$set": {"username": user.username, "first_name": user.first_name, "last_seen": datetime.now()}},
        upsert=True
    )
    await update.message.reply_text("🔥 **Savage Zyrex is ONLINE!**\n\nType something and let me ruin your day.")

async def join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the 'I have joined' button click."""
    query = update.callback_query
    await query.answer()
    
    if await is_subscribed(context.bot, query.from_user.id):
        await query.edit_message_text("✅ **Access Granted!**\n\nNow send me a message and get ready to be roasted.")
    else:
        await query.message.reply_text("❌ **Nice try!** But you haven't joined yet. Join @zyrex_announcements first.")

async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    total = users_col.count_documents({})
    recent = users_col.find().sort("last_seen", -1).limit(10)
    report = f"📊 **Stats Report**\nTotal Victims: {total}\n\n**Recent:**\n"
    for u in recent:
        report += f"• {u.get('first_name')} (@{u.get('username', 'N/A')})\n"
    await update.message.reply_text(report, parse_mode=ParseMode.MARKDOWN)

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID or not context.args: return
    msg = " ".join(context.args)
    users = users_col.find({}, {"user_id": 1})
    s, f = 0, 0
    for u in users:
        try:
            await context.bot.send_message(chat_id=u['user_id'], text=msg)
            s += 1
        except: f += 1
    await update.message.reply_text(f"✅ Sent: {s}\n❌ Failed: {f}")

async def roast_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text or update.message.text.startswith('/'): return
    user = update.effective_user

    # Force Subscribe Check
    if not await is_subscribed(context.bot, user.id):
        await update.message.reply_text("🚫 Join our channel to use this bot!", reply_markup=get_join_keyboard())
        return

    users_col.update_one(
        {"user_id": user.id},
        {"$set": {"first_name": user.first_name, "username": user.username, "last_seen": datetime.now()}},
        upsert=True
    )
    roast = await get_roast(update.message.text)
    await update.message.reply_text(roast)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", admin_stats))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(join_callback, pattern="check_join"))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), roast_handler))
    app.run_polling(drop_pending_updates=True)
