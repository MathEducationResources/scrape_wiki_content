## help: list all commands
help: Makefile
	@sed -n 's/##//p' $<

## all:
all:
	python wiki2csv.py --meta --write_all
	python wiki2csv.py --topic
	python wiki2csv.py --examURL
	python wiki2csv.py --contributors_flags --write_all
	python topics2json.py
	python wiki2json.py --write_all
	python raw2latex.py
	python add2json.py
	python latex2pdf.py


## clean: remove all intermediate files: csv and json
clean:

.PHONY: all clean all_json add_latex summary_data/questions_topic.csv summary_data/questions_meta.csv summary_data/exam_pdf_url.csv summary_data/contributors.csv summary_data/flags.csv

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

## summary_data/contributors.csv: csv with contributors for each question. Optional: ARGS="--verbose --write_all". Same as summary_data/flags.csv
summary_data/contributors.csv: wiki2csv.py helpers.py
	python $< --contributors_flags $(ARGS)

## summary_data/flags.csv: csv with quality flags for each question. Optional: ARGS="--verbose --write_all". Same as summary_data/contributors.csv
summary_data/flags.csv: wiki2csv.py helpers.py
	python $< --contributors_flags $(ARGS)

## topics2json: saves topic video links to json. Optional: ARGS="--q_filter=..."
topics2json: topics2json.py
	python $< $(ARGS)

## raw_json: scrape raw content from UBC wiki. Optional: ARGS="--write_all --q_filter=..."
raw_json: wiki2json.py helpers.py
	python $< $(ARGS)

## add_latex: compiles raw mediawiki version to latex. Optional: ARGS="--verbose --q_filter=..."
add_latex: raw2latex.py 
	python $< $(ARGS)

## add2json: adds contributors, flags, topics, votes and html to json files. Optional: ARGS="--verbose --q_filter=..."
add2json: add2json.py
	python $< $(ARGS)

## create_pdfs: creates pdf version of each exam
create_pdfs: latex2pdf.py
	python $<

## backup_mongodb: backs up production mongodb (currently not working on mongodb 3.x)
backup_mongodb:
	today=`date '+%Y_%m_%d_%H_%M_%S'`; out="./backup_$$today"; export $$(cat prod.env); mongodump -v --host $$MONGOLAB_HOST --db $$MONGOLAB_DB --username $$MONGOLAB_USERNAME --password $$MONGOLAB_PASSWORD --out ./$$out
