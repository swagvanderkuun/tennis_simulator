# Elo-Based Tennis Match Simulation Guide

This guide explains the new Elo-based match simulation system that provides sophisticated tennis match prediction using configurable weights for different surface types and performance metrics.

## Overview

The Elo-based simulation system uses the standard Elo rating formula to calculate win probabilities between two players:

```
P(A beats B) = 1 / (1 + 10^((B_rating - A_rating) / 400))
```

Where the rating is a weighted combination of different Elo metrics:
- **Elo**: Overall Elo rating
- **hElo**: Hard court Elo rating  
- **cElo**: Clay court Elo rating
- **gElo**: Grass court Elo rating
- **yElo**: Year-to-date Elo rating

## Key Components

### EloWeights Configuration

The `EloWeights` class allows you to configure how much weight each Elo type contributes to the final rating:

```python
from tennis_simulator import EloWeights

# Default weights
weights = EloWeights(
    elo_weight=0.4,    # 40% overall performance
    helo_weight=0.2,   # 20% hard court performance
    celo_weight=0.2,   # 20% clay court performance
    gelo_weight=0.1,   # 10% grass court performance
    yelo_weight=0.1    # 10% recent form
)
```

**Important**: Weights must sum to 1.0. The system validates this automatically.

### EloMatchSimulator

The main simulator class that handles match simulation:

```python
from tennis_simulator import EloMatchSimulator

# Create simulator with custom weights
simulator = EloMatchSimulator(weights=weights)

# Calculate win probability
prob = simulator.calculate_win_probability(player1, player2)

# Simulate a match
winner, loser, details = simulator.simulate_match(player1, player2)
```

## Surface-Specific Configurations

The system includes pre-configured weights optimized for different surfaces:

### Hard Court (US Open, Australian Open)
```python
from tennis_simulator import create_match_simulator

hard_simulator = create_match_simulator(surface='hard')
# Weights: Elo=0.3, hElo=0.4, cElo=0.1, gElo=0.1, yElo=0.1
```

### Clay Court (French Open)
```python
clay_simulator = create_match_simulator(surface='clay')
# Weights: Elo=0.3, hElo=0.1, cElo=0.4, gElo=0.1, yElo=0.1
```

### Grass Court (Wimbledon)
```python
grass_simulator = create_match_simulator(surface='grass')
# Weights: Elo=0.3, hElo=0.1, cElo=0.1, gElo=0.4, yElo=0.1
```

### Overall Performance
```python
overall_simulator = create_match_simulator(surface='overall')
# Weights: Elo=0.4, hElo=0.2, cElo=0.2, gElo=0.1, yElo=0.1
```

## Custom Weight Configurations

### Recent Form Focus
For tournaments where recent performance is crucial:

```python
recent_form_weights = EloWeights(
    elo_weight=0.2,
    helo_weight=0.2,
    celo_weight=0.2,
    gelo_weight=0.2,
    yelo_weight=0.2  # Equal weight to recent form
)
```

### Surface Specialist
For players known for specific surface expertise:

```python
surface_specialist_weights = EloWeights(
    elo_weight=0.1,
    helo_weight=0.3,
    celo_weight=0.3,
    gelo_weight=0.3,
    yelo_weight=0.0  # Ignore recent form
)
```

### Tournament-Specific
For specific tournament characteristics:

```python
# Example: Wimbledon with emphasis on grass and recent form
wimbledon_weights = EloWeights(
    elo_weight=0.2,
    helo_weight=0.1,
    celo_weight=0.1,
    gelo_weight=0.4,  # High grass court weight
    yelo_weight=0.2   # High recent form weight
)
```

## Usage Examples

### Basic Match Simulation

```python
from tennis_simulator import EloMatchSimulator, Player, Tier

# Create players
player1 = Player(
    name="Carlos Alcaraz",
    country="ESP",
    seeding=1,
    tier=Tier.A,
    elo=2246.5,
    helo=2129.0,
    celo=2203.5,
    gelo=2129.1,
    yelo=5.0,
    atp_rank=2
)

player2 = Player(
    name="Jannik Sinner",
    country="ITA", 
    seeding=2,
    tier=Tier.A,
    elo=2208.4,
    helo=2177.6,
    celo=2111.5,
    gelo=1955.8,
    yelo=3.0,
    atp_rank=1
)

# Create simulator
simulator = EloMatchSimulator()

# Calculate win probability
prob = simulator.calculate_win_probability(player1, player2)
print(f"{player1.name} win probability: {prob:.3f}")

# Simulate match
winner, loser, details = simulator.simulate_match(player1, player2)
print(f"Winner: {winner.name}")
print(f"Match details: {details}")
```

