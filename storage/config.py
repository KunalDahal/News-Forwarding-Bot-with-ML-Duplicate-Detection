import os
import json
from dotenv import load_dotenv
import logging
load_dotenv()
logger = logging.getLogger(__name__)
BOT_TOKEN = os.getenv("BOT_TOKEN")
SOURCE_CHANNEL_ID = int(os.getenv("SOURCE_CHANNEL_ID"))
BASE_DIR = r"Y:\CODIII\PROJECT\News_Forwarding_bot\storage"
SUBSCRIPTION_FILE = os.path.join(BASE_DIR, "subscriptions.json")
CSV_PATH=r'Y:\CODIII\PROJECT\News_Forwarding_bot\forward\model\data.csv'
TARGET_CHANNEL= os.path.join(BASE_DIR, "target_channel.json")
SUBSCRIPTION_PRICE = "₹299"
GARBAGE_CHANNEL_ID=int(os.getenv("GARBAGE_CHANNEL_ID"))
SUBSCRIPTION_PLANS = f"🌟 Premium Subscription Plans 🌟\n\n- Basic Plan: {SUBSCRIPTION_PRICE}/3 weeks\n(All premium features access)"
TARGET_CHANNEL_ID = os.getenv("TARGET_CHANNEL_ID")
OWNER_ID=int(os.getenv("OWNER_ID"))
UPI_ID=os.getenv("UPI_ID")
SUBSCRIPTION_DAYS = 21  

ALLOWED_EMOJIS = {'💠', '🍀', '🌀', '❄️', '🎂'}
EMOJI_RANGES = [
    (0x1F600, 0x1F64F), (0x1F300, 0x1F5FF), (0x1F680, 0x1F6FF),
    (0x2600, 0x26FF), (0x2700, 0x27BF), (0xFE00, 0xFE0F),
    (0x1F900, 0x1F9FF), (0x1F1E6, 0x1F1FF)
]

from pathlib import Path
MESSAGE_FILE = Path(r"Y:\CODIII\PROJECT\News_Forwarding_bot\storage\message.json")
TARGET_CHANNEL_ID = os.getenv("TARGET_CHANNEL_ID")
TG_PASSWORD= os.getenv("TG_PASSWORD")
API_ID = int(os.getenv('API_ID'))  
API_HASH = os.getenv('API_HASH')  

DATABASE_FILE = os.path.join(BASE_DIR, "s_source.json")

def is_subscribed(user_id: int) -> bool:  # Changed input type to int
    try:
        with open(SUBSCRIPTION_FILE, 'r') as f:
            subscriptions = json.load(f)
    except Exception as e:
        logger.error(f"Error reading subscription file: {e}")
        return False

    # Convert to string to match JSON keys
    user_data = subscriptions.get(str(user_id), {})  # Key fix here
    return user_data.get("subscribed", False)

def load_db_sess():
    """Load session data from a JSON file."""
    if not os.path.exists(DATABASE_FILE):
        return None
    try:
        with open(DATABASE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(f"Error loading session data: {e}")
        return None

def save_db_sess(config):
    """Save session data to a JSON file."""
    try:
        with open(DATABASE_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=4)
    except IOError as e:
        print(f"Error saving session data: {e}")

def load_subscriptions():
    if not os.path.exists(SUBSCRIPTION_FILE):
        with open(SUBSCRIPTION_FILE, 'w') as file:
            json.dump({}, file)
        return {}
    
    with open(SUBSCRIPTION_FILE, 'r') as file:
        try:
            data = json.load(file)
            return data
        except json.JSONDecodeError:
            return {}


def load_json_process(filename):
    """Load and validate JSON files with strict structure checks"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'replace' in filename:
                if isinstance(data, dict) and 'replace' in data:
                    data = data['replace']
                if not isinstance(data, dict):
                    raise ValueError(f"{filename} must contain a dictionary")
                return {str(k): str(v) for k, v in data.items()}
            if 'remove' in filename:
                if isinstance(data, dict) and 'remove' in data:
                    data = data['remove']
                if not isinstance(data, list):
                    raise ValueError(f"{filename} must contain a list")
                return [str(item) for item in data]
            return data
    except Exception as e:
        print(f"Critical error in {filename}: {str(e)}")
        return {} if 'replace' in filename else []
    

def get_all_target_channels():
    subs = load_subscriptions()
    target_channels = set()
    for sub in subs.values():
        if sub.get("subscribed", False):
            channels = sub.get("channels", [])
            target_channels.update(channels)
    return list(target_channels)



def load_json_process(filename):
    """Load and validate JSON files with strict structure checks"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if 'replace' in filename:
                if isinstance(data, dict) and 'replace' in data:
                    data = data['replace']
                if not isinstance(data, dict):
                    raise ValueError(f"{filename} must contain a dictionary")
                return {str(k): str(v) for k, v in data.items()}
            if 'remove' in filename:
                if isinstance(data, dict) and 'remove' in data:
                    data = data['remove']
                if not isinstance(data, list):
                    raise ValueError(f"{filename} must contain a list")
                return [str(item) for item in data]
            return data
    except Exception as e:
        print(f"Critical error in {filename}: {str(e)}")
        return {} if 'replace' in filename else []

REMOVE_WORDS = load_json_process(os.path.join(BASE_DIR, "remove.json"))
REPLACE_WORDS = load_json_process(os.path.join(BASE_DIR, "replace.json"))

def load_subscriptions():
    if not os.path.exists(SUBSCRIPTION_FILE):
        with open(SUBSCRIPTION_FILE, 'w') as file:
            json.dump({}, file)
        return {}
    
    with open(SUBSCRIPTION_FILE, 'r') as file:
        try:
            data = json.load(file)
            return data
        except json.JSONDecodeError:
            return {}
        
def save_subscriptions(data):
    with open(SUBSCRIPTION_FILE, "w") as file:
        json.dump(data, file, indent=4)

REMOVE_PATH=r"Y:\CODIII\PROJECT\News_Forwarding_bot\storage\remove.json"
REPLACE_PATH=r"Y:\CODIII\PROJECT\News_Forwarding_bot\storage\replace.json"