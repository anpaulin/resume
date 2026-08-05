# Makefile for compiling ariel_paulin.tex file and converting to PNG

# The name of the output PDF
OUTPUT_PDF = ariel_paulin.pdf
OUTPUT_ATS_PDF = ariel_paulin_ats.pdf

# The name of the source .tex file
TEX_FILE = ariel_paulin.tex
TEX_ATS_FILE = ariel_paulin_ats.tex

# The name of the output PNG
OUTPUT_PNG = ariel_paulin.png
OUTPUT_ATS_PNG = ariel_paulin_ats.png

# LaTeX command to use (use 'xelatex' or 'lualatex' if needed)
LATEX = pdflatex

# Command to convert PDF to PNG
PDF_TO_PNG = pdftoppm

# Flags for pdflatex (you can modify these if needed)
LATEX_FLAGS = -interaction=nonstopmode

# Default target
all: $(OUTPUT_PNG) $(OUTPUT_ATS_PNG)

# Compile the .tex file to .pdf
$(OUTPUT_PDF): $(TEX_FILE)
	$(LATEX) $(LATEX_FLAGS) $(TEX_FILE)

$(OUTPUT_ATS_PDF): $(TEX_ATS_FILE)
	$(LATEX) $(LATEX_FLAGS) $(TEX_ATS_FILE)

# Convert the PDF to PNG
$(OUTPUT_PNG): $(OUTPUT_PDF)
	$(PDF_TO_PNG) -png $(OUTPUT_PDF) > $(OUTPUT_PNG)

$(OUTPUT_ATS_PNG): $(OUTPUT_ATS_PDF)
	$(PDF_TO_PNG) -png $(OUTPUT_ATS_PDF) > $(OUTPUT_ATS_PNG)

# Clean up auxiliary files created by LaTeX
clean:
	rm -f $(OUTPUT_PDF) $(OUTPUT_ATS_PDF) *.aux *.log *.out *.toc *.lof *.lot $(OUTPUT_PNG) $(OUTPUT_ATS_PNG)

.PHONY: all clean


