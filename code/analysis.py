import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
import os   


#set up file paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT  = os.path.join(BASE_DIR, "..", "data", "clean_nba.csv")


#read in cleaned csv
nba_data = pd.read_csv(INPUT)

#create visualisation for average pace per season over time for playoff teams vs non-playoff teams
playoff_data = nba_data[nba_data["playoffs"]]
regular_data = nba_data[~nba_data["playoffs"]]
plt.figure(figsize=(12, 6))
plt.plot(playoff_data["season"], playoff_data["PACE"], label="Playoff Teams", color="blue")
plt.plot(regular_data["season"], regular_data["PACE"], label="Non-Playoff Teams", color="orange")
plt.xlabel("Season")
plt.ylabel("Average Pace")
plt.title("Average Pace per Season: Playoff vs Non-Playoff Teams")
plt.legend()
plt.grid()
plt.savefig(os.path.join(BASE_DIR, "..", "output", "plots", "pace_trends.png"))
plt.close()     


#doing the same for average 3 point attemtps per game for each season
plt.figure(figsize=(12, 6))
plt.plot(playoff_data["season"], playoff_data["3PA"], label="Playoff Teams", color="blue")
plt.plot(regular_data["season"], regular_data["3PA"], label="Non-Playoff Teams", color="orange")
plt.xlabel("Season")
plt.ylabel("Average 3PA")
plt.title("Average 3PA per Season: Playoff vs Non-Playoff Teams")
plt.legend()
plt.grid()
plt.savefig(os.path.join(BASE_DIR, "..", "output", "plots", "3pa_trends.png"))
plt.close()


#doing the same for average points per game for each season
plt.figure(figsize=(12, 6))
plt.plot(playoff_data["season"], playoff_data["PTS"], label="Playoff Teams", color="blue")
plt.plot(regular_data["season"], regular_data["PTS"], label="Non-Playoff Teams", color="orange")
plt.xlabel("Season")
plt.ylabel("Average PTS")
plt.title("Average PTS per Season: Playoff vs Non-Playoff Teams")
plt.legend()
plt.grid()
plt.savefig(os.path.join(BASE_DIR, "..", "output", "plots", "pts_trends.png"))
plt.close() 




