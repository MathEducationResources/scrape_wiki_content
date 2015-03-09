## help: list all commands
help: Makefile
	@sed -n 's/##//p' $<

## all:
all:

## clean: remove all intermediate files: csv and json
clean:

.PHONY: all, clean
.DELETE_ON_ERROR:
.SECONDARY:

## summary_data/questions_meta.csv: csv with meta data (URL,course,exam,question,num_hints,num_sols). Optional: ARGS="--verbose --write_all"
summary_data/questions_meta.csv: wiki2csv.py
	python $< --meta $(ARGS)
	# Now, re-sort output file summary_data/questions_meta.csv
	(head -n 2 summary_data/questions_meta.csv && tail -n +3 summary_data/questions_meta.csv | sort) > summary_data/questions_meta_temp.csv
	mv summary_data/questions_meta_temp.csv summary_data/questions_meta.csv

## summary_data/questions_topic.csv: csv with topics and parent topics for each question. Optional: ARGS="--verbose"
summary_data/questions_topic.csv: wiki2csv.py summary_data/questions_meta.csv
	python $< --topic $(ARGS)
