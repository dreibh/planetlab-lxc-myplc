#
# MyPLC documentation
#
# Mark Huang <mlhuang@cs.princeton.edu>
# Copyright (C) 2006 The Trustees of Princeton University
#
# $Id: Makefile,v 1.4 2006/04/28 20:16:04 mlhuang Exp $
#

vpath GenDoc.xsl ../../plc_www/doc
vpath %_config.xml ..

all: myplc.pdf myplc.php

# Dependencies
.myplc.xml.valid: architecture.eps architecture.png plc_variables.xml plc_devel_variables.xml

%_variables.xml: variables.xsl %_config.xml
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
