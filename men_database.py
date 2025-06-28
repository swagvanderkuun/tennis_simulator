#!/usr/bin/env python3
"""
Men's Tennis Player Database for Scorito Game
This file contains all men players with their tier assignments.
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
class MenPlayer:
    name: str
    country: str
    seeding: Optional[int]
    tier: Tier
    elo: Optional[float] = None
    helo: Optional[float] = None
    celo: Optional[float] = None
    gelo: Optional[float] = None
    yelo: Optional[float] = None
    atp_rank: Optional[int] = None

# MEN'S PLAYER DATABASE
# You can modify the 'tier' attribute for any player to change their tier assignment
MEN_PLAYERS = [
    MenPlayer("Jannik Sinner", "ITA", 1, Tier.A),
    MenPlayer("Luca Nardi", "ITA", None, Tier.D),
    MenPlayer("Chun Hsin Tseng", "TPE", None, Tier.D),
    MenPlayer("Aleksandar Vukic", "AUS", None, Tier.D),
    MenPlayer("Pedro Martinez", "ESP", None, Tier.D),
    MenPlayer("George Loffhagen", "GBR", None, Tier.D),
    MenPlayer("Mariano Navone", "ARG", None, Tier.D),
    MenPlayer("Denis Shapovalov", "CAN", 27, Tier.C),
    
    MenPlayer("Grigor Dimitrov", "BUL", 19, Tier.C),
    MenPlayer("Yoshihito Nishioka", "JPN", None, Tier.D),
    MenPlayer("Francisco Comesana", "ARG", None, Tier.D),
    MenPlayer("Corentin Moutet", "FRA", None, Tier.D),
    MenPlayer("Sebastian Ofner", "AUT", None, Tier.D),
    MenPlayer("Hamad Medjedovic", "SRB", None, Tier.D),
    MenPlayer("Johannus Monday", "GBR", None, Tier.D),
    MenPlayer("Tommy Paul", "USA", 13, Tier.B),
    
    MenPlayer("Ben Shelton", "USA", 10, Tier.B),
    MenPlayer("Alex Bolt", "AUS", None, Tier.D),
    MenPlayer("Rinky Hijikata", "AUS", None, Tier.D),
    MenPlayer("David Goffin", "BEL", None, Tier.D),
    MenPlayer("Aleksandar Kovacevic", "USA", None, Tier.D),
    MenPlayer("Marton Fucsovics", "HUN", None, Tier.D),
    MenPlayer("Gael Monfils", "FRA", None, Tier.D),
    MenPlayer("Ugo Humbert", "FRA", 18, Tier.C),
    
    MenPlayer("Brandon Nakashima", "USA", 29, Tier.C),
    MenPlayer("Bu Yunchaokete", "CHN", None, Tier.D),
    MenPlayer("Alexander Shevchenko", "KAZ", None, Tier.D),
    MenPlayer("Reilly Opelka", "USA", None, Tier.D),
    MenPlayer("Jaime Faria", "POR", None, Tier.D),
    MenPlayer("Lorenzo Sonego", "ITA", None, Tier.D),
    MenPlayer("Nikoloz Basilashvili", "GEO", None, Tier.D),
    MenPlayer("Lorenzo Musetti", "ITA", 7, Tier.B),
    
    MenPlayer("Jack Draper", "GBR", 4, Tier.A),
    MenPlayer("Sebastian Baez", "ARG", None, Tier.D),
    MenPlayer("Raphael Collignon", "BEL", None, Tier.D),
    MenPlayer("Marin Cilic", "CRO", None, Tier.D),
    MenPlayer("James Mccabe", "AUS", None, Tier.D),
    MenPlayer("Fabian Marozsan", "HUN", None, Tier.D),
    MenPlayer("Jaume Munar", "ESP", None, Tier.D),
    MenPlayer("Alexander Bublik", "KAZ", 28, Tier.C),
    
    MenPlayer("Flavio Cobolli", "ITA", 22, Tier.C),
    MenPlayer("Beibit Zhukayev", "KAZ", None, Tier.D),
    MenPlayer("Tomas Martin Etcheverry", "ARG", None, Tier.D),
    MenPlayer("Jack Pinnington Jones", "GBR", None, Tier.D),
    MenPlayer("Marcos Giron", "USA", None, Tier.D),
    MenPlayer("Camilo Ugo Carabelli", "ARG", None, Tier.D),
    MenPlayer("Hugo Gaston", "FRA", None, Tier.D),
    MenPlayer("Jakub Mensik", "CZE", 15, Tier.B),
    
    MenPlayer("Alex De Minaur", "AUS", 11, Tier.B),
    MenPlayer("Roberto Carballes Baena", "ESP", None, Tier.D),
    MenPlayer("Arthur Cazaux", "FRA", None, Tier.D),
    MenPlayer("Adam Walton", "AUS", None, Tier.D),
    MenPlayer("Quentin Halys", "FRA", None, Tier.D),
    MenPlayer("August Holmgren", "DEN", None, Tier.D),
    MenPlayer("Damir Dzumhur", "BIH", None, Tier.D),
    MenPlayer("Tomas Machac", "CZE", 21, Tier.C),
    
    MenPlayer("Alex Michelsen", "USA", 30, Tier.D),
    MenPlayer("Miomir Kecmanovic", "SRB", None, Tier.D),
    MenPlayer("Jesper De Jong", "NED", None, Tier.D),
    MenPlayer("Christopher Eubanks", "USA", None, Tier.D),
    MenPlayer("Daniel Evans", "GBR", None, Tier.D),
    MenPlayer("Jay Clarke", "GBR", None, Tier.D),
    MenPlayer("Alexandre Muller", "FRA", None, Tier.D),
    MenPlayer("Novak Djokovic", "SRB", 6, Tier.A),
    
    MenPlayer("Taylor Fritz", "USA", 5, Tier.A),
    MenPlayer("Giovanni Mpetshi Perricard", "FRA", None, Tier.C),
    MenPlayer("Gabriel Diallo", "CAN", None, Tier.D),
    MenPlayer("Daniel Altmaier", "GER", None, Tier.D),
    MenPlayer("Matteo Arnaldi", "ITA", None, Tier.D),
    MenPlayer("Botic Van De Zandschulp", "NED", None, Tier.D),
    MenPlayer("Brandon Holt", "USA", None, Tier.D),
    MenPlayer("Alejandro Davidovich Fokina", "ESP", 26, Tier.C),
    
    MenPlayer("Alexei Popyrin", "AUS", 20, Tier.C),
    MenPlayer("Arthur Fery", "GBR", None, Tier.D),
    MenPlayer("Luciano Darderi", "ITA", None, Tier.D),
    MenPlayer("Roman Safiullin", "RUS", None, Tier.D),
    MenPlayer("Vit Kopriva", "CZE", None, Tier.D),
    MenPlayer("Jordan Thompson", "AUS", None, Tier.D),
    MenPlayer("Benjamin Bonzi", "FRA", None, Tier.D),
    MenPlayer("Daniil Medvedev", "RUS", 9, Tier.B),
    
    MenPlayer("Francisco Cerundolo", "ARG", 16, Tier.C),
    MenPlayer("Nuno Borges", "POR", None, Tier.D),
    MenPlayer("Billy Harris", "GBR", None, Tier.D),
    MenPlayer("Hubert Hurkacz", "POL", None, Tier.D),
    MenPlayer("Shintaro Mochizuki", "JPN", None, Tier.D),
    MenPlayer("Giulio Zeppieri", "ITA", None, Tier.D),
    MenPlayer("Mackenzie Mcdonald", "USA", None, Tier.D),
    MenPlayer("Karen Khachanov", "RUS", 17, Tier.C),
    
    MenPlayer("Matteo Berrettini", "ITA", 32, Tier.C),
    MenPlayer("Kamil Majchrzak", "POL", None, Tier.D),
    MenPlayer("Ethan Quinn", "USA", None, Tier.D),
    MenPlayer("Henry Searle", "GBR", None, Tier.D),
    MenPlayer("Pablo Carreno Busta", "ESP", None, Tier.D),
    MenPlayer("Chris Rodesch", "LUX", None, Tier.D),
    MenPlayer("Arthur Rinderknech", "FRA", None, Tier.D),
    MenPlayer("Alexander Zverev", "GER", 3, Tier.A),
    
    MenPlayer("Holger Rune", "DEN", 8, Tier.B),
    MenPlayer("Nicolas Jarry", "CHI", None, Tier.D),
    MenPlayer("Learner Tien", "USA", None, Tier.D),
    MenPlayer("Nishesh Basavareddy", "USA", None, Tier.D),
    MenPlayer("Jacob Fearnley", "GBR", None, Tier.D),
    MenPlayer("Joao Fonseca", "BRA", None, Tier.D),
    MenPlayer("Jenson Brooksby", "USA", None, Tier.D),
    MenPlayer("Tallon Griekspoor", "NED", 31, Tier.C),
    
    MenPlayer("Jiri Lehecka", "CZE", 23, Tier.C),
    MenPlayer("Hugo Dellien", "BOL", None, Tier.D),
    MenPlayer("Mattia Bellucci", "ITA", None, Tier.D),
    MenPlayer("Oliver Crawford", "GBR", None, Tier.D),
    MenPlayer("Cameron Norrie", "GBR", None, Tier.D),
    MenPlayer("Roberto Bautista Agut", "ESP", None, Tier.D),
    MenPlayer("Elmer Moller", "DEN", None, Tier.D),
    MenPlayer("Frances Tiafoe", "USA", 12, Tier.B),
    
    MenPlayer("Andrey Rublev", "RUS", 14, Tier.B),
    MenPlayer("Laslo Djere", "SRB", None, Tier.D),
    MenPlayer("Zizou Bergs", "BEL", None, Tier.D),
    MenPlayer("Lloyd Harris", "RSA", None, Tier.D),
    MenPlayer("Adrian Mannarino", "FRA", None, Tier.D),
    MenPlayer("Christopher Oconnell", "AUS", None, Tier.D),
    MenPlayer("Valentin Royer", "FRA", None, Tier.D),
    MenPlayer("Stefanos Tsitsipas", "GRE", 24, Tier.C),
    
    MenPlayer("Felix Auger Aliassime", "CAN", 25, Tier.C),
    MenPlayer("James Duckworth", "AUS", None, Tier.D),
    MenPlayer("Jan Lennard Struff", "GER", None, Tier.D),
    MenPlayer("Filip Misolic", "AUT", None, Tier.D),
    MenPlayer("Oliver Tarvet", "GBR", None, Tier.D),
    MenPlayer("Leandro Riedi", "SUI", None, Tier.D),
    MenPlayer("Fabio Fognini", "ITA", None, Tier.D),
    MenPlayer("Carlos Alcaraz", "ESP", 2, Tier.A),
]

def get_players_by_tier() -> dict:
    """Get all players organized by tier"""
    tiers = {Tier.A: [], Tier.B: [], Tier.C: [], Tier.D: []}
    for player in MEN_PLAYERS:
        tiers[player.tier].append(player)
    return tiers

def get_player_by_name(name: str) -> MenPlayer:
    """Get a player by name"""
    for player in MEN_PLAYERS:
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
                        atp_rank = int(parts[5]) if parts[5] != 'None' else None
                        
                        elo_data[name] = {
                            'elo': elo,
                            'helo': helo,
                            'celo': celo,
                            'gelo': gelo,
                            'atp_rank': atp_rank
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
    for player in MEN_PLAYERS:
        # Try exact name match first
        if player.name in elo_data:
            data = elo_data[player.name]
            player.elo = data['elo']
            player.helo = data['helo']
            player.celo = data['celo']
            player.gelo = data['gelo']
            player.atp_rank = data['atp_rank']
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
    
    print(f"Updated Elo data for {updated_count} men players")

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
    print("MEN'S TENNIS PLAYER DATABASE")
    print("=" * 50)
    
    # Try to inject Elo data if files exist
    inject_elo_data("elo_men.txt", "yelo_men.txt")
    
    print_players_by_tier()
    
    print(f"\nTotal players: {len(MEN_PLAYERS)}")
    tiers = get_players_by_tier()
    for tier in Tier:
        print(f"Tier {tier.value}: {len(tiers[tier])} players")
