import  pandas as pd
from analysis.scoring import calculate_ppr_points

# ── CONSTANTS ─────────────────────────────────────────────
MIN_GAMES = 6
GRADE_THRESHOLDS = {
    'A': 0.40,
    'B': 0.60,
    'C': 0.80,
    'D': 1.00
}

def calculate_consistency(weekly_stats, season=None):
    scored = calculate_ppr_points(weekly_stats)

    if season:
        scored = scored[scored['season'] == season]

    # filter out weeks players didn't play
    scored = scored[scored['ppr_points'] > 0]

    # create new dataframe that has aggregate data for each player needed for coefficient of variation calculation
    consistency = (
        scored.groupby(['player_id', 'player_name', 'position'])
        .agg(
            games_played = ('week', 'count'),
            avg_ppr_points = ('ppr_points', 'mean'),
            std_ppr_points = ('ppr_points', 'std'),
            min_ppr_points = ('ppr_points', 'min'),
            max_ppr_points = ('ppr_points', 'max'),
        )
        .reset_index()
        .round(2)
    )

    # ensure player has played enough games for data to be accurate
    consistency = consistency[consistency['games_played'] >= MIN_GAMES]

    # calculate coefficient of variation and add to dataframe, used to determine trends
    consistency['cv'] = (
        consistency['std_ppr_points'] / consistency['avg_ppr_points']
    ).round(3)

    # give each player a grade based on cv
    consistency['grade'] = consistency['cv'].apply(assign_grade)

    consistency = consistency.sort_values(
        ['position', 'avg_ppr_points'],
        ascending=[True, False]
    ).reset_index(drop=True)

    return consistency

def assign_grade(cv):
    if pd.isna(cv):
        return 'N/A'
    # loop through each key value pair in grade thresholds, if the cv is lower than the threshold then return the associated grade, if nothing is lower loop finishes and return C
    for grade, threshold in GRADE_THRESHOLDS.items():
        if cv <= threshold:
            return grade
    return 'D'

def get_consistency_by_position(weekly_stats, position, season=None):
    consistency = calculate_consistency(weekly_stats, season)
    return consistency[consistency['position'] == position].reset_index(drop=True)