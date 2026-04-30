import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "..", "data")
FIG_DIR  = os.path.join(BASE_DIR, "..", "output", "figures")
os.makedirs(FIG_DIR, exist_ok=True)

league = pd.read_csv(os.path.join(DATA_DIR, "clean_league_averages.csv"), index_col="Season")
team   = pd.read_csv(os.path.join(DATA_DIR, "clean_team_stats.csv"), index_col="Season")

reg     = league[league["Playoffs"] == False]
playoff = league[league["Playoffs"] == True]

# Shared style
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


def style_ax(ax, seasons):
    """Apply common x-axis styling."""
    ax.set_xticks(seasons)
    ax.set_xticklabels(seasons, rotation=ROTATION, fontsize=TICK_SIZE)
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)


def add_era_markers(ax):
    """Add 1980 3pt introduction line and 1994-97 shortened line shading."""
    ax.axvline(1954, color=VLINE_COLOR, linestyle="--", linewidth=1.2, zorder=3)
    ax.text(1954.3, ax.get_ylim()[1] * 0.97, "Shot clock introduced",
            fontsize=7.5, color=VLINE_COLOR, va="top")
    
    ax.axvline(1980, color=VLINE_COLOR, linestyle="--", linewidth=1.2, zorder=3)
    ax.text(1980.3, ax.get_ylim()[1] * 0.97, "3PT introduced",
            fontsize=7.5, color=VLINE_COLOR, va="top")
    
    ax.axvline(2010, color=VLINE_COLOR, linestyle="--", linewidth=1.2, zorder=3)
    ax.text(2010.3, ax.get_ylim()[1] * 0.97, "Stephen Curry debut season",
            fontsize=7.5, color=VLINE_COLOR, va="top")

    ax.axvspan(1994, 1997, color=SHADE_COLOR, alpha=SHADE_ALPHA, zorder=0)
    ax.text(1994.1, ax.get_ylim()[1] * 0.97, "Shortened 3PT line",
            fontsize=7.5, color="#a07800", va="top")


# ── FIGURE 1: PTS over time ───────────────────────────────────────────────────

seasons = sorted(league.index.unique())

fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)

ax.plot(reg.index,     reg["PTS"],     color=REGULAR_COLOR, linewidth=1.8, label="Regular Season")
ax.plot(playoff.index, playoff["PTS"], color=PLAYOFF_COLOR,  linewidth=1.8, label="Playoffs", linestyle="--")

style_ax(ax, seasons)
add_era_markers(ax)

ax.set_title("NBA League Average Points Per Game Over Time", fontsize=TITLE_SIZE, fontweight="bold")
ax.set_xlabel("Season", fontsize=LABEL_SIZE)
ax.set_ylabel("Points Per Game", fontsize=LABEL_SIZE)
ax.legend(fontsize=LABEL_SIZE)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "fig1_pts_over_time.png"), dpi=150)
plt.close()

# ── FIGURE 2: Pace and 3PA over time (two subplots) ──────────────────────────

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=FIGSIZE_DOUBLE, sharex=True)

# Pace
ax1.plot(reg.index,     reg["Pace"],     color=REGULAR_COLOR, linewidth=1.8, label="Regular Season")
ax1.plot(playoff.index, playoff["Pace"], color=PLAYOFF_COLOR,  linewidth=1.8, label="Playoffs", linestyle="--")
style_ax(ax1, seasons)
add_era_markers(ax1)
ax1.set_ylabel("Pace", fontsize=LABEL_SIZE)
ax1.set_title("NBA League Average Pace and 3PA Over Time", fontsize=TITLE_SIZE, fontweight="bold")
ax1.legend(fontsize=LABEL_SIZE)

# 3PA
ax2.plot(reg.index,     reg["3PA"],     color=REGULAR_COLOR, linewidth=1.8, label="Regular Season")
ax2.plot(playoff.index, playoff["3PA"], color=PLAYOFF_COLOR,  linewidth=1.8, label="Playoffs", linestyle="--")
style_ax(ax2, seasons)
add_era_markers(ax2)
ax2.set_ylabel("3-Point Attempts Per Game", fontsize=LABEL_SIZE)
ax2.set_xlabel("Season", fontsize=LABEL_SIZE)
ax2.legend(fontsize=LABEL_SIZE)

plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "fig2_pace_3pa_over_time.png"), dpi=150)
plt.close()

# ── FIGURES 3 & 4: Best vs worst team by SRS ─────────────────────────────────

team_seasons = sorted(team.index.unique())

team_reset = team.reset_index()

best  = team_reset.loc[team_reset.groupby("Season")["SRS"].idxmax()].set_index("Season")
worst = team_reset.loc[team_reset.groupby("Season")["SRS"].idxmin()].set_index("Season")

