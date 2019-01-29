<?xml version="1.0" ?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:sd="http://www.jgroup.com/2003/Excel/SpecialData"
    xmlns:dl="http://www.jgroup.com/2003/Excel/DataLocation"
    version="1.0">

    <xsl:output method="xml"/>
    <xsl:key name="filter" match="Item" use="@sd:dataType" />
    <xsl:template match="/">
        <Data>
            <xsl:variable name="queryItems">
                <xsl:text>select [*] from Objects[@id in(</xsl:text>
                <xsl:for-each select="//Data/Item[string(@sd:dataType)='']">
                    <xsl:if test="position()>1">,</xsl:if>
                    <xsl:text>'</xsl:text>
                    <xsl:value-of select="@tagID" />
                    <xsl:text>'</xsl:text>
                </xsl:for-each>
                <xsl:text>)]</xsl:text>
            </xsl:variable>

            <xsl:variable name="queryFormuls">
                <xsl:for-each select="//Data/Item[@dl:formul]">
                    <xsl:if test="position()>1">,</xsl:if>
                    <xsl:value-of select="@tagID" />
                    <xsl:text>=</xsl:text>
                    <xsl:value-of select="@dl:formul" />
                </xsl:for-each>
            </xsl:variable>

            <Item queryString='{$queryItems}' queryFormuls='{$queryFormuls}'/>
            <xsl:for-each select="//Data/Item[@sd:dataType and generate-id(.)=generate-id(key('filter',@sd:dataType))]">
                <xsl:variable name="queryItemsEx">
                    <xsl:text>select [*] from Objects[@id in(</xsl:text>
                    <xsl:variable name="sArchiveType" select="@sd:dataType" />
                    <xsl:for-each select="//Data/Item[@sd:dataType = $sArchiveType]">
                        <xsl:if test="position()>1">,</xsl:if>
                        <xsl:text>'</xsl:text>
                        <xsl:value-of select="@tagID" />
                        <xsl:text>'</xsl:text>
                    </xsl:for-each>
                    <xsl:text>)]</xsl:text>
                </xsl:variable>
                <Item dataType='{@sd:dataType}' startTime='{@dl:startTime}' queryString='{$queryItemsEx}' />
            </xsl:for-each>

            <formatedQuery>
                <xsl:for-each select="//Data/Item[string(@sd:dataType)='']">
                    <item id="{@tagID}">
                        <xsl:if test="@sd:specFrom">
                            <xsl:attribute name="specFrom">
                                <xsl:value-of select="@sd:specFrom"/>
                            </xsl:attribute>

                            <xsl:if test="@sd:specTo">
                                <xsl:attribute name="specTo">
                                    <xsl:value-of select="@sd:specTo"/>
                                </xsl:attribute>
                            </xsl:if>

                        </xsl:if>
                    </item>
                </xsl:for-each>
            </formatedQuery>

            <!-- query without items with spec -->
            <liteFormatedQuery>
                <xsl:for-each select="//Data/Item[string(@sd:dataType)='']">
                    <xsl:if test="not(@sd:specFrom)">
                        <item id="{@tagID}"/>
                    </xsl:if>
                </xsl:for-each>
            </liteFormatedQuery>

        </Data>
    </xsl:template>
</xsl:stylesheet>


