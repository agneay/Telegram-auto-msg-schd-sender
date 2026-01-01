import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not set in .env")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    name = update.message.from_user.first_name or "there"

    await update.message.reply_text(
        f"✅ Registration successful!\n\n"
        f"Hello {name} 👋\n"
        f"Your chat_id is:\n"
        f"{chat_id}"
    )

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))

print("🤖 Bot running. Ask users to press /start")
app.run_polling()
