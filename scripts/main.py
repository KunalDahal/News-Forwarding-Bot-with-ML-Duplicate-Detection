from storage.timezone import initialize_timezone_patch
initialize_timezone_patch()

import json
import datetime
import pytz
import asyncio
import logging

from datetime import datetime
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from commands.owner.uuid import list_uuids
from scripts.e_checker import check_expired_subscriptions
from storage.config import BOT_TOKEN, SUBSCRIPTION_FILE, TARGET_CHANNEL,SOURCE_CHANNEL_ID
from commands.subscribe import (
    subscribe_start, get_channels, get_username, payment_proof, cancel_subscription,
    GET_CHANNELS, GET_USERNAME, PAYMENT_PROOF, handle_subscription_callback
)
from commands.owner.set_sources import set_source
from commands.owner.owner_handlers import setup_owner_handlers
from commands.help import help_command
from commands.start import start
from commands.start_news import start_news as start_news_handler
from commands.stop_news import stop_news as stop_news_handler
from commands.dashboard import dashboard
from forward.handle import message_handler
import telegram
from pathlib import Path
from logging.config import dictConfig
from commands.owner.owner_to_user import m_back_command
from commands.user_to_owner import message_command
from commands.owner.broadcast import broadcast
from commands.owner.restart import restart
from commands.owner.tutorial import tutorial
from commands.owner.sub_list import sub_list
from commands.sample_news import sample_news
from commands.owner.syscheck import syscheck
from commands.owner.remove import process_remove_command
from commands.owner.replace import process_replace_command

# Create logs directory if it doesn't exist
LOG_DIR = Path(r"Y:\CODIII\Newsbot\logs")
LOG_DIR.mkdir(exist_ok=True, parents=True)

logging_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'INFO',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': LOG_DIR / 'bot.log',
            'formatter': 'simple',
            'level': 'INFO',
            'encoding': 'utf-8',  # Add this line
        }
    },
    'loggers': {
        'httpx': {
            'handlers': ['console'],
            'level': 'CRITICAL',
            'propagate': False,
        },
        'httpcore': {
            'handlers': ['console'],
            'level': 'CRITICAL',
            'propagate': False,
        },
        'telegram.ext.Updater': {
            'handlers': ['console'],
            'level': 'CRITICAL',
            'propagate': False,
        },
        'telegram.ext._utils.networkloop': {
            'handlers': ['console'],
            'level': 'CRITICAL',
            'propagate': False,
        },
        'asyncio': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'apscheduler': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
    'root': {
        'handlers': ['console', 'file'],  # Add both handlers here
        'level': 'INFO',
    },
}

dictConfig(logging_config)
logger = logging.getLogger(__name__)

def setup_error_handling(application: Application):
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        if isinstance(context.error, telegram.error.NetworkError):
            logger.debug("Suppressed NetworkError: %s", context.error)
            return
        logger.error("Unhandled exception: %s", context.error, exc_info=context.error)

    application.add_error_handler(error_handler)

async def network_monitor():
    while True:
        try:
            # Simple connectivity check
            await asyncio.wait_for(asyncio.get_running_loop().getaddrinfo("api.telegram.org", 443), timeout=5)
            await asyncio.sleep(10)
        except (asyncio.TimeoutError, OSError):
            logger.info("🌐 Network connection unstable...")
            await asyncio.sleep(30)

def update_target_channels():
    try:
        with open(SUBSCRIPTION_FILE, 'r') as f:
            subscriptions = json.load(f)
    except Exception as e:
        logger.error(f"Error loading subscriptions.json: {e}")
        return

    target_channels = set()
    now = datetime.now(pytz.utc)

    for user_data in subscriptions.values():
        if not user_data.get("subscribed", False):
            continue
        if not user_data.get("Active", False):
            continue

        expiry_str = user_data.get("expiry_date", "")
        try:
            expiry_date = datetime.fromisoformat(expiry_str)
            if expiry_date.tzinfo is None:
                expiry_date = expiry_date.replace(tzinfo=pytz.utc)
        except Exception as e:
            logger.error(f"Error parsing expiry_date for user {user_data.get('user-id')}: {e}")
            continue

        if expiry_date < now:
            continue

        channels = user_data.get("ch_id", [])
        for ch in channels:
            target_channels.add(ch)

    try:
        with open(TARGET_CHANNEL, 'w') as f:
            json.dump(list(target_channels), f, indent=4)
        logger.info("Updated target_channel.json with channels: %s", list(target_channels))
    except Exception as e:
        logger.error(f"Error writing target_channel.json: {e}")

