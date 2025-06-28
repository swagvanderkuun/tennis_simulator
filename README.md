# Tennis Simulator

A comprehensive tennis tournament simulation system for ATP and WTA Grand Slam tournaments, specifically designed for Wimbledon and Scorito-style games.

## Features

- **Tournament Simulation**: Realistic tennis tournament simulations with Elo-based match predictions
- **Player Database**: Comprehensive database of ATP and WTA players with tier classifications
- **Scorito Integration**: Support for Scorito-style fantasy tennis games
- **Statistical Analysis**: Advanced analytics and player recommendations
- **Interactive Selection**: Command-line interface for player selection
- **Multiple Formats**: Support for both men's and women's tournaments

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Install from Source

```bash
# Clone the repository
git clone https://github.com/tennissimulator/tennis-simulator.git
cd tennis-simulator

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

### Install Dependencies Only

```bash
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```python
from tennis_simulator import run_tournament_simulation

# Run 1000 simulations
simulator = run_tournament_simulation(num_simulations=1000)
```

### Command Line Interface

```bash
# List all players
python main.py list-players

# Run simulations
python main.py simulate --simulations 1000

# Get player recommendations
python main.py recommend --gender men --tier A

# Interactive player selection
python main.py select-players

# Analyze a selection
python main.py analyze-selection selection.json
```

## Project Structure

```
tennis_simulator/
├── src/
│   └── tennis_simulator/
│       ├── core/
│       │   ├── __init__.py
│       │   └── models.py              # Core data models
│       ├── data/
│       │   ├── __init__.py
│       │   └── player_database.py     # Player database management
│       ├── simulators/
│       │   ├── __init__.py
│       │   └── tournament_simulator.py # Tournament simulation engine
│       ├── utils/
│       │   ├── __init__.py
│       │   └── player_selector.py     # Interactive player selection
│       └── __init__.py                # Package initialization
├── data/
│   ├── elo/                           # Elo rating data files
│   └── import/                        # Import data files
├── tests/                             # Test suite
├── docs/                              # Documentation
├── main.py                            # CLI entry point
├── setup.py                           # Package setup
├── requirements.txt                   # Dependencies
└── README.md                          # This file
```

## Core Components

### Data Models

The system uses several core data models:

- **Player**: Represents a tennis player with attributes like name, country, tier, Elo ratings, and rankings
- **Match**: Represents a tennis match between two players with simulation capabilities
- **Tournament**: Represents a complete tournament with players, matches, and results
- **ScoritoGame**: Represents a fantasy tennis game with player selections

### Player Database

The player database includes:

- **32 Men's Players**: Top ATP players organized into tiers A, B, C, D
- **32 Women's Players**: Top WTA players organized into tiers A, B, C, D
- **Elo Ratings**: Multiple Elo rating types (general, grass, clay, hard court, year-to-date)
- **Rankings**: Current ATP/WTA rankings
- **Seeding**: Tournament seeding information

### Tournament Simulator

The simulator provides:

- **Realistic Draws**: Tournament draws that respect seeding
- **Elo-Based Predictions**: Match outcomes based on Elo rating differences
- **Multiple Simulations**: Statistical analysis through repeated simulations
- **Round Progression**: Players advance through R64 → R32 → R16 → QF → SF → F → W

## Usage Examples

### Running Simulations

```python
from tennis_simulator import TournamentSimulator, Gender

# Create simulator
simulator = TournamentSimulator("Wimbledon")

# Get players
men_players = list(player_db.get_players_by_gender(Gender.MEN).values())
women_players = list(player_db.get_players_by_gender(Gender.WOMEN).values())

# Setup tournaments
simulator.setup_tournaments(men_players, women_players)

# Run simulations
stats = simulator.run_multiple_simulations(1000)

# Get recommendations
recommendations = simulator.get_player_recommendations(Gender.MEN, Tier.A)
```

### Player Selection

