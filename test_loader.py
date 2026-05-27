from data.loader import load_all
from analysis.injuries import (
    calculate_injury_history,
    get_durability_summary,
    get_injury_report,
    get_current_injury_status
)

print("Loading all data...")
weekly_stats, schedule, rosters = load_all()

print("\n── INJURY HISTORY ───────────────────────────")
injury_history = calculate_injury_history(weekly_stats, rosters)
print(f"Rows: {len(injury_history)}")
print(f"Columns: {list(injury_history.columns)}")
print(injury_history.head(5))

print("\n── DURABILITY SUMMARY ───────────────────────")
durability = get_durability_summary(weekly_stats, rosters)
print(f"Rows: {len(durability)}")
print(f"Columns: {list(durability.columns)}")
print("\nTop 5 most durable players:")
print(durability[['player_name', 'position', 'total_games_played', 'avg_games_missed', 'durability_rating']].head())
print("\nRiskiest players:")
print(durability[['player_name', 'position', 'total_games_played', 'avg_games_missed', 'durability_rating']].tail())

print("\n── INJURY REPORT ────────────────────────────")
injury_report = get_injury_report(weekly_stats, rosters)
print(f"Players flagged: {len(injury_report)}")
print(injury_report[['player_name', 'position', 'seasons_with_injury', 'durability_rating']].head())

print("\n── CURRENT INJURY STATUS ────────────────────")
current = get_current_injury_status(rosters)
print(f"Rows: {len(current)}")
print(current[current['status_description_abbr'].notna()].head())

print("\n── ALL CHECKS PASSED ────────────────────────")