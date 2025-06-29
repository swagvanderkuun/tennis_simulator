# Tennis Simulator Streamlit Dashboard

A fast, interactive web dashboard for exploring the tennis simulator database and running match simulations.

## Features

### 🎾 **Match Simulation**
- **Surface-specific simulation**: Choose from hard court, clay court, grass court, or overall
- **Player selection**: Pick any two players from the database
- **Win probability calculation**: See mathematical win probabilities based on Elo ratings
- **Single match simulation**: Simulate individual matches with detailed results
- **Multiple simulations**: Run hundreds of simulations for statistical analysis
- **Results visualization**: Charts showing simulation outcomes

### 📊 **Database Exploration**
- **Database overview**: Statistics and visualizations of player data
- **Player search**: Search players by name with real-time filtering
- **Tier filtering**: Filter players by tier (A, B, C, D)
- **Top players**: View highest-rated players by Elo
- **Tier distribution**: Visual breakdown of player tiers

### ⚖️ **Custom Weight Configuration**
- **Interactive weight sliders**: Adjust Elo weight contributions
- **Real-time validation**: Ensures weights sum to 1.0
- **Surface-specific presets**: Pre-configured weights for different surfaces
- **Custom weight testing**: Test your configurations with sample players

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements_dashboard.txt
```

### 2. Run the Dashboard
```bash
streamlit run streamlit_dashboard.py
```

### 3. Open Your Browser
The dashboard will automatically open at `http://localhost:8501`

## Dashboard Navigation

### Sidebar
- **Gender Selection**: Switch between men's and women's databases
- **Page Navigation**: Choose between different dashboard sections
- **Database Info**: Quick stats about the loaded database

### Main Pages

#### 📊 Database Overview
- Total player count and tier distribution
- Elo rating histograms
- Top 10 players by Elo rating
- Interactive charts and metrics

#### 🔍 Player Search
- Real-time search by player name
- Filter by tier (A, B, C, D)
- Sortable data table with all player attributes
- Export-friendly format

#### 🎾 Match Simulation
- **Surface Selection**: Choose court type for simulation
- **Player Comparison**: Side-by-side player stats
- **Win Probability**: Mathematical prediction based on Elo
- **Match Simulation**: Single match with detailed results
- **Multiple Simulations**: Statistical analysis with charts

#### ⚖️ Custom Weights
- Interactive sliders for all Elo weight types
- Real-time weight validation
- Test configurations with sample players
- Surface-specific presets

## Usage Examples

### Running a Wimbledon Simulation
1. Select "Women" or "Men" in the sidebar
2. Go to "Match Simulation" page
3. Select "Grass" as the surface
4. Choose two players (e.g., top seeds)
5. Click "Simulate Match" or "Run Multiple Simulations"

### Exploring Player Database
1. Go to "Database Overview" page
2. View tier distribution and top players
3. Switch to "Player Search" for detailed exploration
4. Use search and filters to find specific players

### Creating Custom Weights
1. Go to "Custom Weights" page
2. Adjust sliders for different Elo types
3. Ensure weights sum to 1.0
4. Test with sample players
5. Use for specialized tournament simulations

## Data Sources

The dashboard uses the **static database** for fast loading:
- **Men's Database**: 487 players with complete Elo ratings
- **Women's Database**: 515 players with complete Elo ratings
- **Data includes**: Elo, hElo, cElo, gElo, yElo, rankings, tiers

## Performance Features

- **Cached data loading**: Fast database access with Streamlit caching
- **Static database**: No slow parsing of import files
- **Efficient simulations**: Optimized for real-time interaction
- **Responsive design**: Works on desktop and mobile devices

## Troubleshooting

### Dashboard Won't Start
```bash
# Check if Streamlit is installed
pip list | grep streamlit

# Install if missing
pip install streamlit
```

### Database Loading Issues
- Ensure `elo_men.txt`, `yelo_men.txt`, etc. are in the root directory
- Check file permissions and format
- Verify static database script works: `python src/tennis_simulator/data/static_database.py`

### Simulation Errors
- Make sure you've selected different players
- Check that Elo data is available for selected players
- Verify weight configurations sum to 1.0

## Customization

### Adding New Features
The dashboard is modular and easy to extend:
- Add new pages in the main() function
- Create new visualization functions
- Integrate additional simulation features

### Styling
Custom CSS is included for better appearance:
- Responsive design
- Color-coded metrics
- Professional tennis theme

## Integration with Main Simulator

The dashboard uses the same core components as the main simulator:
- `EloMatchSimulator` for match predictions
- `Player` models for data representation
- `static_database` for fast data access

This ensures consistency between the dashboard and command-line tools.

---

**Enjoy exploring tennis simulations with the interactive dashboard! 🎾** 