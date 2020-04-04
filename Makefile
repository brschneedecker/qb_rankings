.PHONY: clean db

bgn_yr = 2002
end_yr = 2018
dbname = data/qb_sqlite.db

all: clean data/qb_season_final.csv

clean:
	rm -f data/*.csv

data/qb_season_final.csv:
	python3 src/qb_etl.py $(bgn_yr) $(end_yr) $@

db:
	python3 src/create_sql_db.py $(dbname)
