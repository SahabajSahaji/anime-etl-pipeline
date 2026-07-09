from __future__ import annotations

import json
import sqlite3
import sys
from html import escape
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import DATABASE_FILE, RAW_DIR


st.set_page_config(
    page_title="Anime Analytics Dashboard",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)


COLORWAY = ["#ff4d6d", "#3a86ff", "#ffbe0b", "#06d6a0", "#8338ec", "#fb5607"]
PLACEHOLDER_IMAGE = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
    "viewBox='0 0 200 300'%3E%3Crect width='200' height='300' "
    "fill='%23111521'/%3E%3Cpath d='M42 204 82 143l30 43 20-28 "
    "26 46z' fill='%233a86ff' opacity='.55'/%3E%3Ccircle cx='134' "
    "cy='96' r='22' fill='%23ffbe0b' opacity='.7'/%3E%3C/svg%3E"
)


def _clean_text(value: Any, fallback: str = "Unknown") -> str:
    if pd.isna(value):
        return fallback
    text = str(value).strip()
    return text if text else fallback


@st.cache_data(show_spinner=False)
def load_anime_data() -> pd.DataFrame:
    with sqlite3.connect(DATABASE_FILE) as connection:
        frame = pd.read_sql("SELECT * FROM anime", connection)

    numeric_columns = [
        "score",
        "scored_by",
        "MyAnimeList_Rank",
        "popularity",
        "members",
        "favorites",
        "year",
        "episodes",
    ]
    for column in numeric_columns:
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce")

    return frame


@st.cache_data(show_spinner=False)
def load_image_lookup() -> dict[int, str]:
    lookup: dict[int, str] = {}
    for path in sorted(RAW_DIR.glob("anime_page_*.json")):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        for anime in payload.get("data", []):
            mal_id = anime.get("mal_id")
            if not mal_id or mal_id in lookup:
                continue

            jpg = ((anime.get("images") or {}).get("jpg") or {})
            image_url = jpg.get("large_image_url") or jpg.get("image_url")
            if image_url:
                lookup[int(mal_id)] = image_url

    return lookup


