RSTFILES=robiphora.rst
43PDFFILES=$(patsubst %.rst,out/%-43.pdf,$(RSTFILES))
169PDFFILES=$(patsubst %.rst,out/%-169.pdf,$(RSTFILES))
1610PDFFILES=$(patsubst %.rst,out/%-1610.pdf,$(RSTFILES))

R2BOPTIONS=--theme=csam

.PHONY: all
all: $(169PDFFILES)

out:
	mkdir -p out

out/%.pdf: %.tex beamerthemecsam.sty | out
	xelatex $<
	mv $(patsubst out/%.pdf,%.pdf,$@) out
	rm -f $(patsubst out/%.pdf,%.log,$@) \
	      $(patsubst out/%.pdf,%.aux,$@) \
	      $(patsubst out/%.pdf,%.nav,$@) \
	      $(patsubst out/%.pdf,%.out,$@) \
	      $(patsubst out/%.pdf,%.snm,$@) \
	      $(patsubst out/%.pdf,%.toc,$@) \
	      $(patsubst out/%.pdf,%.vrb,$@)

%-43.tex: %.rst
	rst2beamer $(R2BOPTIONS) --template=xelatex.tex --documentoptions="aspectratio=43" $< > $@

%-169.tex: %.rst
	rst2beamer $(R2BOPTIONS) --template=xelatex.tex --documentoptions="aspectratio=169" $< > $@

%-1610.tex: %.rst
	rst2beamer $(R2BOPTIONS) --template=xelatex.tex --documentoptions="aspectratio=1610" $< > $@
