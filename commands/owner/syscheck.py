import psutil
from telegram import Update
from telegram.ext import ContextTypes
from storage.config import OWNER_ID

async def syscheck(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if int(update.effective_user.id) != OWNER_ID:
        await update.message.reply_text("🌸 Ara~! This bloom is for the gardener only~ 🌼")
        return
    
    # Get system stats
    cpu_percent = psutil.cpu_percent()
    mem = psutil.virtual_memory()
    
    response = (
        "\n▰▰▰▰▰▰▰▰▰▰▰▰▰\n" 
        "🌸 *Shrine System Status* 🌸\n\n"
        f"💻 *CPU Usage:* {cpu_percent}%\n"
        f"🧠 *Memory Usage:* {mem.percent}%\n"
        f"🔋 *Available Memory:* {round(mem.available/1024/1024)}MB\n"
        "All systems blooming normally~ 🌺\n"
        "\n▰▰▰▰▰▰▰▰▰▰▰▰▰\n" 
    )
    
    await update.message.reply_text(response, parse_mode="Markdown")