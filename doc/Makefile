# Makefile

%.pdf: %.md
	pandoc --include-in-header helvet.tex \
	  -fmarkdown-implicit_figures \
	  -V 'mainfont=Helvetica' \
	  -V 'geometry: margin=3cm' \
	  $*.md \
	  -o $*.pdf

# ----------------------------------------------------------------------

all:	README.pdf

clean:
	rm -rf *~ */*~ __pycache__ */__pycache__ data

# eof
