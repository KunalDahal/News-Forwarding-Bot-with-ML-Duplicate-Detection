import os
import logging
import asyncio
from telethon import TelegramClient, events
from telethon.errors import RPCError, SessionPasswordNeededError, FloodWaitError, CodeInvalidError
from telethon.tl.patched import MessageService
from storage.config import API_HASH, API_ID, load_db_sess, save_db_sess
from aioconsole import ainput
from pathlib import Path
import time
from telethon.tl import types

# Add these global variables at the top with other globals
last_forward_time = 0
forward_lock = asyncio.Lock()

async def safe_forward(target_entity, messages):
    global last_forward_time
    async with forward_lock:
        # Calculate required wait time
        now = time.time()
        required_wait = max(0, 2 - (now - last_forward_time))
        
        if required_wait > 0:
            logger.info(f"🕒 Waiting {required_wait:.1f}s before forwarding")
            await asyncio.sleep(required_wait)
        
        try:
            # Forward the messages
            await client.forward_messages(target_entity, messages)
            logger.info(f"✅ Forwarded {len(messages)} messages to {target_entity.title}")
            
            # Update the last forward time
            last_forward_time = time.time()
            return True
        except Exception as e:
            logger.error(f"❌ Forward error: {e}")
            return False
        
LOG_DIR = Path(r"Y:\CODIII\PROJECT\News_Forwarding_bot\logs")
LOG_DIR.mkdir(exist_ok=True, parents=True)
SESSION_PATH = LOG_DIR / "forward_bot.session"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

client = TelegramClient(str(SESSION_PATH), API_ID, API_HASH)
grouped_cache = {}
grouped_tasks = {}

async def authenticate_client():
    if not await client.is_user_authorized():
        max_resend_attempts = 3
        resend_count = 0
        
        try:
            phone = await ainput("Enter phone (e.g., +1234567890): ").strip()
            if not phone.startswith('+'):
                raise ValueError("Phone must include country code (+XX...)")
            
            sent_code = await client.send_code_request(phone)
            print(f"Code sent via: {sent_code.type}")

            while True:
                code = await ainput("Enter 5-digit code (or 'resend'): ").strip()
                
                if code.lower() == 'resend':
                    if resend_count >= max_resend_attempts:
                        print("Max resend attempts reached. Wait 24h.")
                        return False
                    
                    print(f"Resending code ({resend_count+1}/{max_resend_attempts})...")
                    await client.resend_code_request(phone)
                    resend_count += 1
                    continue
                
                if len(code) != 5 or not code.isdigit():
                    print("Invalid code - must be 5 digits")
                    continue
                
                try:
                    await client.sign_in(phone=phone, code=code)
                    print("Code accepted!")
                    return True
                except SessionPasswordNeededError:
                    password = os.getenv("TG_PASSWORD", "Dos@2712")
                    await client.sign_in(password=password)
                    print("2FA successful!")
                    return True
                except CodeInvalidError:
                    print("Wrong code - try again")
                except FloodWaitError as e:
                    print(f"Wait {e.seconds} seconds before retrying")
                    return False

        except RPCError as e:
            print(f"Auth failed: {e}")
            return False
    return True

async def check_and_correct_last_ids(config):
    for source in config['sources']:
        try:
            source_entity = await client.get_entity(source['source_channel'])
            last_msg = await client.get_messages(source_entity, limit=1)
            current_max_id = last_msg[0].id if last_msg else 0
            stored_last_id = source['last_message_id']
            if stored_last_id > current_max_id:
                logger.warning(f"Correcting last_message_id for {source_entity.title} from {stored_last_id} to {current_max_id}")
                source['last_message_id'] = current_max_id
                save_db_sess(config)
        except Exception as e:
            logger.error(f"Error checking source {source['source_channel']}: {e}")
    return config

async def setup_channels():
    config = load_db_sess()
    if config:
        await check_and_correct_last_ids(config)
        return config

    print("\nFirst-time setup:")
    target = input("Enter target channel ID (format -100xxxxxxx): ")
    sources = []

    try:
        target_entity = await client.get_entity(int(target))
        logger.info(f"Target channel: {target_entity.title}")
    except (ValueError, RPCError) as e:
        logger.error(f"Invalid target channel: {e}")
        return None

    while True:
        source = input("\nEnter source channel ID (or 'done'): ").strip()
        if source.lower() == 'done':
            if not sources:
                print("Add at least one source channel")
                continue
            break

        try:
            source_id = int(source)
            source_entity = await client.get_entity(source_id)
            logger.info(f"Checking access to {source_entity.title}...")
            
            last_msg = await client.get_messages(source_entity, limit=1)
            sources.append({
                'source_channel': source_id,
                'last_message_id': last_msg[0].id if last_msg else 0
            })
            print(f"✓ Added {source_entity.title}")
        except (ValueError, RPCError) as e:
            print(f"× Error: {e}")

    config = {
        'target_channel': int(target),
        'sources': sources
    }
    save_db_sess(config)
    return config

