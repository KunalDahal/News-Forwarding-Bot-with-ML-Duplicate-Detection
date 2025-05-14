import json
from telegram import Update
from telegram.ext import CallbackContext
from storage.config import DATABASE_FILE
async def set_source(update: Update, context: CallbackContext) -> None:  
    # 🏮 Command Syntax Check  
    if len(context.args) < 2:  
        await update.message.reply_text(   
            "🌀 *Sacred Formula:*\n"  
            "`/set_source @channelusername latest_post_id` 🏮\n\n"  
            "▹ Both *channel* and *scroll number* required 📜\n",  
            parse_mode='Markdown'  
        )  
        return  

    username = context.args[0]  
    try:  
        post_id = int(context.args[1])  
    except ValueError:  
        await update.message.reply_text(   
            "❌ *Last message ID* must be *celestial integers*! 🔢\n"  
            "▹ No floating clouds or cherry petals allowed 🌸\n",  
            parse_mode='Markdown'  
        )  
        return  

    # 🎐 Channel Verification  
    try:  
        chat = await context.bot.get_chat(username)  
        channel_id = chat.id  
    except Exception as e:  
        await update.message.reply_text(  
 
            f"🌀 *Failed to glimpse channel*:\n`{e}`\n\n"  
            "▹ Ensure I have *shrine access rights* 🏯\n",  
            parse_mode='Markdown'  
        )  
        return  

    # 🌸 Update Sacred Scrolls (Database)  
    try:  
        with open(DATABASE_FILE, "r") as f:  
            data = json.load(f)  
    except FileNotFoundError:  
        data = {"target_channel": 0, "sources": []}  

    updated = False  
    for source in data["sources"]:  
        if source["source_channel"] == channel_id:  
            source["last_message_id"] = post_id  
            updated = True  
            break  

    if not updated:  
        data["sources"].append({  
            "Username": username,  
            "source_channel": channel_id,  
            "last_message_id": post_id  
        })  

    with open(DATABASE_FILE, "w") as f:  
        json.dump(data, f, indent=4)  

    await update.message.reply_text(     
        f"🌸 *Channel* » @{username} 🏯\n"  
        f"📜 *Last Scroll ID* » `{post_id}`\n\n",
        parse_mode='Markdown'  
    )  