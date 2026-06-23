SCRIPT=pdm run python ./script.py

all: all-ranks.csv all-unfiltered-ranks.csv 2025-ranks.csv 2025-unfiltered-ranks.csv

all-ranks.csv:
	$(SCRIPT) -d ALL -l 500 > $@

all-unfiltered-ranks.csv:
	$(SCRIPT) -d ALL -l 500 --no-filter > $@

2025-ranks.csv:
	$(SCRIPT) -d 2025 -l 500 > $@

2025-unfiltered-ranks.csv:
	$(SCRIPT) -d 2025 -l 500 --no-filter > $@