def apply_theme(background_url: str | None) -> None:
    background = (
        f'url("{background_url}")'
        if background_url
        else "linear-gradient(135deg, #16141f, #231b2e)"
    )
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

        :root {{
            --panel: rgba(18, 20, 31, 0.82);
            --panel-strong: rgba(13, 15, 24, 0.94);
            --line: rgba(255, 255, 255, 0.13);
            --text-soft: rgba(246, 247, 251, 0.72);
            --pink: #ff4d6d;
            --blue: #3a86ff;
            --gold: #ffbe0b;
            --green: #06d6a0;
        }}

        .stApp {{
            background:
                linear-gradient(90deg, rgba(7, 9, 18, 0.96), rgba(7, 9, 18, 0.78), rgba(7, 9, 18, 0.96)),
                {background};
            background-size: cover;
            background-position: center top;
            background-attachment: fixed;
            color: #f8f9ff;
            font-family: Inter, Segoe UI, sans-serif;
        }}

        .block-container {{
            padding-top: 1.8rem;
            padding-bottom: 3rem;
            max-width: 1440px;
        }}

        [data-testid="stSidebar"] {{
            background: rgba(9, 11, 20, 0.94);
            border-right: 1px solid var(--line);
        }}

        [data-testid="stSidebar"] * {{
            font-family: Inter, Segoe UI, sans-serif;
        }}

        h1, h2, h3 {{
            letter-spacing: 0;
        }}

        .hero {{
            min-height: 330px;
            border: 1px solid var(--line);
            border-radius: 8px;
            overflow: hidden;
            background: rgba(13, 15, 28, 0.88);
            box-shadow: 0 22px 80px rgba(0, 0, 0, 0.35);
            display: grid;
            grid-template-columns: minmax(0, 1.2fr) minmax(340px, 0.8fr);
            gap: 1rem;
            margin-bottom: 1.4rem;
        }}

        .hero-copy {{
            padding: 2.4rem;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}

        .hero-kicker {{
            color: var(--gold);
            font-size: 0.82rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.12rem;
            margin-bottom: 0.65rem;
        }}

        .hero h1 {{
            font-size: clamp(2.4rem, 5vw, 5.2rem);
            line-height: 0.95;
            margin: 0 0 1rem;
            color: #ffffff;
            font-weight: 800;
        }}

        .hero p {{
            max-width: 760px;
            margin: 0;
            color: var(--text-soft);
            font-size: 1.02rem;
            line-height: 1.65;
        }}

        .poster-wall {{
            display: grid;
            grid-template-columns: repeat(3, minmax(90px, 1fr));
            gap: 0.7rem;
            padding: 1rem;
            min-height: 330px;
            align-content: center;
        }}

        .poster-wall img {{
            width: 100%;
            aspect-ratio: 2 / 3;
            object-fit: cover;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.14);
            box-shadow: 0 16px 40px rgba(0, 0, 0, 0.36);
        }}

        .metric-card {{
            border: 1px solid var(--line);
            border-radius: 8px;
            padding: 1rem 1.05rem;
            background: var(--panel);
            min-height: 118px;
            box-shadow: 0 16px 48px rgba(0, 0, 0, 0.23);
        }}

        .metric-label {{
            color: var(--text-soft);
            font-size: 0.78rem;
            text-transform: uppercase;
            letter-spacing: 0.08rem;
            font-weight: 800;
        }}

        .metric-value {{
            color: white;
            font-size: clamp(1.5rem, 2.7vw, 2.35rem);
            font-weight: 800;
            margin-top: 0.5rem;
            line-height: 1;
        }}

        .metric-note {{
            color: rgba(246, 247, 251, 0.62);
            font-size: 0.82rem;
            margin-top: 0.55rem;
        }}

        .section-title {{
            margin: 1.8rem 0 0.7rem;
            color: #ffffff;
            font-size: 1.18rem;
            font-weight: 800;
        }}

        .rank-card {{
            display: grid;
            grid-template-columns: 64px minmax(0, 1fr) auto;
            gap: 0.85rem;
            align-items: center;
            border: 1px solid var(--line);
            border-radius: 8px;
            background: var(--panel-strong);
            padding: 0.65rem;
            margin-bottom: 0.65rem;
        }}

        .rank-card img {{
            width: 64px;
            height: 86px;
            object-fit: cover;
            border-radius: 6px;
            background: #111521;
        }}

        .rank-title {{
            color: #ffffff;
            font-weight: 800;
            line-height: 1.2;
            overflow-wrap: anywhere;
        }}

        .rank-meta {{
            color: var(--text-soft);
            font-size: 0.8rem;
            margin-top: 0.35rem;
        }}

        .rank-score {{
            color: var(--gold);
            font-size: 1.35rem;
            font-weight: 800;
            min-width: 58px;
            text-align: right;
        }}

        div[data-testid="stDataFrame"], div[data-testid="stPlotlyChart"] {{
            border: 1px solid var(--line);
            border-radius: 8px;
            background: rgba(13, 15, 24, 0.72);
            overflow: hidden;
        }}

        @media (max-width: 920px) {{
            .hero {{
                grid-template-columns: 1fr;
            }}

            .hero-copy {{
                padding: 1.45rem;
            }}

            .poster-wall {{
                grid-template-columns: repeat(6, 1fr);
                min-height: auto;
                padding-top: 0;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def chart_layout(fig):
    fig.update_layout(
        template="plotly_dark",
        colorway=COLORWAY,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Inter, Segoe UI, sans-serif", "color": "#f8f9ff"},
        margin={"l": 8, "r": 8, "t": 52, "b": 8},
        legend={"orientation": "h", "y": -0.18},
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.09)", zeroline=False)
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.09)", zeroline=False)
    return fig


def metric_card(label: str, value: str, note: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_rank_cards(frame: pd.DataFrame, value_column: str, value_label: str) -> None:
    for _, row in frame.head(8).iterrows():
        image_url = row.get("image_url") or PLACEHOLDER_IMAGE
        score = row.get(value_column)
        display_score = "N/A" if pd.isna(score) else f"{score:,.2f}"
        title = escape(_clean_text(row.get("title")))
        meta = (
            f"{value_label} | Members {row.get('members', 0):,.0f}"
            if not pd.isna(row.get("members"))
            else value_label
        )
        meta = escape(meta)
        st.markdown(
            f"""
            <div class="rank-card">
                <img src="{image_url}" alt="{title}">
                <div>
                    <div class="rank-title">{title}</div>
                    <div class="rank-meta">{meta}</div>
                </div>
                <div class="rank-score">{display_score}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def explode_names(frame: pd.DataFrame, column: str) -> pd.DataFrame:
    values = frame[["mal_id", column]].dropna().copy()
    values[column] = values[column].astype(str).str.split(",")
    values = values.explode(column)
    values[column] = values[column].astype(str).str.strip()
    return values[values[column].ne("")]


def make_sidebar_filters(frame: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.title("Anime Lens")
    st.sidebar.caption("Shape the dashboard by era, season, score, and genre.")

    valid_years = frame["year"].dropna()
    if valid_years.empty:
        year_range = (0, 0)
    else:
        year_range = (int(valid_years.min()), int(valid_years.max()))

    selected_years = st.sidebar.slider(
        "Release year",
        min_value=year_range[0],
        max_value=year_range[1],
        value=year_range,
        disabled=year_range == (0, 0),
    )

    min_score = st.sidebar.slider("Minimum score", 0.0, 10.0, 0.0, 0.1)
    seasons = sorted(_clean_text(value) for value in frame["season"].dropna().unique())
    selected_seasons = st.sidebar.multiselect("Season", seasons, default=seasons)

    genre_values = explode_names(frame, "genres")
    genres = sorted(genre_values["genres"].unique()) if not genre_values.empty else []
    selected_genres = st.sidebar.multiselect("Genre", genres)

    filtered = frame.copy()
    if year_range != (0, 0):
        filtered = filtered[
            filtered["year"].isna()
            | filtered["year"].between(selected_years[0], selected_years[1])
        ]
    filtered = filtered[filtered["score"].isna() | filtered["score"].ge(min_score)]
    if selected_seasons:
        filtered = filtered[filtered["season"].fillna("").isin(selected_seasons)]
    if selected_genres:
        genre_mask = filtered["genres"].fillna("").apply(
            lambda value: any(genre in [part.strip() for part in value.split(",")] for genre in selected_genres)
        )
        filtered = filtered[genre_mask]

    return filtered


df = load_anime_data()
image_lookup = load_image_lookup()
df["image_url"] = df["mal_id"].map(image_lookup)

hero_candidates = (
    df.dropna(subset=["image_url", "score"])
    .sort_values(["members", "score"], ascending=[False, False])
    .head(6)
)
background_url = (
    hero_candidates.iloc[0]["image_url"] if not hero_candidates.empty else None
)
apply_theme(background_url)

filtered_df = make_sidebar_filters(df)

poster_html = "".join(
    f'<img src="{row.image_url}" alt="{escape(_clean_text(row.title))}">'
    for row in hero_candidates.itertuples()
)

st.markdown(
    f"""
    <section class="hero">
        <div class="hero-copy">
            <div class="hero-kicker">Jikan x MyAnimeList ETL</div>
            <h1>Anime Analytics Dashboard</h1>
            <p>
                Explore rankings, genre waves, studio output, fan loyalty, and hidden gems
                across the anime catalog. The visuals use cover art from the raw API snapshot
                so the dashboard feels connected to the data it is analyzing.
            </p>
        </div>
        <div class="poster-wall">{poster_html}</div>
    </section>
    """,
    unsafe_allow_html=True,
)

score_available = filtered_df["score"].notna().sum()
avg_score = filtered_df["score"].mean()
total_members = filtered_df["members"].fillna(0).sum()
genre_count = explode_names(filtered_df, "genres")["genres"].nunique()

metric_columns = st.columns(4)
with metric_columns[0]:
    metric_card("Total Anime", f"{len(filtered_df):,}", "records in the current view")
with metric_columns[1]:
    metric_card("Average Score", "N/A" if pd.isna(avg_score) else f"{avg_score:.2f}", f"{score_available:,} titles scored")
with metric_columns[2]:
    metric_card("Total Members", f"{total_members:,.0f}", "audience reach on MAL")
with metric_columns[3]:
    metric_card("Genres", f"{genre_count:,}", "distinct genre labels")

left, right = st.columns([1.15, 0.85])

with left:
    st.markdown('<div class="section-title">Release Timeline</div>', unsafe_allow_html=True)
    yearly = (
        filtered_df.dropna(subset=["year"])
        .assign(year=lambda frame: frame["year"].astype(int))
        .groupby("year", as_index=False)
        .size()
        .rename(columns={"size": "count"})
    )
    fig = px.area(yearly, x="year", y="count", markers=True, title="Anime released by year")
    fig.update_traces(line={"width": 3}, fillcolor="rgba(58, 134, 255, 0.22)")
    st.plotly_chart(chart_layout(fig), use_container_width=True)

with right:
    st.markdown('<div class="section-title">Catalog Status</div>', unsafe_allow_html=True)
    status_counts = (
        filtered_df["status"].fillna("Unknown").value_counts().reset_index()
    )
    status_counts.columns = ["status", "count"]
    fig = px.pie(
        status_counts,
        names="status",
        values="count",
        hole=0.58,
        title="Airing status mix",
    )
    st.plotly_chart(chart_layout(fig), use_container_width=True)

chart_a, chart_b = st.columns(2)

with chart_a:
    st.markdown('<div class="section-title">Genre Power Map</div>', unsafe_allow_html=True)
    genre_counts = (
        explode_names(filtered_df, "genres")["genres"]
        .value_counts()
        .head(15)
        .reset_index()
    )
    genre_counts.columns = ["genre", "count"]
    fig = px.bar(
        genre_counts.sort_values("count"),
        x="count",
        y="genre",
        orientation="h",
        title="Most common genres",
        color="count",
        color_continuous_scale=["#3a86ff", "#ff4d6d", "#ffbe0b"],
    )
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(chart_layout(fig), use_container_width=True)

with chart_b:
    st.markdown('<div class="section-title">Score vs Audience</div>', unsafe_allow_html=True)
    scatter = filtered_df.dropna(subset=["score", "members"]).copy()
    scatter["year_label"] = scatter["year"].fillna(0).astype(int).replace(0, "Unknown")
    fig = px.scatter(
        scatter,
        x="members",
        y="score",
        size="favorites",
        color="season",
        hover_name="title",
        hover_data=["year", "genres", "studios"],
        log_x=True,
        title="Audience size, score, and favorites",
    )
    fig.update_traces(marker={"opacity": 0.72, "line": {"width": 0}})
    st.plotly_chart(chart_layout(fig), use_container_width=True)

rank_left, rank_right = st.columns(2)

with rank_left:
    st.markdown('<div class="section-title">Top Rated Anime</div>', unsafe_allow_html=True)
    top_rated = (
        filtered_df.dropna(subset=["score"])
        .sort_values(["score", "members"], ascending=[False, False])
        .head(8)
    )
    render_rank_cards(top_rated, "score", "MAL score")

with rank_right:
    st.markdown('<div class="section-title">Hidden Gems</div>', unsafe_allow_html=True)
    hidden_gems = filtered_df[
        filtered_df["score"].notna()
        & filtered_df["favorites"].notna()
        & filtered_df["popularity"].gt(0)
    ].copy()
    hidden_gems["hidden_gem_score"] = (
        hidden_gems["score"] * hidden_gems["favorites"] / hidden_gems["popularity"]
    )
    hidden_gems = hidden_gems.sort_values("hidden_gem_score", ascending=False)
    render_rank_cards(hidden_gems, "hidden_gem_score", "hidden gem score")

studio_col, season_col = st.columns(2)

with studio_col:
    st.markdown('<div class="section-title">Studio Standouts</div>', unsafe_allow_html=True)
    studio_stats = (
        filtered_df.dropna(subset=["score"])
        .assign(studios=lambda frame: frame["studios"].fillna("").str.split(","))
        .explode("studios")
    )
    studio_stats["studios"] = studio_stats["studios"].astype(str).str.strip()
    studio_stats = studio_stats[studio_stats["studios"].ne("")]
    studio_stats = (
        studio_stats.groupby("studios", as_index=False)
        .agg(avg_score=("score", "mean"), anime_count=("mal_id", "count"))
        .query("anime_count >= 5")
        .sort_values("avg_score", ascending=False)
        .head(14)
    )
    fig = px.scatter(
        studio_stats,
        x="anime_count",
        y="avg_score",
        size="anime_count",
        color="avg_score",
        hover_name="studios",
        title="Studios with at least 5 scored titles",
        color_continuous_scale=["#06d6a0", "#ffbe0b", "#ff4d6d"],
    )
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(chart_layout(fig), use_container_width=True)

with season_col:
    st.markdown('<div class="section-title">Seasonal Mood</div>', unsafe_allow_html=True)
    season_order = ["winter", "spring", "summer", "fall"]
    seasonal = (
        filtered_df.dropna(subset=["season", "score"])
        .groupby("season", as_index=False)
        .agg(avg_score=("score", "mean"), anime_count=("mal_id", "count"))
    )
    seasonal["season"] = pd.Categorical(seasonal["season"], season_order, ordered=True)
    seasonal = seasonal.sort_values("season")
    fig = px.bar(
        seasonal,
        x="season",
        y="avg_score",
        color="anime_count",
        title="Average score by release season",
        color_continuous_scale=["#3a86ff", "#8338ec", "#ff4d6d"],
        text="anime_count",
    )
    fig.update_traces(texttemplate="%{text:,} titles", textposition="outside")
    fig.update_layout(coloraxis_showscale=False)
    st.plotly_chart(chart_layout(fig), use_container_width=True)

st.markdown('<div class="section-title">Explore The Dataset</div>', unsafe_allow_html=True)
columns = [
    "title",
    "score",
    "members",
    "favorites",
    "popularity",
    "year",
    "season",
    "studios",
    "genres",
]
st.dataframe(
    filtered_df[columns]
    .sort_values(["score", "members"], ascending=[False, False], na_position="last")
    .head(250),
    use_container_width=True,
    hide_index=True,
)
