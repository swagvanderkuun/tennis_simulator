# Tennis Simulator Deployment Guide

## Overview
This guide explains how to deploy the Tennis Simulator to Streamlit Cloud and handle common issues with data loading in hosted environments.

## Prerequisites
- A GitHub repository containing the tennis simulator code
- A Streamlit Cloud account

## Deployment Steps

### 1. Prepare Your Repository
Ensure your repository has the following structure:
```
tennis_simulator/
├── streamlit_dashboard.py
├── requirements_dashboard.txt
├── src/
│   └── tennis_simulator/
│       └── data/
│           ├── static_database.py
│           ├── data_loader.py
│           └── embedded_data.py
├── data/
│   └── elo/
│       ├── elo_men.txt
│       ├── elo_women.txt
│       ├── yelo_men.txt
│       ├── yelo_women.txt
│       ├── yelo_men_form.txt
│       ├── yelo_women_form.txt
│       ├── tier_men.txt
│       └── tier_women.txt
└── README.md
```

### 2. Deploy to Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Connect your GitHub account
3. Select your repository
4. Set the main file path to `streamlit_dashboard.py`
5. Deploy

## Data Loading Issues and Solutions

### Problem: Empty Database in Hosted Environment
**Symptoms:**
- Database shows 0 players
- Form values show as N/A
- Match simulator doesn't work

**Causes:**
- File paths are relative and don't work in hosted environment
- Data files are not included in the deployment

**Solutions:**

#### Solution 1: Use the Enhanced Data Loader (Recommended)
The application now includes a robust data loading system that:
- Tries multiple file paths
- Falls back to embedded data if files aren't found
- Provides detailed debugging information

#### Solution 2: Include Data Files in Repository
Ensure all data files are committed to your repository:
```bash
git add data/elo/*.txt
git add *.txt
git commit -m "Add data files for deployment"
git push
```

#### Solution 3: Use Embedded Data
The application includes embedded data as a fallback. This ensures the app works even if data files are not accessible.

## Debugging

### Check Data Loading
Run the debug script locally to verify data loading:
```bash
python test_hosted_data_loading.py
```

### Check Environment
Run the environment debug script:
```bash
python debug_hosted_environment.py
```

### Streamlit Cloud Logs
Check the Streamlit Cloud logs for any error messages related to:
- File not found errors
- Import errors
- Data loading issues

## Common Issues

### Issue: "Module not found" errors
**Solution:** Ensure all required packages are in `requirements_dashboard.txt`

### Issue: Data files not found
**Solution:** The enhanced data loader will automatically fall back to embedded data

### Issue: Form values showing as N/A
**Solution:** This indicates the form data file is not being loaded. The enhanced data loader should resolve this.

## Testing Your Deployment

1. **Check Database Population:**
   - Navigate to the "Player Database" page
   - Verify that players are loaded (should show 400+ players for each gender)

2. **Check Form Values:**
   - Navigate to the "Match Simulator" page
   - Select two players
   - Verify that form values are displayed (not N/A)

3. **Test Match Simulation:**
   - Run a match simulation
   - Verify that probabilities are calculated correctly

## Performance Considerations

- The data loader caches data to improve performance
- Embedded data is used as a fallback to ensure reliability
- Temporary files are cleaned up automatically

## Support

If you continue to experience issues:
1. Check the Streamlit Cloud logs
2. Run the debug scripts locally
3. Verify that all data files are included in your repository
4. Ensure the enhanced data loader is being used

## Files Modified for Hosted Deployment

The following files have been enhanced to support hosted deployment:

- `src/tennis_simulator/data/static_database.py` - Enhanced with robust file path handling
- `src/tennis_simulator/data/data_loader.py` - New comprehensive data loading system
- `src/tennis_simulator/data/embedded_data.py` - Fallback data for hosted environments
- `debug_hosted_environment.py` - Debug script for environment issues
- `test_hosted_data_loading.py` - Test script for data loading functionality 