"""
Player database management for tennis simulator.
"""

from typing import Dict, List, Optional, Tuple
from pathlib import Path
import json
from ..core.models import Player, Tier, Gender


class PlayerDatabase:
    """Manages player databases for men and women."""
    
    def __init__(self):
        self.men_players: Dict[str, Player] = {}
        self.women_players: Dict[str, Player] = {}
        self._load_default_data()
    
    def _load_default_data(self):
        """Load default player data."""
        # Men's players
        men_data = [
            ("Novak Djokovic", "SRB", 1, Tier.A, 2200, 1),
            ("Carlos Alcaraz", "ESP", 2, Tier.A, 2100, 2),
            ("Daniil Medvedev", "RUS", 3, Tier.A, 2000, 3),
            ("Jannik Sinner", "ITA", 4, Tier.A, 1950, 4),
            ("Andrey Rublev", "RUS", 5, Tier.B, 1900, 5),
            ("Stefanos Tsitsipas", "GRE", 6, Tier.B, 1850, 6),
            ("Holger Rune", "DEN", 7, Tier.B, 1800, 7),
            ("Casper Ruud", "NOR", 8, Tier.B, 1750, 8),
            ("Hubert Hurkacz", "POL", 9, Tier.B, 1700, 9),
            ("Taylor Fritz", "USA", 10, Tier.B, 1650, 10),
            ("Alexander Zverev", "GER", 11, Tier.C, 1600, 11),
            ("Felix Auger-Aliassime", "CAN", 12, Tier.C, 1550, 12),
            ("Karen Khachanov", "RUS", 13, Tier.C, 1500, 13),
            ("Frances Tiafoe", "USA", 14, Tier.C, 1450, 14),
            ("Cameron Norrie", "GBR", 15, Tier.C, 1400, 15),
            ("Tommy Paul", "USA", 16, Tier.C, 1350, 16),
            ("Lorenzo Musetti", "ITA", 17, Tier.D, 1300, 17),
            ("Borna Coric", "CRO", 18, Tier.D, 1250, 18),
            ("Alex de Minaur", "AUS", 19, Tier.D, 1200, 19),
            ("Grigor Dimitrov", "BUL", 20, Tier.D, 1150, 20),
            ("Daniel Evans", "GBR", 21, Tier.D, 1100, 21),
            ("Roberto Bautista Agut", "ESP", 22, Tier.D, 1050, 22),
            ("Francisco Cerundolo", "ARG", 23, Tier.D, 1000, 23),
            ("Nicolas Jarry", "CHI", 24, Tier.D, 950, 24),
            ("Sebastian Korda", "USA", 25, Tier.D, 900, 25),
            ("Alejandro Davidovich Fokina", "ESP", 26, Tier.D, 850, 26),
            ("Denis Shapovalov", "CAN", 27, Tier.D, 800, 27),
            ("Botic van de Zandschulp", "NED", 28, Tier.D, 750, 28),
            ("Yoshihito Nishioka", "JPN", 29, Tier.D, 700, 29),
            ("Tallon Griekspoor", "NED", 30, Tier.D, 650, 30),
            ("Miomir Kecmanovic", "SRB", 31, Tier.D, 600, 31),
            ("Bernabe Zapata Miralles", "ESP", 32, Tier.D, 550, 32),
        ]
        
        for name, country, seeding, tier, elo, rank in men_data:
            player = Player(
                name=name,
                country=country,
                seeding=seeding,
                tier=tier,
                elo=elo,
                atp_rank=rank
            )
            self.men_players[name] = player
        
        # Women's players
        women_data = [
            ("Iga Swiatek", "POL", 1, Tier.A, 2100, 1),
            ("Aryna Sabalenka", "BLR", 2, Tier.A, 2000, 2),
            ("Elena Rybakina", "KAZ", 3, Tier.A, 1950, 3),
            ("Jessica Pegula", "USA", 4, Tier.A, 1900, 4),
            ("Caroline Garcia", "FRA", 5, Tier.B, 1850, 5),
            ("Ons Jabeur", "TUN", 6, Tier.B, 1800, 6),
            ("Coco Gauff", "USA", 7, Tier.B, 1750, 7),
            ("Maria Sakkari", "GRE", 8, Tier.B, 1700, 8),
            ("Petra Kvitova", "CZE", 9, Tier.B, 1650, 9),
            ("Barbora Krejcikova", "CZE", 10, Tier.B, 1600, 10),
            ("Daria Kasatkina", "RUS", 11, Tier.C, 1550, 11),
            ("Belinda Bencic", "SUI", 12, Tier.C, 1500, 12),
            ("Beatriz Haddad Maia", "BRA", 13, Tier.C, 1450, 13),
            ("Karolina Muchova", "CZE", 14, Tier.C, 1400, 14),
            ("Liudmila Samsonova", "RUS", 15, Tier.C, 1350, 15),
            ("Victoria Azarenka", "BLR", 16, Tier.C, 1300, 16),
            ("Veronika Kudermetova", "RUS", 17, Tier.D, 1250, 17),
            ("Madison Keys", "USA", 18, Tier.D, 1200, 18),
            ("Elise Mertens", "BEL", 19, Tier.D, 1150, 19),
            ("Donna Vekic", "CRO", 20, Tier.D, 1100, 20),
            ("Magda Linette", "POL", 21, Tier.D, 1050, 21),
            ("Anastasia Potapova", "RUS", 22, Tier.D, 1000, 22),
            ("Katerina Siniakova", "CZE", 23, Tier.D, 950, 23),
            ("Marie Bouzkova", "CZE", 24, Tier.D, 900, 24),
            ("Anhelina Kalinina", "UKR", 25, Tier.D, 850, 25),
            ("Sloane Stephens", "USA", 26, Tier.D, 800, 26),
            ("Bernarda Pera", "USA", 27, Tier.D, 750, 27),
            ("Marta Kostyuk", "UKR", 28, Tier.D, 700, 28),
            ("Lesia Tsurenko", "UKR", 29, Tier.D, 650, 29),
            ("Alison Riske-Amritraj", "USA", 30, Tier.D, 600, 30),
            ("Irina-Camelia Begu", "ROU", 31, Tier.D, 550, 31),
            ("Shelby Rogers", "USA", 32, Tier.D, 500, 32),
        ]
        
        for name, country, seeding, tier, elo, rank in women_data:
            player = Player(
                name=name,
                country=country,
                seeding=seeding,
                tier=tier,
                elo=elo,
                wta_rank=rank
            )
            self.women_players[name] = player
    
    def get_players_by_gender(self, gender: Gender) -> Dict[str, Player]:
        """Get all players for a specific gender."""
        return self.men_players if gender == Gender.MEN else self.women_players
    
    def get_players_by_tier(self, gender: Gender, tier: Tier) -> List[Player]:
        """Get players of a specific gender and tier."""
        players = self.get_players_by_gender(gender)
        return [p for p in players.values() if p.tier == tier]
    
    def get_player_by_name(self, name: str, gender: Gender) -> Optional[Player]:
        """Get a specific player by name and gender."""
        players = self.get_players_by_gender(gender)
        return players.get(name)
    
    def update_player_tier(self, name: str, gender: Gender, new_tier: Tier) -> bool:
        """Update a player's tier."""
        player = self.get_player_by_name(name, gender)
        if player:
            player.tier = new_tier
            return True
        return False
    
    def inject_elo_data(self, gender: Gender, elo_file_path: str) -> bool:
        """Inject Elo data from external file."""
        try:
            players = self.get_players_by_gender(gender)
            
            with open(elo_file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    parts = line.split(',')
                    if len(parts) >= 2:
                        name = parts[0].strip()
                        elo_value = float(parts[1].strip())
                        
                        if name in players:
                            players[name].elo = elo_value
            
            return True
        except Exception as e:
            print(f"Error injecting Elo data: {e}")
            return False
    
    def inject_yelo_data(self, gender: Gender, yelo_file_path: str) -> bool:
        """Inject yElo data from external file."""
        try:
            players = self.get_players_by_gender(gender)
            
            with open(yelo_file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    parts = line.split(',')
                    if len(parts) >= 2:
                        name = parts[0].strip()
                        yelo_value = float(parts[1].strip())
                        
                        if name in players:
                            players[name].yelo = yelo_value
            
            return True
        except Exception as e:
            print(f"Error injecting yElo data: {e}")
            return False
    
    def print_players_by_tier(self, gender: Gender) -> None:
        """Print all players organized by tier."""
        print(f"\n{gender.value.upper()} PLAYERS BY TIER:")
        print("=" * 50)
        
        for tier in Tier:
            players = self.get_players_by_tier(gender, tier)
            if players:
                print(f"\nTIER {tier.value}:")
                for player in sorted(players, key=lambda p: p.get_primary_rank() or 999):
                    elo_info = f" [Elo: {player.get_best_elo():.0f}]" if player.get_best_elo() else ""
                    rank_info = f" (Rank: {player.get_primary_rank()})" if player.get_primary_rank() else ""
                    print(f"  {player.name} ({player.country}){rank_info}{elo_info}")
    
    def save_to_json(self, filepath: str, gender: Gender) -> bool:
        """Save player database to JSON file."""
        try:
            players = self.get_players_by_gender(gender)
            data = {}
            
            for name, player in players.items():
                data[name] = {
                    "name": player.name,
                    "country": player.country,
                    "seeding": player.seeding,
                    "tier": player.tier.value,
                    "elo": player.elo,
                    "helo": player.helo,
                    "celo": player.celo,
                    "gelo": player.gelo,
                    "yelo": player.yelo,
                    "atp_rank": player.atp_rank,
                    "wta_rank": player.wta_rank
                }
            
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving database: {e}")
            return False
    
    def load_from_json(self, filepath: str, gender: Gender) -> bool:
        """Load player database from JSON file."""
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            players = self.get_players_by_gender(gender)
            players.clear()
            
            for name, player_data in data.items():
                player = Player(
                    name=player_data["name"],
                    country=player_data["country"],
                    seeding=player_data["seeding"],
                    tier=Tier(player_data["tier"]),
                    elo=player_data.get("elo"),
                    helo=player_data.get("helo"),
                    celo=player_data.get("celo"),
                    gelo=player_data.get("gelo"),
                    yelo=player_data.get("yelo"),
                    atp_rank=player_data.get("atp_rank"),
                    wta_rank=player_data.get("wta_rank")
                )
                players[name] = player
            
            return True
        except Exception as e:
            print(f"Error loading database: {e}")
            return False
    
    def get_statistics(self, gender: Gender) -> Dict:
        """Get statistics about the player database."""
        players = self.get_players_by_gender(gender)
        
        stats = {
            "total_players": len(players),
            "players_by_tier": {},
            "players_with_elo": 0,
            "players_with_rank": 0,
            "seeded_players": 0
        }
        
        for tier in Tier:
            tier_players = self.get_players_by_tier(gender, tier)
            stats["players_by_tier"][tier.value] = len(tier_players)
        
        for player in players.values():
            if player.get_best_elo():
                stats["players_with_elo"] += 1
            if player.get_primary_rank():
                stats["players_with_rank"] += 1
            if player.is_seeded():
                stats["seeded_players"] += 1
        
        return stats


# Global database instance
player_db = PlayerDatabase() 