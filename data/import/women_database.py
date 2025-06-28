#!/usr/bin/env python3
"""
Women's Tennis Player Database for Scorito Game
This file contains all women players with their tier assignments.
You can modify the tier assignments by changing the 'tier' attribute for each player.
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum

class Tier(Enum):
    A = "A"
    B = "B" 
    C = "C"
    D = "D"

@dataclass
class WomenPlayer:
    name: str
    country: str
    seeding: Optional[int]
    tier: Tier
    elo: Optional[float] = None
    helo: Optional[float] = None
    celo: Optional[float] = None
    gelo: Optional[float] = None
    yelo: Optional[float] = None
    wta_rank: Optional[int] = None

# WOMEN'S PLAYER DATABASE
# You can modify the 'tier' attribute for any player to change their tier assignment
WOMEN_PLAYERS = [
    WomenPlayer("Aryna Sabalenka", "BLR", 1, Tier.A),
    WomenPlayer("Carson Branstine", "USA", None, Tier.D),
    WomenPlayer("Lulu Sun", "NZL", None, Tier.D),
    WomenPlayer("Marie Bouzkova", "CZE", None, Tier.C),
    WomenPlayer("Emma Raducanu", "GBR", None, Tier.B),
    WomenPlayer("Mingge Xu", "GBR", None, Tier.D),
    WomenPlayer("Marketa Vondrousova", "CZE", None, Tier.B),
    WomenPlayer("Mccartney Kessler", "USA", 32, Tier.A),
    
    WomenPlayer("Elise Mertens", "BEL", 24, Tier.A),
    WomenPlayer("Linda Fruhvirtova", "CZE", None, Tier.D),
    WomenPlayer("Ann Li", "USA", None, Tier.D),
    WomenPlayer("Viktorija Golubic", "SUI", None, Tier.C),
    WomenPlayer("Varvara Gracheva", "FRA", None, Tier.D),
    WomenPlayer("Aliaksandra Sasnovich", "BLR", None, Tier.D),
    WomenPlayer("Anna Bondar", "HUN", None, Tier.D),
    WomenPlayer("Elina Svitolina", "UKR", 14, Tier.A),
    
    WomenPlayer("Paula Badosa", "ESP", 9, Tier.A),
    WomenPlayer("Katie Boulter", "GBR", None, Tier.B),
    WomenPlayer("Greet Minnen", "BEL", None, Tier.C),
    WomenPlayer("Olivia Gadecki", "AUS", None, Tier.D),
    WomenPlayer("Anca Alexia Todoni", "ROU", None, Tier.B),
    WomenPlayer("Cristina Bucsa", "ESP", None, Tier.D),
    WomenPlayer("Kimberly Birrell", "AUS", None, Tier.D),
    WomenPlayer("Donna Vekic", "CRO", 22, Tier.A),
    
    WomenPlayer("Leylah Fernandez", "CAN", 29, Tier.A),
    WomenPlayer("Hannah Klugman", "GBR", None, Tier.D),
    WomenPlayer("Peyton Stearns", "USA", None, Tier.D),
    WomenPlayer("Laura Siegemund", "GER", None, Tier.D),
    WomenPlayer("Olga Danilovic", "SRB", None, Tier.C),
    WomenPlayer("Shuai Zhang", "CHN", None, Tier.D),
    WomenPlayer("Elena Gabriela Ruse", "ROU", None, Tier.B),
    WomenPlayer("Madison Keys", "USA", 6, Tier.A),
    
    WomenPlayer("Jasmine Paolini", "ITA", 4, Tier.A),
    WomenPlayer("Anastasija Sevastova", "LAT", None, Tier.D),
    WomenPlayer("Kamilla Rakhimova", "RUS", None, Tier.D),
    WomenPlayer("Aoi Ito", "JPN", None, Tier.D),
    WomenPlayer("Eva Lys", "GER", None, Tier.D),
    WomenPlayer("Yue Yuan", "CHN", None, Tier.D),
    WomenPlayer("Bernarda Pera", "USA", None, Tier.D),
    WomenPlayer("Linda Noskova", "CZE", 30, Tier.A),
    
    WomenPlayer("Beatriz Haddad Maia", "BRA", 21, Tier.A),
    WomenPlayer("Rebecca Sramkova", "SVK", None, Tier.D),
    WomenPlayer("Harriet Dart", "GBR", None, Tier.D),
    WomenPlayer("Dalma Galfi", "HUN", None, Tier.C),
    WomenPlayer("Yanina Wickmayer", "BEL", None, Tier.C),
    WomenPlayer("Renata Zarazua", "MEX", None, Tier.D),
    WomenPlayer("Yulia Putintseva", "KAZ", None, Tier.C),
    WomenPlayer("Amanda Anisimova", "USA", 13, Tier.A),
    
    WomenPlayer("Diana Shnaider", "RUS", 12, Tier.A),
    WomenPlayer("Moyuka Uchijima", "JPN", None, Tier.D),
    WomenPlayer("Diane Parry", "FRA", None, Tier.D),
    WomenPlayer("Petra Martic", "CRO", None, Tier.D),
    WomenPlayer("Viktoriya Tomova", "BUL", None, Tier.D),
    WomenPlayer("Sonay Kartal", "GBR", None, Tier.D),
    WomenPlayer("Ons Jabeur", "TUN", None, Tier.C),
    WomenPlayer("Jelena Ostapenko", "LAT", 20, Tier.A),
    
    WomenPlayer("Ashlyn Krueger", "USA", 31, Tier.A),
    WomenPlayer("Mika Stojsavljevic", "GBR", None, Tier.D),
    WomenPlayer("Anastasia Pavlyuchenkova", "RUS", None, Tier.D),
    WomenPlayer("Ajla Tomljanovic", "AUS", None, Tier.C),
    WomenPlayer("Naomi Osaka", "JPN", None, Tier.C),
    WomenPlayer("Talia Gibson", "AUS", None, Tier.D),
    WomenPlayer("Katerina Siniakova", "CZE", None, Tier.C),
    WomenPlayer("Qinwen Zheng", "CHN", 5, Tier.A),
    
    WomenPlayer("Mirra Andreeva", "RUS", 7, Tier.A),
    WomenPlayer("Mayar Sherif", "EGY", None, Tier.D),
    WomenPlayer("Jil Teichmann", "SUI", None, Tier.D),
    WomenPlayer("Lucia Bronzetti", "ITA", None, Tier.D),
    WomenPlayer("Hailey Baptiste", "USA", None, Tier.D),
    WomenPlayer("Sorana Cirstea", "ROU", None, Tier.C),
    WomenPlayer("Anastasia Potapova", "RUS", None, Tier.C),
    WomenPlayer("Magdalena Frech", "POL", 25, Tier.A),
    
    WomenPlayer("Barbora Krejcikova", "CZE", 17, Tier.A),
    WomenPlayer("Alexandra Eala", "PHI", None, Tier.D),
    WomenPlayer("Caroline Dolehide", "USA", None, Tier.D),
    WomenPlayer("Arantxa Rus", "NED", None, Tier.D),
    WomenPlayer("Veronika Kudermetova", "RUS", None, Tier.C),
    WomenPlayer("Lin Zhu", "CHN", None, Tier.D),
    WomenPlayer("Petra Kvitova", "CZE", None, Tier.D),
    WomenPlayer("Emma Navarro", "USA", 10, Tier.A),
    
    WomenPlayer("Karolina Muchova", "CZE", 15, Tier.A),
    WomenPlayer("Xin Yu Wang", "CHN", None, Tier.C),
    WomenPlayer("Zeynep Sonmez", "TUR", None, Tier.D),
    WomenPlayer("Jaqueline Cristian", "ROU", None, Tier.D),
    WomenPlayer("Suzan Lamens", "NED", None, Tier.D),
    WomenPlayer("Iva Jovic", "USA", None, Tier.D),
    WomenPlayer("Priscilla Hon", "AUS", None, Tier.D),
    WomenPlayer("Ekaterina Alexandrova", "RUS", 18, Tier.A),
    
    WomenPlayer("Magda Linette", "POL", 27, Tier.A),
    WomenPlayer("Elsa Jacquemot", "FRA", None, Tier.D),
    WomenPlayer("Alycia Parks", "USA", None, Tier.D),
    WomenPlayer("Belinda Bencic", "SUI", None, Tier.D),
    WomenPlayer("Katie Volynets", "USA", None, Tier.D),
    WomenPlayer("Tatjana Maria", "GER", None, Tier.D),
    WomenPlayer("Elisabetta Cocciaretto", "ITA", None, Tier.D),
    WomenPlayer("Jessica Pegula", "USA", 3, Tier.A),
    
    WomenPlayer("Iga Swiatek", "POL", 8, Tier.A),
    WomenPlayer("Polina Kudermetova", "RUS", None, Tier.D),
    WomenPlayer("Caty Mcnally", "USA", None, Tier.D),
    WomenPlayer("Jodie Burrage", "GBR", None, Tier.D),
    WomenPlayer("Camila Osorio", "COL", None, Tier.D),
    WomenPlayer("Danielle Collins", "USA", None, Tier.D),
    WomenPlayer("Veronika Erjavec", "SLO", None, Tier.D),
    WomenPlayer("Marta Kostyuk", "UKR", 26, Tier.A),
    
    WomenPlayer("Clara Tauson", "DEN", 23, Tier.A),
    WomenPlayer("Heather Watson", "GBR", None, Tier.D),
    WomenPlayer("Anna Kalinskaya", "RUS", None, Tier.D),
    WomenPlayer("Nina Stojanovic", "SRB", None, Tier.D),
    WomenPlayer("Maria Sakkari", "GRE", None, Tier.D),
    WomenPlayer("Anna Blinkova", "RUS", None, Tier.D),
    WomenPlayer("Elina Avanesyan", "ARM", None, Tier.D),
    WomenPlayer("Elena Rybakina", "KAZ", 11, Tier.A),
    
    WomenPlayer("Daria Kasatkina", "AUS", 16, Tier.A),
    WomenPlayer("Emiliana Arango", "COL", None, Tier.D),
    WomenPlayer("Irina Camelia Begu", "ROU", None, Tier.D),
    WomenPlayer("Kaja Juvan", "SLO", None, Tier.D),
    WomenPlayer("Yuliia Starodubtseva", "UKR", None, Tier.D),
    WomenPlayer("Francesca Jones", "GBR", None, Tier.D),
    WomenPlayer("Maya Joint", "AUS", None, Tier.D),
    WomenPlayer("Liudmila Samsonova", "RUS", 19, Tier.A),
    
    WomenPlayer("Sofia Kenin", "USA", 28, Tier.A),
    WomenPlayer("Taylor Townsend", "USA", None, Tier.D),
    WomenPlayer("Jessica Bouzas Maneiro", "ESP", None, Tier.D),
    WomenPlayer("Ella Seidel", "GER", None, Tier.D),
    WomenPlayer("Victoria Azarenka", "BLR", None, Tier.D),
    WomenPlayer("Anastasia Zakharova", "RUS", None, Tier.D),
    WomenPlayer("Dayana Yastremska", "UKR", None, Tier.D),
    WomenPlayer("Coco Gauff", "USA", 2, Tier.A),
]

def get_players_by_tier() -> dict:
    """Get all players organized by tier"""
    tiers = {Tier.A: [], Tier.B: [], Tier.C: [], Tier.D: []}
    for player in WOMEN_PLAYERS:
        tiers[player.tier].append(player)
    return tiers

def get_player_by_name(name: str) -> WomenPlayer:
    """Get a player by name"""
    for player in WOMEN_PLAYERS:
        if player.name == name:
            return player
    return None

def update_player_tier(player_name: str, new_tier: Tier):
    """Update a player's tier assignment"""
    player = get_player_by_name(player_name)
    if player:
        player.tier = new_tier
        print(f"Updated {player_name} to Tier {new_tier.value}")
    else:
        print(f"Player {player_name} not found")

