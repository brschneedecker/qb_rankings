# qb_rankings

NFL QB Analysis using Python 3.

## Setup

1. Run ```git clone https://github.com/brschneedecker/qb_rankings.git``` to clone this repo
2. Install packages (see requirements.txt)

---

## Run Instructions

1. Run ```cd [clone path]/qb_rankings``` to navigate to the repo directory
2. In Makefile, update ```bgn_yr``` and ```end_yr``` to get desired analysis period
3. Run ```make db``` to create the database with empty tables
4. Run ```make extract``` to extract all seasons between ```bgn_yr``` and ```end_yr``` inclusive and load to database