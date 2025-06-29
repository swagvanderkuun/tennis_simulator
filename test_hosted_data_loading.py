#!/usr/bin/env python3
"""
Test script to verify data loading works in hosted environments
"""
import os
import sys

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_data_loading():
    """Test data loading functionality"""
    print("=== TESTING DATA LOADING ===")
    
    try:
        from tennis_simulator.data.static_database import populate_static_database
        from tennis_simulator.data.data_loader import get_data_loader
        
        print("✓ Successfully imported modules")
        
        # Test data loader
        data_loader = get_data_loader()
        print("✓ Data loader created successfully")
        
        # Test men's database
        print("\n--- Testing Men's Database ---")
        men_db = populate_static_database('men')
        print(f"✓ Men's database loaded with {len(men_db)} players")
        
        if men_db:
            print("Sample men's players:")
            for i, (name, data) in enumerate(list(men_db.items())[:3]):
                print(f"  {i+1}. {name}")
                print(f"     Elo: {data.elo}, Form: {data.form}")
                print(f"     Tier: {data.tier}, Ranking: {data.ranking}")
        
        # Test women's database
        print("\n--- Testing Women's Database ---")
        women_db = populate_static_database('women')
        print(f"✓ Women's database loaded with {len(women_db)} players")
        
        if women_db:
            print("Sample women's players:")
            for i, (name, data) in enumerate(list(women_db.items())[:3]):
                print(f"  {i+1}. {name}")
                print(f"     Elo: {data.elo}, Form: {data.form}")
                print(f"     Tier: {data.tier}, Ranking: {data.ranking}")
        
        # Test data sources
        print("\n--- Testing Data Sources ---")
        for gender in ['men', 'women']:
            for data_type in ['elo', 'yelo', 'form', 'tier']:
                data_source = data_loader.get_data_source(gender, data_type)
                if data_source:
                    print(f"✓ {gender} {data_type}: {data_source.source_type} source")
                else:
                    print(f"✗ {gender} {data_type}: No source found")
        
        print("\n=== ALL TESTS PASSED ===")
        return True
        
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_data_loading()
    sys.exit(0 if success else 1) 