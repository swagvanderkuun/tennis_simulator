"""
Embedded data files for hosted environments
This module contains the data files as embedded strings to ensure they're available
when the app is deployed to Streamlit Cloud or other hosting platforms.
"""

# Men's Elo data (first few lines as example)
MEN_ELO_DATA = """Elo Rank	Player	Elo	Elo	Elo	Elo	hElo	hElo	hElo	hElo	cElo	cElo	cElo	cElo	gElo	gElo	gElo	gElo	yElo	yElo	yElo	yElo	ATP Rank	ATP Rank	ATP Rank	ATP Rank	WTA Rank	WTA Rank	WTA Rank	WTA Rank
1	Novak Djokovic	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1
2	Carlos Alcaraz	2	2	2	2	2	2	2	2	2	2	2	2	2	2	2	2	2	2	2	2	2	2	2	2	2	2	2	2
3	Daniil Medvedev	3	3	3	3	3	3	3	3	3	3	3	3	3	3	3	3	3	3	3	3	3	3	3	3	3	3	3	3
4	Jannik Sinner	4	4	4	4	4	4	4	4	4	4	4	4	4	4	4	4	4	4	4	4	4	4	4	4	4	4	4	4
5	Andrey Rublev	5	5	5	5	5	5	5	5	5	5	5	5	5	5	5	5	5	5	5	5	5	5	5	5	5	5	5	5"""

# Women's Elo data (first few lines as example)
WOMEN_ELO_DATA = """Elo Rank	Player	Elo	Elo	Elo	Elo	hElo	hElo	hElo	hElo	cElo	cElo	cElo	cElo	gElo	gElo	gElo	gElo	yElo	yElo	yElo	yElo	ATP Rank	ATP Rank	ATP Rank	ATP Rank	WTA Rank	WTA Rank	WTA Rank	WTA Rank
1	Iga Swiatek	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1	1
2	Aryna Sabalenka	2	2	2	2	2	2	2	2	2	2	2	2	2	2	2	2	2	2	2	2	2	2	2	2	2	2	2	2
3	Coco Gauff	3	3	3	3	3	3	3	3	3	3	3	3	3	3	3	3	3	3	3	3	3	3	3	3	3	3	3	3
4	Elena Rybakina	4	4	4	4	4	4	4	4	4	4	4	4	4	4	4	4	4	4	4	4	4	4	4	4	4	4	4	4
5	Jessica Pegula	5	5	5	5	5	5	5	5	5	5	5	5	5	5	5	5	5	5	5	5	5	5	5	5	5	5	5	5"""

# Men's yElo data (first few lines as example)
MEN_YELO_DATA = """Rank	Player	yElo	yElo	yElo	yElo	yElo_form2w	yElo_form2w	yElo_form2w	yElo_form2w
1	Novak Djokovic	1	1	1	1	1	1	1	1
2	Carlos Alcaraz	2	2	2	2	2	2	2	2
3	Daniil Medvedev	3	3	3	3	3	3	3	3
4	Jannik Sinner	4	4	4	4	4	4	4	4
5	Andrey Rublev	5	5	5	5	5	5	5	5"""

# Women's yElo data (first few lines as example)
WOMEN_YELO_DATA = """Rank	Player	yElo	yElo	yElo	yElo	yElo_form2w	yElo_form2w	yElo_form2w	yElo_form2w
1	Iga Swiatek	1	1	1	1	1	1	1	1
2	Aryna Sabalenka	2	2	2	2	2	2	2	2
3	Coco Gauff	3	3	3	3	3	3	3	3
4	Elena Rybakina	4	4	4	4	4	4	4	4
5	Jessica Pegula	5	5	5	5	5	5	5	5"""

def get_embedded_data(gender: str, data_type: str) -> str:
    """Get embedded data for the specified gender and data type"""
    if gender == 'men':
        if data_type == 'elo':
            return MEN_ELO_DATA
        elif data_type == 'yelo':
            return MEN_YELO_DATA
    elif gender == 'women':
        if data_type == 'elo':
            return WOMEN_ELO_DATA
        elif data_type == 'yelo':
            return WOMEN_YELO_DATA
    
    return ""

def create_temp_file(data: str, suffix: str = '.txt') -> str:
    """Create a temporary file with the given data and return its path"""
    import tempfile
    import os
    
    # Create a temporary file
    fd, path = tempfile.mkstemp(suffix=suffix)
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(data)
    
    return path 