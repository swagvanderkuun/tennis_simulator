#!/usr/bin/env python3
"""
Example usage of the yElo Form Calculator

This script demonstrates how to use the yElo form calculator to analyze
player form trends over time.
"""

from yelo_form_calculator import calculate_form_for_gender, read_yelo_file
import os

def analyze_top_players_form(gender: str, top_n: int = 10):
    """
    Analyze the form of top players.
    
    Args:
        gender: Either 'men' or 'women'
        top_n: Number of top players to analyze
    """
    form_file = f"data/elo/yelo_{gender}_form.txt"
    
    if not os.path.exists(form_file):
        print(f"Form file not found: {form_file}")
        print("Run the form calculator first: python yelo_form_calculator.py")
        return
    
    # Read the form data
    with open(form_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"\nTop {top_n} {gender} players by current yElo ranking:")
    print("=" * 80)
    print(f"{'Rank':<4} {'Player':<20} {'Form 1W':<10} {'Form 2W':<10} {'Trend':<15}")
    print("-" * 80)
    
    for line in lines[1:top_n+1]:  # Skip header
        parts = line.strip().split('\t')
        if len(parts) >= 6:
            rank = parts[0]
            player = parts[1]
            form_1w = float(parts[4])
            form_2w = float(parts[5])
            
            # Determine trend
            if form_1w > 0 and form_2w > 0:
                trend = "↗️ Improving"
            elif form_1w < 0 and form_2w < 0:
                trend = "↘️ Declining"
            elif form_1w > 0 and form_2w < 0:
                trend = "↗️ Recovering"
            elif form_1w < 0 and form_2w > 0:
                trend = "↘️ Sliding"
            else:
                trend = "➡️ Stable"
            
            print(f"{rank:<4} {player:<20} {form_1w:>8.1f} {form_2w:>8.1f} {trend:<15}")

def main():
    """Main function demonstrating form analysis."""
    print("yElo Form Analysis Example")
    print("=" * 50)
    
    # Analyze top 10 players for both genders
    analyze_top_players_form("women", 10)
    analyze_top_players_form("men", 10)
    
    print("\n" + "=" * 50)
    print("Form interpretation:")
    print("- Positive values: Player's yElo has increased (improving form)")
    print("- Negative values: Player's yElo has decreased (declining form)")
    print("- Zero values: No change in yElo (stable form)")
    print("\nTo recalculate form data, run: python yelo_form_calculator.py")

if __name__ == "__main__":
    main() 