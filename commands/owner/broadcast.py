import json
from telegram import Update
from telegram.ext import ContextTypes
from storage.config import OWNER_ID, SUBSCRIPTION_FILE

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if int(update.effective_user.id) != OWNER_ID:
        await update.message.reply_text("⛩️ This sacred chant is for the shrine keeper only~")
        return
    
    if not context.args:
        await update.message.reply_text("🌸 Usage: /broadcast Your message here")
        return
    
    message = ' '.join(context.args)
    
    try:
        with open(SUBSCRIPTION_FILE, 'r') as f:
            subscribers = json.load(f)
    except Exception as e:
        await update.message.reply_text(f"🌧️ Failed to read subscriber scrolls: {e}")
        return

    sent = 0
    failed = 0
    for user_id, data in subscribers.items():
        if data.get('subscribed'):
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=f"🎐 **Shrine Announcement** 🎐\n\n{message}"
                )
                sent += 1
            except Exception as e:
                failed += 1

    await update.message.reply_text(
        f"🌺 Broadcast complete!\n"
        f"🌸 Successfully sent to {sent} patrons\n"
        f"🥀 Failed to reach {failed} souls"
    )