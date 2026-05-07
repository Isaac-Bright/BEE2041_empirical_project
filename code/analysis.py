import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
FIG_DIR  = os.path.join(BASE_DIR, "..", "figures")
os.makedirs(FIG_DIR, exist_ok=True)

league = pd.read_csv(os.path.join(DATA_DIR, "clean_league_averages.csv"), index_col="Season")
team   = pd.read_csv(os.path.join(DATA_DIR, "clean_team_stats.csv"),      index_col="Season")

# Split league averages into regular season and playoff subsets for overlaid plots
reg     = league[~league["Playoffs"]]
playoff = league[league["Playoffs"]]

# ── SHARED STYLE CONSTANTS ────────────────────────────────────────────────────

REGULAR_COLOR  = "#1f77b4"
PLAYOFF_COLOR  = "#d62728"
BEST_COLOR     = "#2ca02c"
WORST_COLOR    = "#d62728"
VLINE_COLOR    = "#333333"
SHADE_COLOR    = "#f0c040"
SHADE_ALPHA    = 0.25
FIGSIZE_SINGLE = (14, 5)
FIGSIZE_DOUBLE = (14, 8)
TITLE_SIZE     = 13
LABEL_SIZE     = 10
TICK_SIZE      = 7.5
ROTATION       = 90

# Full x-axis range used on every time-series plot so all figures share the same scale
ALL_SEASONS = list(range(1947, max(league.index.unique()) + 1))


# ── SHARED HELPERS ────────────────────────────────────────────────────────────

def style_ax(ax, seasons):
    """Apply common x-axis styling spanning the full league history."""
    ax.set_xlim(min(seasons) - 0.5, max(seasons) + 0.5)
    ax.set_xticks(seasons)
    ax.set_xticklabels(seasons, rotation=ROTATION, fontsize=TICK_SIZE)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def add_era_markers(ax):
    """
    Annotate key rule changes and events that visibly shifted league stats:
      - 1954: shot clock introduced, dramatically increased scoring and pace
      - 1980: 3-point line introduced
      - 1994–97: 3-point line temporarily shortened, inflating 3PA
      - 2010: Stephen Curry's debut season, a common anchor for the 3PT era
    Text is positioned near the top of the current y-axis range so it doesn't
    overlap data; call this after plotting so get_ylim() is accurate.
    """
    ax.axvline(1954, color=VLINE_COLOR, linestyle="--", linewidth=1.2, zorder=3)
    ax.text(1954.3, ax.get_ylim()[1] * 0.97, "Shot clock introduced",
            fontsize=7.5, color=VLINE_COLOR, va="top")

    ax.axvline(1980, color=VLINE_COLOR, linestyle="--", linewidth=1.2, zorder=3)
    ax.text(1980.3, ax.get_ylim()[1] * 0.97, "3PT introduced",
            fontsize=7.5, color=VLINE_COLOR, va="top")

    ax.axvline(2010, color=VLINE_COLOR, linestyle="--", linewidth=1.2, zorder=3)
    ax.text(2010.3, ax.get_ylim()[1] * 0.97, "Stephen Curry debut season",
            fontsize=7.5, color=VLINE_COLOR, va="top")

    # Shaded band rather than a single line because the rule was in effect for
    # parts of three seasons
    ax.axvspan(1994, 1997, color=SHADE_COLOR, alpha=SHADE_ALPHA, zorder=0)
    ax.text(1994.1, ax.get_ylim()[1] * 0.97, "Shortened 3PT line",
            fontsize=7.5, color="#a07800", va="top")


# ── FIGURE 1: Points per game over time ──────────────────────────────────────

fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)

ax.plot(reg.index,     reg["PTS"],     color=REGULAR_COLOR, linewidth=1.8, label="Regular Season")
ax.plot(playoff.index, playoff["PTS"], color=PLAYOFF_COLOR,  linewidth=1.8, label="Playoffs", linestyle="--")

style_ax(ax, ALL_SEASONS)
add_era_markers(ax)

ax.set_title("NBA League Average Points Per Game Over Time", fontsize=TITLE_SIZE, fontweight="bold")
ax.set_xlabel("Season", fontsize=LABEL_SIZE)
ax.set_ylabel("Points Per Game", fontsize=LABEL_SIZE)
ax.legend(fontsize=LABEL_SIZE)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "fig1_pts_over_time.png"), dpi=150)
plt.close()

# ── FIGURE 2: Pace over time ──────────────────────────────────────────────────

fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)

ax.plot(reg.index,     reg["Pace"],     color=REGULAR_COLOR, linewidth=1.8, label="Regular Season")
ax.plot(playoff.index, playoff["Pace"], color=PLAYOFF_COLOR,  linewidth=1.8, label="Playoffs", linestyle="--")

style_ax(ax, ALL_SEASONS)
add_era_markers(ax)

ax.set_title("NBA League Average Pace Over Time", fontsize=TITLE_SIZE, fontweight="bold")
ax.set_xlabel("Season", fontsize=LABEL_SIZE)
ax.set_ylabel("Pace", fontsize=LABEL_SIZE)
ax.legend(fontsize=LABEL_SIZE)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "fig2_pace_over_time.png"), dpi=150)
plt.close()