### Tournament-Specific Simulation

```python
# For Wimbledon (grass court)
wimbledon_simulator = create_match_simulator(surface='grass')

# For French Open (clay court)
french_open_simulator = create_match_simulator(surface='clay')

# For US Open (hard court)
us_open_simulator = create_match_simulator(surface='hard')
```

### Multiple Simulations for Statistical Analysis

```python
def run_multiple_simulations(player1, player2, num_simulations=1000, surface='overall'):
    simulator = create_match_simulator(surface=surface)
    
    player1_wins = 0
    for _ in range(num_simulations):
        winner, _, _ = simulator.simulate_match(player1, player2)
        if winner.name == player1.name:
            player1_wins += 1
    
    win_rate = player1_wins / num_simulations
    print(f"{player1.name} won {player1_wins}/{num_simulations} matches ({win_rate:.1%})")
    
    return win_rate
```

## Understanding the Results

### Win Probability
- **0.5**: Equal chance (50/50)
- **0.7**: 70% chance to win
- **0.3**: 30% chance to win

### Rating Difference Impact
- **0 points**: 50% win probability
- **100 points**: ~37% win probability for underdog
- **200 points**: ~26% win probability for underdog
- **400 points**: ~11% win probability for underdog

### Weighted Rating Calculation
The system calculates a weighted rating for each player:

```python
weighted_rating = (
    elo_weight * elo +
    helo_weight * helo +
    celo_weight * celo +
    gelo_weight * gelo +
    yelo_weight * yelo
)
```

## Best Practices

### 1. Choose Appropriate Surface Weights
- Use surface-specific weights for Grand Slams
- Consider tournament history and player strengths

### 2. Balance Recent Form vs Historical Performance
- Higher `yelo_weight` for tournaments where recent form matters
- Lower `yelo_weight` for tournaments where experience is key

### 3. Validate Weight Configurations
- Always ensure weights sum to 1.0
- Test different configurations with known player matchups

### 4. Run Multiple Simulations
- Single simulations can be misleading due to randomness
- Use multiple simulations for statistical analysis

### 5. Consider Player-Specific Factors
- Some players perform better on specific surfaces
- Adjust weights based on player characteristics

## Integration with Tournament Simulator

The Elo match simulator can be integrated with the tournament simulator:

```python
from tennis_simulator import TournamentSimulator, create_match_simulator

# Create tournament simulator with Elo-based match simulation
tournament_sim = TournamentSimulator()
match_simulator = create_match_simulator(surface='grass')  # For Wimbledon

# Use the Elo simulator for match predictions
# (Integration details depend on tournament simulator implementation)
```

## Testing and Validation

Use the provided test scripts to validate your configurations:

```bash
# Test basic functionality
python test_elo_simulator.py

# Test weight configurations
python example_elo_weights.py
```

## Troubleshooting

### Common Issues

1. **Weights don't sum to 1.0**
   - Error: "Elo weights must sum to 1.0, got X"
   - Solution: Adjust weights to sum to exactly 1.0

2. **Missing Elo data**
   - Players with missing Elo ratings will use available data
   - Consider using fallback values or excluding players

3. **Unexpected win probabilities**
   - Check that Elo ratings are in the expected range (typically 1500-2500)
   - Verify weight configurations match your expectations

### Debugging Tips

1. Print weighted ratings to understand calculations:
```python
rating1 = simulator.calculate_weighted_rating(player1)
rating2 = simulator.calculate_weighted_rating(player2)
print(f"Weighted ratings: {player1.name}={rating1:.1f}, {player2.name}={rating2:.1f}")
```

2. Check individual Elo components:
```python
print(f"{player1.name} Elo components: Elo={player1.elo}, hElo={player1.helo}, cElo={player1.celo}, gElo={player1.gelo}, yElo={player1.yelo}")
```

3. Run multiple simulations to verify probabilities:
```python
# Run 1000 simulations and compare to calculated probability
```

This Elo-based system provides a sophisticated and flexible approach to tennis match simulation that can be tailored to different tournaments, surfaces, and player characteristics. 