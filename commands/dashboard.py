from telegram import Update
from telegram.ext import CallbackContext
from commands.command_lock import is_locked
from storage.config import SUBSCRIPTION_FILE,OWNER_ID,is_subscribed
import json
from telegram.helpers import escape_markdown
from datetime import datetime

def get_user_subscription(user_id):
    try:
        with open(SUBSCRIPTION_FILE, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    return data.get(int(user_id))

async def dashboard(update: Update, context: CallbackContext):
    user_id = int(update.effective_user.id)
    if int(user_id) not in [OWNER_ID,is_subscribed(user_id)]:
        await update.message.reply_text(
            "These news petals are still waiting to bloom~\n"
            "▹ Complete your Subscripition first"
        )
        return

    if is_locked(user_id):
        await update.message.reply_text(
            "🎐 *Mizu no Nagare...* 🎐\n"
            "⌜ Your subscription ritual is still flowing ⌟\n"
        )
        return

    user_data = get_user_subscription(user_id)
    if not user_data:
        await update.message.reply_text(
            "Your celestial garden awaits its first bloom~\n"
            "▹ No channels found in your sacred realm 🏯"
        )
        return

    channels_list = user_data.get("ch_id", [])
    payment_username = user_data.get("payment_username", "N/A")
    username = user_data.get("username", "N/A")
    port = user_data.get("Active", False)
    subscribed = user_data.get("subscribed", False)
    expiry_iso = user_data.get("expiry_date", "")

    try:
        expiry_dt = datetime.fromisoformat(expiry_iso)
        expiry_str = expiry_dt.strftime("%B %d, %Y")
    except Exception:
        expiry_str = expiry_iso

    # Escape dynamic content for Markdown
    username = escape_markdown(username, version=1)
    payment_username = escape_markdown(payment_username, version=1)
    expiry_str = escape_markdown(expiry_str, version=1)

    header = (
        "🏯 *Your Personal Shinden* 🏯\n"
        "⌜━━━━━━━━━━━━━━━━━━━━⌟\n"
        "◈ Mizuki's Blessing Portal ◈\n\n"
    )
    user_info = (
        f"🎴 *Namae (Name):* `{username}`\n"
        f"💰 *Omamori Source:* @{payment_username}\n\n"
        f"🌸 *Sacred Bond Status:*\n"
        f"◈ Subscription: {'Engraved in stone 🪨' if subscribed else 'Drifting leaves 🍃'}\n"
        f"◈ Channel Flow: {'Flowing 🌊' if port else 'Still 🍵'}\n"
        f"◈ Next Bloom Cycle: `{expiry_str}`\n\n"
    )

    channels_info = "🎏 *Channel Omamori Collection* 🎏\n"
    if channels_list:
        for ch in channels_list:
            ch_esc = escape_markdown(ch, version=1)
            try:
                chat = await context.bot.get_chat(ch)
                title = escape_markdown(chat.title, version=1) or "Unnamed Realm"
                channels_info += f"▹ `{ch_esc}` ⌜*{title}*⌟\n"
            except Exception:
                channels_info += f"▹ `{ch_esc}` ⌜*Mysterious Realm*⌟\n"
    else:
        channels_info = (
            "No channel omamori in your possession~\n"
            "Await Goshujin-sama's blessings"
        )

    footer = (
        "Manage your realm with:\n"
        "`/start_news` 🌅 Begin morning haiku\n"
        "`/stop_news` 🌙 Enter moonlit silence"
    )

    dashboard_msg = header + user_info + channels_info + footer
    await update.message.reply_text(dashboard_msg, parse_mode="Markdown")
