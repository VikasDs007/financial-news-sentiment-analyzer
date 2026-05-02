import os
from datetime import datetime, timedelta

import pandas as pd
import requests


def _load_newsapi_key() -> str | None:
    key = os.getenv("NEWSAPI_KEY")
    if key:
        return key

    try:
        import streamlit as st

        return st.secrets.get("NEWSAPI_KEY")
    except Exception:
        return None


NEWSAPI_KEY = _load_newsapi_key()


def fetch_headlines(categories, page_size=100):
    categories = ["business", "technology", "science"]
    endpoint = "https://newsapi.org/v2/top-headlines"
    rows = []

    if not NEWSAPI_KEY:
        raise ValueError(
            "NEWSAPI_KEY not found in environment variables or Streamlit secrets."
        )

    for cat in categories:
        params = {
            "country": "us",
            "category": cat,
            "pageSize": 33,
            "apiKey": NEWSAPI_KEY,
        }
        response = requests.get(endpoint, params=params, timeout=30)
        response.raise_for_status()

        payload = response.json()
        for article in payload.get("articles", []):
            source = article.get("source", {}) or {}
            rows.append(
                {
                    "title": article.get("title"),
                    "description": article.get("description"),
                    "source": source.get("name"),
                    "publishedAt": article.get("publishedAt"),
                    "category": cat,
                    "url": article.get("url"),
                }
            )

    df = pd.DataFrame(rows)
    df["fetched_at"] = datetime.now().isoformat()

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    cache_path = os.path.join(data_dir, "news_cache.csv")
    df.to_csv(cache_path, index=False)

    return df


def load_headlines():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cache_path = os.path.join(base_dir, "data", "news_cache.csv")

    if os.path.exists(cache_path):
        modified_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        if datetime.now() - modified_time < timedelta(minutes=30):
            return pd.read_csv(cache_path)

    return fetch_headlines(["business", "technology", "science"])
