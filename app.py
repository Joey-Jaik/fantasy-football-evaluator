import streamlit as st
import pandas as pd
from data.loader import load_all
from analysis.scoring import calculate_ppr_points
from analysis.rankings import get_positional_rankings, get_career_rankings, get_trending_players
from analysis.consistency import calculate_consistency, get_consistency_by_position
from analysis.injuries import get_durability_summary, get_injury_report, get_current_injury_status
from analysis.matchups import get_defensive_rankings, get_player_matchups, get_best_matchups

# ── PAGE CONFIG ───────────────────────────────────────────
st.set_page_config(
    page_title="Fantasy Football Evaluator",
    page_icon="🏈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── LOAD DATA ─────────────────────────────────────────────
# ensure loaded data is stored in cache so it doesn't need to be retrieved each time page refeshes
@st.cache_data
def load_data():
    weekly_stats, schedule, rosters = load_all()
    scored = calculate_ppr_points(weekly_stats)
    return weekly_stats, schedule, rosters, scored

weekly_stats, schedule, rosters, scored = load_data()

# ── SIDEBAR ───────────────────────────────────────────────
st.sidebar.title("Fantasy Football Evaluator")
st.sidebar.markdown("---")

# create page navigation UI
page = st.sidebar.radio(
    "Navigate",
    ["Draft Rankings", "Player Profile", "Who To Start", "Season Stats"]
)

st.sidebar.markdown("---")
# create a selection box for user to choose season, with most recent season as the default selection
selected_season = st.sidebar.selectbox(
    "Season",
    options=[2024, 2023, 2022],
    index=0
)

# create a selection box for user to choose position, with all positions as the default selection
selected_position = st.sidebar.selectbox(
    "Position",
    options=["All", "QB", "RB", "WR", "TE"],
    index=0
)