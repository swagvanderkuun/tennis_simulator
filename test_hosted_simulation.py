#!/usr/bin/env python3
import sys
import os
import shutil

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tennis_simulator.data.static_database import populate_static_database

def test_hosted_simulation():
    print("Simulating hosted environment (no data files)...")
    
    # Create backup directory
    backup_dir = "backup_data_files"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Move data files to simulate hosted environment
    files_to_move = [
        'elo_men.txt', 'elo_women.txt', 'yelo_men.txt', 'yelo_women.txt',
        'data/elo/yelo_men_form.txt', 'data/elo/yelo_women_form.txt',
        'data/elo/tier_men.txt', 'data/elo/tier_women.txt'
    ]
    
    print("Moving data files to simulate hosted environment...")
    for file_path in files_to_move:
        if os.path.exists(file_path):
            backup_path = os.path.join(backup_dir, os.path.basename(file_path))
            shutil.move(file_path, backup_path)
            print(f"  Moved {file_path} to {backup_path}")
    
    try:
        # Test men's data
        print("\n--- Testing Men's Data (Hosted Environment) ---")
        men_db = populate_static_database('men')
        print(f"Men: {len(men_db)} players")
        
        print("Sample men's players:")
        for i, (name, data) in enumerate(list(men_db.items())[:3]):
            print(f"  {name}: Tier {data.tier}, Elo {data.elo}, Form {data.form}")
        
        # Test women's data
        print("\n--- Testing Women's Data (Hosted Environment) ---")
        women_db = populate_static_database('women')
        print(f"Women: {len(women_db)} players")
        
        print("Sample women's players:")
        for i, (name, data) in enumerate(list(women_db.items())[:3]):
            print(f"  {name}: Tier {data.tier}, Elo {data.elo}, Form {data.form}")
            
    finally:
        # Restore data files
        print("\nRestoring data files...")
        for file_path in files_to_move:
            backup_path = os.path.join(backup_dir, os.path.basename(file_path))
            if os.path.exists(backup_path):
                shutil.move(backup_path, file_path)
                print(f"  Restored {file_path}")
        
        # Clean up backup directory
        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)

if __name__ == "__main__":
    test_hosted_simulation() 