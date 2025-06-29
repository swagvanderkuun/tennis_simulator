#!/usr/bin/env python3
"""
yElo Form Calculator

This script calculates form values for tennis players by comparing current yElo values
with values from 1 week ago and 2 weeks ago. The form is calculated as the difference
between current and historical values.
"""

import os
from typing import Dict, Tuple, List
from dataclasses import dataclass


@dataclass
class PlayerData:
    """Data class to store player information and yElo values."""
    rank: int
    player: str
    wins: int
    losses: int
    yelo: float
    yelo_1w: float = None
    yelo_2w: float = None
    
    @property
    def form_1w(self) -> float:
        """Calculate form compared to 1 week ago."""
        if self.yelo_1w is None:
            return 0.0
        return self.yelo - self.yelo_1w
    
    @property
    def form_2w(self) -> float:
        """Calculate form compared to 2 weeks ago."""
        if self.yelo_2w is None:
            return 0.0
        return self.yelo - self.yelo_2w


def read_yelo_file(filepath: str) -> Dict[str, PlayerData]:
    """
    Read a yElo file and return a dictionary of player data.
    
    Args:
        filepath: Path to the yElo file
        
    Returns:
        Dictionary mapping player names to PlayerData objects
    """
    players = {}
    
    if not os.path.exists(filepath):
        print(f"Warning: File {filepath} does not exist")
        return players
    
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Skip header line
    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
            
        parts = line.split('\t')
        if len(parts) >= 4:
            try:
                rank = int(parts[0])
                player = parts[1]
                wins = int(parts[2])
                losses = int(parts[3])
                yelo = float(parts[4])
                
                players[player] = PlayerData(
                    rank=rank,
                    player=player,
                    wins=wins,
                    losses=losses,
                    yelo=yelo
                )
            except (ValueError, IndexError) as e:
                print(f"Error parsing line: {line} - {e}")
    
    return players


def merge_player_data(current: Dict[str, PlayerData], 
                     one_week: Dict[str, PlayerData],
                     two_weeks: Dict[str, PlayerData]) -> Dict[str, PlayerData]:
    """
    Merge player data from all three time periods.
    
    Args:
        current: Current player data
        one_week: 1 week ago player data
        two_weeks: 2 weeks ago player data
        
    Returns:
        Merged player data with all time periods
    """
    merged = {}
    
    # Add all players from current data
    for player_name, player_data in current.items():
        merged[player_name] = player_data
    
    # Add historical data for existing players
    for player_name, player_data in merged.items():
        if player_name in one_week:
            player_data.yelo_1w = one_week[player_name].yelo
        if player_name in two_weeks:
            player_data.yelo_2w = two_weeks[player_name].yelo
    
    # Add players that exist in historical data but not current
    for player_name, player_data in one_week.items():
        if player_name not in merged:
            merged[player_name] = PlayerData(
                rank=player_data.rank,
                player=player_name,
                wins=player_data.wins,
                losses=player_data.losses,
                yelo=0.0,  # No current data
                yelo_1w=player_data.yelo,
                yelo_2w=two_weeks.get(player_name, PlayerData(0, player_name, 0, 0, 0.0)).yelo if player_name in two_weeks else None
            )
    
    for player_name, player_data in two_weeks.items():
        if player_name not in merged:
            merged[player_name] = PlayerData(
                rank=player_data.rank,
                player=player_name,
                wins=player_data.wins,
                losses=player_data.losses,
                yelo=0.0,  # No current data
                yelo_1w=one_week.get(player_name, PlayerData(0, player_name, 0, 0, 0.0)).yelo if player_name in one_week else None,
                yelo_2w=player_data.yelo
            )
    
    return merged


def write_form_file(players: Dict[str, PlayerData], output_file: str):
    """
    Write form data to the output file.
    
    Args:
        players: Dictionary of player data
        output_file: Path to output file
    """
    # Sort players by current yElo (descending)
    sorted_players = sorted(
        players.values(), 
        key=lambda p: p.yelo, 
        reverse=True
    )
    
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write header
        f.write("Rank\tPlayer\tWins\tLosses\tyElo_form1w\tyElo_form2w\n")
        
        # Write player data
        for i, player in enumerate(sorted_players, 1):
            if player.yelo > 0:  # Only include players with current data
                f.write(f"{i}\t{player.player}\t{player.wins}\t{player.losses}\t{player.form_1w:.1f}\t{player.form_2w:.1f}\n")


def calculate_form_for_gender(gender: str, data_dir: str = "data/elo"):
    """
    Calculate form for a specific gender (men/women).
    
    Args:
        gender: Either 'men' or 'women'
        data_dir: Directory containing the yElo files
    """
    print(f"Calculating form for {gender}...")
    
    # File paths
    current_file = os.path.join(data_dir, f"yelo_{gender}.txt")
    one_week_file = os.path.join(data_dir, f"yelo_{gender}_1w.txt")
    two_weeks_file = os.path.join(data_dir, f"yelo_{gender}_2w.txt")
    output_file = os.path.join(data_dir, f"yelo_{gender}_form.txt")
    
    # Read all files
    print(f"Reading current data from {current_file}")
    current_players = read_yelo_file(current_file)
    
    print(f"Reading 1 week ago data from {one_week_file}")
    one_week_players = read_yelo_file(one_week_file)
    
    print(f"Reading 2 weeks ago data from {two_weeks_file}")
    two_weeks_players = read_yelo_file(two_weeks_file)
    
    # Merge data
    print("Merging player data...")
    merged_players = merge_player_data(current_players, one_week_players, two_weeks_players)
    
    # Write form file
    print(f"Writing form data to {output_file}")
    write_form_file(merged_players, output_file)
    
    print(f"Form calculation completed for {gender}")
    print(f"Total players processed: {len(merged_players)}")
    print(f"Players with current data: {len([p for p in merged_players.values() if p.yelo > 0])}")


def main():
    """Main function to calculate form for both men and women."""
    print("yElo Form Calculator")
    print("=" * 50)
    
    # Calculate form for women
    calculate_form_for_gender("women")
    print()
    
    # Calculate form for men
    calculate_form_for_gender("men")
    print()
    
    print("All form calculations completed!")


if __name__ == "__main__":
    main() 