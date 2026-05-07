import pandas as pd
import os

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
RAW_TEAM   = os.path.join(BASE_DIR, "..", "data", "raw_team_stats.csv")
RAW_LEAGUE = os.path.join(BASE_DIR, "..", "data", "raw_league_averages.csv")
OUT_TEAM   = os.path.join(BASE_DIR, "..", "data", "clean_team_stats.csv")
OUT_LEAGUE = os.path.join(BASE_DIR, "..", "data", "clean_league_averages.csv")


# ── HELPERS ───────────────────────────────────────────────────────────────────

JUNK_TEAM_VALUES = {"nan", "", "Team", "Tm", "League Average"}

def clean_team_names(series):
    """
    Normalise a Series of team name strings.
    Removes playoff asterisks BBRef appends to some team names, collapses
    internal whitespace, and strips leading/trailing whitespace.
    """
    return (
        series
        .astype(str)
        .str.strip()
        .str.replace(r"\*", "", regex=True)   # e.g. "Boston Celtics*" → "Boston Celtics"
        .str.replace(r"\s+", " ", regex=True) # collapse any internal whitespace
        .str.strip()
    )

def drop_non_team_rows(df):
    """
    Remove rows that are not real teams.
    BBRef raw exports contain repeated header rows, rank-only rows, and
    summary rows (e.g. 'League Average') that must be removed before analysis.
    """
    df = df[~df["Team"].isin(JUNK_TEAM_VALUES)]
    df = df[~df["Team"].str.match(r"^\d+$")]  # rows where team cell is just a rank number
    df = df[~df["Team"].str.match(r"^nan$")]
    return df


# ── TEAM STATS ────────────────────────────────────────────────────────────────

df = pd.read_csv(RAW_TEAM)

# Coerce stat columns to numeric — BBRef sometimes exports them as strings
for col in ["3PA", "Pace", "SRS"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

df["Team"] = clean_team_names(df["Team"])
df = drop_non_team_rows(df)

# Drop rows where every stat column is null — these carry no usable information
df = df.dropna(subset=["3PA", "Pace", "SRS"], how="all")

# A team should appear at most once per season; keep the first occurrence if
# duplicates exist (can happen if BBRef tables overlapped during scraping)
df = df.drop_duplicates(subset=["Team", "season"])
df = df.sort_values(["season", "Team"]).reset_index(drop=True)

# Capitalise column name for consistency with the league averages output
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

# The CSV's first data row is the real header (artefact of how BBRef exports
# multi-season history tables), so promote it and drop the placeholder header
lg.columns = lg.iloc[0]
lg = lg.iloc[1:].reset_index(drop=True)

# BBRef concatenates regular season and playoff rows in one table, with Rk
# resetting to 1 at the start of each section. Use those reset points to split.
rk = pd.to_numeric(lg["Rk"], errors="coerce")
reset_points = lg.index[rk == 1].tolist()

if len(reset_points) >= 2:
    # Expected case: two clear sections separated by a header/rank reset
    reg     = lg.iloc[reset_points[0]:reset_points[1]].copy()
    playoff = lg.iloc[reset_points[1]:].copy()
else:
    # Fallback for edge cases where the reset point detection fails
    half    = len(lg) // 2
    reg     = lg.iloc[:half].copy()
    playoff = lg.iloc[half:].copy()

reg["Playoffs"]     = False
playoff["Playoffs"] = True

combined = pd.concat([reg, playoff], ignore_index=True)
combined = combined[["Season", "3PA", "PTS", "Pace", "Playoffs"]]

# Drop rows that are not real seasons: nulls, repeated header rows, and anything
# that doesn't match the "YYYY-YY" format BBRef uses for season strings
combined = combined.dropna(subset=["Season"])
combined = combined[combined["Season"] != "Season"]
combined = combined[combined["Season"].str.match(r"^\d{4}-\d{2}$")]

# Convert "YYYY-YY" to a single integer end-year so seasons align with the
# team stats index (e.g. "1996-97" → 1997)
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