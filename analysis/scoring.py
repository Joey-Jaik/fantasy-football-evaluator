import pandas as pd

# ── PPR SCORING WEIGHTS ───────────────────────────────────
PASSING_YARD_PTS    = 0.04
PASSING_TD_PTS      = 4.0
INTERCEPTION_PTS    = -2.0
RUSHING_YARD_PTS    = 0.1
RUSHING_TD_PTS      = 6.0
RECEPTION_PTS       = 1.0
RECEIVING_YARD_PTS  = 0.1
RECEIVING_TD_PTS    = 6.0
FUMBLE_LOST_PTS     = -2.0

def calculate_ppr_points(df):
    # take the weekly stats dataframe that gets passed in and make a copy to not affect the original
    scored = df.copy()

    # create new column in dataframe for the fantasy points scored, calculate points based on scoring constants
    scored['ppr_points'] = (
        (scored['passing_yards']          * PASSING_YARD_PTS)   + 
        (scored['passing_tds']            * PASSING_TD_PTS)     + 
        (scored['interceptions']          * INTERCEPTION_PTS)   + 
        (scored['rushing_yards']          * RUSHING_YARD_PTS)   +
        (scored['rushing_tds']            * RUSHING_TD_PTS)     + 
        (scored['receptions']             * RECEPTION_PTS)      + 
        (scored['receiving_yards']        * RECEIVING_YARD_PTS) + 
        (scored['receiving_tds']          * RECEIVING_TD_PTS)   +
        (scored['sack_fumbles_lost']      * FUMBLE_LOST_PTS)    +
        (scored['rushing_fumbles_lost']   * FUMBLE_LOST_PTS)    + 
        (scored['receiving_fumbles_lost'] * FUMBLE_LOST_PTS)
    )

    return scored

def get_season_averages(df):
    # create new dataframe for player averages per season, group every unique player by their season and perform aggregate function to determine values for each new column in dataframe
    averages = (
        df.groupby(['player_id', 'player_name', 'position', 'season'])
        .agg(
            games_played    = ('week', 'count'),
            avg_ppr_points  = ('ppr_points', 'mean'),
            total_ppr_points= ('ppr_points', 'sum'),
            avg_passing_yds = ('passing_yards', 'mean'),
            avg_rushing_yds = ('rushing_yards', 'mean'),
            avg_receiving_yds=('receiving_yards', 'mean'),
            avg_receptions  = ('receptions', 'mean'),
            avg_targets     = ('targets', 'mean'),
            avg_carries     = ('carries', 'mean'),
        )
        .reset_index()
        .round(2)
    )
    return averages

def get_career_averages(df):
    # same logic as season averages above, just grouping by player only not season as well
    averages = (
        df.groupby(['player_id', 'player_name', 'position'])
        .agg(
            total_games      = ('week', 'count'),
            avg_ppr_points   = ('ppr_points', 'mean'),
            total_ppr_points = ('ppr_points', 'sum'),
        )
        .reset_index()
        .round(2)
    )
    return averages