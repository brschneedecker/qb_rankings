.PHONY: clean db extract

bgn_yr = 2017
end_yr = 2018

rm_db:
	rm -f data/*.db

rm_logs:
	rm -f logs/*.log

db: rm_db
	python3 src/db_create.py

extract:
	python3 src/qb_etl.py $(bgn_yr) $(end_yr)
