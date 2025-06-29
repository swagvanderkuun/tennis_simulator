# yElo Form Calculator

This tool calculates form values for tennis players by comparing current yElo values with historical values from 1 week ago and 2 weeks ago.

## Overview

The yElo form calculator analyzes player performance trends by calculating the difference between current yElo ratings and historical ratings. This helps identify players who are improving, declining, or maintaining stable performance.

## Files

### Input Files (in `data/elo/`)
- `yelo_women.txt` - Current yElo values for women players
- `yelo_women_1w.txt` - yElo values for women players from 1 week ago
- `yelo_women_2w.txt` - yElo values for women players from 2 weeks ago
- `yelo_men.txt` - Current yElo values for men players
- `yelo_men_1w.txt` - yElo values for men players from 1 week ago
- `yelo_men_2w.txt` - yElo values for men players from 2 weeks ago

### Output Files (in `data/elo/`)
- `yelo_women_form.txt` - Form calculations for women players
- `yelo_men_form.txt` - Form calculations for men players

## File Format

All files use tab-separated values with the following columns:
- `Rank` - Player's current ranking
- `Player` - Player name
- `Wins` - Number of wins
- `Losses` - Number of losses
- `yElo_form1w` - Form compared to 1 week ago (current - 1w_ago)
- `yElo_form2w` - Form compared to 2 weeks ago (current - 2w_ago)

## Usage

### Calculate Form for All Players

```bash
python yelo_form_calculator.py
```

This will:
1. Read all yElo files (current, 1 week ago, 2 weeks ago)
2. Merge player data from all time periods
3. Calculate form values for each player
4. Write results to the form files

### Analyze Form Trends

```bash
python example_form_usage.py
```

This will display a formatted analysis of the top players showing:
- Current ranking
- Form changes over 1 week and 2 weeks
- Trend indicators (Improving, Declining, Stable, etc.)

## Form Interpretation

- **Positive values**: Player's yElo has increased (improving form)
- **Negative values**: Player's yElo has decreased (declining form)
- **Zero values**: No change in yElo (stable form)

### Trend Categories

- **↗️ Improving**: Positive form in both time periods
- **↘️ Declining**: Negative form in both time periods
- **↗️ Recovering**: Positive recent form, negative longer-term form
- **↘️ Sliding**: Negative recent form, positive longer-term form
- **➡️ Stable**: No significant change in form

## Code Structure

### Main Functions

1. **`read_yelo_file(filepath)`** - Reads a yElo file and returns player data
2. **`merge_player_data(current, one_week, two_weeks)`** - Merges data from all time periods
3. **`write_form_file(players, output_file)`** - Writes form data to output file
4. **`calculate_form_for_gender(gender)`** - Calculates form for a specific gender

### Data Classes

- **`PlayerData`** - Stores player information and yElo values with form calculation properties

## Example Output

```
Top 10 women players by current yElo ranking:
================================================================================
Rank Player               Form 1W    Form 2W    Trend          
--------------------------------------------------------------------------------
1    Aryna Sabalenka         -27.6    -27.6 ↘️ Declining   
2    Coco Gauff              -49.9    -49.9 ↘️ Declining   
3    Elina Svitolina           0.0      0.0 ➡️ Stable      
4    Iga Swiatek               0.0      0.0 ➡️ Stable      
5    Mirra Andreeva          -47.2    -47.2 ↘️ Declining   
```

## Requirements

- Python 3.6+
- No external dependencies required

## Notes

- The calculator handles players who may not appear in all time periods
- Players without current data are excluded from the output
- Form values are calculated as simple differences (current - historical)
- Files are sorted by current yElo ranking (descending)

## Updating Form Data

To update form data with new yElo values:

1. Update the current yElo files (`yelo_women.txt`, `yelo_men.txt`)
2. Move the old current files to the historical positions:
   - `yelo_women.txt` → `yelo_women_1w.txt`
   - `yelo_women_1w.txt` → `yelo_women_2w.txt`
   - (same for men)
3. Run the form calculator: `python yelo_form_calculator.py` 