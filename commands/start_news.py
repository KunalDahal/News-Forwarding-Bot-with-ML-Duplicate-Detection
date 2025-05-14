from telegram import Update
from telegram.ext import CallbackContext
from storage.config import load_subscriptions, save_subscriptions
import logging
from commands.command_lock import is_locked

logger = logging.getLogger(__name__)

async def start_news(update: Update, context: CallbackContext):  
    user_id = str(update.effective_user.id)  

    # 🎐 Lock Check  
    if is_locked(user_id):  
        await update.message.reply_text(      
            "🌀 *A ritual is already underway...* 🌙\n"  
            "▹ Complete your *current offering* before\n"  
            "stepping into the hinode garden~ 🏯\n",  
            parse_mode='Markdown'  
        )  
        return  

    subs = load_subscriptions()  
    logger.info(f"start_news: user_id {user_id}, subscription data: {subs.get(user_id)}")  

    # 🏮 Subscription Check  
    if not subs.get(user_id, {}).get('subscribed'):  
        await update.message.reply_text(      
            "❌ *Gomenasai!* No active blessing found 🌫️\n"  
            "▹ Rekindle with `/subscribe` first! 🏮\n" ,  
            parse_mode='Markdown'  
        )  
        return  

    # 🌸 Activation  
    subs[user_id]['Active'] = True  
    save_subscriptions(subs)  
    await update.message.reply_text(     
        "✅ *Yatta!* *Mizuki* awakens from slumber~ ✨\n\n"  
        "🗝️ *Ensure I'm ADMIN in your channel!* 🏯\n"  
        "▹ Else, my whispers cannot reach you... 🌙\n",  
        parse_mode='Markdown'  
    ) 