# Figure 3: Pace
fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
ax.plot(best.index,  best["Pace"],  color=BEST_COLOR,  linewidth=1.8, label="Best team by SRS")
ax.plot(worst.index, worst["Pace"], color=WORST_COLOR, linewidth=1.8, label="Worst team by SRS", linestyle="--")
style_ax(ax, team_seasons)
add_era_markers(ax)
ax.set_title("Pace of Best vs Worst Team (by SRS) Each Season", fontsize=TITLE_SIZE, fontweight="bold")
ax.set_xlabel("Season", fontsize=LABEL_SIZE)
ax.set_ylabel("Pace", fontsize=LABEL_SIZE)
ax.legend(fontsize=LABEL_SIZE)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "fig3_pace_best_worst.png"), dpi=150)
plt.close()

# Figure 4: 3PA
fig, ax = plt.subplots(figsize=FIGSIZE_SINGLE)
ax.plot(best.index,  best["3PA"],  color=BEST_COLOR,  linewidth=1.8, label="Best team by SRS")
ax.plot(worst.index, worst["3PA"], color=WORST_COLOR, linewidth=1.8, label="Worst team by SRS", linestyle="--")
style_ax(ax, team_seasons)
add_era_markers(ax)
ax.set_title("3PA of Best vs Worst Team (by SRS) Each Season", fontsize=TITLE_SIZE, fontweight="bold")
ax.set_xlabel("Season", fontsize=LABEL_SIZE)
ax.set_ylabel("3-Point Attempts Per Game", fontsize=LABEL_SIZE)
ax.legend(fontsize=LABEL_SIZE)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "fig4_3pa_best_worst.png"), dpi=150)
plt.close()

# ── FIGURE 5: SRS vs Pace scatter (1980+) ────────────────────────────────────

df80 = team_reset[team_reset["Season"] >= 1980]

highlights5 = [
    {"Season": 2015, "Team": "Golden State Warriors", "label": "2015 Warriors"},
    {"Season": 1991, "Team": "Denver Nuggets",        "label": "1991 Nuggets"},
    {"Season": 2020, "Team": "Milwaukee Bucks",       "label": "2020 Bucks"},
]

fig, ax = plt.subplots(figsize=(9, 6))

ax.scatter(df80["Pace"], df80["SRS"], color="steelblue", alpha=0.3, s=18, zorder=2)

for h in highlights5:
    row = df80[(df80["Season"] == h["Season"]) & (df80["Team"] == h["Team"])]
    if row.empty:
        print(f"  [warn] not found: {h}")
        continue
    x, y = row["Pace"].values[0], row["SRS"].values[0]
    ax.scatter(x, y, color="crimson", s=60, zorder=5)
    ax.annotate(h["label"], xy=(x, y), xytext=(8, 4),
                textcoords="offset points", fontsize=9,
                color="crimson", fontweight="bold")

ax.set_title("Team SRS vs Pace (1980–present)", fontsize=TITLE_SIZE, fontweight="bold")
ax.set_xlabel("Pace", fontsize=LABEL_SIZE)
ax.set_ylabel("SRS", fontsize=LABEL_SIZE)
ax.grid(linestyle="--", alpha=0.4)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "fig5_srs_vs_pace.png"), dpi=150)
plt.close()

# ── FIGURE 6: SRS vs 3PA scatter (1980+) ─────────────────────────────────────

highlights6 = [
    {"Season": 2015, "Team": "Golden State Warriors", "label": "2015 Warriors"},
    {"Season": 2018, "Team": "Houston Rockets",       "label": "2018 Rockets"},
]

fig, ax = plt.subplots(figsize=(9, 6))

ax.scatter(df80["3PA"], df80["SRS"], color="steelblue", alpha=0.3, s=18, zorder=2)

for h in highlights6:
    row = df80[(df80["Season"] == h["Season"]) & (df80["Team"] == h["Team"])]
    if row.empty:
        print(f"  [warn] not found: {h}")
        continue
    x, y = row["3PA"].values[0], row["SRS"].values[0]
    ax.scatter(x, y, color="crimson", s=60, zorder=5)
    ax.annotate(h["label"], xy=(x, y), xytext=(8, 4),
                textcoords="offset points", fontsize=9,
                color="crimson", fontweight="bold")

ax.set_title("Team SRS vs 3PA (1980–present)", fontsize=TITLE_SIZE, fontweight="bold")
ax.set_xlabel("3-Point Attempts Per Game", fontsize=LABEL_SIZE)
ax.set_ylabel("SRS", fontsize=LABEL_SIZE)
ax.grid(linestyle="--", alpha=0.4)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
plt.savefig(os.path.join(FIG_DIR, "fig6_srs_vs_3pa.png"), dpi=150)
plt.close()