# ── FIGURE 3: 3-point attempts per game over time ────────────────────────────

fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)

ax.plot(reg.index,     reg["3PA"],     color=REGULAR_COLOR, linewidth=1.8, label="Regular Season")
ax.plot(playoff.index, playoff["3PA"], color=PLAYOFF_COLOR,  linewidth=1.8, label="Playoffs", linestyle="--")

style_ax(ax, ALL_SEASONS)
add_era_markers(ax)

ax.set_title("NBA League Average 3-Point Attempts Per Game Over Time", fontsize=TITLE_SIZE, fontweight="bold")
ax.set_xlabel("Season", fontsize=LABEL_SIZE)
ax.set_ylabel("3-Point Attempts Per Game", fontsize=LABEL_SIZE)
ax.legend(fontsize=LABEL_SIZE)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "fig3_3pa_over_time.png"), dpi=150)
plt.close()

# ── FIGURES 4 & 5: Best vs worst team by SRS each season ─────────────────────

# Reset index so Season is a column available for groupby operations
team_reset = team.reset_index()

# Identify the highest and lowest SRS team for each season;
# idxmax/idxmin return the row index of the extreme value within each group
best  = team_reset.loc[team_reset.groupby("Season")["SRS"].idxmax()].set_index("Season")
worst = team_reset.loc[team_reset.groupby("Season")["SRS"].idxmin()].set_index("Season")

# Figure 4: Pace of best vs worst team
fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
ax.plot(best.index,  best["Pace"],  color=BEST_COLOR,  linewidth=1.8, label="Best team by SRS")
ax.plot(worst.index, worst["Pace"], color=WORST_COLOR, linewidth=1.8, label="Worst team by SRS", linestyle="--")
style_ax(ax, ALL_SEASONS)
add_era_markers(ax)
ax.set_title("Pace of Best vs Worst Team (by SRS) Each Season", fontsize=TITLE_SIZE, fontweight="bold")
ax.set_xlabel("Season", fontsize=LABEL_SIZE)
ax.set_ylabel("Pace", fontsize=LABEL_SIZE)
ax.legend(fontsize=LABEL_SIZE)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "fig4_pace_best_worst.png"), dpi=150)
plt.close()

# Figure 5: 3PA of best vs worst team
fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
ax.plot(best.index,  best["3PA"],  color=BEST_COLOR,  linewidth=1.8, label="Best team by SRS")
ax.plot(worst.index, worst["3PA"], color=WORST_COLOR, linewidth=1.8, label="Worst team by SRS", linestyle="--")
style_ax(ax, ALL_SEASONS)
add_era_markers(ax)
ax.set_title("3PA of Best vs Worst Team (by SRS) Each Season", fontsize=TITLE_SIZE, fontweight="bold")
ax.set_xlabel("Season", fontsize=LABEL_SIZE)
ax.set_ylabel("3-Point Attempts Per Game", fontsize=LABEL_SIZE)
ax.legend(fontsize=LABEL_SIZE)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "fig5_3pa_best_worst.png"), dpi=150)
plt.close()


# ── FIGURE 6: Table — % of seasons where best SRS team shoots more 3PA ───────

def pct_best_above_worst_3pa(df, from_season):
    """
    For each season from `from_season` onwards, check whether the team with
    the highest SRS attempted more 3s per game than the team with the lowest SRS.
    Returns (count of seasons where best > worst, total valid seasons, percentage).
    Seasons where either team is missing a 3PA value are skipped.
    """
    subset = df[df["Season"] >= from_season]
    seasons = subset["Season"].unique()
    count = 0
    total = 0
    for s in seasons:
        s_data = subset[subset["Season"] == s]
        # Need at least two teams with SRS values to define a best and worst
        if s_data["SRS"].notna().sum() < 2:
            continue
        best_3pa  = s_data.loc[s_data["SRS"].idxmax(), "3PA"]
        worst_3pa = s_data.loc[s_data["SRS"].idxmin(), "3PA"]
        if pd.notna(best_3pa) and pd.notna(worst_3pa):
            total += 1
            if best_3pa > worst_3pa:
                count += 1
    return count, total, round(100 * count / total, 1) if total > 0 else None

# Compute for two windows: full 3PT era and the modern era anchored to Curry's debut
c80,   t80,   p80   = pct_best_above_worst_3pa(team_reset, 1980)
c2010, t2010, p2010 = pct_best_above_worst_3pa(team_reset, 2010)

table_data = [
    ["Since 1980", t80,   c80,   f"{p80}%"],
    ["Since 2010", t2010, c2010, f"{p2010}%"],
]
col_labels = ["Period", "Seasons", "Best > Worst 3PA", "% of Seasons"]

fig, ax = plt.subplots(figsize=(7, 2))
ax.axis("off")
tbl = ax.table(
    cellText=table_data,
    colLabels=col_labels,
    loc="center",
    cellLoc="center",
)
tbl.auto_set_font_size(False)
tbl.set_fontsize(11)
tbl.scale(1, 2)

