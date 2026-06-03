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

# ── PAGES ─────────────────────────────────────────────────
if page == "Draft Rankings":
    st.title("📋 Draft Rankings")
    st.markdown("Player rankings  based on PPR scoring across the last three seasons")
    st.markdown("---")

    # create two columns, first columns twice as wide as the second column
    col1, col2 = st.columns([2, 1])
    with col1:
        rank_type = st.radio(
            "Ranking Type",
            ["Season Rankings", "Career Rankings (3 year average)"],
            horizontal=True
        )
    with col2:
        show_trending = st.checkbox("Show Trending Players", value=False)

    st.markdown("---")

    # if user chooses season then show them dat for selected season, if not then just show them the averages for the past 3 seasons
    if rank_type == "Season Rankings":
        rankings = get_positional_rankings(weekly_stats, season=selected_season)
    else:
        rankings = get_career_rankings(weekly_stats)
    
    consistency = calculate_consistency(weekly_stats, season=selected_season)

    # show all positions, unless a specific postion has been selected
    positions_to_show = ['QB', 'RB', 'WR', 'TE'] if selected_position == "All" else [selected_position]

    # loop through each position and get the rankings dataframe, and filter the consistency dataframe for each position
    for position in positions_to_show:
        st.subheader(f"{position} Rankings")

        pos_rankings = rankings[position].copy()
        pos_consistency = consistency[consistency['position'] == position][
            # select only the player name and grade column from dataframe
            ['player_name', 'grade']
        ].rename(columns={'grade': 'consistency_grade'})

        # merge consistency dataframe into rankings dataframe using player name to match values
        pos_rankings = pos_rankings.merge(
            pos_consistency,
            on='player_name',
            how='left'
        )

        # create array for columns to display
        display_cols = ['rank', 'player_name', 'avg_ppr_points', 'games_played', 'consistency_grade']
        if rank_type == "Career Rankings (3 year average)":
            display_cols = ['rank', 'player_name', 'avg_ppr_points', 'total_games', 'consistency_grade']

        st.dataframe(
            pos_rankings[display_cols].rename(columns={
                'rank':               'Rank',
                'player_name':        'Player',
                'avg_ppr_points':     'Avg PPR Pts',
                'games_played':       'Games Played',
                'total_games':        'Total Games',
                'consistency_grade':  'Consistency'
            }),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")