.PHONY: clean src_data

bgn_yr = 2002
end_yr = 2018

all: clean data/qb_season_final.csv

clean:
	rm -f data/*.csv

data/qb_season_final.csv:
	python3 src/qb_etl.py $(bgn_yr) $(end_yr) $@
