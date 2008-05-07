<?xml version="1.0" encoding="UTF-8"?>

<!--
PLC configuration file-to-DocBook conversion stylesheet

Mark Huang <mlhuang@cs.princeton.edu>
Copyright (C) 2006 The Trustees of Princeton University

$Id$
-->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version='1.0'>

  <xsl:output omit-xml-declaration="yes" encoding="UTF-8" indent="yes" />

  <xsl:template match="/">

    <xsl:for-each select="configuration/variables/category">
      <xsl:variable name="category_id" select="translate(@id,
					       'abcdefghijklmnopqrstuvwxyz',
					       'ABCDEFGHIJKLMNOPQRSTUVWXYZ')" />
      <xsl:variable name="category_desc" select="description" />
      <section>
	<title> 
	  Category 
	  <filename><xsl:value-of select="$category_id" /> </filename>
	</title>
	<para> 
	  <xsl:value-of select="$category_desc" /> 
	</para>
	<variablelist> 
	  <xsl:for-each select="variablelist/variable">
	    <xsl:variable name="variable_id" select="translate(@id,
						     'abcdefghijklmnopqrstuvwxyz',
						     'ABCDEFGHIJKLMNOPQRSTUVWXYZ')" />
	    <varlistentry>
	      <term>
		<filename>
		  <xsl:value-of select="$category_id" />_<xsl:value-of select="$variable_id" />
		</filename>
		(Default:<filename><xsl:value-of select="value" /></filename>)
	      </term>
	      <listitem>
		<para>
		  <xsl:value-of select="description" />
		</para>
	      </listitem>
	    </varlistentry>
	  </xsl:for-each>
	</variablelist>
      </section>
    </xsl:for-each>
  </xsl:template>

</xsl:stylesheet>
