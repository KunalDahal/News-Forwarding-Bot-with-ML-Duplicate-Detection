import re
from deep_translator import GoogleTranslator
from forward.editor import format_editor
from storage.config import EMOJI_RANGES, ALLOWED_EMOJIS, REMOVE_WORDS, REPLACE_WORDS

def is_emoji(c):
    cp = ord(c)
    return any(start <= cp <= end for start, end in EMOJI_RANGES)

def custom_escape_markdown(text):
    # Corrected escape_chars without backslash
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    # Only match characters that aren't already escaped
    pattern = r'(?<!\\)([{}])'.format(re.escape(escape_chars))
    return re.sub(pattern, r'\\\1', text)

def process_text(text):
    # Handle empty input gracefully
    if not text:
        return custom_escape_markdown("💠 ~ @Animes_News_Ocean")
    
    # Safely format the text
    try:
        e_text = format_editor(text)
    except Exception as e:
        print(f"Error in format_editor: {e}")
        e_text = text  # Fallback to original text
    
    # Rest of the function remains the same
    try:
        translated = GoogleTranslator(source='it', target='en').translate(e_text)
    except Exception:
        translated = e_text
    
    processed = []
    contains_birthday = "🎂" in e_text

    for line in translated.split('\n'):
        line = ''.join(c for c in line if not (is_emoji(c) and c not in ALLOWED_EMOJIS))
        for old, new in REPLACE_WORDS.items():
            line = re.sub(re.escape(old), new, line, flags=re.IGNORECASE)
        for word in REMOVE_WORDS:
            line = re.sub(re.escape(word), '', line, flags=re.IGNORECASE)
        line = ' '.join(word for word in line.split() if not word.startswith('#'))
        if line.strip():
            processed.append(line.strip().title())

    if not processed:
        return custom_escape_markdown("💠 ~ @Animes_News_Ocean")

    formatted = []
    
    for i, line in enumerate(processed):
        cleaned = line.lstrip()
        while cleaned and (is_emoji(cleaned[0]) or cleaned.startswith('▪')):
            cleaned = cleaned[1:].lstrip()

        if 'Studio' in cleaned or 'Animation Studio' in cleaned:
            formatted_line = f"\n🌀 _*{custom_escape_markdown(cleaned)}*_"
        elif i == 0:
            formatted_line = f"\n❄️ *{custom_escape_markdown(cleaned)}*"
        elif i == 1:
            formatted_line = f"\n🔻 _{custom_escape_markdown(cleaned)}_"
        else:
            formatted_line = custom_escape_markdown(line)
        
        formatted.append(formatted_line)
    
    footer = custom_escape_markdown("💠 ~ @Animes_News_Ocean")
    final_text = '\n'.join(formatted) + f"\n\n> *{footer}*"
    return final_text