async def process_missed_messages(client, source_config, target_channel, config):
    try:
        source_entity = await client.get_entity(source_config['source_channel'])
        target_entity = await client.get_entity(target_channel)

        last_id = source_config['last_message_id']
        logger.info(f"🔍 Processing missed messages from {source_entity.title} (last ID {last_id})")

        # Collect messages in chronological order
        messages = []
        async for message in client.iter_messages(
            source_entity,
            min_id=last_id,
            reverse=True  # Oldest first
        ):
            if isinstance(message, MessageService):
                continue
            messages.append(message)

        if not messages:
            logger.info(f"📭 No missed messages in {source_entity.title}")
            return

        logger.info(f"📨 Collected {len(messages)} messages to process in {source_entity.title}")

        current_group = []
        current_group_id = None

        for message in messages:
            if message.grouped_id:
                if current_group_id != message.grouped_id:
                    # Process previous group if exists
                    if current_group:
                        if await safe_forward(target_entity, current_group):
                            max_id = max(msg.id for msg in current_group)
                            source_config['last_message_id'] = max_id
                            save_db_sess(config)
                        current_group = []
                    current_group_id = message.grouped_id
                current_group.append(message)
            else:
                # Process any remaining group first
                if current_group:
                    if await safe_forward(target_entity, current_group):
                        max_id = max(msg.id for msg in current_group)
                        source_config['last_message_id'] = max_id
                        save_db_sess(config)
                    current_group = []
                    current_group_id = None
                
                # Process individual message
                if await safe_forward(target_entity, [message]):
                    source_config['last_message_id'] = message.id
                    save_db_sess(config)

        # Process any remaining group
        if current_group:
            if await safe_forward(target_entity, current_group):
                max_id = max(msg.id for msg in current_group)
                source_config['last_message_id'] = max_id
                save_db_sess(config)

        logger.info(f"🏁 Finished processing missed messages in {source_entity.title}")

    except Exception as e:
        logger.error(f"🔥 Error processing missed messages: {e}")

async def main():

    if not await authenticate_client():
        return

    config = await setup_channels()
    if not config:
        return

    try:
        target_entity = await client.get_entity(config['target_channel'])
        logger.info(f"Target channel set to: {target_entity.title}")
    except RPCError as e:
        logger.error(f"Target channel error: {e}")
        return

    for source in config['sources']:
        await process_missed_messages(client, source, config['target_channel'], config)

    async def process_group_after_delay(group_id, chat_id, config):
        await asyncio.sleep(2)  # Initial grouping delay
        group = grouped_cache.pop(group_id, None)
        if group:
            try:
                target_entity = await client.get_entity(config['target_channel'])
                if await safe_forward(target_entity, group):
                    max_id = max(msg.id for msg in group)
                    for source in config['sources']:
                        if chat_id == source['source_channel']:
                            source['last_message_id'] = max_id
                            save_db_sess(config)
                            logger.info(f"🔄 Updated last ID for {chat_id} to {max_id}")
                            break
            except RPCError as e:
                logger.error(f"🚫 Group forward error: {e}")
        grouped_tasks.pop(group_id, None)

    @client.on(events.NewMessage(chats=[s['source_channel'] for s in config['sources']]))
    async def message_handler(event):
        message = event.message
        if isinstance(message, MessageService):
            return

        if message.grouped_id:
            group_id = message.grouped_id
            grouped_cache.setdefault(group_id, []).append(message)

            if group_id not in grouped_tasks:
                grouped_tasks[group_id] = asyncio.create_task(
                    process_group_after_delay(group_id, event.chat_id, config)
                )
        else:
            try:
                target_entity = await client.get_entity(config['target_channel'])
                if await safe_forward(target_entity, [message]):
                    for source in config['sources']:
                        if event.chat_id == source['source_channel']:
                            source['last_message_id'] = message.id
                            save_db_sess(config)
                            break
            except RPCError as e:
                logger.error(f"📡 Live forward error: {e}")

    logger.info("Bot is now running...")
    await client.run_until_disconnected()

async def main_loop():
    backoff_time = 5
    max_backoff = 300
    
    # Advanced logging filter configuration
    class TelethonNetworkFilter(logging.Filter):
        def filter(self, record):
            suppress_messages = [
                "Server closed the connection",
                "network connection was aborted",
                "network location cannot be reached",
                "Attempt 1 at connecting failed",
                "Failed reconnection attempt"
            ]
            if any(msg in record.getMessage() for msg in suppress_messages):
                return False
            return True

    # Apply filter to all relevant Telethon loggers
    for logger_name in ['telethon.network.connection.connection',
                       'telethon.network.mtprotosender',
                       'telethon.network.connection',
                       'telethon.network']:
        logging.getLogger(logger_name).addFilter(TelethonNetworkFilter())

    # Set higher log level for noisy components
    logging.getLogger('telethon.network.mtprotosender').setLevel(logging.ERROR)
    logging.getLogger('telethon.network.connection').setLevel(logging.ERROR)

    while True:
        try:
            async with client:
                await main()
                backoff_time = 5  # Reset on successful run
        except (KeyboardInterrupt, SystemExit):
            logger.info("Graceful shutdown")
            break
        except FloodWaitError as e:
            logger.warning(f"⏳ Flood protection: Waiting {e.seconds}s")
            await asyncio.sleep(e.seconds)
        except (OSError, ConnectionError, 
               asyncio.TimeoutError) as e:
            logger.info("🌐 Network instability detected. Reconnecting...")
            await asyncio.sleep(15)
        except Exception as e:
            logger.error(f"🚨 Critical error: {str(e)}")
            logger.info(f"⏳ Retrying in {backoff_time}s...")
            await asyncio.sleep(backoff_time)
            backoff_time = min(backoff_time * 2, max_backoff)

if __name__ == '__main__':
    asyncio.run(main_loop())