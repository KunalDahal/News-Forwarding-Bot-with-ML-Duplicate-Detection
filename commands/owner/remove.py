# remove.py (debug version)
import json
import os
import re
import aiofiles
import logging
from typing import List
from storage.config import REMOVE_PATH,OWNER_ID

logger = logging.getLogger(__name__)

async def load_remove_list() -> List[str]:
    try:
        if os.path.exists(REMOVE_PATH):
            async with aiofiles.open(REMOVE_PATH, 'r', encoding='utf-8') as f:
                content = await f.read()
                logger.info(f"Loaded remove list: {content[:50]}...")
                return json.loads(content)
        logger.warning("Remove file not found, starting fresh")
        return []
    except Exception as e:
        logger.error(f"Load error: {str(e)}")
        return []

async def save_remove_list(remove_list: List[str]):
    try:
        async with aiofiles.open(REMOVE_PATH, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(remove_list, indent=2, ensure_ascii=False))
            logger.info(f"Saved {len(remove_list)} items to remove list")
    except Exception as e:
        logger.error(f"Save error: {str(e)}")
        raise

async def process_remove_command(update, context) -> None:
    
    if int(update.effective_user.id) != OWNER_ID:
        await update.message.reply_text("⛩️ This sacred chant is for the shrine keeper only~")
        return
    
    
    
    logger.info(f"Received remove command: {update.message.text}")
    try:
        args = ' '.join(context.args) if context.args else ''
        logger.debug(f"Raw args: {args}")

        match = re.search(r'"([^"]+)"', args)
        if not match:
            error_msg = "No quoted text found in command"
            logger.warning(error_msg)
            raise ValueError(error_msg)

        text = match.group(1)
        logger.info(f"Processing remove for: {text}")

        remove_list = await load_remove_list()
        logger.debug(f"Current remove list: {remove_list}")

        if text not in remove_list:
            remove_list.append(text)
            await save_remove_list(remove_list)
            logger.info(f"Added '{text}' to remove list")

            reply = (
                "🌿 **Removal Successful**\n\n"
                "➤ **Text Removed:**\n"
                f"`{text}`\n\n"
                "✔ *The text has been added to the removal list.*"
            )
        else:
            reply = (
                "⚠️ **Notice**\n\n"
                "➤ **Text Already Removed:**\n"
                f"`{text}`\n\n"
                "✏ *The text is already in the removal list.*"
            )

        await update.message.reply_text(
            text=reply,
            parse_mode='Markdown',
            reply_to_message_id=update.message.message_id,
            disable_web_page_preview=True
        )

    except Exception as e:
        error_reply = (
            "🚫 **Error Occurred**\n\n"
            "➤ *Details:* `" + str(e) + "`\n\n"
            "ℹ **Usage:** `/remove \"text to remove\"`"
        )
        await update.message.reply_text(
            text=error_reply,
            parse_mode='Markdown'
        )
