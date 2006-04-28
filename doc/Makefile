#
# MyPLC documentation
#
# Mark Huang <mlhuang@cs.princeton.edu>
# Copyright (C) 2006 The Trustees of Princeton University
#
# $Id: Makefile,v 1.3 2006/04/24 22:14:56 mlhuang Exp $
#

vpath GenDoc.xsl ../../plc_www/doc
vpath plc_config.xml ..

all: myplc.pdf myplc.php

# Dependencies
.myplc.xml.valid: architecture.eps architecture.png variables.xml

variables.xml: variables.xsl plc_config.xml
	xsltproc $(XSLFLAGS) --output $@ $^

# Validate the XML
.%.xml.valid: %.xml
	xmllint --valid --output $@ $<

# Compile it into other formats
FORMATS := dvi html man ps rtf tex texi txt

DOCBOOK2FLAGS := -V biblio-number=1

define docbook2
%.$(1): %.xml .%.xml.valid
	docbook2$(1) --nochunks $$(DOCBOOK2FLAGS) $$<
endef

# docbook2pdf craps out on figures
%.pdf: %.ps
	ps2pdf $< $@

# PHP for the website
%.php: GenDoc.xsl .%.xml.valid
	xsltproc $(XSLFLAGS) --output $@ $^

$(foreach format,$(FORMATS),$(eval $(call docbook2,$(format))))

docclean:
	rm -f $(patsubst %,*.%,$(FORMATS)) *.pdf .*.xml.valid variables.xml

clean: docclean

.PHONY: docclean
