import nfl_data_py as nfl
import pandas as pd
import os
import datetime

# ── CONSTANTS ────────────────────────────────────────────
CACHE_DIR = "data/cache"
SEASONS = [2022, 2023, 2024]
CACHE_DURATION_OFFSEASON =  168 # Don't need to check for current data in offseason
CACHE_DURATION_INSEASON = 24 

# ── CACHE HELPERS ─────────────────────────────────────────
def is_active_season():
    month = datetime.datetime.now().month
    return month >= 9 or month <= 2

def cache_duration_hours():
    return CACHE_DURATION_INSEASON if is_active_season() else CACHE_DURATION_OFFSEASON

def cache_path(name):
    return os.path.join(CACHE_DIR, f"{name}.csv")

def cache_is_valid(name):
    path = cache_path(name)
    # if file doesn't exit then return
    if not os.path.exists(path):
        return False
    # get the time the file was last modified
    modified = datetime.datetime.fromtimestamp(os.path.getmtime(path))
    # calculate how many hours ago it was last modified
    age_hours = (datetime.datetime.now() - modified).total_seconds() / 3600
    return age_hours < cache_duration_hours()

def save_cache(df, name):
    os.makedirs(CACHE_DIR, exist_ok=True)
    df.to_csv(cache_path(name), index=False)

def load_cache(name):
    return pd.read_csv(cache_path(name))

# ── DATA LOADERS ──────────────────────────────────────────
def load_weekly_stats():
    # try to load from cache first if available
    if cache_is_valid("weekly_stats"):
        return load_cache("weekly_stats")
    
    print("Fetching weekly stats...")

    dfs = []
    # loop through every season collecting the data we need for each year into a dataframe, and add it to array of dataframes
    for season in SEASONS:
        df = nfl.import_weekly_data(
            years=[season],
            columns=[
                'player_id', 'player_name', 'position', 'recent_team',
                'season', 'week', 'opponent_team',
                'completions', 'attempts', 'passing_yards', 'passing_tds',
                'interceptions', 'carries', 'rushing_yards', 'rushing_tds',
                'receptions', 'targets', 'receiving_yards', 'receiving_tds',
                'sack_fumbles_lost', 'rushing_fumbles_lost','receiving_fumbles_lost', 
                'fantasy_points'
            ]
        )
        dfs.append(df)

    # combine the dataframes for each season into one dataframe
    combined = pd.concat(dfs, ignore_index=True)
    # only keep the positions in the combined dataframe that we need
    combined = combined[combined['position'].isin(['QB', 'RB', 'WR', 'TE'])]

    save_cache(combined, "weekly_stats")
    return combined

def load_schedule():
    if cache_is_valid("schedule"):
        return load_cache("schedule")
    
    print("Fetching schedule data...")

    dfs = []
    for season in SEASONS:
        df = nfl.import_schedules(years=[season])
        df = df[[
            'season', 'week', 'game_type',
            'home_team', 'away_team',
            'home_score', 'away_score'
        ]]
        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)
    # only include regular season games
    combined = combined[combined['game_type'] == 'REG']

    save_cache(combined, "schedule")
    return combined

def load_rosters():
    if cache_is_valid("rosters"):
        return load_cache("rosters")
    
    print("Fetching roster data...")

    dfs = []
    for season in SEASONS:
        df = nfl.import_weekly_rosters(
            years=[season],
            columns=[
                'player_id', 'player_name', 'position', 'team',
                'season', 'week', 'game_type', 'status',
                'status_description_abbr', 'years_exp',
                'entry_year', 'rookie_year',
                'headshot_url', 'age'
            ]
        )
        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)
    # only keep the positions in the combined dataframe that we need
    combined = combined[combined['position'].isin(['QB', 'RB', 'WR', 'TE'])]
    # only include regular season games
    combined = combined[combined['game_type'] == 'REG']

    save_cache(combined, "rosters")
    return combined

def load_all():
    weekly_stats = load_weekly_stats()
    schedule = load_schedule()
    rosters = load_rosters()
    return weekly_stats, schedule, rosters