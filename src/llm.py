"""LLM integration helpers."""

from __future__ import annotations

import os
from datetime import date

import pandas as pd
import streamlit as st
from groq import Groq


def get_groq_client() -> Groq:
    try:
        key = st.secrets["GROQ_KEY"]
    except Exception:
        key = os.environ.get("GROQ_KEY", "")

    if not key:
        raise ValueError("GROQ_KEY not found in secrets or environment")

    return Groq(api_key=key)


def prepare_context(df: pd.DataFrame, region: str = "Global") -> str:
    today = date.today().strftime("%d %b %Y")
    total = len(df)

    if total == 0:
        return f"Today's {region} Financial News Analysis\nDate: {today}\nNo news data available."

    bullish = len(df[df["sentiment_label"] == "Bullish"])
    bearish = len(df[df["sentiment_label"] == "Bearish"])
    neutral = len(df[df["sentiment_label"] == "Neutral"])

    bull_pct = round(bullish / total * 100, 1)
    bear_pct = round(bearish / total * 100, 1)
    neut_pct = round(neutral / total * 100, 1)

    dominant = df["sentiment_label"].mode()[0]
    avg_score = round(df["sentiment_score"].mean(), 3)

    sector_summary = df.groupby("sector")["sentiment_score"].mean().round(3)
    sector_text = "\n".join([f"  - {s}: {v} avg score" for s, v in sector_summary.items()])

    top_headlines = df.head(30)
    headlines_text = "\n".join(
        [
            f"{i + 1}. [{row['sentiment_label']} {row['sentiment_score']:.3f}] {row['title']} ({row['source']})"
            for i, (_, row) in enumerate(top_headlines.iterrows())
        ]
    )

    context = f"""
Today's {region} Financial News Analysis
Date: {today}
Overall Market Mood: {dominant} (avg score: {avg_score})
Total Headlines Analyzed: {total}

Sentiment Breakdown:
  Bullish: {bull_pct}% ({bullish} articles)
  Bearish: {bear_pct}% ({bearish} articles)
  Neutral: {neut_pct}% ({neutral} articles)

Sector Sentiment Scores:
{sector_text}

Top Headlines with Sentiment:
{headlines_text}
""".strip()

    return context


def ask_analyst(question: str, context: str, region: str = "Global") -> str:
    client = get_groq_client()

    system_prompt = f"""You are an expert financial analyst and market intelligence advisor specializing in {region} markets.

You have access to today's financial news headlines with AI-computed sentiment scores.

Your rules:
- Answer ONLY based on the news context given
- Be specific and cite actual headlines when relevant
- Give actionable insights not just summaries
- Keep answers under 200 words, concise
- Format with bullet points where helpful
- If asked about something not in the data, say clearly: "This is not covered in today's headlines"
- For India tab: reference Indian markets, RBI, BSE, NSE, rupee where relevant
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"""News Context:
{context}

Question: {question}""",
            },
        ],
        max_tokens=400,
        temperature=0.3,
    )

    return response.choices[0].message.content
