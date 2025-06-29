#!/usr/bin/env python3
"""
Debug script to test file loading in hosted environment
"""
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tennis_simulator.data.static_database import populate_static_database, get_file_paths

def debug_environment():
    """Debug the environment and file loading"""
    print("=== ENVIRONMENT DEBUG ===")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    
    # Check environment variables
    print("\n=== ENVIRONMENT VARIABLES ===")
    for key, value in os.environ.items():
        if 'STREAM' in key.upper() or 'APP' in key.upper() or 'PATH' in key.upper():
            print(f"{key}: {value}")
    
    # List files in current directory
    print("\n=== CURRENT DIRECTORY FILES ===")
    try:
        files = os.listdir('.')
        for file in sorted(files):
            if file.endswith('.txt') or file.endswith('.py'):
                print(f"  {file}")
    except Exception as e:
        print(f"Error listing files: {e}")
    
    # Test file paths for men
    print("\n=== TESTING FILE PATHS FOR MEN ===")
    try:
        paths = get_file_paths('men')
        for key, path in paths.items():
            exists = os.path.exists(path)
            print(f"  {key}: {path} - {'EXISTS' if exists else 'NOT FOUND'}")
    except Exception as e:
        print(f"Error getting file paths: {e}")
    
    # Test file paths for women
    print("\n=== TESTING FILE PATHS FOR WOMEN ===")
    try:
        paths = get_file_paths('women')
        for key, path in paths.items():
            exists = os.path.exists(path)
            print(f"  {key}: {path} - {'EXISTS' if exists else 'NOT FOUND'}")
    except Exception as e:
        print(f"Error getting file paths: {e}")
    
    # Test database population
    print("\n=== TESTING DATABASE POPULATION ===")
    try:
        print("Testing men's database...")
        men_db = populate_static_database('men')
        print(f"Men's database has {len(men_db)} players")
        
        if men_db:
            print("Sample men's players:")
            for i, (name, data) in enumerate(list(men_db.items())[:3]):
                print(f"  {i+1}. {name} - Elo: {data.elo}, Form: {data.form}")
        
        print("\nTesting women's database...")
        women_db = populate_static_database('women')
        print(f"Women's database has {len(women_db)} players")
        
        if women_db:
            print("Sample women's players:")
            for i, (name, data) in enumerate(list(women_db.items())[:3]):
                print(f"  {i+1}. {name} - Elo: {data.elo}, Form: {data.form}")
                
    except Exception as e:
        print(f"Error populating database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_environment() 