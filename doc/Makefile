#
# MyPLC documentation
#
# Mark Huang <mlhuang@cs.princeton.edu>
# Copyright (C) 2006 The Trustees of Princeton University
#
# $Id$
#

all: myplc.html

# XML - as opposed to SGML - requires an identifier - see 
# http://www.docbook.org/tdg/en/html/appb.html
# and, openjade opens http connections when using the official URL 
# as an identifier; this is slow, and sometimes fails and breaks the build

# locating locally installed docbook43 dtd - fedora-specific
remote-docbook-43 = http://www.oasis-open.org/docbook/xml/4.3/docbookx.dtd
local-docbook-43 = $(wildcard /usr/share/sgml/docbook/xml-dtd-4.3-*/docbookx.dtd)
docbook-43=$(if $(local-docbook-43),$(local-docbook-43),$(remote-docbook-43))

myplc.xml: myplc.xml.in
	$(if $(local-docbook-43), \
	echo Using locally installed DTD $(local-docbook-43), \
	echo WARNING - could not locate local DTD - using remote $(remote-docbook-43))
	sed -e s:@DOCBOOK-43@:$(docbook-43): $< > $@

# Dependencies
.myplc.xml.valid: architecture.eps architecture.png plc_variables.xml 

plc_variables.xml: variables.xsl ../default_config.xml
	xsltproc $(XSLFLAGS) --output $@ $^

# Validate the XML
.%.xml.valid: %.xml
	xmllint --valid --output $@ $<

# docbook2pdf craps out on figures
%.pdf: %.ps
	ps2pdf $< $@

# Compile it into other formats
FORMATS := dvi html man ps rtf tex texi txt

DOCBOOK2FLAGS := -V biblio-number=1

define docbook2
%.$(1): %.xml .%.xml.valid
	docbook2$(1) --nochunks $$(DOCBOOK2FLAGS) $$<
endef

$(foreach format,$(FORMATS),$(eval $(call docbook2,$(format))))

clean:
	rm -f $(patsubst %,*.%,$(FORMATS)) *.pdf .*.xml.valid plc_variables.xml 

.PHONY: all docclean