async def monitor_subscriptions(context: ContextTypes.DEFAULT_TYPE):
    update_target_channels()

def setup_error_handling(application: Application):
    async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
        if isinstance(context.error, (telegram.error.NetworkError, telegram.error.TimedOut)):
            logger.debug("Suppressed network issue: %s", context.error)
            return
        logger.error("Unhandled exception: %s", context.error, exc_info=context.error)

    application.add_error_handler(error_handler)

def setup_dispatcher(application: Application):
    setup_error_handling(application)
    
    # Channel post handler (FORWARDING)
    application.add_handler(
        MessageHandler(
            filters.Chat(chat_id=SOURCE_CHANNEL_ID) & filters.UpdateType.CHANNEL_POST,
            message_handler
        )
    )

    # Conversation handler (keep existing)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('subscribe', subscribe_start)],
        states={
            GET_CHANNELS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_channels)],
            GET_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_username)],
            PAYMENT_PROOF: [
                MessageHandler(filters.PHOTO, payment_proof),
                MessageHandler(filters.TEXT & ~filters.COMMAND, payment_proof)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel_subscription)]
    )
    application.add_handler(conv_handler)

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("start_news", start_news_handler))
    application.add_handler(CommandHandler("stop_news", stop_news_handler))
    application.add_handler(CommandHandler("dashboard", dashboard))
    application.add_handler(CommandHandler("set_source", set_source))
    application.add_handler(CommandHandler("message", message_command))
    application.add_handler(CommandHandler("m_back", m_back_command))
    application.add_handler(CommandHandler("syscheck", syscheck))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("sub_list", sub_list))
    application.add_handler(CommandHandler("restart", restart))
    application.add_handler(CommandHandler("sample_news", sample_news))
    application.add_handler(CommandHandler("tutorial", tutorial))
    application.add_handler(CommandHandler("uuid", list_uuids))
    application.add_handler(CommandHandler("remove", process_remove_command))
    application.add_handler(CommandHandler("replace", process_replace_command))

    setup_owner_handlers(application)
    application.add_handler(CallbackQueryHandler(handle_subscription_callback))

    # FIXED unrecognized message handler (only for private messages)
    async def ignore_unrecognized_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.message:  # Only respond to direct messages
            await update.message.reply_text("⚠️ Unrecognized command. Use /help for available commands.")
    
    application.add_handler(MessageHandler(
        filters.UpdateType.MESSAGE & 
        ~filters.COMMAND & 
        filters.ChatType.PRIVATE,
        ignore_unrecognized_message
    ))


async def run_bot_commands():
    application = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .arbitrary_callback_data(True)
        .concurrent_updates(True)
        .get_updates_http_version("1.1")
        .read_timeout(30)
        .write_timeout(30)
        .pool_timeout(30)
        .connect_timeout(30)  # Add connection timeout
        .connection_pool_size(20)  # Increase connection pool
        .build()
    )

    setup_dispatcher(application)
    application.job_queue.run_repeating(check_expired_subscriptions, interval=86400, first=0)
    application.job_queue.run_repeating(monitor_subscriptions, interval=30, first=0)
    
    logger.info("Main bot commands task starting...")

    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    await asyncio.Event().wait()

async def run_with_restart(main_function):
    backoff_time = 5
    max_backoff = 300  # 5 minutes
    while True:
        try:
            await main_function()
            backoff_time = 5  # Reset on success
        except (KeyboardInterrupt, SystemExit):
            logger.info("Graceful shutdown initiated")
            break
        except Exception as e:
            logger.error(f"Critical error: {str(e)}", exc_info=True)
            logger.info(f"Restarting in {backoff_time} seconds...")
            await asyncio.sleep(backoff_time)
            backoff_time = min(backoff_time * 2, max_backoff)

async def main():
    monitor_task = asyncio.create_task(network_monitor())
    await run_with_restart(run_bot_commands)
    monitor_task.cancel()

if __name__ == "__main__":
    asyncio.run(main())