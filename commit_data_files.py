import os
import subprocess

def check_data_files():
    required_files = [
        "elo_men.txt",
        "elo_women.txt",
        "yelo_men.txt",
        "yelo_women.txt",
        "data/elo/yelo_men_form.txt",
        "data/elo/yelo_women_form.txt",
        "data/elo/tier_men.txt",
        "data/elo/tier_women.txt"
    ]
    missing = []
    for f in required_files:
        if not os.path.exists(f):
            missing.append(f)
    if missing:
        print("Missing data files:")
        for f in missing:
            print("  -", f)
    else:
        print("All required data files are present.")
    return missing

def add_and_commit_data_files():
    required_files = [
        "elo_men.txt",
        "elo_women.txt",
        "yelo_men.txt",
        "yelo_women.txt",
        "data/elo/yelo_men_form.txt",
        "data/elo/yelo_women_form.txt",
        "data/elo/tier_men.txt",
        "data/elo/tier_women.txt"
    ]
    # Add files to git
    for f in required_files:
        if os.path.exists(f):
            subprocess.run(["git", "add", f])
    # Commit
    subprocess.run(["git", "commit", "-m", "Add all required tennis data files for hosted deployment"])
    print("Committed all required data files to git.")

if __name__ == "__main__":
    missing = check_data_files()
    if missing:
        print("Please add the missing files before committing.")
    else:
        add_and_commit_data_files() 