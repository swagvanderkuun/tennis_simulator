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
    r64_chance: float
    r32_chance: float
    r16_chance: float
    qf_chance: float
    sf_chance: float
    f_chance: float
    w_chance: float

# WOMEN'S PLAYER DATABASE
# You can modify the 'tier' attribute for any player to change their tier assignment
WOMEN_PLAYERS = [
    WomenPlayer("Aryna Sabalenka", "BLR", 1, Tier.A, 0.932, 0.806, 0.588, 0.449, 0.351, 0.270, 0.193),
    WomenPlayer("Carson Branstine", "USA", None, Tier.D, 0.068, 0.022, 0.004, 0.001, 0.000, 0.000, 0.000),
    WomenPlayer("Lulu Sun", "NZL", None, Tier.D, 0.401, 0.057, 0.015, 0.004, 0.001, 0.000, 0.000),
    WomenPlayer("Marie Bouzkova", "CZE", None, Tier.D, 0.599, 0.115, 0.038, 0.015, 0.006, 0.002, 0.001),
    WomenPlayer("Emma Raducanu", "GBR", None, Tier.C, 0.853, 0.354, 0.111, 0.056, 0.029, 0.015, 0.007),
    WomenPlayer("Mingge Xu", "GBR", None, Tier.D, 0.147, 0.016, 0.001, 0.000, 0.000, 0.000, 0.000),
    WomenPlayer("Marketa Vondrousova", "CZE", None, Tier.D, 0.584, 0.386, 0.159, 0.098, 0.062, 0.039, 0.022),
    WomenPlayer("Mccartney Kessler", "USA", 32, Tier.D, 0.416, 0.243, 0.083, 0.045, 0.025, 0.014, 0.006),
    
    WomenPlayer("Elise Mertens", "BEL", 24, Tier.C, 0.759, 0.540, 0.295, 0.105, 0.059, 0.032, 0.015),
    WomenPlayer("Linda Fruhvirtova", "CZE", None, Tier.D, 0.241, 0.107, 0.032, 0.005, 0.002, 0.000, 0.000),
    WomenPlayer("Ann Li", "USA", None, Tier.D, 0.334, 0.086, 0.022, 0.003, 0.001, 0.000, 0.000),
    WomenPlayer("Viktorija Golubic", "SUI", None, Tier.D, 0.666, 0.266, 0.104, 0.023, 0.009, 0.003, 0.001),
    WomenPlayer("Varvara Gracheva", "FRA", None, Tier.D, 0.416, 0.096, 0.029, 0.004, 0.001, 0.000, 0.000),
    WomenPlayer("Aliaksandra Sasnovich", "BLR", None, Tier.D, 0.584, 0.168, 0.062, 0.011, 0.004, 0.001, 0.000),
    WomenPlayer("Anna Bondar", "HUN", None, Tier.D, 0.130, 0.047, 0.011, 0.001, 0.000, 0.000, 0.000),
    WomenPlayer("Elina Svitolina", "UKR", 14, Tier.B, 0.870, 0.689, 0.445, 0.180, 0.109, 0.065, 0.034),
    
    WomenPlayer("Paula Badosa", "ESP", 9, Tier.B, 0.520, 0.346, 0.235, 0.140, 0.056, 0.031, 0.015),
    WomenPlayer("Katie Boulter", "GBR", None, Tier.D, 0.480, 0.312, 0.207, 0.119, 0.045, 0.024, 0.011),
    WomenPlayer("Greet Minnen", "BEL", None, Tier.D, 0.764, 0.303, 0.175, 0.085, 0.026, 0.011, 0.004),
    WomenPlayer("Olivia Gadecki", "AUS", None, Tier.D, 0.236, 0.040, 0.012, 0.003, 0.000, 0.000, 0.000),
    WomenPlayer("Anca Alexia Todoni", "ROU", None, Tier.D, 0.566, 0.220, 0.067, 0.023, 0.005, 0.001, 0.000),
    WomenPlayer("Cristina Bucsa", "ESP", None, Tier.D, 0.434, 0.142, 0.036, 0.010, 0.002, 0.000, 0.000),
    WomenPlayer("Kimberly Birrell", "AUS", None, Tier.D, 0.322, 0.167, 0.050, 0.017, 0.003, 0.001, 0.000),
    WomenPlayer("Donna Vekic", "CRO", 22, Tier.C, 0.678, 0.471, 0.219, 0.111, 0.036, 0.017, 0.007),
    
    WomenPlayer("Leylah Fernandez", "CAN", 29, Tier.C, 0.860, 0.531, 0.225, 0.101, 0.028, 0.012, 0.004),
    WomenPlayer("Hannah Klugman", "GBR", None, Tier.D, 0.140, 0.029, 0.003, 0.000, 0.000, 0.000, 0.000),
    WomenPlayer("Peyton Stearns", "USA", None, Tier.D, 0.514, 0.230, 0.074, 0.026, 0.005, 0.002, 0.000),
    WomenPlayer("Laura Siegemund", "GER", None, Tier.D, 0.486, 0.210, 0.066, 0.022, 0.004, 0.001, 0.000),
    WomenPlayer("Olga Danilovic", "SRB", None, Tier.D, 0.537, 0.161, 0.079, 0.030, 0.007, 0.002, 0.001),
    WomenPlayer("Shuai Zhang", "CHN", None, Tier.D, 0.463, 0.125, 0.057, 0.020, 0.004, 0.001, 0.000),
    WomenPlayer("Elena Gabriela Ruse", "ROU", None, Tier.D, 0.368, 0.237, 0.146, 0.074, 0.024, 0.011, 0.004),
    WomenPlayer("Madison Keys", "USA", 6, Tier.A, 0.632, 0.477, 0.349, 0.220, 0.097, 0.058, 0.030),
    
    WomenPlayer("Jasmine Paolini", "ITA", 4, Tier.A, 0.713, 0.617, 0.467, 0.312, 0.188, 0.089, 0.047),
    WomenPlayer("Anastasija Sevastova", "LAT", None, Tier.D, 0.287, 0.207, 0.116, 0.053, 0.020, 0.006, 0.002),
    WomenPlayer("Kamilla Rakhimova", "RUS", None, Tier.D, 0.656, 0.134, 0.050, 0.015, 0.003, 0.001, 0.000),
    WomenPlayer("Aoi Ito", "JPN", None, Tier.D, 0.344, 0.042, 0.010, 0.002, 0.000, 0.000, 0.000),
    WomenPlayer("Eva Lys", "GER", None, Tier.D, 0.493, 0.212, 0.068, 0.025, 0.007, 0.002, 0.000),
    WomenPlayer("Yue Yuan", "CHN", None, Tier.D, 0.507, 0.222, 0.073, 0.027, 0.008, 0.002, 0.000),
    WomenPlayer("Bernarda Pera", "USA", None, Tier.D, 0.453, 0.245, 0.088, 0.036, 0.012, 0.003, 0.001),
    WomenPlayer("Linda Noskova", "CZE", 30, Tier.C, 0.547, 0.321, 0.128, 0.057, 0.022, 0.006, 0.002),
    
    WomenPlayer("Beatriz Haddad Maia", "BRA", 21, Tier.C, 0.544, 0.348, 0.164, 0.076, 0.032, 0.010, 0.003),
    WomenPlayer("Rebecca Sramkova", "SVK", None, Tier.D, 0.456, 0.274, 0.118, 0.050, 0.019, 0.005, 0.002),
    WomenPlayer("Harriet Dart", "GBR", None, Tier.D, 0.438, 0.151, 0.047, 0.015, 0.004, 0.001, 0.000),
    WomenPlayer("Dalma Galfi", "HUN", None, Tier.D, 0.562, 0.226, 0.082, 0.030, 0.009, 0.002, 0.001),
    WomenPlayer("Yanina Wickmayer", "BEL", None, Tier.D, 0.601, 0.185, 0.084, 0.031, 0.010, 0.002, 0.001),
    WomenPlayer("Renata Zarazua", "MEX", None, Tier.D, 0.399, 0.091, 0.033, 0.009, 0.002, 0.000, 0.000),
    WomenPlayer("Yulia Putintseva", "KAZ", None, Tier.C, 0.400, 0.270, 0.161, 0.080, 0.036, 0.012, 0.005),
    WomenPlayer("Amanda Anisimova", "USA", 13, Tier.B, 0.600, 0.454, 0.312, 0.184, 0.101, 0.042, 0.020),
    
    WomenPlayer("Diana Shnaider", "RUS", 12, Tier.B, 0.798, 0.597, 0.318, 0.197, 0.115, 0.049, 0.024),
    WomenPlayer("Moyuka Uchijima", "JPN", None, Tier.D, 0.202, 0.086, 0.020, 0.006, 0.002, 0.000, 0.000),
    WomenPlayer("Diane Parry", "FRA", None, Tier.D, 0.453, 0.134, 0.036, 0.012, 0.004, 0.001, 0.000),
    WomenPlayer("Petra Martic", "CRO", None, Tier.D, 0.547, 0.183, 0.055, 0.021, 0.007, 0.002, 0.000),
    WomenPlayer("Viktoriya Tomova", "BUL", None, Tier.D, 0.278, 0.069, 0.023, 0.008, 0.002, 0.000, 0.000),
    WomenPlayer("Ons Jabeur", "TUN", None, Tier.D, 0.722, 0.327, 0.180, 0.102, 0.054, 0.020, 0.009),
    WomenPlayer("Sonay Kartal", "GBR", None, Tier.D, 0.291, 0.133, 0.060, 0.027, 0.012, 0.003, 0.001),
    WomenPlayer("Jelena Ostapenko", "LAT", 20, Tier.C, 0.709, 0.471, 0.307, 0.206, 0.130, 0.063, 0.034),
    
    WomenPlayer("Ashlyn Krueger", "USA", 31, Tier.D, 0.901, 0.435, 0.196, 0.075, 0.032, 0.009, 0.003),
    WomenPlayer("Mika Stojsavljevic", "GBR", None, Tier.D, 0.099, 0.009, 0.001, 0.000, 0.000, 0.000, 0.000),
    WomenPlayer("Anastasia Pavlyuchenkova", "RUS", None, Tier.D, 0.425, 0.219, 0.094, 0.034, 0.014, 0.004, 0.001),
    WomenPlayer("Ajla Tomljanovic", "AUS", None, Tier.D, 0.575, 0.337, 0.168, 0.072, 0.034, 0.011, 0.004),
    WomenPlayer("Naomi Osaka", "JPN", None, Tier.D, 0.737, 0.302, 0.150, 0.058, 0.025, 0.007, 0.002),
    WomenPlayer("Talia Gibson", "AUS", None, Tier.D, 0.263, 0.052, 0.014, 0.003, 0.001, 0.000, 0.000),
    WomenPlayer("Katerina Siniakova", "CZE", None, Tier.D, 0.450, 0.279, 0.156, 0.069, 0.034, 0.012, 0.005),
    WomenPlayer("Qinwen Zheng", "CHN", 5, Tier.B, 0.550, 0.366, 0.222, 0.109, 0.059, 0.023, 0.010),
    
    WomenPlayer("Mirra Andreeva", "RUS", 7, Tier.A, 0.764, 0.617, 0.408, 0.241, 0.124, 0.054, 0.023),
    WomenPlayer("Mayar Sherif", "EGY", None, Tier.D, 0.236, 0.135, 0.051, 0.016, 0.004, 0.001, 0.000),
    WomenPlayer("Jil Teichmann", "SUI", None, Tier.D, 0.374, 0.072, 0.018, 0.004, 0.001, 0.000, 0.000),
    WomenPlayer("Lucia Bronzetti", "ITA", None, Tier.D, 0.626, 0.176, 0.063, 0.019, 0.004, 0.001, 0.000),
    WomenPlayer("Hailey Baptiste", "USA", None, Tier.D, 0.388, 0.135, 0.047, 0.015, 0.004, 0.001, 0.000),
    WomenPlayer("Sorana Cirstea", "ROU", None, Tier.D, 0.612, 0.280, 0.126, 0.053, 0.018, 0.005, 0.001),
    WomenPlayer("Anastasia Potapova", "RUS", None, Tier.D, 0.582, 0.359, 0.186, 0.091, 0.038, 0.013, 0.004),
    WomenPlayer("Magdalena Frech", "POL", 25, Tier.C, 0.418, 0.225, 0.100, 0.041, 0.014, 0.004, 0.001),
    
    WomenPlayer("Barbora Krejcikova", "CZE", 17, Tier.B, 0.618, 0.457, 0.206, 0.105, 0.043, 0.015, 0.005),
    WomenPlayer("Alexandra Eala", "PHI", None, Tier.D, 0.382, 0.244, 0.083, 0.033, 0.010, 0.002, 0.001),
    WomenPlayer("Caroline Dolehide", "USA", None, Tier.D, 0.548, 0.174, 0.042, 0.012, 0.003, 0.000, 0.000),
    WomenPlayer("Arantxa Rus", "NED", None, Tier.D, 0.452, 0.125, 0.026, 0.007, 0.001, 0.000, 0.000),
    WomenPlayer("Veronika Kudermetova", "RUS", None, Tier.D, 0.760, 0.405, 0.272, 0.159, 0.078, 0.032, 0.013),
    WomenPlayer("Lin Zhu", "CHN", None, Tier.D, 0.240, 0.065, 0.026, 0.008, 0.002, 0.000, 0.000),
    WomenPlayer("Petra Kvitova", "CZE", None, Tier.D, 0.357, 0.158, 0.088, 0.041, 0.015, 0.004, 0.001),
    WomenPlayer("Emma Navarro", "USA", 10, Tier.B, 0.643, 0.373, 0.256, 0.154, 0.078, 0.033, 0.014),
    
    WomenPlayer("Karolina Muchova", "CZE", 15, Tier.B, 0.446, 0.328, 0.148, 0.077, 0.041, 0.016, 0.006),
    WomenPlayer("Xin Yu Wang", "CHN", None, Tier.D, 0.554, 0.428, 0.215, 0.124, 0.072, 0.032, 0.014),
    WomenPlayer("Zeynep Sonmez", "TUR", None, Tier.D, 0.619, 0.171, 0.046, 0.015, 0.005, 0.001, 0.000),
    WomenPlayer("Jaqueline Cristian", "ROU", None, Tier.D, 0.381, 0.073, 0.014, 0.003, 0.001, 0.000, 0.000),
    WomenPlayer("Suzan Lamens", "NED", None, Tier.D, 0.248, 0.054, 0.015, 0.004, 0.001, 0.000, 0.000),
    WomenPlayer("Iva Jovic", "USA", None, Tier.D, 0.752, 0.322, 0.170, 0.088, 0.047, 0.018, 0.007),
    WomenPlayer("Priscilla Hon", "AUS", None, Tier.D, 0.112, 0.025, 0.005, 0.001, 0.000, 0.000, 0.000),
    WomenPlayer("Ekaterina Alexandrova", "RUS", 18, Tier.C, 0.888, 0.600, 0.386, 0.246, 0.159, 0.081, 0.040),
    
    WomenPlayer("Magda Linette", "POL", 27, Tier.C, 0.710, 0.361, 0.157, 0.061, 0.028, 0.009, 0.003),
    WomenPlayer("Elsa Jacquemot", "FRA", None, Tier.D, 0.290, 0.088, 0.022, 0.005, 0.001, 0.000, 0.000),
    WomenPlayer("Alycia Parks", "USA", None, Tier.D, 0.295, 0.119, 0.035, 0.009, 0.003, 0.001, 0.000),
    WomenPlayer("Belinda Bencic", "SUI", None, Tier.D, 0.705, 0.432, 0.210, 0.093, 0.048, 0.018, 0.006),
    WomenPlayer("Katie Volynets", "USA", None, Tier.D, 0.319, 0.079, 0.027, 0.007, 0.002, 0.000, 0.000),
    WomenPlayer("Tatjana Maria", "GER", None, Tier.D, 0.681, 0.276, 0.145, 0.058, 0.027, 0.009, 0.003),
    WomenPlayer("Elisabetta Cocciaretto", "ITA", None, Tier.D, 0.305, 0.157, 0.076, 0.027, 0.012, 0.004, 0.001),
    WomenPlayer("Jessica Pegula", "USA", 3, Tier.B, 0.695, 0.488, 0.329, 0.182, 0.114, 0.055, 0.026),
    
    WomenPlayer("Iga Swiatek", "POL", 8, Tier.A, 0.870, 0.739, 0.555, 0.365, 0.224, 0.149, 0.084),
    WomenPlayer("Polina Kudermetova", "RUS", None, Tier.D, 0.130, 0.060, 0.019, 0.005, 0.001, 0.000, 0.000),
    WomenPlayer("Caty Mcnally", "USA", None, Tier.D, 0.623, 0.141, 0.056, 0.017, 0.005, 0.001, 0.000),
    WomenPlayer("Jodie Burrage", "GBR", None, Tier.D, 0.377, 0.060, 0.017, 0.004, 0.001, 0.000, 0.000),
    WomenPlayer("Camila Osorio", "COL", None, Tier.D, 0.457, 0.233, 0.078, 0.030, 0.010, 0.004, 0.001),
    WomenPlayer("Danielle Collins", "USA", None, Tier.D, 0.543, 0.299, 0.110, 0.046, 0.017, 0.007, 0.002),
    WomenPlayer("Veronika Erjavec", "SLO", None, Tier.D, 0.206, 0.047, 0.007, 0.001, 0.000, 0.000, 0.000),
    WomenPlayer("Marta Kostyuk", "UKR", 26, Tier.C, 0.794, 0.421, 0.158, 0.068, 0.026, 0.011, 0.004),
    
    WomenPlayer("Clara Tauson", "DEN", 23, Tier.C, 0.593, 0.270, 0.092, 0.030, 0.010, 0.003, 0.001),
    WomenPlayer("Heather Watson", "GBR", None, Tier.D, 0.407, 0.151, 0.040, 0.010, 0.003, 0.001, 0.000),
    WomenPlayer("Anna Kalinskaya", "RUS", None, Tier.D, 0.771, 0.498, 0.218, 0.093, 0.038, 0.018, 0.007),
    WomenPlayer("Nina Stojanovic", "SRB", None, Tier.D, 0.229, 0.081, 0.016, 0.003, 0.001, 0.000, 0.000),
    WomenPlayer("Maria Sakkari", "GRE", None, Tier.D, 0.528, 0.161, 0.079, 0.027, 0.009, 0.003, 0.001),
    WomenPlayer("Anna Blinkova", "RUS", None, Tier.D, 0.472, 0.133, 0.062, 0.020, 0.006, 0.002, 0.001),
    WomenPlayer("Elina Avanesyan", "ARM", None, Tier.D, 0.227, 0.112, 0.053, 0.017, 0.005, 0.002, 0.001),
    WomenPlayer("Elena Rybakina", "KAZ", 11, Tier.A, 0.773, 0.594, 0.441, 0.263, 0.155, 0.100, 0.054),
    
    WomenPlayer("Daria Kasatkina", "AUS", 16, Tier.C, 0.840, 0.529, 0.311, 0.144, 0.066, 0.034, 0.014),
    WomenPlayer("Emiliana Arango", "COL", None, Tier.D, 0.160, 0.040, 0.010, 0.002, 0.000, 0.000, 0.000),
    WomenPlayer("Irina Camelia Begu", "ROU", None, Tier.D, 0.347, 0.118, 0.044, 0.012, 0.003, 0.001, 0.000),
    WomenPlayer("Kaja Juvan", "SLO", None, Tier.D, 0.653, 0.313, 0.161, 0.063, 0.024, 0.011, 0.004),
    WomenPlayer("Yuliia Starodubtseva", "UKR", None, Tier.D, 0.555, 0.145, 0.040, 0.008, 0.002, 0.000, 0.000),
    WomenPlayer("Francesca Jones", "GBR", None, Tier.D, 0.445, 0.099, 0.023, 0.004, 0.001, 0.000, 0.000),
    WomenPlayer("Maya Joint", "AUS", None, Tier.D, 0.220, 0.121, 0.036, 0.008, 0.002, 0.000, 0.000),
    WomenPlayer("Liudmila Samsonova", "RUS", 19, Tier.C, 0.780, 0.635, 0.375, 0.183, 0.088, 0.048, 0.021),
    
    WomenPlayer("Sofia Kenin", "USA", 28, Tier.C, 0.738, 0.490, 0.180, 0.087, 0.035, 0.016, 0.006),
    WomenPlayer("Taylor Townsend", "USA", None, Tier.D, 0.262, 0.110, 0.020, 0.005, 0.001, 0.000, 0.000),
    WomenPlayer("Jessica Bouzas Maneiro", "ESP", None, Tier.D, 0.715, 0.326, 0.090, 0.034, 0.011, 0.004, 0.001),
    WomenPlayer("Ella Seidel", "GER", None, Tier.D, 0.285, 0.074, 0.010, 0.002, 0.000, 0.000, 0.000),
    WomenPlayer("Victoria Azarenka", "BLR", None, Tier.D, 0.807, 0.273, 0.164, 0.082, 0.034, 0.016, 0.006),
    WomenPlayer("Anastasia Zakharova", "RUS", None, Tier.D, 0.193, 0.022, 0.006, 0.001, 0.000, 0.000, 0.000),
    WomenPlayer("Dayana Yastremska", "UKR", None, Tier.D, 0.252, 0.135, 0.077, 0.037, 0.014, 0.006, 0.002),
    WomenPlayer("Coco Gauff", "USA", 2, Tier.A, 0.748, 0.570, 0.453, 0.326, 0.208, 0.146, 0.087),
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

def print_players_by_tier():
    """Print all players organized by tier"""
    tiers = get_players_by_tier()
    for tier in Tier:
        print(f"\nTier {tier.value}:")
        for player in tiers[tier]:
            seeding_info = f"(#{player.seeding})" if player.seeding else "(unseeded)"
            print(f"  {player.name} {seeding_info} ({player.country})")

if __name__ == "__main__":
    print("WOMEN'S TENNIS PLAYER DATABASE")
    print("=" * 50)
    print_players_by_tier()
    
    print(f"\nTotal players: {len(WOMEN_PLAYERS)}")
    tiers = get_players_by_tier()
    for tier in Tier:
        print(f"Tier {tier.value}: {len(tiers[tier])} players")
