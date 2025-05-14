from telegram import Update
from telegram.ext import ContextTypes
from storage.config import OWNER_ID

async def tutorial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.effective_user.id) != OWNER_ID:
        await update.message.reply_text("💃 These dance steps are still secret~")
        return
    
    await update.message.reply_text(
        "\n▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
        "🌸 **Mizuki's Dance Tutorial** 🌸\n\n"
        "1. Start the journey with `/start`\n"
        "2. Check your personal dashboard with `/dashboard`\n"
        "3. Unlock exclusive features by subscribing using `/subscribe`\n"
        "4. To let Mizuki post on your channel, activate it with `/start_news`\n"
        "5. To stop posting, simply use `/stop_news`\n\n"
        "💡 For further assistance, use `/help <command>` to learn more!\n"
        "▰▰▰▰▰▰▰▰▰▰▰▰▰\n",
        parse_mode='Markdown'
    )