# Style header row
for col in range(len(col_labels)):
    tbl[0, col].set_facecolor("#1f77b4")
    tbl[0, col].set_text_props(color="white", fontweight="bold")

# Alternating row shading for readability
for row in range(1, len(table_data) + 1):
    fc = "#eaf2fb" if row % 2 == 0 else "white"
    for col in range(len(col_labels)):
        tbl[row, col].set_facecolor(fc)

ax.set_title(
    "Best SRS Team Has More 3PA Than Worst SRS Team",
    fontsize=TITLE_SIZE, fontweight="bold", pad=12
)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "fig6_3pa_best_worst_table.png"), dpi=150, bbox_inches="tight")
plt.close()


# ── FIGURE 7: SRS vs Pace & 3PA scatter (2010–present) ───────────────────────

# Restrict to the modern era where both Pace and 3PA are consistently available
df2010 = team_reset[team_reset["Season"] >= 2010]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle("Team SRS vs Pace and 3PA (2010–present)", fontsize=TITLE_SIZE, fontweight="bold")


def add_lobf(ax, x_col, color="darkorange"):
    """Fit and plot an OLS line of best fit over the 2010-present scatter."""
    m, b = np.polyfit(x_col, df2010["SRS"], 1)
    x_line = np.linspace(x_col.min(), x_col.max(), 200)
    ax.plot(x_line, m * x_line + b, color=color, linewidth=1.8, linestyle="-", zorder=4)


def add_scatter_highlights(ax, highlights, x_col_name, source_df):
    """
    Annotate specific (Season, Team) points on a scatter plot.
    Each entry in `highlights` is a dict with keys:
      Season, Team, label — required
      color, marker      — optional, default to crimson and circle
    Prints a warning and skips silently if a team/season combination is not found.
    """
    for h in highlights:
        row = source_df[(source_df["Season"] == h["Season"]) & (source_df["Team"] == h["Team"])]
        if row.empty:
            print(f"  [warn] not found: {h}")
            continue
        x, y   = row[x_col_name].values[0], row["SRS"].values[0]
        color  = h.get("color", "crimson")
        marker = h.get("marker", "o")
        ax.scatter(x, y, color=color, s=60, zorder=5, marker=marker)
        ax.annotate(h["label"], xy=(x, y), xytext=(8, 4),
                    textcoords="offset points", fontsize=9,
                    color=color, fontweight="bold")


# Left panel: SRS vs Pace
# The 1991 Nuggets are included as a historical outlier for context even though
# they fall outside the 2010-present scatter data
highlights_pace = [
    {"Season": 2015, "Team": "Golden State Warriors", "label": "2015 Warriors"},
    {"Season": 2020, "Team": "Milwaukee Bucks",       "label": "2020 Bucks"},
    {"Season": 1991, "Team": "Denver Nuggets",        "label": "1991 Nuggets (historical)",
     "color": "darkorchid", "marker": "^"},
]
ax1.scatter(df2010["Pace"], df2010["SRS"], color="steelblue", alpha=0.3, s=18, zorder=2)
ax1.axhline(0, color=VLINE_COLOR, linestyle="--", linewidth=1.2, zorder=3)
ax1.text(df2010["Pace"].min(), 0.15, "Average", fontsize=8, color=VLINE_COLOR, va="bottom")
add_lobf(ax1, df2010["Pace"])
add_scatter_highlights(ax1, highlights_pace, "Pace", team_reset)
ax1.set_xlabel("Pace", fontsize=LABEL_SIZE)
ax1.set_ylabel("SRS", fontsize=LABEL_SIZE)
ax1.set_title("SRS vs Pace", fontsize=LABEL_SIZE, fontweight="bold")
ax1.grid(linestyle="--", alpha=0.4)
ax1.spines["top"].set_visible(False)
ax1.spines["right"].set_visible(False)

# Right panel: SRS vs 3PA
highlights_3pa = [
    {"Season": 2015, "Team": "Golden State Warriors", "label": "2015 Warriors"},
    {"Season": 2018, "Team": "Houston Rockets",       "label": "2018 Rockets"},
]
ax2.scatter(df2010["3PA"], df2010["SRS"], color="steelblue", alpha=0.3, s=18, zorder=2)
ax2.axhline(0, color=VLINE_COLOR, linestyle="--", linewidth=1.2, zorder=3)
ax2.text(df2010["3PA"].min(), 0.15, "Average", fontsize=8, color=VLINE_COLOR, va="bottom")
add_lobf(ax2, df2010["3PA"])
add_scatter_highlights(ax2, highlights_3pa, "3PA", team_reset)
ax2.set_xlabel("3-Point Attempts Per Game", fontsize=LABEL_SIZE)
ax2.set_ylabel("SRS", fontsize=LABEL_SIZE)
ax2.set_title("SRS vs 3PA", fontsize=LABEL_SIZE, fontweight="bold")
ax2.grid(linestyle="--", alpha=0.4)
ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)

plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "fig7_srs_vs_pace_and_3pa.png"), dpi=150)
plt.close()