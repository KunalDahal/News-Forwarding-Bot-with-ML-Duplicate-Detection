import os
import sys
from telegram import Update
from telegram.ext import ContextTypes
from storage.config import OWNER_ID

async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if int(update.effective_user.id) != OWNER_ID:
        await update.message.reply_text("🌸 Only the gardener can perform this ritual~")
        return
    
    await update.message.reply_text("🌸 Beginning rebirth ritual...")
    
    # Close application
    await context.application.stop()
    
    # Restart script
    os.execl(sys.executable, sys.executable, *sys.argv)