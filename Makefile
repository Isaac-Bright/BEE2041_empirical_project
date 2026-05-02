all: report/blog.html report/blog.pdf

data/raw_team_stats.csv: code/scraping.py
	python code/scraping.py

data/clean_team_stats.csv data/clean_league_averages.csv: data/raw_team_stats.csv data/raw_league_averages.csv code/cleaning.py
	python code/cleaning.py

figures/fig1_pts_over_time.png: data/clean_team_stats.csv data/clean_league_averages.csv code/analysis.py
	python code/analysis.py

report/blog.html report/blog.pdf: report/blog.qmd figures/fig1_pts_over_time.png
	quarto render report/blog.qmd --to html
	quarto render report/blog.qmd --to pdf
