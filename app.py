import streamlit as st
import pandas as pd
from data.loader import load_all
from analysis.scoring import calculate_ppr_points
from analysis.rankings import get_positional_rankings, get_career_rankings, get_trending_players
from analysis.consistency import calculate_consistency, get_consistency_by_position
from analysis.injuries import calculate_injury_history, get_durability_summary, get_injury_report, get_current_injury_status
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

        if show_trending:
            st.subheader("📈 Trending Players")
            st.markdown("Players with the biggest improvement or decline from last season to this season")

            trending = get_trending_players(
                weekly_stats,
                position=None if selected_position == "All" else selected_position
            )

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Most Improved**")
                st.dataframe(
                    trending[['player_name', 'position', 'trend']].head(10).rename(columns={
                        'player_name': 'Player',
                        'position':    'Position',
                        'trend':       'Point Change'
                    }),
                    use_container_width=True,
                    hide_index=True
                )
            with col2:
                st.markdown("**Most Declined**")
                st.dataframe(
                    trending[['player_name', 'position', 'trend']].tail(10).rename(columns={
                        'player_name': 'Player',
                        'position':    'Position',
                        'trend':       'Point Change'
                    }),
                    use_container_width=True,
                    hide_index=True
                )

elif page == "Player Profile":
    st.title("Player Profile")
    st.markdown("Detailed stats and analysis for individual players")
    st.markdown("---")

    # get full names from rosters to display in search bar
    full_names = (
        rosters[['player_id', 'first_name', 'last_name']]
        .drop_duplicates(subset=['player_id'])
    )

    # create unique player options using full name and position
    player_options = (
        scored[['player_id', 'position']]
        .drop_duplicates(subset=['player_id'])
    )

    player_options = player_options.merge(
        full_names,
        on='player_id',
        how='left'
    )

    player_options['display'] = (
        player_options['first_name'] + " " +
        player_options['last_name'] +
        " (" + player_options['position'] + ")"
    )

    player_options = player_options.sort_values('display')

    selected_display = st.selectbox(
        "Search for a player",
        options=player_options['display'].tolist()
    )

    selected_id = player_options[
        player_options['display'] == selected_display
    ]['player_id'].iloc[0]

    if selected_display:
        player_data = scored[scored['player_id'] == selected_id]
        player_ids = [selected_id]
        player_roster = rosters[rosters['player_id'].isin(player_ids)]

        if player_data.empty:
            st.warning("No data found for this player")
        else:
            # get player position and team, take from first row only for simplicity
            position = player_data['position'].iloc[0]
            # make sure team is from the players most recent season
            latest_season_data = player_data[player_data['season'] == player_data['season'].max()]
            team = latest_season_data['recent_team'].iloc[0]

            col1, col2, col3 = st.columns([1, 2, 3])

            # if headshot exists then extract it and display
            with col1:
                if not player_roster.empty:
                    headshot = player_roster['headshot_url'].dropna()
                    if not headshot.empty:
                        st.image(headshot.iloc[0], width=150)

            # display player information
            with col2:
                st.markdown(f"### {player_data['player_name'].iloc[0]}")
                st.markdown(f"**Position:** {position}")
                st.markdown(f"**Team:** {team}")

                if not player_roster.empty:
                    years_exp = player_roster['years_exp'].dropna()
                    if not years_exp.empty:
                        st.markdown(f"**Experience:** {int(years_exp.iloc[0])} years")

            # display player stats
            with col3:
                career_avg = player_data['ppr_points'].mean()
                career_total = player_data['ppr_points'].sum()
                total_games = len(player_data)

                st.metric("Avg PPR (3 Seasons)", f"{career_avg:.1f}")
                st.metric("Games Played", total_games)
                st.metric("Total PPR Points", f"{career_total:.1f}")

            st.markdown("---")

            # group data by season, calculate aggregate totals, and display dataframe to user
            st.subheader("Season by Season Stats")
            season_data = (
                player_data.groupby('season')
                .agg(
                    games_played      = ('week', 'count'),
                    avg_ppr_points    = ('ppr_points', 'mean'),
                    total_ppr_points  = ('ppr_points', 'sum'),
                    avg_passing_yds   = ('passing_yards', 'mean'),
                    avg_rushing_yds   = ('rushing_yards', 'mean'),
                    avg_receiving_yds = ('receiving_yards', 'mean'),
                    avg_receptions    = ('receptions', 'mean'),
                    avg_targets       = ('targets', 'mean'),
                )
                .reset_index()
                .round(2)
            )

            st.dataframe(
                season_data.rename(columns={
                    'season': 'Season',
                    'games_played': 'Games',
                    'avg_ppr_points': 'Avg PPR',
                    'total_ppr_points': 'Total PPR',
                    'avg_passing_yds': 'Avg Pass Yds',
                    'avg_rushing_yds': 'Avg Rush Yds',
                    'avg_receiving_yds': 'Avg Rec Yds',
                    'avg_receptions': 'Avg Rec',
                    'avg_targets': 'Avg Targets'
                }),
                use_container_width=True,
                hide_index=True
            )

            st.markdown("---")

            # create line chart that shows a players points scored each week, seperated by season
            st.subheader("Weekly PPR Points")

            import plotly.express as px
            fig = px.line(
                # sort the data by season and then by week
                player_data.sort_values(['season', 'week']),
                x='week',
                y='ppr_points',
                # create a seperate line for each season
                color='season',
                markers=True,
                labels={
                    'week': 'Week',
                    'ppr_points': 'PPR Points',
                    'season': 'Season'
                },
                title=f"{player_data['player_name'].iloc[0]} - Weekly PPR Points by Season"
            )
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='rgba(128, 128, 128, 0.2)')
            )
            st.plotly_chart(fig, use_container_width=True)

            st.markdown("---")

            # determine and display consistency data for this specific player
            st.subheader("Consistency Rating")

            # get all consistency data for this specific player
            consistency_data = calculate_consistency(weekly_stats)
            player_cons = consistency_data[consistency_data['player_id'].isin(player_ids)]

            if not player_cons.empty:
                grade = player_cons['grade'].iloc[0]
                cv = player_cons['cv'].iloc[0]

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Consistency Grade", grade)
                with col2:
                    st.metric("Std Deviation", f"{player_cons['std_ppr_points'].iloc[0]:.2f}")
                with col3:
                    st.metric("Floor (Min)", f"{player_cons['min_ppr_points'].iloc[0]:.1f}")
                with col4:
                    st.metric("Ceiling (Max)", f"{player_cons['max_ppr_points'].iloc[0]:.1f}")
            else:
                st.info("Not enough games to calculate consistency rating (minimum 6 games required)")

            st.markdown("---")

            # display injury history for selected player
            st.subheader("Injury History")

            # get injury data for selected player
            injury_data = calculate_injury_history(weekly_stats, rosters)
            player_injury = injury_data[injury_data['player_id'].isin(player_ids)]

            # create dataframe and display to user
            if not player_injury.empty:
                st.dataframe(
                    player_injury[['season', 'games_played', 'games_missed', 'availability_pct', 'injury_risk']].rename(columns={
                        'season': 'Season',
                        'games_played': 'Games Played',
                        'games_missed': 'Games Missed',
                        'availability_pct': 'Availability %',
                        'injury_risk': 'Injury Risk'
                    }),
                    use_container_width=True,
                    hide_index=True
                )