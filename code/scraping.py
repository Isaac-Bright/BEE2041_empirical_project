import pandas as pd
import cloudscraper
import time
import io
import os

scraper = cloudscraper.create_scraper(
    browser={"browser": "chrome", "platform": "linux", "mobile": False}
)

SEASONS = range(1950, 2026)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE_DIR, "..", "data", "raw_team_stats.csv")


def fetch_tables(url):
    try:
        r = scraper.get(url, timeout=15)
        print(f"  {url.split('/')[-1]} → {r.status_code}")
        if r.status_code != 200:
            return []
        html = r.text.replace("<!--", "").replace("-->", "")
        tables = pd.read_html(io.StringIO(html))
        cleaned = []
        for t in tables:
            # Flatten MultiIndex columns to their last level
            if isinstance(t.columns, pd.MultiIndex):
                t.columns = [col[-1] for col in t.columns]
            else:
                t.columns = [str(c) for c in t.columns]
            cleaned.append(t)
        return cleaned
    except Exception as e:
        print(f"  [error] {e}")
        return []


def has_col(df, name):
    return name in df.columns


def clean_teams(df):
    team_col = next((c for c in df.columns if c in ["Team", "Tm"]), None)
    if team_col is None:
        return None
    df = df.copy().rename(columns={team_col: "Team"})
    df["Team"] = df["Team"].astype(str).str.strip()
    junk = {"League Average", "nan", "", "Team", "Tm"}
    df = df[~df["Team"].isin(junk)]
    df = df[~df["Team"].str.match(r"^\d+$")]
    return df


team_frames = []

for season in SEASONS:
    print(f"Fetching {season}...")
    tables = fetch_tables(f"https://www.basketball-reference.com/leagues/NBA_{season}.html")
    time.sleep(4)

    per_game = None
    advanced = None

    for t in tables:
        t = clean_teams(t)
        if t is None:
            continue
        if has_col(t, "PTS") and has_col(t, "3PA") and per_game is None:
            per_game = t
        if (has_col(t, "Pace") or has_col(t, "SRS")) and advanced is None:
            advanced = t

    if per_game is None and advanced is None:
        print("  ✗ no usable tables")
        continue

    # Build merged — per_game provides 3PA, advanced provides Pace/SRS
    # Either can be missing for old seasons
    if per_game is not None and advanced is not None:
        pg_cols  = ["Team"] + [c for c in ["3PA"] if c in per_game.columns]
        adv_cols = ["Team"] + [c for c in ["Pace", "SRS"] if c in advanced.columns]
        merged = per_game[pg_cols].merge(advanced[adv_cols], on="Team", how="outer")
    elif per_game is not None:
        merged = per_game[["Team"] + [c for c in ["3PA"] if c in per_game.columns]]
    else:
        merged = advanced[["Team"] + [c for c in ["Pace", "SRS"] if c in advanced.columns]]

    merged["season"] = season
    team_frames.append(merged)
    print(f"  ✓ {season}: {len(merged)} teams")

if team_frames:
    out = pd.concat(team_frames, ignore_index=True)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    out.to_csv(OUT, index=False)
    print(f"\nSaved {len(out)} rows → {OUT}")