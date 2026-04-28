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


#plot line graph showing the pace stat of the highest and lowest SRS teams for each season
highest_srs = nba_data.loc[nba_data.groupby("season")["SRS"].idxmax()]
lowest_srs = nba_data.loc[nba_data.groupby("season")["SRS"].idxmin()]
plt.figure(figsize=(12, 6))
plt.plot(highest_srs["season"], highest_srs["PACE"], label="Highest SRS Team", color="green")
plt.plot(lowest_srs["season"], lowest_srs["PACE"], label="Lowest SRS Team", color="red")
plt.xlabel("Season")
plt.ylabel("Pace")
plt.title("Pace of Highest vs Lowest SRS Teams per Season")
plt.legend()
plt.grid()
plt.savefig(os.path.join(BASE_DIR, "..", "output", "plots", "pace_extremes.png"))
plt.close()   


#plot line graph showing the 3PA stat of the highest and lowest SRS teams for each season
plt.figure(figsize=(12, 6))
plt.plot(highest_srs["season"], highest_srs["3PA"], label="Highest SRS Team", color="green")
plt.plot(lowest_srs["season"], lowest_srs["3PA"], label="Lowest SRS Team", color="red")
plt.xlabel("Season")
plt.ylabel("3PA")
plt.title("3PA of Highest vs Lowest SRS Teams per Season")
plt.legend()
plt.grid()
plt.savefig(os.path.join(BASE_DIR, "..", "output", "plots", "3pa_extremes.png"))
plt.close()



#2 scatter plot that shows the relationship betwee SRS (y) and 3pa (x) 
plt.figure(figsize=(12, 6))
plt.scatter(playoff_data["3PA"], playoff_data["SRS"], label="Playoff Teams", color="blue", alpha=0.6)
plt.scatter(regular_data["3PA"], regular_data["SRS"], label="Non-Playoff Teams", color="orange", alpha=0.6)
plt.xlabel("3PA")
plt.ylabel("SRS")
plt.title("SRS vs 3PA: Playoff vs Non-Playoff Teams")
plt.legend()
plt.grid()
plt.savefig(os.path.join(BASE_DIR, "..", "output", "plots", "srs_vs_3pa.png"))
plt.close()
