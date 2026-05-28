import pandas as pd
from analysis.scoring import calculate_ppr_points

# ── CONSTANTS ─────────────────────────────────────────────
POSITIONS = ['QB', 'RB', 'WR', 'TE']
MIN_GAMES_DEFENSE = 4

MATCHUP_LABELS = {
    1: 'Excellent',
    2: 'Good',
    3: 'Average',
    4: 'Tough',
    5: 'Very Tough'
}

def get_defensive_rankings(weekly_stats, season=None):
    scored = calculate_ppr_points(weekly_stats)

    if season:
        scored = scored[scored['season'] == season]

    # filter out any players that did not play
    scored = scored[scored['ppr_points'] > 0]

    # create dataframe that is grouped by player position and opposing team, and calculate aggregate values for the total points and average points that defense has allowed agains that position
    defense_allowed = (
        scored.groupby(['opponent_team', 'position'])
        .agg(
            games_played = ('week', 'count'),
            avg_pts_allowed = ('ppr_points', 'mean'),
            total_pts_allowed = ('ppr_points', 'sum')
        )
        .reset_index()
        .round(2)
    )

    # ensure defense has enough games played for data to be accurate
    defense_allowed = defense_allowed[
        defense_allowed['games_played'] >= MIN_GAMES_DEFENSE
    ]

    # create a new rank column, creates a ranking based on average points allowed by that defence, and it grouped by position
    defense_allowed['rank'] = (
        defense_allowed.groupby('position')['avg_pts_allowed']
        .rank(ascending=False, method='min')
        .astype(int)
    )

    # create a new column that assigns a matchup label to each defence, labels match with matchup labels dictionary
    defense_allowed['matchup_tier'] = (
        defense_allowed.groupby('position')['avg_pts_allowed']
        .transform(assign_matchup_tier)
    )

    return defense_allowed

def assign_matchup_tier(series):
    # split series into 5 equal sections and apply same label to everything in each section
    labels = pd.qcut(
        series, 
        q=5,
        labels=[5, 4, 3, 2, 1]
    )

    return labels.astype(int)

def get_player_matchups(weekly_stats, schedule, season, week):
    scored = calculate_ppr_points(weekly_stats)
    defensive_rankings = get_defensive_rankings(weekly_stats, season=season)

    week_schedule = schedule[
        (schedule['season'] == season) &
        (schedule['week'] == week)
    ]

    matchups = []
    # loop through each game of the specified week and season, add both matchups to a list
    for _, game in week_schedule.iterrows():
        matchups.append({
            'team': game ['home_team'],
            'opponent': game['away_team']
        })
        matchups.append({
            'team': game['away_team'],
            'opponent': game['home_team']
        })

    # turn list into dataframe
    matchups_df = pd.DataFrame(matchups)

    # create frame that has the total average amount of points each player has scored for the entire specified season
    season_stats = (
        scored[scored['season'] == season]
        .groupby(['player_id', 'player_name', 'position', 'recent_team'])
        .agg(avg_ppr_points=('ppr_points', 'mean'))
        .reset_index()
        .round(2)
    )

    # merge season stats frame with matchups frame, merge based on recent team matching team, a new row is created with all the information from both tables where the specifed values match
    season_stats = season_stats.merge(
        matchups_df,
        left_on='recent_team',
        right_on='team',
        how='inner'
    )

    # merge with defensive rankings based on matching opponent teams and position, this creates a row that has a player, their position, their opponent and then we add the defensive data from the row that matches opponent and position
    season_stats = season_stats.merge(
        defensive_rankings[['opponent_team', 'position', 'matchup_tier', 'avg_pts_allowed']],
        left_on=['opponent', 'position'],
        right_on=['opponent_team', 'position'],
        how='left'
    )

    season_stats['matchup_label'] = season_stats['matchup_tier'].map(MATCHUP_LABELS)

    return season_stats.sort_values(
        ['position', 'avg_ppr_points'],
        ascending=[True, False]
    ).reset_index(drop=True)

def get_best_matchups(weekly_stats, schedule, season, week, position=None):
    matchups = get_player_matchups(weekly_stats, schedule, season, week)

    best = matchups[matchups['matchup_tier'].isin([1,2])]

    if position:
        best = best[best['position'] == position]

    return best.reset_index(drop=True)