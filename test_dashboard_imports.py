#!/usr/bin/env python3
"""
Test script to verify all dashboard imports work correctly
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test all imports used in the dashboard"""
    
    print("Testing dashboard imports...")
    
    try:
        # Test core models
        from tennis_simulator.core.models import Player, Tier
        print("✅ Core models imported successfully")
        
        # Test static database
        from tennis_simulator.data.static_database import populate_static_database
        print("✅ Static database imported successfully")
        
        # Test Elo simulator
        from tennis_simulator.simulators.elo_match_simulator import EloMatchSimulator, EloWeights, create_match_simulator
        print("✅ Elo simulator imported successfully")
        
        # Test data loading
        print("\nTesting data loading...")
        men_db = populate_static_database('men')
        print(f"✅ Men's database loaded: {len(men_db)} players")
        
        women_db = populate_static_database('women')
        print(f"✅ Women's database loaded: {len(women_db)} players")
        
        # Test simulator creation
        print("\nTesting simulator creation...")
        simulator = create_match_simulator(surface='grass')
        print("✅ Grass court simulator created successfully")
        
        # Test custom weights
        weights = EloWeights(elo_weight=0.4, helo_weight=0.2, celo_weight=0.2, gelo_weight=0.1, yelo_weight=0.1)
        print("✅ Custom weights created successfully")
        
        print("\n🎉 All tests passed! Dashboard should work correctly.")
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_imports() 