.PHONY: all report install

# Top level target
all: report/blog.html report/blog.pdf

# Install dependencies
install:
	pip install -r requirements.txt

# Scraping produces raw data files
data/raw_team_stats.csv data/raw_league_averages.csv: code/scraping.py
	python code/scraping.py

# Cleaning depends on raw data and cleaning script
data/clean_team_stats.csv data/clean_league_averages.csv: data/raw_team_stats.csv data/raw_league_averages.csv code/cleaning.py
	python code/cleaning.py

# Figures depend on clean data and visualisation script
figures/fig1_pts_over_time.png: data/clean_team_stats.csv data/clean_league_averages.csv code/visualisations.py
	python code/visualisations.py

# Report depends on figures and the qmd file
report/blog.html: report/blog.qmd figures/fig1_pts_over_time.png
	quarto render report/blog.qmd --to html

report/blog.pdf: report/blog.qmd figures/fig1_pts_over_time.png
	quarto render report/blog.qmd --to pdf