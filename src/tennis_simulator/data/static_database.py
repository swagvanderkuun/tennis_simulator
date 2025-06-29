import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import sys

def get_file_paths(gender: str):
    """Get file paths for data files, handling both local and hosted environments"""
    
    # Get the current working directory
    cwd = os.getcwd()
    
    # Try multiple possible base paths
    possible_paths = [
        cwd,  # Current working directory
        os.path.join(cwd, 'data'),  # data subdirectory
        os.path.join(cwd, 'src', 'tennis_simulator', 'data'),  # src structure
        os.path.dirname(os.path.abspath(__file__)),  # Current file directory
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'),  # Project root
    ]
    
    # For hosted environments, also try the app directory
    if 'STREAMLIT_SERVER_RUN_ON_SAVE' in os.environ or 'STREAMLIT_SERVER_HEADLESS' in os.environ:
        possible_paths.extend([
            '/app',  # Streamlit Cloud default
            '/home/appuser',  # Alternative Streamlit Cloud path
            os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'),  # Go up more levels
        ])
    
    def find_file(filename):
        """Find a file in the possible paths"""
        for base_path in possible_paths:
            file_path = os.path.join(base_path, filename)
            if os.path.exists(file_path):
                print(f"Found {filename} at: {file_path}")
                return file_path
        
        print(f"Warning: Could not find {filename} in any of the following paths:")
        for base_path in possible_paths:
            print(f"  - {base_path}")
        
        # Try to use embedded data as fallback
        try:
            from .embedded_data import get_embedded_data, create_temp_file
            
            # Determine data type from filename
            data_type = None
            if 'elo_' in filename and 'form' not in filename:
                data_type = 'elo'
            elif 'yelo_' in filename:
                data_type = 'yelo'
            
            if data_type:
                embedded_data = get_embedded_data(gender, data_type)
                if embedded_data:
                    temp_path = create_temp_file(embedded_data)
                    print(f"Using embedded data for {filename} at: {temp_path}")
                    return temp_path
        except ImportError:
            print("Embedded data module not available")
        
        return filename  # Return original if not found
    
    if gender == 'men':
        return {
            'elo': find_file('elo_men.txt'),
            'yelo': find_file('yelo_men.txt'),
            'tier': find_file('data/elo/tier_men.txt'),
            'form': find_file('data/elo/yelo_men_form.txt'),
        }
    elif gender == 'women':
        return {
            'elo': find_file('elo_women.txt'),
            'yelo': find_file('yelo_women.txt'),
            'tier': find_file('data/elo/tier_women.txt'),
            'form': find_file('data/elo/yelo_women_form.txt'),
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
    form: Optional[float]

def get_player_names(gender: str) -> List[str]:
    """Extract player names from the Elo file"""
    from .data_loader import get_data_loader
    
    data_loader = get_data_loader()
    data_source = data_loader.get_data_source(gender, 'elo')
    
    names = []
    if not data_source:
        print(f"Warning: Could not load Elo data for {gender}")
        return names
    
    for line in data_source.content.split('\n'):
        line = line.strip()
        if line and not line.startswith('Elo Rank'):
            # Extract name from the line (tab-separated format)
            parts = line.split('\t')
            if len(parts) >= 2:
                name = parts[1].strip()
                if name and name != 'Player':
                    names.append(name)
    
    print(f"Loaded {len(names)} player names from {data_source.source_type} source")
    return names

def get_player_tiers(gender: str) -> Dict[str, str]:
    """Extract player tiers from the tier file"""
    from .data_loader import get_data_loader
    
    data_loader = get_data_loader()
    data_source = data_loader.get_data_source(gender, 'tier')
    
    tiers = {}
    if not data_source:
        print(f"Warning: Could not load tier data for {gender}")
        return tiers
    
    import re
    pattern = r'(?:MenPlayer|WomenPlayer)\("([^"]+)",\s*"[^"]+",\s*[^,]*,\s*Tier\.([A-D])(?:,[^)]*)?\)'
    matches = re.findall(pattern, data_source.content)
    for name, tier in matches:
        tiers[name] = tier
    
    print(f"Loaded {len(tiers)} player tiers from {data_source.source_type} source")
    return tiers

def get_player_elo(gender: str) -> Dict[str, float]:
    """Extract Elo ratings from the Elo file"""
    from .data_loader import get_data_loader
    
    data_loader = get_data_loader()
    data_source = data_loader.get_data_source(gender, 'elo')
    
    if not data_source:
        print(f"Warning: Could not load Elo data for {gender}")
        return {}
    
    return _extract_elo_values_from_content(data_source.content, 3)  # Elo is in column 3

def get_player_helo(gender: str) -> Dict[str, float]:
    """Extract hElo ratings from the Elo file"""
    from .data_loader import get_data_loader
    
    data_loader = get_data_loader()
    data_source = data_loader.get_data_source(gender, 'elo')
    
    if not data_source:
        print(f"Warning: Could not load Elo data for {gender}")
        return {}
    
    return _extract_elo_values_from_content(data_source.content, 6)  # hElo is in column 6

def get_player_celo(gender: str) -> Dict[str, float]:
    """Extract cElo ratings from the Elo file"""
    from .data_loader import get_data_loader
    
    data_loader = get_data_loader()
    data_source = data_loader.get_data_source(gender, 'elo')
    
    if not data_source:
        print(f"Warning: Could not load Elo data for {gender}")
        return {}
    
    return _extract_elo_values_from_content(data_source.content, 8)  # cElo is in column 8

def get_player_gelo(gender: str) -> Dict[str, float]:
    """Extract gElo ratings from the Elo file"""
    from .data_loader import get_data_loader
    
    data_loader = get_data_loader()
    data_source = data_loader.get_data_source(gender, 'elo')
    
    if not data_source:
        print(f"Warning: Could not load Elo data for {gender}")
        return {}
    
    return _extract_elo_values_from_content(data_source.content, 10)  # gElo is in column 10

def get_player_yelo(gender: str) -> Dict[str, float]:
    """Extract yElo ratings from the yElo file"""
    from .data_loader import get_data_loader
    
    data_loader = get_data_loader()
    data_source = data_loader.get_data_source(gender, 'yelo')
    
    if not data_source:
        print(f"Warning: Could not load yElo data for {gender}")
        return {}
    
    return _extract_yelo_values_from_content(data_source.content)

def get_player_form(gender: str) -> Dict[str, float]:
    """Extract player form values from the form file (yElo_form2w column)"""
    from .data_loader import get_data_loader
    
    data_loader = get_data_loader()
    data_source = data_loader.get_data_source(gender, 'form')
    
    form_values = {}
    if not data_source:
        print(f"Warning: Could not load form data for {gender}")
        return form_values
    
    print(f"Loading form data from {data_source.source_type} source")
    for line_num, line in enumerate(data_source.content.split('\n'), 1):
        line = line.strip()
        if line and not line.startswith('Rank'):
            parts = line.split('\t')
            if len(parts) >= 6:  # yElo_form2w is in column 5 (index 5)
                name = parts[1].strip()  # Name is in column 1
                try:
                    value = float(parts[5].strip()) if parts[5].strip() else None
                    if value is not None:
                        form_values[name] = value
                        if len(form_values) <= 5:  # Debug first 5 entries
                            print(f"  Loaded form for {name}: {value}")
                except (ValueError, IndexError) as e:
                    if line_num <= 5:  # Debug first 5 errors
                        print(f"  Error parsing line {line_num}: {e} - {line}")
                    continue
    
    print(f"Loaded form data for {len(form_values)} players from {data_source.source_type} source")
    return form_values

def get_player_ranking(gender: str) -> Dict[str, int]:
    """Extract player rankings from the Elo file"""
    from .data_loader import get_data_loader
    
    data_loader = get_data_loader()
    data_source = data_loader.get_data_source(gender, 'elo')
    
    ranking = {}
    if not data_source:
        print(f"Warning: Could not load Elo data for {gender}")
        return ranking
    
    for line in data_source.content.split('\n'):
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
    
    print(f"Loaded {len(ranking)} player rankings from {data_source.source_type} source")
    return ranking

def _extract_elo_values_from_content(content: str, column_index: int) -> Dict[str, float]:
    """Extract Elo values from content string"""
    elo_values = {}
    for line in content.split('\n'):
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

def _extract_yelo_values_from_content(content: str) -> Dict[str, float]:
    """Extract yElo values from content string"""
    yelo_values = {}
    for line in content.split('\n'):
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
    print(f"Found {len(names)} player names")
    
    tiers = get_player_tiers(gender)
    print(f"Found {len(tiers)} player tiers")
    
    elo_ratings = get_player_elo(gender)
    print(f"Found {len(elo_ratings)} Elo ratings")
    
    helo_ratings = get_player_helo(gender)
    print(f"Found {len(helo_ratings)} hElo ratings")
    
    celo_ratings = get_player_celo(gender)
    print(f"Found {len(celo_ratings)} cElo ratings")
    
    gelo_ratings = get_player_gelo(gender)
    print(f"Found {len(gelo_ratings)} gElo ratings")
    
    yelo_ratings = get_player_yelo(gender)
    print(f"Found {len(yelo_ratings)} yElo ratings")
    
    form_values = get_player_form(gender)
    print(f"Found {len(form_values)} form values")
    
    rankings = get_player_ranking(gender)
    print(f"Found {len(rankings)} rankings")
    
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
            form=form_values.get(name),
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
        print(f"     Form: {data.form}")
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