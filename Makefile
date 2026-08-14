# Makefile for compiling all resume versions
# Each version lives in its own subdirectory

LATEX       = pdflatex
LATEX_FLAGS = -interaction=nonstopmode
PDF_TO_PNG  = pdftoppm

.PHONY: all clean standard ats se fde formats

all: standard ats se fde

standard: standard/ariel_paulin.png standard/ariel_paulin.json standard/ariel_paulin.txt
ats:      ats/ariel_paulin_ats.png
se:       se/ariel_paulin_se.png
fde:      fde/ariel_paulin_fde.png

formats: standard/ariel_paulin.json standard/ariel_paulin.txt

# --- Standard ---
standard/ariel_paulin.pdf: standard/ariel_paulin.tex
	cd standard && $(LATEX) $(LATEX_FLAGS) ariel_paulin.tex

standard/ariel_paulin.png: standard/ariel_paulin.pdf
	cd standard && $(PDF_TO_PNG) -png ariel_paulin.pdf > ariel_paulin.png

standard/ariel_paulin.json standard/ariel_paulin.txt: standard/ariel_paulin.tex experience/*.tex education.tex scripts/generate_formats.py
	python3 scripts/generate_formats.py

# --- ATS ---
ats/ariel_paulin_ats.pdf: ats/ariel_paulin_ats.tex
	cd ats && $(LATEX) $(LATEX_FLAGS) ariel_paulin_ats.tex

ats/ariel_paulin_ats.png: ats/ariel_paulin_ats.pdf
	cd ats && $(PDF_TO_PNG) -png ariel_paulin_ats.pdf ariel_paulin_ats

# --- Sales Engineering ---
se/ariel_paulin_se.pdf: se/ariel_paulin_se.tex
	cd se && $(LATEX) $(LATEX_FLAGS) ariel_paulin_se.tex

se/ariel_paulin_se.png: se/ariel_paulin_se.pdf
	cd se && $(PDF_TO_PNG) -png ariel_paulin_se.pdf > ariel_paulin_se.png

# --- Forward Deployed Engineering ---
fde/ariel_paulin_fde.pdf: fde/ariel_paulin_fde.tex fde/experience/*.tex
	cd fde && $(LATEX) $(LATEX_FLAGS) ariel_paulin_fde.tex

fde/ariel_paulin_fde.png: fde/ariel_paulin_fde.pdf
	cd fde && $(PDF_TO_PNG) -png ariel_paulin_fde.pdf > ariel_paulin_fde.png

# --- Clean ---
clean:
	rm -f standard/ariel_paulin.pdf standard/ariel_paulin.png standard/ariel_paulin.json standard/ariel_paulin.txt \
	      ats/ariel_paulin_ats.pdf  ats/ariel_paulin_ats.png ats/ariel_paulin_ats-*.png \
	      se/ariel_paulin_se.pdf    se/ariel_paulin_se.png \
	      fde/ariel_paulin_fde.pdf  fde/ariel_paulin_fde.png \
	      standard/*.aux standard/*.log standard/*.out \
	      ats/*.aux      ats/*.log      ats/*.out \
	      se/*.aux       se/*.log       se/*.out \
	      fde/*.aux      fde/*.log      fde/*.out \
	      ariel_paulin.pdf ariel_paulin.png \
	      ariel_paulin_ats.pdf ariel_paulin_ats.png ariel_paulin_ats-*.png \
	      ariel_paulin_se.pdf ariel_paulin_se.png \
	      ariel_paulin_fde.pdf ariel_paulin_fde.png
