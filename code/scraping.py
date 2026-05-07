import pandas as pd
import cloudscraper
import time
import io
import os

# cloudscraper spoofs a real browser to avoid Cloudflare bot detection on BBRef
scraper = cloudscraper.create_scraper(
    browser={"browser": "chrome", "platform": "linux", "mobile": False}
)

SEASONS = range(1950, 2026)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE_DIR, "..", "data", "raw_team_stats.csv")


def fetch_tables(url):
    #Fetch all HTML tables from a BBRef page, stripping HTML comments that hide some tables.
    try:
        r = scraper.get(url, timeout=15)
        print(f"  {url.split('/')[-1]} → {r.status_code}")
        if r.status_code != 200:
            return []
        # BBRef wraps several tables in HTML comments to defer rendering — strip them first
        html = r.text.replace("<!--", "").replace("-->", "")
        tables = pd.read_html(io.StringIO(html))
        cleaned = []
        for t in tables:
            # BBRef uses MultiIndex headers on some tables (e.g. shooting splits);
            # collapse to the innermost label so column names are always plain strings
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
    #Convenience wrapper for a readable column existence check
    return name in df.columns


def find_tables(tables):
    """
    Identify the per-game and advanced tables from all tables on the page.
    Per-game is identified by having both PTS and 3PA columns.
    Advanced is identified by having Pace or SRS columns.
    Returns the first match of each to avoid duplicates that BBRef sometimes includes.
    """
    per_game = None
    advanced = None
    for t in tables:
        t = drop_junk_rows(t)
        if t is None:
            continue
        if has_col(t, "PTS") and has_col(t, "3PA") and per_game is None:
            per_game = t
        if (has_col(t, "Pace") or has_col(t, "SRS")) and advanced is None:
            advanced = t
    return per_game, advanced


def drop_junk_rows(df):
    """
    Normalise the team column and drop non-team rows.
    BBRef tables include mid-table header repetitions, subtotal rows, and
    'League Average' rows that need removing before any numeric work.
    Returns None if no team column is found (i.e. the table is not a team table).
    """
    # Support both 'Team' (per-game tables) and 'Tm' (advanced tables)
    team_col = next((c for c in df.columns if c in ["Team", "Tm"]), None)
    if team_col is None:
        return None
    df = df.copy().rename(columns={team_col: "Team"})
    df["Team"] = df["Team"].astype(str).str.strip()
    # Drop summary and repeated header rows BBRef injects mid-table
    junk = {"League Average", "nan", "", "Team", "Tm"}
    df = df[~df["Team"].isin(junk)]
    # Rows where the team cell is just a rank number are repeated headers
    df = df[~df["Team"].str.match(r"^\d+$")]
    return df


team_frames = []

for season in SEASONS:
    print(f"Fetching {season}...")
    tables = fetch_tables(f"https://www.basketball-reference.com/leagues/NBA_{season}.html")
    # Respect BBRef's crawl rate — they block clients that hit too fast
    time.sleep(4)
    # Rate limit is 20 requests per minute, but set to 4 to be safe 

    per_game, advanced = find_tables(tables)

    if per_game is None and advanced is None:
        print("  ✗ no usable tables")
        continue

    # Merge per-game and advanced on Team using an outer join so that seasons
    # where one table is absent (e.g. no Pace before the shot-clock era) still
    # produce rows. Column selection is guarded in case a column is missing for
    # a given season.
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
    # Save without any cleaning — the cleaning script handles all transformations
    out.to_csv(OUT, index=False)
    print(f"\nSaved {len(out)} rows → {OUT}")