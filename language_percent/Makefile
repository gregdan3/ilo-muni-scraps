SCRIPT=pdm run python ./script.py
LIMIT=99999

all: all-ranks.csv all-unfiltered-ranks.csv 2025-ranks.csv 2025-unfiltered-ranks.csv

clean:
	rm -rf ./*.csv

all-ranks.csv:
	$(SCRIPT) -d ALL -l $(LIMIT) > $@

all-unfiltered-ranks.csv:
	$(SCRIPT) -d ALL -l $(LIMIT) --no-filter > $@

2025-ranks.csv:
	$(SCRIPT) -d 2025 -l $(LIMIT) > $@

2025-unfiltered-ranks.csv:
	$(SCRIPT) -d 2025 -l $(LIMIT) --no-filter > $@
