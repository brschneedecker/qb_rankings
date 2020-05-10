.PHONY: qb_env all

bgn_yr = 2002
end_yr = 2019

dirs:
	mkdir -p logs
	mkdir -p data

rm_db:
	rm -f data/*.db

db:
	python3 src/db_create.py

extract:
	python3 src/qb_etl.py $(bgn_yr) $(end_yr)

all: dirs rm_db db extract