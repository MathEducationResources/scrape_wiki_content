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

## questions_meta.csv: csv with meta data (URL,course,exam,question,num_hints,num_sols). optional: ARGS="--verbose --write_all"
questions_meta.csv: wiki2csv.py
	python $< --meta --verbose $(ARGS)

## questions_topic.csv: csv with topics and parent topics for each question
questions_topic.csv: wiki2csv.py questions_meta.csv
	python $< --topic
