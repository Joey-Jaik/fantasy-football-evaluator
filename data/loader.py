# =============================================================================
# Author:  Joey Jaikaran
# Date:    June 10, 2026
# Purpose: Handles all data fetching and caching for the Fantasy Football
#          Evaluator. Fetches weekly player stats, schedule data, and roster
#          information from nfl_data_py for the 2022, 2023, and 2024 seasons.
#          Implements a file based caching system that saves data to CSV files
#          to avoid repeated API calls. Cache duration is 24 hours during the
#          active NFL season and 7 days during the offseason.
# =============================================================================

import nflreadpy as nfl
import pandas as pd
import os
import datetime

def get_current_seasons():
    current_year = datetime.datetime.now().year
    current_month = datetime.datetime.now().month
    
    # NFL season runs Sep-Feb, so if we are before September
    # the most recent completed season is last year
    # if we are in September or later the current year season has started
    if current_month >= 9:
        latest_season = current_year
    else:
        latest_season = current_year - 1
    
    return [latest_season - 2, latest_season - 1, latest_season]

# ── CONSTANTS ────────────────────────────────────────────
CACHE_DIR = "data/cache"
SEASONS = get_current_seasons()
CACHE_DURATION_OFFSEASON =  168 # Don't need to check for current data in offseason
CACHE_DURATION_INSEASON = 24 

# ── CACHE HELPERS ─────────────────────────────────────────
def is_active_season():
    month = datetime.datetime.now().month
    return month >= 9 or month <= 2

def get_season_info():
    if not is_active_season():
        return False, None, None
    
    try:
        current_season = nfl.get_current_season()
        current_week = nfl.get_current_week
        return True, current_season, current_week
    except:
        return False, None, None 

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
    if cache_is_valid("weekly_stats"):
        return load_cache("weekly_stats")

    print("Fetching weekly stats...")

    dfs = []
    for season in SEASONS:
        df = nfl.load_player_stats(
            seasons=[season],
            summary_level='week'
        ).to_pandas()

        df = df[[
            'player_id', 'player_name', 'position', 'team',
            'season', 'week', 'opponent_team',
            'completions', 'attempts', 'passing_yards', 'passing_tds',
            'passing_interceptions', 'carries', 'rushing_yards', 'rushing_tds',
            'receptions', 'targets', 'receiving_yards', 'receiving_tds',
            'sack_fumbles_lost', 'rushing_fumbles_lost', 'receiving_fumbles_lost',
            'fantasy_points'
        ]]

        df = df.rename(columns={
            'team':                  'recent_team',
            'passing_interceptions': 'interceptions'
        })

        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)
    combined = combined[combined['week'] <= 18]
    combined = combined[combined['position'].isin(['QB', 'RB', 'WR', 'TE'])]

    save_cache(combined, "weekly_stats")
    return combined

def load_schedule():
    if cache_is_valid("schedule"):
        return load_cache("schedule")

    print("Fetching schedule data...")

    dfs = []
    for season in SEASONS:
        df = nfl.load_schedules(seasons=[season]).to_pandas()
        df = df[[
            'season', 'week', 'game_type',
            'home_team', 'away_team',
            'home_score', 'away_score'
        ]]
        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)
    combined = combined[combined['game_type'] == 'REG']

    save_cache(combined, "schedule")
    return combined

def load_rosters():
    if cache_is_valid("rosters"):
        return load_cache("rosters")

    print("Fetching roster data...")

    dfs = []
    for season in SEASONS:
        df = nfl.load_rosters_weekly(seasons=[season]).to_pandas()
        df = df[[
            'gsis_id', 'full_name', 'first_name', 'last_name', 'position', 'team',
            'season', 'week', 'game_type', 'status',
            'status_description_abbr', 'years_exp',
            'entry_year', 'rookie_year', 'headshot_url'
        ]]
        df = df.rename(columns={
            'gsis_id':   'player_id',
            'full_name': 'player_name'
        })
        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)
    combined = combined[combined['position'].isin(['QB', 'RB', 'WR', 'TE'])]
    combined = combined[combined['game_type'] == 'REG']

    save_cache(combined, "rosters")
    return combined

def load_all():
    weekly_stats = load_weekly_stats()
    schedule = load_schedule()
    rosters = load_rosters()
    return weekly_stats, schedule, rosters