import pandas as pd

# ── CONSTANTS ─────────────────────────────────────────────
NFL_REGULAR_SEASON_GAMES = 17
INJURY_RISK_THRESHOLD = 5

def calculate_injury_history(weekly_stats, rosters):
    # create dataframe indexed by each player per season, and counts the weeks they played
    games_played = (
        weekly_stats.groupby(['player_id', 'player_name', 'position', 'season'])
        .agg(games_played = ('week', 'count'))
        .reset_index()
    )

    # add a column for the numbers of games missed by a player
    games_played['games_missed'] = (
        NFL_REGULAR_SEASON_GAMES - games_played['games_played']
    ).clip(lower=0) # ensure that the minimum number of games missed is 0

    # add column for the percentage of games the player plays in
    games_played['availability_pct'] = (
        (games_played['games_played'] / NFL_REGULAR_SEASON_GAMES) * 100
    ).round(1)

    # add column checking if player played above injury threshold
    games_played['injury_risk'] = (
        games_played['games_missed'] >= INJURY_RISK_THRESHOLD
    )

    return games_played

def get_durability_summary(weekly_stats, rosters):
    injury_history = calculate_injury_history(weekly_stats, rosters)

    # create dataframe that gives career injury data for players
    summary = (
        injury_history.groupby(['player_id', 'player_name', 'position'])
        .agg(
            total_games_played  = ('games_played', 'sum'),
            avg_games_played    = ('games_played', 'mean'),
            total_games_missed  = ('games_missed', 'sum'),
            avg_games_missed    = ('games_missed', 'mean'),
            seasons_with_injury = ('injury_risk', 'sum'),
            seasons_tracked     = ('season', 'count')
        )
        .reset_index()
        .round(2)
    )

    # add column that calculates a rating for players durability
    summary['durability_rating'] = summary.apply(
        calculate_durability_rating, axis=1
    )

    summary = summary[summary['seasons_tracked'] >= 2]

    summary = summary.sort_values(
        'avg_games_played', ascending=False
    ).reset_index(drop=True)

    return summary

def calculate_durability_rating(row):
    # calculate an availability score based on how many games a player has played, and return a rating
    availability = (
        row['total_games_played'] / (row['seasons_tracked'] * NFL_REGULAR_SEASON_GAMES)
    ) * 100

    if availability >= 90:
        return 'Elite'
    elif availability >= 75:
        return 'Good'
    elif availability >= 60:
        return 'Average'
    else:
        return 'Risky'
    
def get_injury_report(weekly_stats, rosters, position=None):
    summary = get_durability_summary(weekly_stats, rosters)

    # filter dataframe so that it only shows players with average or worse durability
    risky = summary[
        (summary['durability_rating'].isin(['Average', 'Risky'])) & 
        (summary['seasons_tracked'] >= 2) &
        (summary['avg_games_played'] >= 8)
        ]

    # if a position was provivded then filter to only show that position
    if position:
        risky = risky[risky['position'] == position]

    return risky.reset_index(drop=True)

def get_current_injury_status(rosters):
    latest_season = rosters['season'].max()
    latest_week = rosters[
        rosters['season'] == latest_season
    ]['week'].max()

    current = rosters[
        (rosters['season'] == latest_season) &
        (rosters['week'] == latest_week)
    ][['player_id', 'player_name', 'position',
      'team', 'status', 'status_description_abbr']]
    
    current = current[
        current['position'].isin(['QB', 'RB', 'WR', 'TE'])
    ]

    return current.reset_index(drop=True)