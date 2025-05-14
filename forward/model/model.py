import re
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import os
import csv
try: 
    from storage.config import CSV_PATH
except:
    CSV_PATH=r"Y:\CODIII\PROJECT\News_Forwarding_bot\forward\model\data.csv"

def preprocess_text(text):

    text = re.sub(r'http\S+', '', text)

    text = re.sub(r'[^\w\s@#]', '', text)

    text = text.lower()

    text = re.sub(r'\s+', ' ', text).strip()
    return text


def is_banned(text):
    banned_keywords = [
        "purchase","amazon","€","Amazon Prime","¥","$"," Instagram","Steam","Selling"
    ] 
    return any(keyword in text for keyword in banned_keywords)

# Duplicate content checker
def is_duplicate(new_text, existing_texts, threshold=0.72):
    if not existing_texts:
        return False
    
    # Combine existing texts with new text for TF-IDF calculation
    all_texts = existing_texts + [new_text]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(all_texts)
    
    # Calculate cosine similarity between new text and all existing texts
    cosine_similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
    return np.max(cosine_similarities) > threshold

# Main processing function
def process_input(new_text):
    # Load existing data
    if os.path.exists(CSV_PATH):
        # Use engine='python' and skip bad lines if any issues occur
        df = pd.read_csv(CSV_PATH, engine='python', on_bad_lines='skip')
        existing_texts = df['text'].tolist()
    else:
        existing_texts = []
    
    # Preprocess new text
    new_text_processed = preprocess_text(new_text)
    
    # Classification logic
    if is_banned(new_text_processed):
        result = 1
    elif is_duplicate(new_text_processed, existing_texts):
        result = 2
    else:
        result = 0
    
    # Store results if allowed or duplicate
    if result in [0, 1, 2]:
        df_new = pd.DataFrame({'text': [new_text_processed], 'result': [result]})
        df_new.to_csv(CSV_PATH, mode='a', header=not os.path.exists(CSV_PATH),
                      index=False, quoting=csv.QUOTE_ALL)
    
    return result
