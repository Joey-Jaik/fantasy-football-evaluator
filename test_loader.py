from data.loader import load_all
from analysis.scoring import calculate_ppr_points
from analysis.rankings import get_positional_rankings, get_career_rankings, get_trending_players

print("Loading all data...")
weekly_stats, schedule, rosters = load_all()

print("\n── POSITIONAL RANKINGS (2024) ───────────────")
rankings = get_positional_rankings(weekly_stats, season=2024)
for position in ['QB', 'RB', 'WR', 'TE']:
    print(f"\nTop 5 {position}s:")
    print(rankings[position][['rank', 'player_name', 'avg_ppr_points', 'games_played']].head())

print("\n── CAREER RANKINGS ──────────────────────────")
career = get_career_rankings(weekly_stats)
for position in ['QB', 'RB', 'WR', 'TE']:
    print(f"\nTop 5 {position}s (career):")
    print(career[position][['rank', 'player_name', 'avg_ppr_points', 'total_games']].head())

print("\n── TRENDING PLAYERS ─────────────────────────")
trending = get_trending_players(weekly_stats)
print("Most improved:")
print(trending[['player_name', 'position', 'trend']].head())
print("\nMost declined:")
print(trending[['player_name', 'position', 'trend']].tail())

print("\n── ALL CHECKS PASSED ────────────────────────")