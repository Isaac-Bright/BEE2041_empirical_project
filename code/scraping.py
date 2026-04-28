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

ADVANCED_TABLE_IDS = ["advanced-team", "misc_stats"]
PER_GAME_TABLE_IDS = ["per_game-team", "team-stats-per_game"]


# ── HELPERS ───────────────────────────────────────────────────────────────────

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


def get_first_table(soup, table_ids):
    """Try a list of table IDs and return the first one that exists."""
    for tid in table_ids:
        df = get_table(soup, tid)
        if df is not None and not df.empty:
            return df, tid
    return None, None


def find_team_col(df):
    if df is None or df.empty:
        return None
    # Exact known names
    for candidate in ["Team", "Tm", "Franchise", "School"]:
        if candidate in df.columns:
            return candidate
    # Flattened MultiIndex ending in known names
    for c in df.columns:
        if str(c).endswith((" Team", " Tm")):
            return c
    return None


def clean_team_col(df, col):
    """Drop non-team rows (repeated headers, totals, nulls) and cast col to str."""
    df = df.copy()
    df[col] = df[col].astype(str).str.strip()
    junk = {"nan", "", "Team", "Tm", "League Average"}
    df = df[~df[col].isin(junk)]
    df = df[~df[col].str.match(r"^\d+$")]
    return df


def build_merged(advanced, per_game, season, phase):
    adv_team_col = find_team_col(advanced)
    pg_team_col  = find_team_col(per_game)

    if advanced is not None and adv_team_col:
        advanced = clean_team_col(advanced, adv_team_col)
        advanced = advanced.rename(columns={adv_team_col: "Team"})
        advanced["season"] = season

    if per_game is not None and pg_team_col:
        per_game = clean_team_col(per_game, pg_team_col)
        per_game = per_game.rename(columns={pg_team_col: "Team"})
        per_game["season"] = season

    if advanced is not None and adv_team_col and per_game is not None and pg_team_col:
        merged = advanced.merge(
            per_game, on=["Team", "season"],
            suffixes=("_adv", "_pg"), how="outer"
        )
    elif advanced is not None and adv_team_col:
        merged = advanced
    elif per_game is not None and pg_team_col:
        merged = per_game
    else:
        print(f"    [warn] could not identify team column for {season} {phase}")
        return pd.DataFrame()

    merged["phase"] = phase
    return merged


# ── SCRAPERS ──────────────────────────────────────────────────────────────────

def scrape_regular_season(season):
    soup = fetch(f"{BASE}/leagues/NBA_{season}.html")
    if soup is None:
        return pd.DataFrame()
    time.sleep(4)

    advanced, _ = get_first_table(soup, ADVANCED_TABLE_IDS)
    per_game, _ = get_first_table(soup, PER_GAME_TABLE_IDS)

    # Fallback for very old seasons that have neither
    if advanced is None and per_game is None:
        east = get_table(soup, "divs_standings_E")
        west = get_table(soup, "divs_standings_W")
        parts = [df for df in [east, west] if df is not None]
        if parts:
            standings = pd.concat(parts, ignore_index=True)
            standings["season"] = season
            standings["phase"] = "regular_season"
            return standings
        return pd.DataFrame()

    return build_merged(advanced, per_game, season, "regular_season")


def scrape_playoffs(season):
    soup = fetch(f"{BASE}/playoffs/NBA_{season}.html")
    if soup is None:
        return pd.DataFrame()
    time.sleep(4)

    advanced, _ = get_first_table(soup, ADVANCED_TABLE_IDS)
    per_game, _ = get_first_table(soup, PER_GAME_TABLE_IDS)

    if advanced is None and per_game is None:
        print(f"    [warn] no recognisable tables found for {season} playoffs")
        return pd.DataFrame()

    return build_merged(advanced, per_game, season, "playoffs")


# ── MAIN ──────────────────────────────────────────────────────────────────────

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