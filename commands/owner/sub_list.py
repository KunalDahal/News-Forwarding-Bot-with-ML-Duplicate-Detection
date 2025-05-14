import json
from telegram import Update
from telegram.ext import ContextTypes
from storage.config import OWNER_ID, SUBSCRIPTION_FILE

async def sub_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if int(update.effective_user.id) != OWNER_ID:
        await update.message.reply_text("🔒 These patron records are sealed~")
        return
    
    try:
        with open(SUBSCRIPTION_FILE, 'r') as f:
            subscribers = json.load(f)
    except Exception as e:
        await update.message.reply_text(f"🌧️ Failed to read patron scrolls: {e}")
        return

    if not subscribers:
        await update.message.reply_text("🌸 The patron garden is empty...")
        return

    response = ["🌸 **Patron Blossom List** 🌸\n"]
    for user_id, data in subscribers.items():
        if data.get('subscribed'):
            line = f"▫️ {data.get('username', 'Unknown')} "
            line += f"(ID: {user_id}) "
            line += f"| Channel: {data.get('channel', 'Not set')}"
            response.append(line)

    await update.message.reply_text('\n'.join(response[:20]))  # Prevent message too long