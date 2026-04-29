import pandas as pd
import os



#set up file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT  = os.path.join(BASE_DIR, "..", "data", "raw_nba.csv")
OUTPUT_SEASON = os.path.join(BASE_DIR, "..", "data", "season_averages.csv")
OUTPUT_TEAM = os.path.join(BASE_DIR, "..", "data", "team_averages.csv")


#read in raw csv
nba_data = pd.read_csv(INPUT)


#split into season and team datasets
season_averages = nba_data[nba_data["table"] == "team-stats-per_game"]
team_averages = nba_data[nba_data["table"] == "advanced-team"]


#keep only season, playoff, PACE, 3PA and PTS for season averages
season_averages = season_averages[["season", "phase", "Unnamed: 13_level_0 Pace", "3PA", "PTS"]] 


#keep only season, team, PACE, 3PA and SRS for team averages
team_averages = team_averages[["season", "Team", "phase", "Unnamed: 13_level_0 Pace", "3PA", "Unnamed: 9_level_0 SRS"]]


#save cleaned data to new csv files
season_averages.to_csv(OUTPUT_SEASON, index=False)
team_averages.to_csv(OUTPUT_TEAM, index=False)








