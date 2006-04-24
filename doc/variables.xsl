<?xml version="1.0" encoding="UTF-8"?>

<!--
PLC configuration file-to-DocBook conversion stylesheet

Mark Huang <mlhuang@cs.princeton.edu>
Copyright (C) 2006 The Trustees of Princeton University

$Id: GenDoc.xsl,v 1.8 2005/10/10 17:46:36 mlhuang Exp $
-->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version='1.0'>

<xsl:output omit-xml-declaration="yes" encoding="UTF-8" indent="yes" />

<xsl:template match="/">

  <variablelist>
	<xsl:for-each select="configuration/variables/category">
	  <xsl:variable name="category_id" select="translate(@id,
						   'abcdefghijklmnopqrstuvwxyz',
						   'ABCDEFGHIJKLMNOPQRSTUVWXYZ')" />
	  <xsl:for-each select="variablelist/variable">
	    <xsl:variable name="variable_id" select="translate(@id,
						     'abcdefghijklmnopqrstuvwxyz',
						     'ABCDEFGHIJKLMNOPQRSTUVWXYZ')" />
	    <varlistentry>
	      <term>
		<xsl:value-of select="$category_id" />_<xsl:value-of select="$variable_id" />
	      </term>
	      <listitem>
		<para>
		  Type: <xsl:value-of select="@type" />
		</para>
		<para>
		  Default: <xsl:value-of select="value" />
		</para>
		<para>
		  <xsl:value-of select="description" />
		</para>
	      </listitem>
	    </varlistentry>
	  </xsl:for-each>
	</xsl:for-each>

    </variablelist>

</xsl:template>

</xsl:stylesheet>
