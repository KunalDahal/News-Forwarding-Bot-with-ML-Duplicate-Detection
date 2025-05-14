from telegram import Update
from telegram.ext import ContextTypes
from storage.config import MESSAGE_FILE, OWNER_ID
import json
import uuid
from pathlib import Path
from datetime import datetime

async def message_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # ====== 🌸 Path Handling Magic 🌸 ======
        if isinstance(MESSAGE_FILE, tuple):
            correct_path = Path(MESSAGE_FILE[0])
        else:
            correct_path = MESSAGE_FILE
        
        correct_path = correct_path.resolve()
        correct_path.parent.mkdir(parents=True, exist_ok=True)

        moon_script = ' '.join(context.args) or ""
        if not moon_script:
            await update.message.reply_text(
                "━━━━━━━━━━━━━━\n"
                "📜 *Notice:* _Your message has been archived._\n"
                "⌜ *Please send your next message using `/message`* ⌟\n\n"
                "━━━━━━━━━━━━━━\n",
                parse_mode='Markdown'
            )
 
            return

        # 🌸 Generate Celestial UUID
        message_uuid = str(uuid.uuid4())
        
        # 📜 Load Ancient Scrolls
        messages = {}
        if correct_path.exists():
            with open(correct_path, "r", encoding="utf-8") as f:
                messages = json.load(f)

        # 🖋️ Inscribe New Message
        messages[message_uuid] = {
            "user_id": update.effective_user.id,
            "username": update.effective_user.username,
            "message": moon_script,
            "timestamp": datetime.now().isoformat(),
            "responded": False
        }

        # 🏯 Save to Sacred Archives
        with open(correct_path, "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=2)

        # 🕊️ Send to Goshujin-sama
        await context.bot.send_message(
        chat_id=OWNER_ID,
        text = (
            "▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
            f"📜 *UUID* » `{message_uuid}`\n"
            f"🎐 *From* » @{update.effective_user.username} (`{update.effective_user.id}`)\n"
            "▹▹▹▹▹▹▹▹▹▹▹▹▹\n"
            f"_{moon_script[:150].replace('_', '＿')}..._\n\n"
            "▰▰▰▰▰▰▰▰▰▰▰▰▰"
        ),
        parse_mode='Markdown'
    )

        await update.message.reply_text(
            "━━━━━━━━━━━━━━\n"
            "• *Destination:* _Goshujin-sama's desk_ 📜\n\n"
            "• *Response Pending:*\n"
            "• *Heartfelt Thanks:* *arigatou* 🎎\n"
            "━━━━━━━━━━━━━━\n",
            parse_mode='Markdown'
        )


    except Exception as e:
        print(f"🌧️ Celestial Error: {str(e)}")
        await update.message.reply_text(  
            "🌧️ Paper cranes soaked in autumn rain... 💧\n"  
            "▹ Resend when the moon *glows brighter* 🌸🌙",  
            parse_mode='Markdown'  
        )  