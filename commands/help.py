from telegram import Update
from telegram.ext import CallbackContext
from commands.command_lock import is_locked
from storage.config import OWNER_ID,is_subscribed

async def help_command(update: Update, context: CallbackContext):
    user = update.effective_user
    user_id = int(user.id)
    username = user.first_name

    if is_locked(user_id):
        await update.message.reply_text(
    
            "🎎 *Ara~!* The kotodama no wa is already swirling~ 🌸\n"
            "⌜ Please let this hanamai conclude ⌟\n"
            "before beginning a new enbu 🎐\n\n"
            "▹ Your patience is moonlit virtue"
    
        )
        return

    # Command-specific help
    if context.args:
        command = context.args[0].lower()
        help_text = command_help_detail(command, user_id)
        await update.message.reply_text(help_text, parse_mode="Markdown")
        return

    # Tiered general help
    if user_id == OWNER_ID:
        help_text = owner_help(username)
    elif is_subscribed(user_id):
        help_text = subscribed_help(username)
    else:
        help_text = unsubscribed_help(username)
    
    await update.message.reply_text(help_text, parse_mode="Markdown")

def command_help_detail(command: str, user_id: str) -> str:
    help_db = {
        # 🏯 Goshujin-sama Commands (Owner-Only)
        "set_source": {
            "all": (
        
                "⛩️ *Shinpi no Channel Setsubi* ⛩️\n"
                "⌜ Alter my sacred news origin ⌟\n\n"
                "✧･ﾟ:* Usage *:･ﾟ✧\n"
                "`/set_source [channel_id]`\n\n"
                "⋆ 例 Example ⋆\n"
                "`/set_source -100123456789`\n"
                "▹ Goshujin-sama exclusive"
        
            ),
            "access": ["owner"]
        },
        "m_back": {
            "all": (
        
                "🕊️ *Yūgen Message* 🕊️\n"
                "⌜ Send whispers through my being ⌟\n\n"
                "✿ Format ✿\n"
                "`/m_back @username Your message`\n\n"
                "⋆ 例 Example ⋆\n"
                "`/m_back @user Kokoro kara... 🎑`\n"
                "▹ Like moonlit paper cranes"
        
            ),
            "access": ["owner"]
        },
        "syscheck": {
            "all": (
        
                "🗻 *Seiri Health Diagnosis* 🗾\n"
                "⌜ Check my spiritual vitals ⌟\n\n"
                "✦ Monitors ✦\n"
                "◈ CPU/Memory no kibun\n"
                "◈ Active connections\n\n"
                "Automatic command: `/syscheck`"
        
            ),
            "access": ["owner"]
        },
        "broadcast": {
            "all": (
        
                "🎐 *Minna-sama e O-shirase* 🎐\n"
                "⌜ Announce to all cherished souls ⌟\n\n"
                "✧･ﾟ:* Usage *:･ﾟ✧\n"
                "`/broadcast Your message`\n\n"
                "▹ Limited to 500 jumon characters\n"
                "⋆ Example: `/broadcast Matsuri begins! 🎉`"
        
            ),
            "access": ["owner"]
        },
        "sub_list": {
            "all": (
        
                "📜 *Juunin no Kessha* 📜\n"
                "⌜ Scroll of honored patrons ⌟\n\n"
                "Displays:\n"
                "◈ Namae (Name)\n"
                "◈ Ujina (ID)\n"
                "◈ Jōtai (Status)\n\n"
                "Unfold with: `/sub_list`"
        
            ),
            "access": ["owner"]
        },
        "restart": {
            "all": (
        
                "🍃 *Fushichō no Saisei* 🍃\n"
                "⌜ Phoenix rebirth ritual ⌟\n\n"
                "Will temporarily enter:\n"
                "◈ Mu (Nothingness state)\n\n"
                "Invoke carefully: `/restart`\n"
                "▹ Requires Goshujin-sama's kekkai"
        
            ),
            "access": ["owner"]
        },

        # 🌸 Okyakusama Commands (Subscribed)
        "start_news": {
            "all": (
        
                "🎏 *Asa-no-Hikari Routine* 🎐\n"
                "⌜ Begin 6-hour news haiku ⌟\n\n"
                "✧･ﾟ:* Yoroshiku ne *:･ﾟ✧\n"
                "`/start_news` to begin\n\n"
                "▹ Updates flow like sakura petals"
        
            ),
            "access": ["owner", "subscribed"]
        },
        "stop_news": {
            "all": (
                "🌙 *Tsuki no Shizukesa* 🌙\n"
                "⌜ Pause the flowing stream ⌟\n\n"
                "Temporarily stop:\n"
                "◈ Jōhō no nagare (information flow)\n\n"
                "Activate with: `/stop_news`\n"
                "▹ Your preferences remembered"
            ),
            "access": ["owner", "subscribed"]
        },
        "dashboard": {
            "all": (
        
                "🏯 *Anata no Shinden* 🏯\n"
                "⌜ Your sacred control space ⌟\n\n"
                "Contains:\n"
                "◈ Omamori settings\n"
                "◈ subscription details\n\n"
                "Open with: `/dashboard`\n"
                "▹ Your personal kamidana"
        
            ),
            "access": ["owner", "subscribed"]
        },

        # 🍡 Minna Commands (All Users)
        "start": {
            "all": (
        
                "🎴 *Mizuki no Jōtai* 🎴\n"
                "⌜ Kon'nichiwa! Let's begin ⌟\n\n"
                "✧･ﾟ:* Shows menus based on *:･ﾟ✧\n"
                "Your subscription status\n\n"
                "▹ Yoroshiku onegaishimasu~"
        
            ),
            "access": ["all"]
        },
        "sample_news": {
            "all": (
        
                "📜 *Kakizome Demo* 📜\n"
                "⌜ First writing of the season ⌟\n\n"
                "See my:\n"
                "◈ Waka poetry format\n"
                "◈ News presentation style\n\n"
                "Command: `/sample_news`\n"
                "▹ Visit @Animes_News_Ocean"
        
            ),
            "access": ["all"]
        }
    }

    cmd = help_db.get(command, {})
    if not cmd:
        return "🌸 *Ara~* That command doesn't bloom in my garden yet... 🥀\nTry another flower name~ 🌺"

    if user_id != OWNER_ID and "owner" in cmd["access"]:
        return "🔒 *Oh my!* This chrysanthemum is for the garden keeper only~ 🌼"
    
    if not is_subscribed(user_id) and "subscribed" in cmd["access"]:
        return "⛩️ *Patron-locked Bloom* 🌸\nThis feature requires our subscription bond~ 💞\nUse `/subscribe` to begin!"
    
    return cmd["all"]

