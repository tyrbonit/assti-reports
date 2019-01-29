<?xml version="1.0"?>
<xsl:stylesheet
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"  version="1.0">

    <xsl:output method="xml"/>
    <xsl:key name="filter" match="object" use="rectime" />

    <xsl:template match="/">
        <Data>
            <Item>
                <xsl:for-each select="//*/object[not(specTo)]">
                    <xsl:variable name="ItemName">tag<xsl:value-of select="@id"/></xsl:variable>
                    <xsl:element name="{$ItemName}">
                        <xsl:for-each select="*">
                            <xsl:attribute name="{name()}"><xsl:value-of select="."/></xsl:attribute>
                        </xsl:for-each>
                        <xsl:value-of select="value"/>
                    </xsl:element>
                </xsl:for-each>
            </Item>

            <xsl:for-each select="/*/object[specTo and generate-id(.)=generate-id(key('filter',rectime))]">
                <Item>
                    <rectime><xsl:value-of select="rectime"/></rectime>
                    <tagdate><xsl:value-of select="substring-before(rectime,' ')"/></tagdate>
                    <tagtime><xsl:value-of select="substring-after(rectime,' ')"/></tagtime>

                    <tagfromdate><xsl:value-of select="substring-before(fromtime,' ')"/></tagfromdate>
                    <tagfromtime><xsl:value-of select="substring-after(fromtime,' ')"/></tagfromtime>

                    <xsl:variable name="curRT"><xsl:value-of select="rectime"/></xsl:variable>
                    <xsl:for-each select="/*/object[$curRT=rectime]">
                        <xsl:variable name="ItemName">tag<xsl:value-of select="@id"/></xsl:variable>
                        <xsl:element name="{$ItemName}">
                            <xsl:for-each select="*">
                                <xsl:attribute name="{name()}"><xsl:value-of select="."/></xsl:attribute>
                            </xsl:for-each>
                            <xsl:value-of select="value"/>
                        </xsl:element>
                    </xsl:for-each>
                </Item>
            </xsl:for-each>

        </Data>
    </xsl:template>
</xsl:stylesheet>

