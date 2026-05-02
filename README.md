# 📈 Financial News Sentiment Analyzer

> **A real-time AI-powered market intelligence dashboard that analyzes financial news sentiment across Global and Indian markets, with an LLM-powered analyst you can question in plain English.**

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-Live-red?style=flat-square&logo=streamlit)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/LLM-Llama%203%20(Groq)-orange?style=flat-square)](https://groq.com)
[![NLP](https://img.shields.io/badge/NLP-VADER%20Sentiment-green?style=flat-square)](https://github.com/cjhutto/vaderSentiment)
[![Status](https://img.shields.io/badge/Status-Live-brightgreen?style=flat-square)]()

---

## 🎯 The Business Problem

Financial analysts and investors spend hours manually scanning news to gauge market mood. They miss signals buried across hundreds of sources — and by the time a human reads them, the opportunity has moved.

This project answers a real business question:

> *"What is the market mood RIGHT NOW — and which sectors should I be watching?"*

Built as a dual-source intelligence dashboard:
- **Global tab** — US/Global markets via NewsAPI
- **India tab** — Indian markets via NewsData.io (Economic Times, Times of India, Business Standard)

---

## 🚀 Live Demo

> 📌 *[Add your Streamlit Cloud URL here once deployed]*

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🌍 Global + 🇮🇳 India tabs | Separate market intelligence for global and Indian news |
| 📊 Real-time sentiment | VADER NLP scores every headline as Bullish / Bearish / Neutral |
| 🏢 Sector classification | Auto-classifies news into BFSI, Tech, Energy, Retail, Healthcare |
| 🤖 AI Analyst Q&A | Ask plain English questions, get answers backed by actual headlines |
| 📅 Date filtering | Filter by last 24 hours, 3 days, 7 days, or all available |
| ♻️ Auto-refresh | News cached and refreshed every 30 minutes |
| 📥 Data freshness | "Data as of" timestamp on every view |

---

## 🔍 How It Works

### 1. Data Pipeline
```python
# Fetches headlines from two sources
NewsAPI    → Global/US financial news
NewsData.io → India-specific news (ET, TOI, BS)
```

### 2. Sentiment Analysis
Each headline is scored using VADER (Valence Aware Dictionary and sEntiment Reasoner) — optimized for short-form text:

```
score >= 0.05  → Bullish  📈
score <= -0.05 → Bearish  📉
else           → Neutral  ➡️
```

### 3. Sector Classification
Keywords map each article to a sector:
- **BFSI** — bank, RBI, stock, fund, crypto
- **Tech** — AI, software, cloud, startup
- **Energy** — oil, gas, solar, power
- **Retail** — ecommerce, consumer, sales
- **Healthcare** — pharma, hospital, FDA

### 4. AI Analyst Layer
Headlines + sentiment scores are passed as context to **Llama 3 (via Groq API)**. Users ask natural language questions and get answers grounded in today's actual news.

Example questions:
- *"What is the overall market mood today?"*
- *"Which sector looks most concerning?"*
- *"What's happening in the BFSI sector?"*

---

## 📊 Sample Insights (02 May 2026)

| Metric | Global | India |
|--------|--------|-------|
| Headlines analyzed | 98 | 10 |
| Overall mood | 🟢 Bullish (54.1%) | 🔴 Bearish (60%) |
| Top sector | Tech (47 articles) | BFSI (5 articles) |
| Most bullish sector | Retail (0.912) | BFSI (0.330) |

---

## 🛠️ Tech Stack

| Layer | Tools |
|-------|-------|
| Data Sources | NewsAPI, NewsData.io |
| NLP | VADER (nltk), TextBlob |
| AI/LLM | Llama 3.1 via Groq API |
| Visualization | Plotly, Streamlit |
| Language | Python 3.9+ |
| Deployment | Streamlit Cloud |

---

## 📁 Project Structure

```
financial-news-sentiment-analyzer/
│
├── app/
│   └── main.py              # Streamlit dashboard
│
├── src/
│   ├── fetcher.py           # NewsAPI + NewsData.io
│   ├── sentiment.py         # VADER sentiment engine
│   └── llm.py               # Groq/Llama 3 Q&A layer
│
├── data/
│   ├── news_cache.csv       # Global news cache
│   └── india_news_cache.csv # India news cache
│
├── notebooks/
│   └── EDA.ipynb            # Exploratory analysis
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Run Locally

```bash
# Clone the repo
git clone https://github.com/VikasDs007/financial-news-sentiment-analyzer.git
cd financial-news-sentiment-analyzer

# Install dependencies
pip install -r requirements.txt

# Add your API keys
# Create .streamlit/secrets.toml:
# NEWSAPI_KEY = "your_key"
# NEWSDATA_KEY = "your_key"
# GROQ_KEY = "your_key"

# Run the app
streamlit run app/main.py
```

---

## 🔑 API Keys Required

| API | Free Tier | Get Key |
|-----|-----------|---------|
| NewsAPI | 100 requests/day | newsapi.org |
| NewsData.io | 6,000 requests/month | newsdata.io |
| Groq (Llama 3) | Very generous free tier | console.groq.com |

---

## 💡 Key Learnings

1. **VADER outperforms TextBlob for headlines** — short, punchy financial text needs lexicon-based scoring, not ML models
2. **Context window matters for LLMs** — passing structured context (scores + headlines) gives far better answers than raw text dumps
3. **India ≠ Global sentiment** — on 02 May 2026, Indian markets showed 60% Bearish while Global showed 54% Bullish — same day, opposite mood

---

## 🔮 Future Enhancements

- [ ] Historical sentiment tracking — chart mood over 30 days
- [ ] Stock price correlation — link sentiment to NSE/BSE price movement
- [ ] Alert system — notify when sector sentiment crosses a threshold
- [ ] Hindi news support — expand India coverage to vernacular sources
- [ ] WhatsApp/Telegram bot integration

---

## 👤 Author

**Vikas Chaurasia** — Data Analyst | AI-Powered Analytics

[![LinkedIn](https://img.shields.io/badge/LinkedIn-vikasds007-blue?style=flat-square&logo=linkedin)](https://linkedin.com/in/vikasds007)
[![GitHub](https://img.shields.io/badge/GitHub-VikasDs007-black?style=flat-square&logo=github)](https://github.com/VikasDs007)
[![Portfolio](https://img.shields.io/badge/Portfolio-vikasds007.github.io-orange?style=flat-square)](https://vikasds007.github.io)

---

*If this project was useful, a ⭐ on the repo means a lot!*

