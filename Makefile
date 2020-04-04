.PHONY: clean db extract

bgn_yr = 2017
end_yr = 2018
dbname = data/qb_sqlite.db

clean:
	rm -f data/*.db

extract:
	python3 src/qb_etl.py $(bgn_yr) $(end_yr)

db: clean
	python3 src/create_sql_db.py $(dbname)
