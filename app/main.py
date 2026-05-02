"""Streamlit dashboard for the Financial News Sentiment Analyzer."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.fetcher import load_headlines, load_india_headlines
from src.sentiment import analyze_headlines


st.set_page_config(
    page_title="Financial News Sentiment Analyzer",
    page_icon="📈",
    layout="wide",
)

THEME_CSS = """
<style>
    :root {
        --bg: #0d0d1e;
        --card: rgba(17, 21, 41, 0.92);
        --accent: #e94560;
        --bullish: #00c853;
        --bearish: #e94560;
        --neutral: #ffab00;
        --text: #f5f7ff;
        --muted: rgba(245, 247, 255, 0.72);
        --border: rgba(233, 69, 96, 0.42);
    }

    .stApp {
        background: radial-gradient(circle at top left, rgba(233, 69, 96, 0.14), transparent 28%),
                    radial-gradient(circle at top right, rgba(0, 200, 83, 0.12), transparent 24%),
                    linear-gradient(180deg, #101126 0%, #0d0d1e 100%);
        color: var(--text);
        font-family: "Segoe UI", "Inter", "Helvetica Neue", sans-serif;
    }

    .hero {
        padding: 2rem 2rem 1.5rem 2rem;
        border: 1px solid #e94560;
        border-radius: 22px;
        background: linear-gradient(135deg, #1a0a2e 0%, #16213e 50%, #0f3460 100%);
        box-shadow: 0 18px 40px rgba(0, 0, 0, 0.35);
        margin-bottom: 1.2rem;
    }

    .hero h1 {
        margin: 0;
        font-size: 2.3rem;
        line-height: 1.1;
        color: var(--text);
    }

    .hero p {
        margin: 0.55rem 0 0 0;
        color: var(--muted);
        font-size: 1.02rem;
    }

    .banner-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 0.85rem;
        margin-top: 1.25rem;
    }

    .stat-card, .sector-card, .panel-card {
        background: var(--card);
        border-radius: 18px;
        border: 1px solid var(--border);
        box-shadow: 0 12px 26px rgba(0, 0, 0, 0.24);
    }

    .stat-card {
        padding: 1rem 1.05rem;
        border-top-width: 3px;
    }

    .stat-label {
        font-size: 0.82rem;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        color: var(--muted);
        margin-bottom: 0.35rem;
    }

    .stat-value {
        font-size: 1.6rem;
        font-weight: 700;
        margin-bottom: 0.15rem;
    }

    .stat-value.total-headlines {
        color: white;
    }

    .stat-value.bullish {
        color: #00c853;
    }

    .stat-value.bearish {
        color: #e94560;
    }

    .stat-value.neutral {
        color: #ffab00;
    }

    .stat-subtext {
        font-size: 0.85rem;
        color: var(--muted);
    }

    .section-title {
        margin: 1.4rem 0 0.75rem 0;
        font-size: 1.2rem;
        font-weight: 700;
        color: var(--text);
    }

    .sector-card {
        padding: 1rem 1.05rem;
        margin-bottom: 0.85rem;
        border-top-width: 3px;
    }

    .sector-name {
        font-size: 1.05rem;
        font-weight: 700;
        margin-bottom: 0.35rem;
        color: var(--text);
    }

    .sector-meta {
        color: var(--muted);
        font-size: 0.9rem;
        line-height: 1.55;
    }

    .footer {
        margin-top: 1.5rem;
        padding: 1rem 0 0.5rem 0;
        color: var(--muted);
        text-align: center;
        font-size: 0.92rem;
        border-top: 1px solid rgba(255, 255, 255, 0.08);
    }

    div[data-testid="stSidebar"] {
        background: linear-gradient(180deg, rgba(13, 13, 30, 0.98), rgba(17, 21, 41, 0.98));
        border-right: 1px solid rgba(233, 69, 96, 0.18);
    }

    div[data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(233, 69, 96, 0.28);
        border-radius: 16px;
        padding: 0.45rem 0.7rem;
    }

    .stDataFrame {
        border: 1px solid rgba(233, 69, 96, 0.24);
        border-radius: 14px;
        overflow: hidden;
    }
</style>
"""

st.markdown(THEME_CSS, unsafe_allow_html=True)


def load_dashboard_data(refresh_token: int) -> pd.DataFrame:
    """Load and enrich headlines for the dashboard."""
    _ = refresh_token
    raw_df = load_headlines()
    analyzed_df = analyze_headlines(raw_df)
    if analyzed_df is None:
        return pd.DataFrame()
    return analyzed_df.copy()


@st.cache_data(ttl=1800, show_spinner=False)
def cached_dashboard_data(refresh_token: int) -> pd.DataFrame:
    return load_dashboard_data(refresh_token)


@st.cache_data(ttl=1800, show_spinner=False)
def cached_india_data(refresh_token: int) -> pd.DataFrame:
    # load_india_headlines returns raw India headlines; analyze and return
    try:
        raw = load_india_headlines()
        analyzed = analyze_headlines(raw)
        return analyzed if analyzed is not None else pd.DataFrame()
    except Exception:
        return pd.DataFrame()


def sentiment_badge_style(label: str) -> str:
    if label == "Bullish":
        return "background: rgba(0, 200, 83, 0.16); color: #00ff88;"
    if label == "Bearish":
        return "background: rgba(233, 69, 96, 0.16); color: #ff8aa0;"
    return "background: rgba(255, 171, 0, 0.16); color: #ffd166;"


def sentiment_color(label: str) -> str:
    if label == "Bullish":
        return "#00c853"
    if label == "Bearish":
        return "#e94560"
    return "#ffab00"


def apply_date_filter(df: pd.DataFrame, date_choice: str) -> pd.DataFrame:
    if date_choice == "All available":
        return df
    now = pd.Timestamp.utcnow()
    if date_choice == "Last 24 hours":
        cutoff = now - pd.Timedelta(days=1)
    elif date_choice == "Last 3 days":
        cutoff = now - pd.Timedelta(days=3)
    else:
        cutoff = now - pd.Timedelta(days=7)

    pub = pd.to_datetime(df.get("publishedAt"), errors="coerce", utc=True)
    return df[pub >= cutoff].copy()


def mood_from_score(score: float) -> str:
    if score >= 0.05:
        return "Bullish"
    if score <= -0.05:
        return "Bearish"
    return "Neutral"


def format_percentage(value: float) -> str:
    return f"{value:.1f}%"


def render_heading(text: str) -> None:
    st.markdown(
        f"<div style='font-size:1.4rem;font-weight:700;color:white;margin:1rem 0 0.5rem 0;'>{text}</div>",
        unsafe_allow_html=True,
    )


def render_stat_card(label: str, value: str, subtext: str, accent: str) -> None:
    value_text, value_class = value.rsplit("|", 1)
    st.markdown(
        f"""
        <div class="stat-card" style="border-top-color: {accent};">
            <div class="stat-label">{label}</div>
            <div class="stat-value {value_class}">{value_text}</div>
            <div class="stat-subtext">{subtext}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sector_card(sector_name: str, dominant_sentiment: str, article_count: int, average_score: float) -> None:
    accent = sentiment_color(dominant_sentiment)
    st.markdown(
        f"""
        <div class="sector-card" style="border-top-color: {accent};">
            <div class="sector-name">{sector_name}</div>
            <div class="sector-meta">
                Dominant sentiment: <strong>{dominant_sentiment}</strong><br />
                Article count: <strong>{article_count}</strong><br />
                Average score: <strong>{average_score:.3f}</strong>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def style_headline_table(frame: pd.DataFrame) -> pd.io.formats.style.Styler:
    styled = frame.style.format({"Score": "{:.3f}"})
    styled = styled.apply(
        lambda row: [
            sentiment_badge_style(row["Sentiment"]) if column == "Sentiment" else ""
            for column in row.index
        ],
        axis=1,
    )
    styled = styled.set_properties(**{"color": "white", "background-color": "rgba(255,255,255,0.02)"})
    styled = styled.set_table_styles(
        [
            {"selector": "th", "props": [("background-color", "#15182c"), ("color", "white"), ("border", "1px solid rgba(233, 69, 96, 0.18)")]},
            {"selector": "td", "props": [("border", "1px solid rgba(233, 69, 96, 0.10)")]},
        ]
    )
    return styled


def main() -> None:
    refresh_token = st.session_state.get("refresh_token", 0)

    with st.sidebar:
        st.markdown("### Controls")
        if st.button("Refresh Data", width="stretch"):
            st.session_state["refresh_token"] = refresh_token + 1
            st.cache_data.clear()
            st.rerun()

        with st.spinner("Fetching latest financial news..."):
            df = cached_dashboard_data(st.session_state.get("refresh_token", 0))

        if df.empty:
            st.warning("No headlines available right now.")
            st.stop()

        if "sector" not in df.columns:
            st.error("Sentiment analysis output is missing the sector column.")
            st.stop()

        sectors = sorted(df["sector"].dropna().unique().tolist())
        sentiments = ["Bullish", "Bearish", "Neutral"]

        sector_choice = st.multiselect(
            "Sector filter",
            options=["All sectors"] + sectors,
            default=["All sectors"],
        )
        sentiment_choice = st.multiselect(
            "Sentiment filter",
            options=["All labels"] + sentiments,
            default=["All labels"],
        )

        if "All sectors" in sector_choice or not sector_choice:
            selected_sectors = sectors
        else:
            selected_sectors = sector_choice

        if "All labels" in sentiment_choice or not sentiment_choice:
            selected_sentiments = sentiments
        else:
            selected_sentiments = sentiment_choice

        latest_timestamp = pd.to_datetime(df["fetched_at"], errors="coerce").max()
        last_updated = (
            latest_timestamp.strftime("%Y-%m-%d %H:%M:%S") if pd.notna(latest_timestamp) else "Unknown"
        )

        st.markdown("---")
        st.caption("Dataset stats")
        st.write(f"Headlines: {len(df)}")
        st.write(f"Sectors: {df['sector'].nunique()}")
        st.write(f"Sources: {df['source'].nunique()}")
        st.write(f"Last updated: {last_updated}")

        date_choice = st.radio(
            "Show news from:",
            ["Last 24 hours", "Last 3 days", "Last 7 days", "All available"],
            index=3,
        )

    # load India data as well
    india_raw = cached_india_data(st.session_state.get("refresh_token", 0))


    # Apply basic sector/sentiment filters, then date filtering per tab
    global_df = df.copy()
    india_df = india_raw.copy()

    def apply_filters(df_in: pd.DataFrame) -> pd.DataFrame:
        df_out = df_in[df_in["sector"].isin(selected_sectors) & df_in["sentiment_label"].isin(selected_sentiments)].copy()
        df_out = apply_date_filter(df_out, date_choice)
        return df_out

    filtered_global = apply_filters(global_df)
    filtered_india = apply_filters(india_df)

    tab1, tab2 = st.tabs(["🌍 Global", "🇮🇳 India"])

    def render_region(region_df: pd.DataFrame, region_name: str):
        st.markdown(
            """
            <div class="hero">
                <div style='font-size:2rem;font-weight:700;color:white;margin-bottom:0.5rem;'>📈 Financial News Sentiment Analyzer</div>
                <div style='color:rgba(245,247,255,0.72);font-size:1.02rem;'>Real-time market mood powered by AI + NLP</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if region_df.empty:
            st.warning("No headlines match the selected filters for this region.")
            return

        # Data as of: latest publishedAt
        pub_dates = pd.to_datetime(region_df.get("publishedAt"), errors="coerce", utc=True)
        latest_pub = pub_dates.max()
        latest_str = latest_pub.strftime("%d %b %Y %H:%M") if pd.notna(latest_pub) else "Unknown"

        overall_score = region_df["sentiment_score"].mean()
        mood = mood_from_score(overall_score)
        bullish_pct = (region_df["sentiment_label"].eq("Bullish").mean()) * 100
        bearish_pct = (region_df["sentiment_label"].eq("Bearish").mean()) * 100
        mood_color = sentiment_color(mood)

        banner_cols = st.columns(4)
        with banner_cols[0]:
            render_stat_card(
                "Total Headlines analyzed today",
                f"{len(region_df)}|total-headlines",
                f"{len(selected_sectors)} sector(s) selected",
                "#e94560",
            )
        with banner_cols[1]:
            render_stat_card(
                "% Bullish",
                f"{format_percentage(bullish_pct)}|bullish",
                "Bullish sentiment share",
                "#00c853",
            )
        with banner_cols[2]:
            render_stat_card(
                "% Bearish",
                f"{format_percentage(bearish_pct)}|bearish",
                "Bearish sentiment share",
                "#e94560",
            )
        with banner_cols[3]:
            render_stat_card(
                "Overall Market Mood",
                f"{mood}|{mood.lower()}",
                f"Average score: {overall_score:.3f}",
                mood_color,
            )

        # Data as of timestamp
        st.markdown(
            f"<div style='text-align:center;color:#aaa;font-size:0.8rem;margin-top:0.5rem;'>Data as of: {latest_str} UTC</div>",
            unsafe_allow_html=True,
        )

        render_heading("Sector Sentiment Cards")
        sector_rows = []
        for sector_name, sector_df in region_df.groupby("sector", dropna=False):
            dominant_sentiment = sector_df["sentiment_label"].value_counts().idxmax()
            article_count = int(len(sector_df))
            average_score = float(sector_df["sentiment_score"].mean())
            sector_rows.append((sector_name, dominant_sentiment, article_count, average_score))

        sector_rows = sorted(sector_rows, key=lambda item: item[0])
        for start in range(0, len(sector_rows), 3):
            columns = st.columns(min(3, len(sector_rows) - start))
            for column, payload in zip(columns, sector_rows[start : start + len(columns)]):
                with column:
                    render_sector_card(*payload)

        render_heading("Top Headlines")
        display_df = region_df.copy()
        display_df["publishedAt"] = pd.to_datetime(display_df["publishedAt"], errors="coerce", utc=True)
        display_df = display_df.sort_values(["publishedAt", "sentiment_score"], ascending=[False, False]).head(20)
        # Add formatted Published column
        display_df["Published"] = display_df["publishedAt"].dt.strftime("%d %b %Y %H:%M")
        display_df = display_df[
            ["Published", "title", "source", "sector", "sentiment_label", "sentiment_score"]
        ].rename(
            columns={
                "title": "Title",
                "source": "Source",
                "sector": "Sector",
                "sentiment_label": "Sentiment",
                "sentiment_score": "Score",
            }
        )
        st.dataframe(style_headline_table(display_df), width="stretch", hide_index=True)

        render_heading("Sentiment Charts")
        chart_left, chart_right = st.columns(2)

        sentiment_counts = region_df["sentiment_label"].value_counts().reindex(["Bullish", "Bearish", "Neutral"]).fillna(0)
        pie_fig = go.Figure(
            data=[
                go.Pie(
                    labels=sentiment_counts.index.tolist(),
                    values=sentiment_counts.values.tolist(),
                    hole=0.35,
                    marker=dict(colors=["#00c853", "#e94560", "#ffab00"]),
                    textinfo="label+percent",
                )
            ]
        )
        pie_fig.update_layout(
            title="Sentiment Distribution",
            plot_bgcolor="#0d0d1e",
            paper_bgcolor="#0d0d1e",
            font=dict(color="white", family="sans-serif"),
            margin=dict(l=20, r=20, t=60, b=20),
            showlegend=True,
        )

        sector_avg = region_df.groupby("sector", as_index=False)["sentiment_score"].mean().sort_values("sentiment_score")
        bar_fig = px.bar(
            sector_avg,
            x="sector",
            y="sentiment_score",
            color="sentiment_score",
            color_continuous_scale=["#e94560", "#ffab00", "#00c853"],
            title="Average Sentiment by Sector",
            labels={"sector": "Sector", "sentiment_score": "Average Sentiment Score"},
        )
        bar_fig.update_layout(
            plot_bgcolor="#0d0d1e",
            paper_bgcolor="#0d0d1e",
            font=dict(color="white", family="sans-serif"),
            margin=dict(l=20, r=20, t=60, b=20),
            coloraxis_colorbar=dict(title="Score"),
        )
        bar_fig.update_xaxes(gridcolor="rgba(255,255,255,0.08)")
        bar_fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)")

        with chart_left:
            st.plotly_chart(pie_fig, width="stretch")
        with chart_right:
            st.plotly_chart(bar_fig, width="stretch")

    with tab1:
        render_region(filtered_global, "Global")

    with tab2:
        st.markdown(
            "<div style='font-size:0.9rem;color:#bbb;margin-bottom:1rem;'>Sources: Economic Times, Times of India, Business Standard and more</div>",
            unsafe_allow_html=True,
        )
        render_region(filtered_india, "India")

    st.markdown(
        """
        <div class="footer">
            Built by Vikas Chaurasia · Data Analyst | AI-Powered Analytics ·
            <a href="https://www.linkedin.com/in/vikasds007/" target="_blank" style="color:#e94560; text-decoration:none;">LinkedIn</a>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
