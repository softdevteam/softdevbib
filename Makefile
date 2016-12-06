# Run prebib and check that bibtex accepts our bibliography.

.PHONY: check clean

all: clean check

check:
	python3.5 ./bin/prebib softdev.bib > out.bib
	pdflatex check
	bibtex check
	pdflatex check
	pdflatex check

clean:
	-rm -f check.aux check.bbl check.blg check.log check.out check.pdf \
		out.bib
