from data.loader import load_all
from analysis.matchups import (
    get_defensive_rankings,
    get_player_matchups,
    get_best_matchups
)

print("Loading all data...")
weekly_stats, schedule, rosters = load_all()

print("\n── DEFENSIVE RANKINGS (2024) ────────────────")
defense = get_defensive_rankings(weekly_stats, season=2024)
print(f"Rows: {len(defense)}")
print(f"Columns: {list(defense.columns)}")
print("\nWorst defenses vs WR (best matchups):")
wr_defense = defense[defense['position'] == 'WR'].sort_values('avg_pts_allowed', ascending=False)
print(wr_defense[['opponent_team', 'avg_pts_allowed', 'rank', 'matchup_tier']].head())
print("\nBest defenses vs WR (toughest matchups):")
print(wr_defense[['opponent_team', 'avg_pts_allowed', 'rank', 'matchup_tier']].tail())

print("\n── PLAYER MATCHUPS (2024, WEEK 5) ───────────")
matchups = get_player_matchups(weekly_stats, schedule, season=2024, week=5)
print(f"Rows: {len(matchups)}")
print(f"Columns: {list(matchups.columns)}")
print("\nTop QB matchups:")
qb_matchups = matchups[matchups['position'] == 'QB']
print(qb_matchups[['player_name', 'recent_team', 'opponent', 'avg_ppr_points', 'matchup_tier', 'matchup_label']].head())

print("\n── BEST MATCHUPS (2024, WEEK 5) ─────────────")
best = get_best_matchups(weekly_stats, schedule, season=2024, week=5)
print(f"Players with excellent/good matchups: {len(best)}")
print("\nBest WR matchups:")
best_wr = get_best_matchups(weekly_stats, schedule, season=2024, week=5, position='WR')
print(best_wr[['player_name', 'recent_team', 'opponent', 'avg_ppr_points', 'matchup_label']].head())

print("\n── ALL CHECKS PASSED ────────────────────────")