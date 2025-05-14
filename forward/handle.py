import json
import asyncio
from telegram import InputMediaPhoto, InputMediaVideo
from telegram.constants import ParseMode
from storage.config import GARBAGE_CHANNEL_ID, TARGET_CHANNEL
from forward.processor import process_text
from forward.model.model import process_input
from storage.config import TARGET_CHANNEL
import json
from storage.config import SOURCE_CHANNEL_ID

pending_media = {}

async def message_handler(update, context):
    message = update.effective_message
    if not message:
        return

    # Process only messages from the source channel
    if not update.channel_post or update.channel_post.chat.id != SOURCE_CHANNEL_ID:
        return

    media_group_id = message.media_group_id
    key = media_group_id if media_group_id else f"single_{message.message_id}"

    if key not in pending_media:
        pending_media[key] = {
            'messages': []
        }
        asyncio.create_task(schedule_media_processing(key, context))

    pending_media[key]['messages'].append(message)


async def schedule_media_processing(key, context):

    await asyncio.sleep(2)
    await process_media(key, context)

async def process_media(key, context):
    data = pending_media.pop(key, None)
    if not data:
        return
    messages = data['messages']
    
    try:
        original_text = messages[0].caption or ""
        processed_text = process_text(original_text)
        label = process_input(processed_text)

        media_group = []
        for i, msg in enumerate(messages):
            if msg.photo:
                media_type = InputMediaPhoto
                media_file = msg.photo[-1].file_id
            elif msg.video:
                media_type = InputMediaVideo
                media_file = msg.video.file_id
            else:
                continue

            media_group.append(media_type(
                media=media_file,
                caption= processed_text if i == 0 else None,
                parse_mode=ParseMode.MARKDOWN_V2
            ))

        is_group = len(media_group) > 1


        try:
            with open(TARGET_CHANNEL, 'r') as f:
                channels = json.load(f)
            if not isinstance(channels, list):
                print("TARGET_CHANNEL is not a list. Using empty list.")
                channels = []
        except Exception as e:
            print(f"Error loading target channels: {e}")
            channels = []

        if label == 0: 
            for channel_id in channels:
                try:
                    if is_group:
                        await context.bot.send_media_group(
                            chat_id=channel_id,
                            media=media_group
                        )
                    else:
                        await forward_single_media(context.bot, channel_id, messages[0], processed_text)
                except Exception as e:
                    print(f"Error forwarding to {channel_id}: {e}")
        else:
            try:
                if is_group:
                    await context.bot.send_media_group(
                        chat_id=GARBAGE_CHANNEL_ID,
                        media=media_group
                    )
                else:
                    # Pass processed_text here to ensure escaping
                    await forward_single_media(context.bot, GARBAGE_CHANNEL_ID, messages[0], processed_text)
            except Exception as e:
                print(f"Error forwarding to garbage: {e}")

    except Exception as e:
        print(f"Error processing media group: {e}")

async def forward_single_media(bot, chat_id, message, caption=None):
    try:
        final_caption = caption if caption is not None else message.caption
        if message.photo:
            await bot.send_photo(
                chat_id=chat_id,
                photo=message.photo[-1].file_id,
                caption=final_caption,
                parse_mode=ParseMode.MARKDOWN_V2
            )
        elif message.video:
            await bot.send_video(
                chat_id=chat_id,
                video=message.video.file_id,
                caption=final_caption,
                parse_mode=ParseMode.MARKDOWN_V2
            )
    except Exception as e:
        print(f"Error forwarding single media: {e}")

async def load_target_channels():
    try:
        with open(TARGET_CHANNEL, 'r') as f:
            channels = json.load(f)
        if not isinstance(channels, list):
            print("TARGET_CHANNEL is not a list. Using empty list.")
            channels = []
    except Exception as e:
        print(f"Error loading target channels: {e}")
        channels = []
    return channels