from telegram import Update
from telegram.ext import ContextTypes
from storage.config import OWNER_ID

async def sample_news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    
    await update.message.reply_text(
        "🌸 **Sample News Format** 🌸\n\n"
        "Please visit our news channel:\n"
        "[@Animes_News_Ocean](https://t.me/Animes_News_Ocean)\n"
        "to see live news examples! 🌊\n\n"
        "—— You'll need to join the channel first ——",
        parse_mode="Markdown",
        disable_web_page_preview=True
    )