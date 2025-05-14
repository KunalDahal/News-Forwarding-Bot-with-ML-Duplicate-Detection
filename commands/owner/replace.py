# replace.py (debug version)
import json
import os
import re
import aiofiles
import logging
from typing import Dict
from storage.config import REPLACE_PATH,OWNER_ID

logger = logging.getLogger(__name__)

async def load_replace_dict() -> Dict[str, str]:
    try:
        if os.path.exists(REPLACE_PATH):
            async with aiofiles.open(REPLACE_PATH, 'r', encoding='utf-8') as f:
                content = await f.read()
                logger.info(f"Loaded replace dict: {content[:50]}...")
                return json.loads(content)
        logger.warning("Replace file not found, starting fresh")
        return {}
    except Exception as e:
        logger.error(f"Load error: {str(e)}")
        return {}

async def save_replace_dict(replace_dict: Dict[str, str]):
    try:
        async with aiofiles.open(REPLACE_PATH, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(replace_dict, indent=2, ensure_ascii=False))
            logger.info(f"Saved {len(replace_dict)} items to replace dict")
    except Exception as e:
        logger.error(f"Save error: {str(e)}")
        raise

async def process_replace_command(update, context) -> None:

    if int(update.effective_user.id) != OWNER_ID:
        await update.message.reply_text("⛩️ This sacred chant is for the shrine keeper only~")
        return
    
    logger.info(f"Received replace command: {update.message.text}")
    try:
        args = ' '.join(context.args) if context.args else ''
        logger.debug(f"Raw args: {args}")

        match = re.search(r'"([^"]+)"\s*:\s*"([^"]+)"', args)
        if not match:
            error_msg = "Invalid replace format"
            logger.warning(error_msg)
            raise ValueError(error_msg)

        before, after = match.groups()
        logger.info(f"Processing replace: {before} → {after}")

        replace_dict = await load_replace_dict()
        logger.debug(f"Current replace dict: {replace_dict}")

        if before not in replace_dict:
            replace_dict[before] = after
            await save_replace_dict(replace_dict)
            logger.info(f"Added replacement: {before} → {after}")

            reply = (
                "🎋 **Mizuki's Transformation in Action** 🎋\n\n"
                "➤ **Performed Operation:**\n"
                f"`{before}` → `{after}`\n\n"
                "✔ *Replacement has been successfully added.*"
            )
        else:
            current = replace_dict[before]
            reply = (
                "⚠️ **Notice**\n"
                "➤ **Existing Mapping:**\n"
                f"`{before}` → `{current}`\n\n"
                "✏ *Consider revising if necessary.*"
            )

        await update.message.reply_text(
            text=reply,
            parse_mode='Markdown',
            reply_to_message_id=update.message.message_id,
            disable_web_page_preview=True
        )

    except Exception as e:
        error_reply = (
            "🚫 **Error Encountered**\n"
            f"➤ *Details:* `{str(e)}`\n\n"
            "ℹ **Usage:** `/replace \"old\" : \"new\"`"
        )
        await update.message.reply_text(
            text=error_reply,
            parse_mode='Markdown'
        )