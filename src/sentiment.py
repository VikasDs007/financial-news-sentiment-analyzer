"""Sentiment analysis for financial news headlines."""

import os
import re

import nltk
import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer
from textblob import TextBlob


# Download NLTK data on first run.
# Works on both local and Streamlit Cloud.
nltk_data_dir = os.path.join(os.path.expanduser("~"), "nltk_data")


def ensure_nltk_data():
    packages = [
        "vader_lexicon",
        "punkt",
        "stopwords",
    ]
    for package in packages:
        try:
            nltk.data.find(f"tokenizers/{package}")
        except LookupError:
            try:
                nltk.data.find(f"sentiment/{package}")
            except LookupError:
                nltk.download(package, quiet=True)


ensure_nltk_data()


# Initialize once at module level
_vader = SentimentIntensityAnalyzer()


def clean_text(text):
    """Remove special characters, URLs, and extra spaces from text."""
    if not isinstance(text, str):
        return ""
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+', '', text)
    # Remove special characters but keep spaces
    text = re.sub(r'[^\w\s]', ' ', text)
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)
    # Convert to lowercase and strip
    text = text.lower().strip()
    
    return text


def get_vader_score(text):
    """Get VADER sentiment score for text."""
    if not text or not isinstance(text, str):
        return 0.0

    scores = _vader.polarity_scores(str(text))
    return scores['compound']


def get_sentiment_label(score):
    """Convert sentiment score to label."""
    if score >= 0.05:
        return "Bullish"
    elif score <= -0.05:
        return "Bearish"
    else:
        return "Neutral"


def classify_sector(text):
    """Classify text into financial sectors based on keywords."""
    if not isinstance(text, str):
        return "General"
    
    text_lower = text.lower()
    
    # BFSI sector keywords
    bfsi_keywords = ['bank', 'finance', 'loan', 'rbi', 'stock', 'market', 
                     'invest', 'fund', 'insurance', 'crypto', 'bitcoin', 'rupee']
    
    # Tech sector keywords
    tech_keywords = ['tech', 'ai', 'software', 'apple', 'google', 'microsoft', 
                     'startup', 'cloud', 'data', 'digital', 'computing']
    
    # Energy sector keywords
    energy_keywords = ['oil', 'gas', 'energy', 'solar', 'power', 'coal', 'petroleum']
    
    # Retail sector keywords
    retail_keywords = ['retail', 'ecommerce', 'amazon', 'consumer', 'sales', 'shopping']
    
    # Healthcare sector keywords
    healthcare_keywords = ['health', 'pharma', 'drug', 'hospital', 'fda', 'medical']
    
    # Check which sector keywords match
    if any(keyword in text_lower for keyword in bfsi_keywords):
        return "BFSI"
    elif any(keyword in text_lower for keyword in tech_keywords):
        return "Tech"
    elif any(keyword in text_lower for keyword in energy_keywords):
        return "Energy"
    elif any(keyword in text_lower for keyword in retail_keywords):
        return "Retail"
    elif any(keyword in text_lower for keyword in healthcare_keywords):
        return "Healthcare"
    else:
        return "General"


def analyze_headlines(df):
    """Analyze sentiment and classify sectors for headlines DataFrame."""
    if df is None or (isinstance(df, pd.DataFrame) and df.empty):
        return df
    
    # Create a copy to avoid modifying original
    df = df.copy()
    
    # Combine title and description for analysis
    df['combined_text'] = (df.get('title', '') + ' ' + df.get('description', '')).fillna('')
    
    # Clean text
    df['cleaned_text'] = df['combined_text'].apply(clean_text)
    
    # Calculate sentiment scores
    df['sentiment_score'] = df['cleaned_text'].apply(get_vader_score)
    
    # Get sentiment labels
    df['sentiment_label'] = df['sentiment_score'].apply(get_sentiment_label)
    
    # Classify sectors
    df['sector'] = df['combined_text'].apply(classify_sector)
    
    # Drop intermediate columns
    df = df.drop(columns=['combined_text', 'cleaned_text'], errors='ignore')
    
    return df
