from data.loader import load_all
from analysis.consistency import calculate_consistency, get_consistency_by_position

print("Loading all data...")
weekly_stats, schedule, rosters = load_all()

print("\n── CONSISTENCY (2024) ───────────────────────")
consistency = calculate_consistency(weekly_stats, season=2024)
print(f"Rows: {len(consistency)}")
print(f"Columns: {list(consistency.columns)}")

print("\n── GRADE DISTRIBUTION ───────────────────────")
print(consistency['grade'].value_counts())

print("\n── TOP 5 MOST CONSISTENT WRs (2024) ─────────")
wr_consistency = get_consistency_by_position(weekly_stats, 'WR', season=2024)
print(wr_consistency[['player_name', 'avg_ppr_points', 'std_ppr_points', 'cv', 'grade']].head())

print("\n── TOP 5 MOST CONSISTENT QBs (2024) ─────────")
qb_consistency = get_consistency_by_position(weekly_stats, 'QB', season=2024)
print(qb_consistency[['player_name', 'avg_ppr_points', 'std_ppr_points', 'cv', 'grade']].head())

print("\n── ALL CHECKS PASSED ────────────────────────")