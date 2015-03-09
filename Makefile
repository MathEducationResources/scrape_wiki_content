## help: list all commands
help: Makefile
	@sed -n 's/##//p' $<

## all:
all:

## clean: remove all intermediate files: csv and json
clean:

.PHONY: all, clean, all_json

## summary_data/questions_meta.csv: csv with meta data (URL,course,exam,question,num_hints,num_sols). Optional: ARGS="--verbose --write_all"
summary_data/questions_meta.csv: wiki2csv.py helpers.py
	python $< --meta $(ARGS)
	# Now, re-sort output file summary_data/questions_meta.csv
	(head -n 2 summary_data/questions_meta.csv && tail -n +3 summary_data/questions_meta.csv | sort) > summary_data/questions_meta_temp.csv
	mv summary_data/questions_meta_temp.csv summary_data/questions_meta.csv

## summary_data/questions_topic.csv: csv with topics and parent topics for each question. Optional: ARGS="--verbose"
summary_data/questions_topic.csv: wiki2csv.py helpers.py summary_data/questions_meta.csv
	python $< --topic $(ARGS)

## summary_data/exam_pdf_url.csv: csv with url of each exam. Optional: ARGS="--verbose"
summary_data/exam_pdf_url.csv: wiki2csv.py helpers.py summary_data/questions_meta.csv
	python $< --examURL $(ARGS)

## raw_json: scrape raw content from UBC wiki Optional: ARGS="--write_all --filter=..."
raw_json: wiki2json.py helpers.py summary_data/questions_meta.csv
	python $< $(ARGS)

## backup_mongodb: backs up production mongodb
backup_mongodb:
	today=`date '+%Y_%m_%d_%H_%M_%S'`; out="./backup_$$today"; export $$(cat prod.env); mongodump -v --host $$MONGOLAB_HOST --db $$MONGOLAB_DB --username $$MONGOLAB_USERNAME --password $$MONGOLAB_PASSWORD --out ./$$out

