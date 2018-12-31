.PHONY: clean src_data

bgn_yr = 2002
end_yr = 2018

all: data/processed/qb_season_final.csv

clean:
	rm -f data/raw/*.csv
	rm -f data/processed/*.csv
	rm -f reports/figures/*.png
	
src_data:
	python3 src/data/download.py $(bgn_yr) $(end_yr)

data/processed/qb_season_final.csv: src_data
	python3 src/data/preprocess.py $@