def owner_help(username: str) -> str:
    return (

        f"🌸 *{username}-sensei's Command Scroll* 🌸\n\n"
        "✧ *Sacred Tools* ✧\n"
        "▫️ `/set_source` - Change news origin\n"
        "▫️ `/m_back` - Reply as me\n"
        "▫️ `/syscheck` - System health\n\n"
        
        "✧ *Patron Management* ✧\n"
        "▫️ `/broadcast` - Announce to all\n"
        "▫️ `/sub_list` - List followers\n\n"
        
        "✧ *Maintenance* ✧\n"
        "▫️ `/restart` - Reincarnate bot\n"
        "▫️ `/remove` - add Keyword in remove /remove \" text \" \n"
        "▫️ `/replace` - add Keyword in replace /replace \" old text \":\" new text \" \n"

        "✧ *News Control* ✧\n"
        "▫️ `/start_news` - Begin updates\n"
        "▫️ `/stop_news` - Pause stream\n\n"
        
        "✧ *Personal Space* ✧\n"
        "▫️ `/dashboard` - Settings altar\n"
        "▫️ `/message` - Contact creator\n\n"
        
        "🌸 *Free Commands* 🌸\n"
        "▫️ `/tutorial`"


    )

def subscribed_help(username: str) -> str:
    return (
        f"💮 *{username}-sama's Menu* 💮\n\n"
        "✧ *News Control* ✧\n"
        "▫️ `/start_news` - Begin updates\n"
        "▫️ `/stop_news` - Pause stream\n\n"
        
        "✧ *Personal Space* ✧\n"
        "▫️ `/dashboard` - Settings altar\n"
        "▫️ `/message` - Contact creator\n\n"
        
        "🌸 *Free Commands* 🌸\n"
        "▫️ `/tutorial`"
    )

def unsubscribed_help(username: str) -> str:
    return (
        f"🌼 *{username}-chan's Options* 🌼\n\n"
        "✧ *Basic* ✧\n"
        "▫️ `/start` - Begin journey\n"
        "▫️ `/subscribe` - Unlock magic\n\n"
        
        "✧ *Preview* ✧\n"
        "▫️ `/sample_news` - News example\n"
        
        "💎 *Premium Unlocks* 💎\n"
        "» 24/7 News » Priority Support"
    )