from pathlib import Path
from datetime import datetime
import json
from storage.config import MESSAGE_FILE

async def list_uuids(update, context):
    try:
        message_path = Path(MESSAGE_FILE) if not isinstance(MESSAGE_FILE, Path) else MESSAGE_FILE

        if not message_path.exists():
            await update.message.reply_text("🌌 The Void Archives are empty...")
            return

        with open(message_path, "r", encoding="utf-8") as f:
            scrolls = json.load(f)

        response = f"🌸 {len(scrolls)} Unread Moon Letters 🌙\n"
        
        for idx, (uuid, scroll) in enumerate(scrolls.items(), 1):
            moon_time = datetime.fromisoformat(scroll['timestamp']).strftime("%Y-%m-%d %H:%M")
            response += (
                "\n▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
                f"🗝️ 【Celestial ID {idx}】\n"
                f"🌠 UUID: {uuid}\n"
                "⌜━━━━━━━━━━━━━━━━━━━━⌟\n"
            )

        await update.message.reply_text(response)

    except json.JSONDecodeError:
        await update.message.reply_text("🌧️ The scrolls have been damaged by rain...")
    except Exception as e:
        await update.message.reply_text(f"🌪️ Celestial disturbance: {str(e)}")
