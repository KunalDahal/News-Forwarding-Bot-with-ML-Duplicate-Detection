# 🌸 Mizuki News Forwarding Bot

*A sophisticated Telegram bot that aggregates, processes, and forwards anime/news content from source channels to subscribed target channels with duplicate detection and subscription management.*

![Bot Demo](https://via.placeholder.com/800x400.png?text=Mizuki+Bot+Demo)

---

## 🌟 Features

### 🏮 Core Functionality
- **Multi-Channel Forwarding**: Automatically forwards messages from configured source channels to multiple subscribed target channels.
- **Telethon Integration**: Efficient message handling with Telethon library.
- **Media Support**: Handles photos, videos, and media groups with proper caption formatting.

### 🛡️ Content Protection
- **ML-Powered Duplicate Detection**: Uses TF-IDF + Cosine Similarity to prevent duplicate content forwarding.
- **Banned Content Filter**: Blocks messages containing prohibited keywords (ads, spam, etc.).
- **Text Processing**: Cleans and formats messages with emoji filtering and Markdown escaping.

### 💎 Subscription System
- **Tiered Access**: Different command sets for owners, subscribers, and non-subscribers.
- **Channel Ownership**: Prevents channel ID conflicts between users.
- **Expiration Handling**: Automatic subscription expiry checks and notifications.
- **Payment Flow**: Integrated payment verification with UPI/photo proof.

### 🎴 User Experience
- **Japanese-Themed UI**: Beautifully formatted messages with emoji and Markdown.
- **Conversation Locking**: Prevents command conflicts with `command_lock.py`.
- **Dashboard**: `/dashboard` shows subscription status and info.
- **Help System**: `/help` provides rich command descriptions.

### ⚙️ Admin Tools
- **Owner Commands**: `/broadcast`, `/sub_list`, `/syscheck`, `/restart`
- **Message Relay**: `/message` for users, `/m_back` for owner replies
- **Content Moderation**: `/remove` and `/replace` for keyword management

---

## 📥 Installation

```bash
git clone https://github.com/yourusername/news-forwarding-bot.git
cd news-forwarding-bot
pip install -r requirements.txt
```

Create a `.env` file:

```ini
API_ID=your_telegram_api_id
API_HASH=your_telegram_api_hash
BOT_TOKEN=your_bot_token
OWNER_ID=your_user_id
SOURCE_CHANNEL_ID=-1001234567890
```

---

## 📂 Project Structure

```
Newsbot/
├── commands/
│   ├── owner/
│   │   ├── __init__.py  
│   │   ├── broadcast.py  
│   │   ├── counter.py  
│   │   ├── owner_handlers.py  
│   │   ├── owner_to_user.py  
│   │   ├── remove.py  
│   │   ├── replace.py  
│   │   ├── restart.py  
│   │   ├── set_sources.py  
│   │   ├── sub_list.py  
│   │   ├── syscheck.py  
│   │   ├── tutorial.py  
│   │   ├── uuid.py  
│   ├── command_lock.py  
│   ├── dashboard.py  
│   ├── help.py  
│   ├── sample_news.py  
│   ├── start_news.py  
│   ├── start.py  
│   ├── stop_news.py  
│   ├── subscribe.py  
│   ├── user_to_owner.py  
├── Fix/
│   ├── __init__.py  
│   ├── crash.py  
├── forward/
│   ├── model/
│   │   ├── __init__.py  
│   │   ├── data.csv  
│   │   ├── gui.py  
│   │   ├── model.py  
│   │   ├── editor.py  
│   │   ├── handle.py  
│   │   ├── processor.py  
├── logs/
│   ├── __init__.py  
├── scripts/
│   ├── __init__.py  
│   ├── e_checker.py  
│   ├── main.py  
│   ├── session.py  
├── storage/
│   ├── __init__.py  
│   ├── config.py  
│   ├── message.json  
│   ├── remove.json  
│   ├── replace.json  
│   ├── s_source.json  
│   ├── subscriptions.json  
│   ├── target_channel.json  
│   ├── timezone.py  
├── launcher.py  
├── README.md  
├── requirements.txt  
```

---
## 🧠 Machine Learning Integration

- **Duplicate Detection**: Uses `TF-IDF + Cosine Similarity`.
- **Training GUI**: Launch `python gui.py` to manage datasets.
- **Live Filtering**: ML is integrated with forwarding pipeline to reject duplicate news.
- **Future Work**: Neural networks, multilingual models.

---

## 🧵 Commands Reference

### 🧑 User Commands

| Command         | Description                                |
|----------------|--------------------------------------------|
| `/start`        | Bot greeting and registration              |
| `/help`         | Displays help text                         |
| `/subscribe`    | Begins subscription flow                   |
| `/dashboard`    | Shows current subscription status          |
| `/start_news`   | Starts news forwarding to user's channel   |
| `/stop_news`    | Stops news forwarding                      |
| `/sample_news`  | Sends a sample formatted news message      |
| `/message`      | Sends message to owner                     |

### 👑 Owner-Only Commands

| Command         | Description                                |
|----------------|--------------------------------------------|
| `/set_source`   | Set the source channel to forward from     |
| `/broadcast`    | Send broadcast message to all subscribers  |
| `/sub_list`     | Lists all current subscriptions            |
| `/restart`      | Restarts the bot                           |
| `/syscheck`     | Checks system and config status            |
| `/m_back`       | Replies to a user message                  |
| `/remove`       | Remove banned words                        |
| `/replace`      | Replace specific words in content          |
| `/uuid`         | List subscription UUIDs                    |

---

## 🎌 Theming & UX

- 🏯 Temple: Notices
- 🌸 Sakura: Success
- 🌙 Moon: Inactive
- 🎐 Wind chime: Notifications

Example formatted message:

```python
await update.message.reply_text(
    "▰▰▰▰▰▰▰▰▰▰▰▰▰\n"
    "🌸 *Yatta!* Operation successful!\n"
    "⌜ Your request has been processed ⌟\n"
    "▰▰▰▰▰▰▰▰▰▰▰▰▰\n",
    parse_mode='Markdown'
)
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit and push your changes
4. Open a pull request

---

## 📜 License

MIT License. See `LICENSE` for full details.

> *"Like cherry blossoms in spring, may your news flow beautifully." 🎴*
>>>>>>> 3707b65 (addded full folder)
