import pandas as pd
import cloudscraper
import time
import io
import os

scraper = cloudscraper.create_scraper(
    browser={"browser": "chrome", "platform": "linux", "mobile": False}
)

SEASONS = range(1950, 2026)
BASE = "https://www.basketball-reference.com"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_SEASON = os.path.join(BASE_DIR, "..", "data", "season_averages.csv")
OUT_TEAM   = os.path.join(BASE_DIR, "..", "data", "team_reg_season.csv")


def fetch_tables(url):
    try:
        r = scraper.get(url, timeout=15)
        if r.status_code != 200:
            print(f"  [skip] {url} → {r.status_code}")
            return []
        html = r.text.replace("<!--", "").replace("-->", "")
        tables = pd.read_html(io.StringIO(html))
        # Flatten any MultiIndex columns
        for t in tables:
            if isinstance(t.columns, pd.MultiIndex):
                t.columns = [" ".join(str(c) for c in col).strip() for col in t.columns]
            else:
                t.columns = [str(c) for c in t.columns]
        return tables
    except Exception as e:
        print(f"  [error] {url}: {e}")
        return []


def find_league_avg_row(tables):
    """Return the League Average row from whichever table contains it."""
    for t in tables:
        mask = t.isin(["League Average"]).any(axis=1)
        if mask.any():
            return t[mask].iloc[0].to_dict()
    return None


def find_team_table(tables):
    """Return the per-game team table (has Team/Tm column and PTS)."""
    for t in tables:
        team_col = next((c for c in t.columns if c in ["Team", "Tm"]), None)
        if team_col and "PTS" in t.columns:
            return t, team_col
    return None, None


season_rows = []
team_frames = []

for season in SEASONS:
    print(f"Fetching {season}...")

    # ── Regular season ────────────────────────────────────────────────────────
    tables = fetch_tables(f"{BASE}/leagues/NBA_{season}.html")
    time.sleep(4)

    row = find_league_avg_row(tables)
    if row:
        row["season"] = season
        row["phase"] = "regular_season"
        season_rows.append(row)
        print(f"  ✓ reg season avg")
    else:
        print(f"  ✗ no reg season avg")

    t, team_col = find_team_table(tables)
    if t is not None:
        t = t.copy()
        junk = {"League Average", "nan", ""}
        t = t[~t[team_col].astype(str).str.strip().isin(junk)]
        t = t.dropna(subset=[team_col])
        t["season"] = season
        team_frames.append(t)
        print(f"  ✓ team data: {len(t)} teams")
    else:
        print(f"  ✗ no team data")

    # ── Playoffs ──────────────────────────────────────────────────────────────
    tables = fetch_tables(f"{BASE}/playoffs/NBA_{season}.html")
    time.sleep(4)

    row = find_league_avg_row(tables)
    if row:
        row["season"] = season
        row["phase"] = "playoffs"
        season_rows.append(row)
        print(f"  ✓ playoff avg")
    else:
        print(f"  ✗ no playoff avg")

os.makedirs(os.path.dirname(OUT_SEASON), exist_ok=True)

pd.DataFrame(season_rows).to_csv(OUT_SEASON, index=False)
print(f"\nSaved season averages → {OUT_SEASON}")

if team_frames:
    pd.concat(team_frames, ignore_index=True).to_csv(OUT_TEAM, index=False)
    print(f"Saved team data → {OUT_TEAM}")