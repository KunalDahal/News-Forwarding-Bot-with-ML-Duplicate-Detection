from telegram import Update
from telegram.ext import ContextTypes
import json
from storage.config import OWNER_ID,MESSAGE_FILE

async def m_back_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /m_back command with UUID reference (Deletes after response)"""
    if int(update.effective_user.id) != OWNER_ID:
        await update.message.reply_text("⛩️ This sacred chant is for the shrine keeper only~")
        return

    if int(update.effective_user.id) != OWNER_ID:
        await update.message.reply_text(
            " *Sacred Restriction!* 🎴\n"
            "🎴_This command is for Goshujin-sama alone~_ 🌸"
        )
        return

    # 🎐 Format validation
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "⌜📜 Usage ⌟: `/m_back <message_id> <message>`📜\n\n"
            "✧･ﾟ:* Example *:･ﾟ✧\n"
            "`/m_back 550e8400... 'The sakura await your reply...' 🌸`\n"
        )
        return

    # 🌸 Extract components
    msg_uuid = context.args[0]
    response_text = ' '.join(context.args[1:])

    try:
        with open(MESSAGE_FILE, "r+") as f:
            messages = json.load(f)
            
            # 🌌 Check if message exists
            if msg_uuid not in messages:
                await update.message.reply_text(
                    "This message scroll has already returned to the void\n"
                    "▹ Perhaps it was answered in a parallel world?"
                )
                return

            msg_data = messages[msg_uuid]
            
            # 🕊️ Send celestial response
            await context.bot.send_message(
                chat_id=msg_data['user_id'],
                text=(
    
                    "🌸 *A Response from the Goshujin Sama* 🌸\n"
                    "⌜━━━━━━━━━━━━━━━━━━━━⌟\n"
                    f"_{response_text}_\n\n"
    
                ),
                parse_mode='Markdown'
            )

            # 🎴 Remove from existence
            del messages[msg_uuid]
            
            # 📜 Rewrite cosmic records
            f.seek(0)
            json.dump(messages, f, indent=2)
            f.truncate()

        # 🏯 Confirm to owner
        remaining = len(messages)
        await update.message.reply_text(
            f"✨ *Message Cycle Completed* ✨\n"
            f"Response to {msg_uuid[:8]}... dissolved into stardust\n\n"
            f"🗝️ Preview: 『{response_text[:30]}...』\n"
            f"🌌 Remaining scrolls: {remaining}\n\n"
        )
        
    except Exception as e:
        error_message = str(e).lower()
        reason = (
            "◈ Recipient sealed their heart 🗝️" if "forbidden" in error_message else
            "◈ Temporal coordinates invalid ⏳" if "not found" in error_message else
            "◈ Void spirits intercepted 🕳️"
        )
        
        await update.message.reply_text(
            "🌧️ *Message Consumed by Shadows* 🌧️\n"
            f"Failed to complete cycle for {msg_uuid[:8]}...\n\n"
            f"Celestial diagnosis:\n{reason}\n\n"
            f"Oracle's whisper: {str(e)[:100]}..."
        )