```python
from tennis_simulator import PlayerSelector, run_interactive_selector

# Interactive selection
selector = run_interactive_selector()

# Create Scorito game
game = selector.create_scorito_game("My Game")

# Validate selection
if selector.validate_selection():
    print("Selection is valid!")
```

### Database Management

```python
from tennis_simulator import player_db, Gender

# Get players by tier
tier_a_men = player_db.get_players_by_tier(Gender.MEN, Tier.A)

# Update player tier
player_db.update_player_tier("Novak Djokovic", Gender.MEN, Tier.A)

# Inject Elo data
player_db.inject_elo_data(Gender.MEN, "data/elo/elo_men.txt")

# Get statistics
stats = player_db.get_statistics(Gender.MEN)
```

## Command Line Interface

The CLI provides several commands:

### `list-players`
List all players in the database.

```bash
# List all players
python main.py list-players

# List only men's players
python main.py list-players --gender men

# List only Tier A players
python main.py list-players --tier A

# Sort by Elo rating
python main.py list-players --sort-by elo
```

### `simulate`
Run tournament simulations.

```bash
# Run 1000 simulations
python main.py simulate --simulations 1000

# Run simulations for specific tournament
python main.py simulate --tournament "Australian Open"

# Save results to file
python main.py simulate --output results.json
```

### `recommend`
Get player recommendations for specific tiers.

```bash
# Get recommendations for men's Tier A
python main.py recommend --gender men --tier A

# Get recommendations with more simulations
python main.py recommend --gender women --tier B --simulations 2000
```

### `select-players`
Interactive player selection.

```bash
# Start interactive selection
python main.py select-players

# Load existing selection
python main.py select-players --input selection.json

# Save selection to file
python main.py select-players --output my_selection.json
```

### `analyze-selection`
Analyze a player selection with simulations.

```bash
# Analyze selection file
python main.py analyze-selection selection.json

# Analyze with more simulations
python main.py analyze-selection selection.json --simulations 500
```

### `stats`
Show database statistics.

```bash
# Show all statistics
python main.py stats

# Show only men's statistics
python main.py stats --gender men
```

## Configuration

### Elo Data Files

The system can load Elo ratings from external files. Create files in the `data/elo/` directory:

**elo_men.txt**:
```
Novak Djokovic,2200
Carlos Alcaraz,2100
Daniil Medvedev,2000
...
```

**yelo_men.txt**:
```
Novak Djokovic,2150
Carlos Alcaraz,2080
Daniil Medvedev,1980
...
```

### Player Selections

Player selections can be saved and loaded as JSON files:

```json
{
  "men": {
    "A": ["Novak Djokovic", "Carlos Alcaraz", "Daniil Medvedev"],
    "B": ["Andrey Rublev", "Stefanos Tsitsipas", "Holger Rune"],
    "C": ["Alexander Zverev", "Felix Auger-Aliassime", "Karen Khachanov"],
    "D": ["Lorenzo Musetti", "Borna Coric", "Alex de Minaur"]
  },
  "women": {
    "A": ["Iga Swiatek", "Aryna Sabalenka", "Elena Rybakina"],
    "B": ["Caroline Garcia", "Ons Jabeur", "Coco Gauff"],
    "C": ["Daria Kasatkina", "Belinda Bencic", "Beatriz Haddad Maia"],
    "D": ["Veronika Kudermetova", "Madison Keys", "Elise Mertens"]
  }
}
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Run tests with coverage
pytest --cov=tennis_simulator
```

### Code Formatting

```bash
# Format code
black src/ tests/

# Check code style
flake8 src/ tests/

# Type checking
mypy src/
```

### Building Documentation

```bash
# Install documentation dependencies
pip install -e .[docs]

# Build documentation
cd docs
make html
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- ATP and WTA for player data
- Scorito for the fantasy tennis concept
- The tennis community for inspiration and feedback

## Support

For support and questions:

- Create an issue on GitHub
- Check the documentation
- Contact the development team

## Changelog

### Version 1.0.0
- Initial release
- Core tournament simulation engine
- Player database with tier system
- Interactive player selection
- Command-line interface
- Statistical analysis and recommendations 