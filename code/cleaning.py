import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_TEAM   = os.path.join(BASE_DIR, "..", "data", "raw_team_stats.csv")
RAW_LEAGUE = os.path.join(BASE_DIR, "..", "data", "raw_league_averages.csv")
OUT_TEAM   = os.path.join(BASE_DIR, "..", "data", "clean_team_stats.csv")
OUT_LEAGUE = os.path.join(BASE_DIR, "..", "data", "clean_league_averages.csv")

# ── TEAM STATS ────────────────────────────────────────────────────────────────

df = pd.read_csv(RAW_TEAM)

# Coerce stat columns to numeric
for col in ["3PA", "Pace", "SRS"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Clean team names
junk = {"nan", "", "Team", "Tm", "League Average"}
df["Team"] = (
    df["Team"]
    .astype(str)
    .str.strip()
    .str.replace(r"\*", "", regex=True)
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)

# Drop junk rows
df = df[~df["Team"].isin(junk)]
df = df[~df["Team"].str.match(r"^\d+$")]
df = df[~df["Team"].str.match(r"^nan$")]

# Drop rows where all stats are missing
df = df.dropna(subset=["3PA", "Pace", "SRS"], how="all")

# Drop duplicates
df = df.drop_duplicates(subset=["Team", "season"])
df = df.sort_values(["season", "Team"]).reset_index(drop=True)

# Capitalise season
df = df.rename(columns={"season": "Season"})
df = df.set_index("Season")

df.to_csv(OUT_TEAM)
print(f"Team stats: {len(df)} rows → {OUT_TEAM}")
print(df.head(10))
print(f"\nNull counts:\n{df.isnull().sum()}")
print(f"\nSeasons covered: {df.index.min()} – {df.index.max()}")
print(f"Unique teams: {df['Team'].nunique()}")

# ── LEAGUE AVERAGES ───────────────────────────────────────────────────────────

lg = pd.read_csv(RAW_LEAGUE)

# First row is the real header
lg.columns = lg.iloc[0]
lg = lg.iloc[1:].reset_index(drop=True)

# Split regular season and playoffs by where Rk resets to 1
rk = pd.to_numeric(lg["Rk"], errors="coerce")
reset_points = lg.index[rk == 1].tolist()

if len(reset_points) >= 2:
    reg     = lg.iloc[reset_points[0]:reset_points[1]].copy()
    playoff = lg.iloc[reset_points[1]:].copy()
else:
    half    = len(lg) // 2
    reg     = lg.iloc[:half].copy()
    playoff = lg.iloc[half:].copy()

reg["Playoffs"]     = False
playoff["Playoffs"] = True

combined = pd.concat([reg, playoff], ignore_index=True)
combined = combined[["Season", "3PA", "PTS", "Pace", "Playoffs"]]

# Drop junk rows
combined = combined.dropna(subset=["Season"])
combined = combined[combined["Season"] != "Season"]
combined = combined[combined["Season"].str.match(r"^\d{4}-\d{2}$")]

# Convert "YYYY-YY" to ending year e.g. "1996-97" → 1997
combined["Season"] = combined["Season"].str[:4].astype(int) + 1

for col in ["3PA", "PTS", "Pace"]:
    combined[col] = pd.to_numeric(combined[col], errors="coerce")

combined = combined.sort_values(["Season", "Playoffs"]).reset_index(drop=True)
combined = combined.set_index("Season")

combined.to_csv(OUT_LEAGUE)
print(f"\nLeague averages: {len(combined)} rows → {OUT_LEAGUE}")
print(combined.head(10))
print(f"\nNull counts:\n{combined.isnull().sum()}")
print(f"Seasons covered: {combined.index.min()} – {combined.index.max()}")