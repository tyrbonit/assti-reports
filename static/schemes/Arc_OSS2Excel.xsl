<?xml version="1.0"?>
<xsl:stylesheet
   xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
   version="1.0">

<xsl:output method="xml"/>

<xsl:key name="filter" match="rectime" use="."/>

<xsl:template match="/">
  <Data>
    <xsl:for-each select="//objects/object[generate-id(rectime)=generate-id(key('filter',rectime))]">
      <Item>
        <rectime><xsl:value-of select="rectime"/></rectime>
        <tagdate><xsl:value-of select="substring-before(rectime,' ')"/></tagdate>
        <tagtime><xsl:value-of select="substring-after(rectime,' ')"/></tagtime>

        <rectime><xsl:value-of select="fromtime"/></rectime>
        <tagfromdate><xsl:value-of select="substring-before(fromtime,' ')"/></tagfromdate>
        <tagfromtime><xsl:value-of select="substring-after(fromtime,' ')"/></tagfromtime>

        <xsl:variable name="rectime"><xsl:value-of select="rectime"/></xsl:variable>
        <xsl:for-each select="//objects/object[rectime=$rectime]">
          <xsl:variable name="tagName">tag<xsl:value-of select="id"/></xsl:variable>
          <xsl:for-each select="value">
            <xsl:element name="{$tagName}">

               <xsl:for-each select="@*">
                  <xsl:attribute name="{name(.)}">
                   <xsl:value-of select="."/>
                </xsl:attribute>


              </xsl:for-each>

              <xsl:value-of select="."/>

            </xsl:element>
          </xsl:for-each>
        </xsl:for-each>
      </Item>
    </xsl:for-each>
  </Data>
</xsl:template>

</xsl:stylesheet>

