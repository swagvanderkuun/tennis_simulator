#!/usr/bin/env python3
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tennis_simulator.data.static_database import populate_static_database

def test_fallback():
    print("Testing fallback data generation...")
    
    # Test men's data
    print("\n--- Testing Men's Data ---")
    men_db = populate_static_database('men')
    print(f"Men: {len(men_db)} players")
    
    print("Sample men's players:")
    for i, (name, data) in enumerate(list(men_db.items())[:3]):
        print(f"  {name}: Tier {data.tier}, Elo {data.elo}, Form {data.form}")
    
    # Test women's data
    print("\n--- Testing Women's Data ---")
    women_db = populate_static_database('women')
    print(f"Women: {len(women_db)} players")
    
    print("Sample women's players:")
    for i, (name, data) in enumerate(list(women_db.items())[:3]):
        print(f"  {name}: Tier {data.tier}, Elo {data.elo}, Form {data.form}")

if __name__ == "__main__":
    test_fallback() 