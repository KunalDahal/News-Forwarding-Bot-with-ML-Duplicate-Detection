import json
import datetime
import pytz
from datetime import date, datetime
from telegram.ext import  CallbackContext
from storage.config import SUBSCRIPTION_FILE, TARGET_CHANNEL
from commands.subscribe import load_subscriptions, save_subscriptions

def update_target_channels():
    try:
        with open(SUBSCRIPTION_FILE, 'r') as f:
            subscriptions = json.load(f)
    except Exception as e:
        print(f"Error loading subscriptions.json: {e}")
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
            print(f"Error parsing expiry_date for user {user_data.get('user-id')}: {e}")
            continue

        if expiry_date < now:
            continue

        # Fetch channel IDs.
        channels = user_data.get("ch_id", [])
        for ch in channels:
            target_channels.add(ch)

    try:
        with open(TARGET_CHANNEL, 'w') as f:
            json.dump(list(target_channels), f, indent=4)
        print("Updated target_channel.json with channels:", list(target_channels))
    except Exception as e:
        print(f"Error writing target_channel.json: {e}")

async def monitor_subscriptions(context: CallbackContext):
    update_target_channels()

async def check_expired_subscriptions(context: CallbackContext):
    subs = load_subscriptions()
    today = date.today()
    expired_users = []

    for user_id, data in subs.items():
        try:
            expiry_date = datetime.fromisoformat(data['expiry_date']).date()
        except Exception as e:
            print(f"Error parsing expiry_date for user {user_id}: {e}")
            continue

        if today >= expiry_date:
            expired_users.append(user_id)
    
    for user_id in expired_users:
        del subs[user_id]
        await context.bot.send_message(
            chat_id=user_id,
            text="⚠️ Your bot subscription has expired, and your access has been removed. Please renew to continue using premium features."
        )

    if expired_users:
        save_subscriptions(subs)
        print(f"Removed {len(expired_users)} expired users from subscriptions.json")
