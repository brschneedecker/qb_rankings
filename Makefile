.PHONY: clean db extract

bgn_yr = 2017
end_yr = 2018

clean:
	rm -f data/*.db

db: clean
	python3 src/db_create.py

extract:
	python3 src/qb_etl.py $(bgn_yr) $(end_yr)
