import pandas as pd
from analysis.scoring import calculate_ppr_points, get_season_averages, get_career_averages

# ── CONSTANTS ─────────────────────────────────────────────
POSITIONS = ['QB', 'RB', 'WR', 'TE']
MIN_GAMES = 6

def get_positional_rankings(weekly_stats, season=None):
    # create two dataframes, one that has weekly stats for every player and includes their fantasy points scored, then take that data and create a new dataframe that has players fantasy points season averages
    scored = calculate_ppr_points(weekly_stats)
    season_avgs = get_season_averages(scored)

    # if a season was included as argument, then filter season averages dataframe to just include data for that season
    if season:
        season_avgs = season_avgs[season_avgs['season'] == season]

    # only include data for players that have played min number of games to ensure accurate data
    season_avgs = season_avgs[season_avgs['games_played'] >= MIN_GAMES]

    rankings = {}
    # go through each position, create a dataframe that just has season averages for that position, sort that frame from highest to lowest, add to dictionary where key is the position and value is the dataframe with season averages
    for position in POSITIONS:
        pos_df = season_avgs[season_avgs['position'] == position].copy()
        pos_df = pos_df.sort_values('avg_ppr_points', ascending=False)
        pos_df['rank'] = range(1, len(pos_df) + 1)
        rankings[position] = pos_df.reset_index(drop=True)

    return rankings

def get_career_rankings(weekly_stats):
    # logic is the same as above, just for career stats instead of season
    scored = calculate_ppr_points(weekly_stats)
    career_avgs = get_career_averages(scored)

    career_avgs = career_avgs[career_avgs['total_games'] >= MIN_GAMES]

    rankings = {}
    for position in POSITIONS:
        pos_df = career_avgs[career_avgs['position'] == position].copy()
        pos_df = pos_df.sort_values('avg_ppr_points', ascending=False)
        pos_df['rank'] = range(1, len(pos_df) + 1)
        rankings[position] = pos_df.reset_index(drop=True)

    return rankings

def get_trending_players(weekly_stats, position=None):
    scored = calculate_ppr_points(weekly_stats)
    season_avgs = get_season_averages(scored)

    season_avgs = season_avgs[season_avgs['games_played'] >= MIN_GAMES]

    # create table where each row is classified by an unique player, and columns are each season found in the season averages dataframe, values are each average points value found that matches row and column. 
    pivot = season_avgs.pivot_table(
        index = ['player_id', 'player_name', 'position'],
        columns = 'season',
        values = 'avg_ppr_points'
    ).reset_index()

    # remove any name for the columns, so onyl the year values are left
    pivot.columns.name = None
    # use list comprehension to go through every column value, and if it is an int add it to list
    season_cols = [c for c in pivot.columns if isinstance(c, int)]

    # if player has played at least two season then get average points from past 2 seasons, subtract previous from latest to get a trend for players points
    if len(season_cols) >= 2:
        latest = season_cols[-1]
        previous = season_cols[-2]
        pivot['trend'] = pivot[latest] - pivot[previous]
        pivot = pivot.dropna(subset=['trend'])
        pivot = pivot.sort_values('trend', ascending=False)

    if position:
        pivot = pivot[pivot['position'] == position]

    return pivot.reset_index(drop=True)