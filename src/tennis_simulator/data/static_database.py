import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import sys

def get_file_paths(gender: str):
    if gender == 'men':
        return {
            'elo': 'elo_men.txt',
            'yelo': 'yelo_men.txt',
            'tier': 'data/elo/tier_men.txt',
        }
    elif gender == 'women':
        return {
            'elo': 'elo_women.txt',
            'yelo': 'yelo_women.txt',
            'tier': 'data/elo/tier_women.txt',
        }
    else:
        raise ValueError('gender must be "men" or "women"')

@dataclass
class PlayerData:
    name: str
    tier: str
    elo: Optional[float]
    helo: Optional[float]
    celo: Optional[float]
    gelo: Optional[float]
    yelo: Optional[float]
    ranking: Optional[int]

def get_player_names(gender: str) -> List[str]:
    """Extract player names from the Elo file"""
    paths = get_file_paths(gender)
    names = []
    elo_file = paths['elo']
    
    if not os.path.exists(elo_file):
        print(f"Warning: {elo_file} not found")
        return names
    
    with open(elo_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('Elo Rank'):
                # Extract name from the line (tab-separated format)
                parts = line.split('\t')
                if len(parts) >= 2:
                    name = parts[1].strip()
                    if name and name != 'Player':
                        names.append(name)
    return names

def get_player_tiers(gender: str) -> Dict[str, str]:
    """Extract player tiers from the tier file"""
    paths = get_file_paths(gender)
    tiers = {}
    db_file = paths['tier']
    if not os.path.exists(db_file):
        print(f"Warning: {db_file} not found")
        return tiers
    with open(db_file, 'r', encoding='utf-8') as f:
        content = f.read()
    import re
    pattern = r'(?:MenPlayer|WomenPlayer)\("([^"]+)",\s*"[^"]+",\s*[^,]*,\s*Tier\.([A-D])(?:,[^)]*)?\)'
    matches = re.findall(pattern, content)
    for name, tier in matches:
        tiers[name] = tier
    return tiers

def get_player_elo(gender: str) -> Dict[str, float]:
    paths = get_file_paths(gender)
    return _extract_elo_values(paths['elo'], 3)  # Elo is in column 3

def get_player_helo(gender: str) -> Dict[str, float]:
    paths = get_file_paths(gender)
    return _extract_elo_values(paths['elo'], 6)  # hElo is in column 6 (actual Elo value)

def get_player_celo(gender: str) -> Dict[str, float]:
    paths = get_file_paths(gender)
    return _extract_elo_values(paths['elo'], 8)  # cElo is in column 8 (actual Elo value)

def get_player_gelo(gender: str) -> Dict[str, float]:
    paths = get_file_paths(gender)
    return _extract_elo_values(paths['elo'], 10)  # gElo is in column 10 (actual Elo value)

def get_player_yelo(gender: str) -> Dict[str, float]:
    paths = get_file_paths(gender)
    return _extract_yelo_values(paths['yelo'])

def get_player_ranking(gender: str) -> Dict[str, int]:
    paths = get_file_paths(gender)
    ranking = {}
    elo_file = paths['elo']
    if not os.path.exists(elo_file):
        print(f"Warning: {elo_file} not found")
        return ranking
    with open(elo_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('Elo Rank'):
                parts = line.split('\t')
                if len(parts) >= 16:  # ATP rank is in column 15 (0-indexed = 15)
                    name = parts[1].strip()
                    try:
                        rank = int(parts[15].strip()) if parts[15].strip() else None
                        if rank is not None:
                            ranking[name] = rank
                    except (ValueError, IndexError):
                        continue
    return ranking

def _extract_elo_values(filename: str, column_index: int) -> Dict[str, float]:
    elo_values = {}
    if not os.path.exists(filename):
        print(f"Warning: {filename} not found")
        return elo_values
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('Elo Rank'):
                parts = line.split('\t')
                if len(parts) > column_index:
                    name = parts[1].strip()  # Name is in column 1
                    try:
                        value = float(parts[column_index].strip()) if parts[column_index].strip() else None
                        if value is not None:
                            elo_values[name] = value
                    except (ValueError, IndexError):
                        continue
    return elo_values

def _extract_yelo_values(filename: str) -> Dict[str, float]:
    yelo_values = {}
    if not os.path.exists(filename):
        print(f"Warning: {filename} not found")
        return yelo_values
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('Rank'):
                parts = line.split('\t')
                if len(parts) >= 5:  # yElo is in column 4 (index 4)
                    name = parts[1].strip()  # Name is in column 1
                    try:
                        value = float(parts[4].strip()) if parts[4].strip() else None
                        if value is not None:
                            yelo_values[name] = value
                    except (ValueError, IndexError):
                        continue
    return yelo_values

def populate_static_database(gender: str) -> Dict[str, PlayerData]:
    print(f"Populating static database for {gender}...")
    names = get_player_names(gender)
    tiers = get_player_tiers(gender)
    elo_ratings = get_player_elo(gender)
    helo_ratings = get_player_helo(gender)
    celo_ratings = get_player_celo(gender)
    gelo_ratings = get_player_gelo(gender)
    yelo_ratings = get_player_yelo(gender)
    rankings = get_player_ranking(gender)
    static_db = {}
    for name in names:
        player_data = PlayerData(
            name=name,
            tier=tiers.get(name, "D"),
            elo=elo_ratings.get(name),
            helo=helo_ratings.get(name),
            celo=celo_ratings.get(name),
            gelo=gelo_ratings.get(name),
            yelo=yelo_ratings.get(name),
            ranking=rankings.get(name)
        )
        static_db[name] = player_data
    print(f"Static database populated with {len(static_db)} players")
    return static_db

def print_static_database(db: Dict[str, PlayerData], limit: int = 10):
    print(f"\nStatic Database Preview (first {limit} players):")
    print("=" * 80)
    for i, (name, data) in enumerate(list(db.items())[:limit]):
        print(f"{i+1:2d}. {name}")
        print(f"     Tier: {data.tier}")
        print(f"     Elo: {data.elo}, hElo: {data.helo}, cElo: {data.celo}, gElo: {data.gelo}, yElo: {data.yelo}")
        print(f"     Ranking: {data.ranking}")
        print()

if __name__ == "__main__":
    # Get gender from command line argument, default to men
    gender = sys.argv[1] if len(sys.argv) > 1 else "men"
    
    if gender not in ["men", "women"]:
        print("Usage: python static_database.py [men|women]")
        print("Default: men")
        sys.exit(1)
    
    # Print the full static database for face-validation
    print(f"\nFULL STATIC DATABASE FOR {gender.upper()} (FACE VALIDATION):")
    print("=" * 80)
    db = populate_static_database(gender)
    for i, (name, data) in enumerate(db.items()):
        print(f"{i+1:3d}. {name}")
        print(f"     Tier: {data.tier}")
        print(f"     Elo: {data.elo}, hElo: {data.helo}, cElo: {data.celo}, gElo: {data.gelo}, yElo: {data.yelo}")
        print(f"     Ranking: {data.ranking}")
        print()
    
    # Print summary statistics
    print("Summary Statistics:")
    print(f"Total players: {len(db)}")
    tier_counts = {}
    for data in db.values():
        tier = data.tier
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
    for tier in sorted(tier_counts.keys()):
        print(f"Tier {tier}: {tier_counts[tier]} players")