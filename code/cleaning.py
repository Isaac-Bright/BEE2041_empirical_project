import pandas as pd 
import os 


#set up file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT  = os.path.join(BASE_DIR, "..", "data", "raw_nba.csv")
OUTPUT = os.path.join(BASE_DIR, "..", "data", "clean_nba.csv")


#read in raw csv
nba_data = pd.read_csv(INPUT)


#get rid of all columns except for season, team, SRS, 3PA, PTS,PACE and phase (playoffs or regular season)
clean_data = nba_data[["season", "Team", "Unnamed: 9_level_0 SRS", "3PA", "PTS", "Unnamed: 13_level_0 Pace", "phase"]]


#give relevant columns more intuitive names
clean_data = clean_data.rename(columns={"Unnamed: 9_level_0 SRS": "SRS", "Unnamed: 13_level_0 Pace": "PACE", "phase": "playoffs"})


#change playoffs column to boolean
clean_data["playoffs"] = clean_data["playoffs"].apply(lambda x: True if x == "playoffs" else False)


#remove * from team names and any whitespace
clean_data["Team"] = clean_data["Team"].str.replace("*", "", regex=False).str.strip()


#drop any league average rows and any blank rows
clean_data = clean_data[clean_data["Team"].notna() & (clean_data["Team"] != "League Average")]


#remove the row with na PTS value (season 1974, Buffalo Braves)
clean_data = clean_data.dropna(subset=["PTS"])


#saving cleaned data to a new csv file
clean_data.to_csv(OUTPUT, index=False)


#print every season that has teams with playoff appearances and the number of teams that made the playoffs in that season
playoff_counts = clean_data[clean_data["playoffs"]].groupby("season")["Team"].count()
for season, count in playoff_counts.items():
    print(f"{season}: {count} teams made the playoffs")


