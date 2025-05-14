
from telegram import Update
from telegram.ext import CallbackContext, CallbackQueryHandler
from commands.subscribe import approve_subscription, reject_subscription
from storage.config import OWNER_ID

async def handle_approval(update: Update, context: CallbackContext):
    query = update.callback_query
    action, user_id = query.data.split('_')
    
    # 🏮 Owner Verification
    if int(update.effective_user.id) != OWNER_ID:
        await query.answer("🧎♀️ *Gomenasai!* Only Goshujin-sama may perform this ritual 🏮", show_alert=True)
        return
        
    if action == 'approve':
        await approve_subscription(user_id)
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "🌸 *Yorokonde!* Your omamori has been blessed ✨\n"
                "▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
                "🌌 Full access to the moonlit garden granted~\n"
                "▹ Use `/start_news` to begin your journey 🏮"
                "\n▰▰▰▰▰▰▰▰▰▰▰▰▰\n" 
            ),
            parse_mode='Markdown'
        )
        await query.answer("🌸 *Omamori Blessed!*", show_alert=True)
        
    elif action == 'reject':
        await reject_subscription(user_id)
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                "🏮 *Zannen...* Your offering could not be accepted 🌸\n"
                "▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
                "▹ The shrine maidens found impurities...\n"
                "▹ Try again with purer intentions~ 🌙"
                "\n▰▰▰▰▰▰▰▰▰▰▰▰▰\n" 
            ),
            parse_mode='Markdown'
        )
        await query.answer("🎴 *Rejected with sorrow...*", show_alert=True)
    
    # Edit original query message
    result_text = (
        f"✨ *Processed {action} for* `{user_id}`\n"
        "▹ Status sealed with a cherry blossom stamp 🌸"
    )
    if query.message.text:
        await query.edit_message_text(text=result_text, parse_mode='Markdown')
    elif query.message.caption:
        await query.edit_message_caption(caption=result_text, parse_mode='Markdown')
def setup_owner_handlers(dp):
    dp.add_handler(CallbackQueryHandler(handle_approval, pattern=r"^(approve|reject)_\d+$"))