def inject_elo_data(elo_file_path: str, yelo_file_path: str):
    """Inject Elo data from files into the player database"""
    # Load Elo data
    elo_data = {}
    yelo_data = {}
    
    # Read Elo file
    try:
        with open(elo_file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split(',')
                    if len(parts) >= 6:
                        name = parts[0].strip()
                        elo = float(parts[1]) if parts[1] != 'None' else None
                        helo = float(parts[2]) if parts[2] != 'None' else None
                        celo = float(parts[3]) if parts[3] != 'None' else None
                        gelo = float(parts[4]) if parts[4] != 'None' else None
                        wta_rank = int(parts[5]) if parts[5] != 'None' else None
                        
                        elo_data[name] = {
                            'elo': elo,
                            'helo': helo,
                            'celo': celo,
                            'gelo': gelo,
                            'wta_rank': wta_rank
                        }
    except FileNotFoundError:
        print(f"Warning: Elo file {elo_file_path} not found")
    
    # Read yElo file
    try:
        with open(yelo_file_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split(',')
                    if len(parts) >= 2:
                        name = parts[0].strip()
                        yelo = float(parts[1]) if parts[1] != 'None' else None
                        yelo_data[name] = yelo
    except FileNotFoundError:
        print(f"Warning: yElo file {yelo_file_path} not found")
    
    # Inject data into players
    updated_count = 0
    for player in WOMEN_PLAYERS:
        # Try exact name match first
        if player.name in elo_data:
            data = elo_data[player.name]
            player.elo = data['elo']
            player.helo = data['helo']
            player.celo = data['celo']
            player.gelo = data['gelo']
            player.wta_rank = data['wta_rank']
            updated_count += 1
        elif player.name in yelo_data:
            player.yelo = yelo_data[player.name]
            updated_count += 1
        
        # Try partial name matching for yElo
        if player.yelo is None:
            for yelo_name, yelo_value in yelo_data.items():
                if player.name.lower() in yelo_name.lower() or yelo_name.lower() in player.name.lower():
                    player.yelo = yelo_value
                    break
    
    print(f"Updated Elo data for {updated_count} women players")

def print_players_by_tier():
    """Print all players organized by tier"""
    tiers = get_players_by_tier()
    for tier in Tier:
        print(f"\nTier {tier.value}:")
        for player in tiers[tier]:
            seeding_info = f"(#{player.seeding})" if player.seeding else "(unseeded)"
            elo_info = f" [Elo: {player.elo:.0f}]" if player.elo else ""
            yelo_info = f" [yElo: {player.yelo:.0f}]" if player.yelo else ""
            print(f"  {player.name} {seeding_info} ({player.country}){elo_info}{yelo_info}")

if __name__ == "__main__":
    print("WOMEN'S TENNIS PLAYER DATABASE")
    print("=" * 50)
    
    # Try to inject Elo data if files exist
    inject_elo_data("elo_women.txt", "yelo_women.txt")
    
    print_players_by_tier()
    
    print(f"\nTotal players: {len(WOMEN_PLAYERS)}")
    tiers = get_players_by_tier()
    for tier in Tier:
        print(f"Tier {tier.value}: {len(tiers[tier])} players")
