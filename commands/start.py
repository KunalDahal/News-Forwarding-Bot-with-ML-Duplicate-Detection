from telegram import Update
from telegram.ext import CallbackContext
from commands.command_lock import is_locked
from storage.config import is_subscribed
from commands.owner.counter import get_pending_omamori, get_blessed_followers
from storage.config import OWNER_ID 

async def start(update: Update, context: CallbackContext):  
    user = update.effective_user  
    user_id = int(user.id)  
    username = user.first_name  

    # 🎐 Conversation Lock Check  
    if is_locked(user_id):  
        await update.message.reply_text(  
            "▰▰▰▰▰▰▰▰▰▰▰▰▰\n"  
            "🎎 *Our tea ceremony continues...* 🌙\n"  
            "⌜ Finish this *chanoyu* before new rituals ⌟\n\n"  
            "▹ *Matcha must be savored fully* 🫖✨\n" 
            "▰▰▰▰▰▰▰▰▰▰▰▰▰\n",  
            parse_mode='Markdown'  
        )  
        return  

    # 🏯 Goshujin-sama's Sacred Greeting  
    if user_id == OWNER_ID:  
        owner_text = (  
            "▰▰▰▰▰▰▰▰▰▰▰▰▰\n"  
            "🌸 *Mizuki* bows deeply... *kashikomarimashita!* 🧎♀️\n\n"  
            "🌌 *Seichi Jōtai* (Sacred Status):\n"  
            f"▹ Pending Omamori » `{get_pending_omamori()}` 📜\n"  
            f"▹ Blessed Followers » `{get_blessed_followers()}` 🎎\n\n"  
            "🗻 *Your whisper moves mountains...*\n"  
            "▰▰▰▰▰▰▰▰▰▰▰▰▰\n"  
        )  
        await update.message.reply_text(owner_text, parse_mode="Markdown")  
        return  

    try:  
        # 🎋 Subscribed User Path  
        if is_subscribed(user_id):  
            start_text = (    
                "▰▰▰▰▰▰▰▰▰▰▰▰▰\n"  
                f"🏮 *{username}-dono*, welcome back to the twilight garden~ ✨\n"
                "▰▰▰▰▰▰▰▰▰▰▰▰▰\n"    
            )  

        # 🍁 Unsubscribed User Path  
        else:  
            start_text = (  
                "▰▰▰▰▰▰▰▰▰▰▰▰▰\n"    
                f"🌸 *{username}-chan*, I am *Mizuki*—guardian of digital realms 🏯\n\n"  
                "🌙 *You wander through moonlit tsukimi gardens...*\n"  
                "▹ Unlock *hinode privileges* at dawn:\n"  
                "`/subscribe` 🗝️ → Become *jūninin*\n\n"  
                "🎑 *Jūninin no Tokken* 🎑\n"  
                "▹ Unlimited *News* streams 🌊\n"  
                "▹ Priority *supports* offerings 🪔\n\n"  
                "🌸 The path of *sakura* awaits your step...\n"
                "▰▰▰▰▰▰▰▰▰▰▰▰▰\n"    
            )  

        await update.message.reply_text(start_text, parse_mode="Markdown")  

    except Exception as e:  
        print(f"Start Error: {e}")  
        await update.message.reply_text(  
            "▰▰▰▰▰▰▰▰▰▰▰▰▰\n"  
            "🌀 *Yuki-onna* froze our connection... ❄️\n"  
            "▹ Try again under the next full moon 🌕\n",  
            "▰▰▰▰▰▰▰▰▰▰▰▰▰\n", 
            parse_mode="Markdown"  
        )  