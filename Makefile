.PHONY: dirs clean extract all

bgn_yr = 2002
end_yr = 2019

dirs:
	mkdir -p logs
	mkdir -p data

clean:
	rm -f data/*
	rm -f logs/*

extract:
	python3 src/qb_etl.py $(bgn_yr) $(end_yr)

all: dirs clean extract