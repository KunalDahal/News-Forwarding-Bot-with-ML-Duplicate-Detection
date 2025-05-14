from telegram import Update
from telegram.ext import CallbackContext
from storage.config import load_subscriptions, save_subscriptions
import logging
from commands.command_lock import is_locked

logger = logging.getLogger(__name__)

async def stop_news(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)

    if is_locked(user_id):
        await update.message.reply_text(
            "🎎 *Our tea ceremony continues...* 🌙\n"
            "⌜ Finish this *chanoyu* before new rituals ⌟\n\n",
            parse_mode='Markdown'
        )
        return

    subs = load_subscriptions()
    logger.info("stop_news: user_id %s, subscription data: %s", user_id, subs.get(user_id))
    
    user_sub = subs.get(user_id, {})
    if not user_sub.get('subscribed'):
        await update.message.reply_text(
            "🚫 *Bot Deactivated!* The service is inactive for your account.\n"
            "👉 Use `/start_news` to reactivate the bot.",
            parse_mode='Markdown'
        )
        return

    subs[user_id]['Active'] = False
    save_subscriptions(subs)

    await update.message.reply_text(
        "✅ *Mizuki-chan* _drifts into slumber..._ 💤\n\n"
        "🌸 *Arigatou for our shared moonlit path...*",
        parse_mode='Markdown'
    )