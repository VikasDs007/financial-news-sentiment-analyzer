import os
import time
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


def _load_newsdata_key() -> str:
    """Load NEWSDATA_KEY from Streamlit secrets or environment.

    Prefer Streamlit secrets first, then environment variable. Raise helpful error if missing.
    """
    try:
        import streamlit as st

        key = st.secrets.get("NEWSDATA_KEY")
        if key:
            return key
    except Exception:
        # fall back to environment variable
        pass

    key = os.getenv("NEWSDATA_KEY")
    if key:
        return key

    raise ValueError(
        "NEWSDATA_KEY not found. Set NEWSDATA_KEY in .streamlit/secrets.toml or environment variable."
    )


NEWSDATA_KEY: str | None = None
try:
    NEWSDATA_KEY = _load_newsdata_key()
except Exception:
    # Keep None to allow optional India functionality to surface clear errors when used
    NEWSDATA_KEY = None


def fetch_headlines(categories=None, page_size=100):
    if categories is None:
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
            "pageSize": page_size,
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
                    "region": "Global",
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


def fetch_india_headlines():
    """Fetch India headlines from NewsData.io and return DataFrame with region='India'.

    Uses NEWSDATA_KEY from secrets or env. Parses `results` array.
    NOTE: Do NOT pass `page` or `page_size` — NewsData.io /1/news endpoint doesn't accept them.
    """
    if not NEWSDATA_KEY:
        raise ValueError(
            "NEWSDATA_KEY not configured. Add NEWSDATA_KEY to .streamlit/secrets.toml or set environment variable."
        )

    endpoint = "https://newsdata.io/api/1/news"
    params = {
        "apikey": NEWSDATA_KEY,
        "country": "in",
        "language": "en",
        "category": "business,technology",
    }

    rows = []
    try:
        response = requests.get(endpoint, params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()
    except Exception as exc:
        raise

    for article in payload.get("results", []):
        title = article.get("title")
        description = article.get("description") or ""
        source = article.get("source_id")
        published = article.get("pubDate")
        category = None
        try:
            cats = article.get("category") or []
            if isinstance(cats, list) and len(cats) > 0:
                category = cats[0]
        except Exception:
            category = None

        rows.append(
            {
                "title": title,
                "description": description,
                "source": source,
                "publishedAt": published,
                "category": category,
                "url": article.get("link"),
                "region": "India",
            }
        )

    df = pd.DataFrame(rows)
    df["fetched_at"] = datetime.now().isoformat()

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    cache_path = os.path.join(data_dir, "india_news_cache.csv")
    df.to_csv(cache_path, index=False)

    return df


def load_headlines(force_refresh: bool = False):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cache_path = os.path.join(base_dir, "data", "news_cache.csv")
    # If force_refresh is True, skip the cache and fetch fresh data
    if not force_refresh and os.path.exists(cache_path):
        mod_time = os.path.getmtime(cache_path)
        age_minutes = (time.time() - mod_time) / 60
        if age_minutes < 30:
            return pd.read_csv(cache_path)

    return fetch_headlines(["business", "technology", "science"])


def load_india_headlines(force_refresh: bool = False):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cache_path = os.path.join(base_dir, "data", "india_news_cache.csv")
    # If force_refresh is True, skip the cache and fetch fresh data
    if not force_refresh and os.path.exists(cache_path):
        mod_time = os.path.getmtime(cache_path)
        age_minutes = (time.time() - mod_time) / 60
        if age_minutes < 30:
            return pd.read_csv(cache_path)

    return fetch_india_headlines()
