# Makefile for compiling all resume versions
# Each version lives in its own subdirectory

LATEX       = pdflatex
LATEX_FLAGS = -interaction=nonstopmode
PDF_TO_PNG  = pdftoppm

# Source files
STANDARD_TEX = standard/ariel_paulin.tex
ATS_TEX      = ats/ariel_paulin_ats.tex
SE_TEX       = se/ariel_paulin_se.tex

# Output PDFs
STANDARD_PDF = standard/ariel_paulin.pdf
ATS_PDF      = ats/ariel_paulin_ats.pdf
SE_PDF       = se/ariel_paulin_se.pdf

# Output PNGs
STANDARD_PNG = standard/ariel_paulin.png
ATS_PNG      = ats/ariel_paulin_ats.png
SE_PNG       = se/ariel_paulin_se.png

.PHONY: all clean standard ats se

all: standard ats se

standard: $(STANDARD_PNG)
ats:      $(ATS_PNG)
se:       $(SE_PNG)

# --- Standard ---
$(STANDARD_PDF): $(STANDARD_TEX)
	cd standard && $(LATEX) $(LATEX_FLAGS) ariel_paulin.tex

$(STANDARD_PNG): $(STANDARD_PDF)
	$(PDF_TO_PNG) -png $(STANDARD_PDF) > $(STANDARD_PNG)

# --- ATS ---
$(ATS_PDF): $(ATS_TEX)
	cd ats && $(LATEX) $(LATEX_FLAGS) ariel_paulin_ats.tex

$(ATS_PNG): $(ATS_PDF)
	$(PDF_TO_PNG) -png $(ATS_PDF) > $(ATS_PNG)

# --- Sales Engineering ---
$(SE_PDF): $(SE_TEX)
	cd se && $(LATEX) $(LATEX_FLAGS) ariel_paulin_se.tex

$(SE_PNG): $(SE_PDF)
	$(PDF_TO_PNG) -png $(SE_PDF) > $(SE_PNG)

# --- Clean ---
clean:
	rm -f $(STANDARD_PDF) $(ATS_PDF) $(SE_PDF) \
	      $(STANDARD_PNG) $(ATS_PNG) $(SE_PNG) \
	      standard/*.aux standard/*.log standard/*.out \
	      ats/*.aux      ats/*.log      ats/*.out \
	      se/*.aux       se/*.log       se/*.out
