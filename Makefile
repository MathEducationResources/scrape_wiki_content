## help: list all commands
help: Makefile
	@sed -n 's/##//p' $<

## all:
all:
	python wiki2csv.py --meta --write_all
	python wiki2csv.py --topic
	python wiki2csv.py --examURL
	python wiki2json.py
	python raw2latex.py
	python latex2pdf.py

## clean: remove all intermediate files: csv and json
clean:

.PHONY: all, clean, all_json, add_latex, summary_data/questions_topic.csv, summary_data/questions_meta.csv, summary_data/exam_pdf_url.csv

## summary_data/questions_meta.csv: csv with meta data (URL,course,exam,question,num_hints,num_sols). Optional: ARGS="--verbose --write_all"
summary_data/questions_meta.csv: wiki2csv.py helpers.py
	python $< --meta $(ARGS)
	# Now, re-sort output file summary_data/questions_meta.csv
	(head -n 2 summary_data/questions_meta.csv && tail -n +3 summary_data/questions_meta.csv | sort) > summary_data/questions_meta_temp.csv
	mv summary_data/questions_meta_temp.csv summary_data/questions_meta.csv

## summary_data/questions_topic.csv: csv with topics and parent topics for each question. Optional: ARGS="--verbose"
summary_data/questions_topic.csv: wiki2csv.py helpers.py
	python $< --topic $(ARGS)

## summary_data/exam_pdf_url.csv: csv with url of each exam. Optional: ARGS="--verbose"
summary_data/exam_pdf_url.csv: wiki2csv.py helpers.py
	python $< --examURL $(ARGS)

## raw_json: scrape raw content from UBC wiki Optional: ARGS="--write_all --filter=..."
raw_json: wiki2json.py helpers.py
	python $< $(ARGS)

## add_latex: compiles raw mediawiki version to latex
add_latex: raw2latex.py 
	python $<

## create_pdfs: creates pdf version of each exam
create_pdfs: latex2pdf.py
	python $<

## backup_mongodb: backs up production mongodb (currently not working on mongodb 3.x)
backup_mongodb:
	today=`date '+%Y_%m_%d_%H_%M_%S'`; out="./backup_$$today"; export $$(cat prod.env); mongodump -v --host $$MONGOLAB_HOST --db $$MONGOLAB_DB --username $$MONGOLAB_USERNAME --password $$MONGOLAB_PASSWORD --out ./$$out
