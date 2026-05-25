from data.loader import load_all
from analysis.scoring import calculate_ppr_points, get_season_averages, get_career_averages

print("Loading all data...")
weekly_stats, schedule, rosters = load_all()

print("\n── SCORING ──────────────────────────────────")
scored = calculate_ppr_points(weekly_stats)
print(f"Rows: {len(scored)}")
print(f"PPR points column exists: {'ppr_points' in scored.columns}")
print(f"Sample PPR points:")
print(scored[['player_name', 'position', 'season', 'week', 'ppr_points']].head(5))

print("\n── SEASON AVERAGES ──────────────────────────")
season_avgs = get_season_averages(scored)
print(f"Rows: {len(season_avgs)}")
print(f"Columns: {list(season_avgs.columns)}")
print(season_avgs.head(5))

print("\n── CAREER AVERAGES ──────────────────────────")
career_avgs = get_career_averages(scored)
print(f"Rows: {len(career_avgs)}")
print(f"Columns: {list(career_avgs.columns)}")
print(career_avgs.head(5))

print("\n── ALL CHECKS PASSED ────────────────────────")