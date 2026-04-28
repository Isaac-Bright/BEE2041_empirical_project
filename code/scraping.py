import pandas as pd
import cloudscraper
from bs4 import BeautifulSoup
import time
import io
import os

scraper = cloudscraper.create_scraper(
    browser={"browser": "chrome", "platform": "linux", "mobile": False}
)

SEASONS = range(1947, 2026)
BASE = "https://www.basketball-reference.com"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT = os.path.join(BASE_DIR, "..", "data", "raw_nba.csv")


def fetch(url):
    try:
        r = scraper.get(url, timeout=15)
        print(f"    {url.split('/')[-1]} → {r.status_code}")
        if r.status_code != 200:
            return None
        html = r.text.replace("<!--", "").replace("-->", "")
        return BeautifulSoup(html, "lxml")
    except Exception as e:
        print(f"    [error] {e}")
        return None


def get_table(soup, table_id):
    if soup is None:
        return None
    table = soup.find("table", {"id": table_id})
    if table is None:
        return None
    try:
        df = pd.read_html(io.StringIO(str(table)))[0]
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [" ".join(str(c) for c in col).strip() for col in df.columns]
        return df
    except Exception as e:
        print(f"    [parse error] {table_id}: {e}")
        return None


def find_team_col(df):
    if df is None or df.empty:
        return None
    return next((c for c in df.columns if str(c).endswith("Team")), None)


def scrape_regular_season(season):
    soup = fetch(f"{BASE}/leagues/NBA_{season}.html")
    if soup is None:
        return pd.DataFrame()
    time.sleep(4)

    advanced = get_table(soup, "advanced-team")
    per_game = get_table(soup, "per_game-team")

    adv_team_col = find_team_col(advanced)
    pg_team_col  = find_team_col(per_game)

    if adv_team_col and pg_team_col:
        advanced = advanced.rename(columns={adv_team_col: "Team"})
        per_game = per_game.rename(columns={pg_team_col: "Team"})
        advanced["season"] = season
        per_game["season"] = season
        merged = advanced.merge(per_game, on=["Team", "season"], suffixes=("_adv", "_pg"), how="outer")
        merged["phase"] = "regular_season"
        return merged

    # Fallback to standings for SRS
    standings = pd.DataFrame()
    east = get_table(soup, "divs_standings_E")
    west = get_table(soup, "divs_standings_W")
    parts = [df for df in [east, west] if df is not None]
    if parts:
        standings = pd.concat(parts, ignore_index=True)

    std_team_col = standings.columns[0] if not standings.empty else None

    if not standings.empty and pg_team_col:
        standings["season"] = season
        per_game["season"]  = season
        merged = standings.merge(per_game, left_on=[std_team_col, "season"], right_on=[pg_team_col, "season"], how="outer")
        merged["phase"] = "regular_season"
        return merged

    return pd.DataFrame()


def scrape_playoffs(season):
    soup = fetch(f"{BASE}/playoffs/NBA_{season}.html")
    if soup is None:
        return pd.DataFrame()
    time.sleep(4)

    advanced = get_table(soup, "advanced-team")
    per_game = get_table(soup, "per_game-team")

    adv_team_col = find_team_col(advanced)
    pg_team_col  = find_team_col(per_game)

    if adv_team_col and pg_team_col:
        advanced = advanced.rename(columns={adv_team_col: "Team"})
        per_game = per_game.rename(columns={pg_team_col: "Team"})
        advanced["season"] = season
        per_game["season"] = season
        merged = advanced.merge(per_game, on=["Team", "season"], suffixes=("_adv", "_pg"), how="outer")
        merged["phase"] = "playoffs"
        return merged
    elif adv_team_col:
        advanced = advanced.rename(columns={adv_team_col: "Team"})
        advanced["season"] = season
        advanced["phase"]  = "playoffs"
        return advanced
    elif pg_team_col:
        per_game = per_game.rename(columns={pg_team_col: "Team"})
        per_game["season"] = season
        per_game["phase"]  = "playoffs"
        return per_game

    return pd.DataFrame()


# ── MAIN ─────────────────────────────────────────────────────────────────────

all_frames = []

for season in SEASONS:
    print(f"\nFetching {season}...")

    reg = scrape_regular_season(season)
    if not reg.empty:
        all_frames.append(reg)
        print(f"  ✓ regular season: {len(reg)} teams")
    else:
        print(f"  ✗ no regular season data")

    pl = scrape_playoffs(season)
    if not pl.empty:
        all_frames.append(pl)
        print(f"  ✓ playoffs: {len(pl)} teams")
    else:
        print(f"  ✗ no playoff data")

if all_frames:
    combined = pd.concat(all_frames, ignore_index=True)
    combined.to_csv(OUTPUT, index=False)
    print(f"\nDone! {len(combined)} rows saved to {OUTPUT}")
    print(combined.head(5).to_string())
else:
    print("\nNo data collected.")