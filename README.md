# BEE2041_empirical_project

This project is a data-driven blog post that attempts to answer the question: what has Stephen Curry and the ‘91 Nuggets done to the modern NBA? 


## Data Source 

Data was downloaded and scraped from [Basketball Reference](https://www.basketball-reference.com/) in accordance with their terms of service ([data_use.html](https://www.sports-reference.com/data_use.html)) and rate limits ([bot-traffic.html](https://www.sports-reference.com/bot-traffic.html)). None of the pages accessed are disallowed under the User-agent: * section of the robots.txt file. 

Two datasets are used:
* *League averages* - downloaded manually from [NBA Stats Per Game page](https://www.basketball-reference.com/leagues/NBA_stats_per_game.html) (as it is only 2 tables) and committed to the repo. Running ‘make’ does not re-download this file.
* *Team averages* –  data is from many different pages so is scraped using code/scraping.py and is not committed. Running ‘make’ creates a csv of this raw data (data/raw_team_stats.csv).


## Audience 

This is aimed at an audience that has some prior knowledge of basketball (I do not explain some terms like the playoffs and “bigs”) but not an expert in the statistics related to it (I explain other terms like SRS). Because of the subject matter this is a more informal piece of writing and I will be using predominantly other online articles and blogs as references rather than academic journals. 


## Requirements

Requirements.txt has only the names of the python packages to prevent issues on new systems but exact versions are as follows:
* cloudscraper==1.2.71
* numpy==2.4.4
* matplotlib==3.10.9
* pandas==3.0.2

Also requires:
* Python 3.12+
* [Quarto](https://quarto.org/docs/get-started/) 1.5+
* TinyTex (‘*quarto install tinytex*’)
* Make
* Linux command line (windows users should use WSL)


## Installation 

 ```bash
git clone https://github.com/Isaac-Bright/BEE2041_empirical_project
python3 -m venv nba-env 
cd BEE2041_empirical_project 
source nba-env/bin/activate 
pip install -r requirements.txt
make
```
First clone the repo, create and activate a python virtual environment and install requirements. Then run 'make' to run the scripts and format the quarto file. 


## Repository Overview 

```
BEE2041_empirical_project/
├── Makefile                        # automates the pipeline
├── requirements.txt                # Python dependencies
├── README.md
├── code/
│   ├── scraping.py                 # scrapes raw team stats from Basketball Reference
│   ├── cleaning.py                 # cleans and processes raw data
│   └── visualisations.py          # generates figures
├── data/
│   └── raw_league_averages.csv    # manually downloaded raw data
├── figures/                        # directory for generated figures
└── report/
    ├── blog.pdf                   # report formatted output
    └── blog.qmd                   # report source file
```