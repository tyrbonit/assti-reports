# -*- coding: utf-8 -*-
from gluon.storage import Storage
from gluon.fileutils import read_file
import os, re
from datetime import datetime, timedelta
from gluon.tools import fetch
from lxml import etree
import copy
from random import random
RE_NS = re.compile(r"(^\w+?):")
NS = Storage(
    ss="urn:schemas-microsoft-com:office:spreadsheet",
    dl="http://www.jgroup.com/2003/Excel/DataLocation",
    sd="http://www.jgroup.com/2003/Excel/SpecialData")

def ns_marker(key, ns=NS):
    if ns:
        key = RE_NS.sub(r"{%(\1)s}", key)
        key = key % ns
    return key


def EL(tag, attrib=None, nsmap=NS):
    tag = ns_marker(tag, nsmap)
    if attrib:
        attrib = {ns_marker(k, nsmap): v for k, v in attrib.items()}
    return etree.Element(tag, attrib=attrib, nsmap=nsmap)

DL_STYLE = ns_marker("dl:style")
DL_ROWINDEX = ns_marker("dl:rowIndex")
DL_CELLINDEX = ns_marker("dl:cellIndex")
DL_FULLROWINDEX = ns_marker("dl:fullRowIndex")
DL_FULLCELLINDEX = ns_marker("dl:fullCellIndex")
DL_OPER = ns_marker("dl:oper")
DL_DATAPOS = ns_marker("dl:datapos")
DL_MULT = ns_marker("dl:mult")
DL_ROUND = ns_marker("dl:round")
SD_NAME = ns_marker("sd:name")
SS_INDEX = ns_marker("ss:Index")
SS_TYPE = ns_marker("ss:Type")
SS_FORMULA = ns_marker("ss:Formula")
SS_HEIGHT = ns_marker("ss:Height")
SS_STYLEID = ns_marker("ss:StyleID")
SS_EXPROWCOUNT = ns_marker("ss:ExpandedRowCount")
SS_D = etree.XPath("ss:Data[1]", namespaces=NS)
SS_DATA = lambda el: SS_D(el)[0]
SS_ROW = lambda el, i: etree.XPath("ss:Row[%d]" % (i+1), namespaces=NS)(el)[0]
SS_ROW_COUNT = etree.XPath("count(ss:Row)", namespaces=NS)
SS_CELL = lambda el, i: etree.XPath("ss:Cell[%d]" % (i+1), namespaces=NS)(el)[0]#etree.XPath("ss:Cell", namespaces=NS)
X_DATA = etree.XPath("//Data/Item", namespaces=NS)


class ASSTIBRIDGE(object):

    def __init__(self, serverurl, reports_path="Reports", schemes_path="Schemes", testdata=False, randomdata=False):
        self.t=datetime.now()
        self.serverURL = serverurl
        self.reports_path = reports_path
        self.schemes_path = schemes_path
        self.request = Storage(vars=Storage())
        self.s_usePrecalc = self.request.vars.dataSave
        self.testdata=testdata
        self.randomdata = randomdata

    def localLoadNewXML(self, fileName, transform=None):
        # fileName is path to xml file, transform is path to xslt scheme
        sXML = etree.parse(fileName)
        if transform:
            xslt_transformer = etree.XSLT(self.localLoadNewXML(transform))
            sXML = xslt_transformer(sXML)
        return sXML

    @staticmethod
    def getLastSmeneTime():
        s_date  = datetime.now()
        s_hours = s_date.hour
        if (s_hours>=20):
            s_deltaHours = s_hours-20
        elif (s_hours<=8):
            s_deltaHours = 24-20+s_hours
        else:
            s_deltaHours = s_hours-8
        s_deltaHours = timedelta(hours=s_deltaHours)
        s_date  = s_date - s_deltaHours
        s_data = "%d.%d.%d %d:00"%(s_date.day, s_date.month, s_date.year, s_date.hour)
        return s_data


    def queryServerData(self, queryString, s_formatedQuery, s_queryFormuls, s_dataType, fromDate, toDate):
        if self.testdata:
            return self.testdata
        self.s_queryString = queryString
        postData, s_addon = Storage(), Storage()
        if s_queryFormuls:
            s_addon.formuls  = s_queryFormuls
        if s_dataType == 'getMirror':
            # connectionString = serverURL+"OSS/bridge/queryData?fromIntervalName=lastSmene&queryString="
            connectionString = self.serverURL + "OSS/bridge/getBataByFormat"
            # connectionString = serverURL + "OSS/fastBridge/queryData"
            postData.query = s_formatedQuery
        else:
            smartScript = self.request.vars.smartReportId
            s_precalcAddon = ""
            if (smartScript == "" or not smartScript or str(smartScript) == "undefined"):
                if (self.s_usePrecalc == "true"): s_precalcAddon = "&precalc=False"
                connectionString = self.serverURL+"OSS/bridge/getArc"
                postData.update(**dict(
                    deltaDateTime=s_dataType,
                    startDate=fromDate,
                    endDate=toDate + s_precalcAddon,
                    queryString=self.s_queryString
                ))
            else:
                if (self.s_usePrecalc == "true"): s_precalcAddon = "&precalc=False"
                connectionString = self.serverURL+"OSS/smartQuery"
                postData.update(**dict(
                    script_name=smartScript,
                    deltaDateTime=s_dataType,
                    startDate=fromDate,
                    endDate=toDate + s_precalcAddon,
                    queryString=self.s_queryString
                ))

        # Response.Write(connectionString + "?" + postData + s_addon)
        # Response.End()
        postData.update(**s_addon)
        http = fetch(connectionString, postData)
        return http

    def queryData(self, reportId, s_dataType, fromDate, toDate):
        xmlExcelTemplate = self.localLoadNewXML(
            os.path.join(self.reports_path, "Template_" + reportId),
            os.path.join(self.schemes_path, "queryData.xsl")
        )
        # query data
        s_nodes = xmlExcelTemplate.xpath("//*/Item")
        if not s_nodes:
            return # TODO 'log error - no data'
        #sdataXML = etree.parse("")
        #sdataXML.setProperty("SelectionNamespaces",'xmlns:sd="http://www.jgroup.com/2003/Excel/SpecialData" xmlns:dl="http://www.jgroup.com/2003/Excel/DataLocation"')

        for i in range(len(s_nodes)):
            s_node = s_nodes[i]
            s_queryString = s_node.get("queryString")
            s_queryFormuls = s_node.get("queryFormuls")
            s_formatedQuery = etree.tostring(xmlExcelTemplate.xpath("/*/formatedQuery[1]")[0])
            #print etree.tostring(xmlExcelTemplate)
            #print etree.tostring(s_formatedQuery)
            s_liteFormatedQuery = etree.tostring(xmlExcelTemplate.xpath("/*/liteFormatedQuery[1]")[0])
            if i > 0:
                s_dataType = s_node.get("dataType")
                fromDate   = s_node.get("startTime")
                if fromDate == 'lastSmene':
                    fromDate = self.getLastSmeneTime()
                toDate = fromDate

            s_result = self.queryServerData(s_queryString, s_formatedQuery, s_queryFormuls, s_dataType, fromDate, toDate)
            if s_dataType == 'getMirror':
                return etree.fromstring(s_result)
                # s_schemePath = os.path.join(self.schemes_path, "Cur_OSS2Excel.xsl")
            else:
                s_schemePath = os.path.join(self.schemes_path, "Arc_OSS2Excel.xsl")

            s_tempXML = etree.fromstring(s_result)
            s_tempXSL = etree.XSLT(self.localLoadNewXML(s_schemePath))
            s_result = s_tempXSL(s_tempXML)

            if i == 0:
                sXML = s_result
            else:
                sdataXML = s_result
                s_destnodes = sXML.xpath("//*/Item")
                s_srcnodes = sdataXML.xpath("//*/Item")
                if s_destnodes and s_srcnodes:
                    for ii in range(len(s_destnodes)):
                        if ii < len(s_srcnodes):
                            s_srcnode = s_srcnodes[ii]
                            childNodes = s_srcnode.getchildren()
                            for j in range(len(childNodes) - 1, 0, -1):
                                childNodes[j].set("dataType", s_dataType)
                                s_destnodes[ii].append(childNodes[j])
                        else:
                            break
        return sXML

    def initReport(self):
        excelXML = self.excelXML
        # create error style - red color
        s_excelStyles = excelXML.xpath("//ss:Workbook/ss:Styles[1]", namespaces=NS)[0]
        # Error Color
        s_newStyle = EL("ss:Style", {"ss:ID": "sErrorItem"})
        s_interior = EL("ss:Interior", {
            "ss:Color": "#FF0000",
            "ss:Pattern": "DiagCross",
            "ss:PatternColor": "#FFFFFF"})
        s_newStyle.append(s_interior)
        s_excelStyles.append(s_newStyle)

        # HandMake Color
        s_newStyle = EL("ss:Style", {"ss:ID": "sHandMake"})
        s_interior = EL("ss:Interior",
                        {"ss:Color": "#F5F5DC",
                         "ss:Pattern": "DiagCross",
                         "ss:PatternColor": "#FFFFFF",
                         })
        s_borders = EL("ss:Borders")
        s_borderRight = EL("ss:Border", {
            "ss:Position": "Right",
            "ss:LineStyle": "Continuous",
            "ss:Weight": "1.0"})

        s_borderBottom = EL("ss:Border", {
            "ss:Position": "Bottom",
            "ss:LineStyle": "Continuous",
            "ss:Weight": "1.0"})
        s_borders.append(s_borderRight)
        s_borders.append(s_borderBottom)
        s_newStyle.append(s_borders)

        """<ss:Borders><ss:Border ss:Position="Right" ss:LineStyle="Continuous" ss:Weight="1.0" />
        <ss:Border ss:Position="Bottom" ss:LineStyle="Continuous" ss:Weight="1.0" />
        </ss:Borders>"""
        s_newStyle.append(s_interior)
        s_excelStyles.append(s_newStyle)

    def prepareString(self, s_mapItem):
        """ готовит xpath строку запроса по атрибутам типа [@type='a' and @x='z']"""
        sd_ns = "{%s}" % NS.sd
        s_sdNs_nodes = ["@%s='%s'" % (k.replace(sd_ns, ""), v) for k, v in s_mapItem.attrib.items() if sd_ns in k and SD_NAME not in k]
        s_value = "[%s]" % (" and ".join(s_sdNs_nodes)) if s_sdNs_nodes else ""
        # print s_value
        return s_value

    def callFunction(self, s_row, s_cell, s_count, s_number, s_mapItem):
        s_function = s_mapItem.get("func")
        if (s_function == 'number'):
            s_cell.xpath("ss:Data[1]")[0].text = s_number + 1
            # s_cell.selectSingleNode("ss:Data").setAttribute("ss:Type", "Number")
            return True
        return False

    def reindexExcelXML(self, s_excelItem, startIndex, deltaRow):
        for i in range(deltaRow):
            # клонировать мы должны предыдущий узел и копировать как текущий
            s_rowNodePrev = SS_ROW(s_excelItem, startIndex)
            s_rowNodePrevClone = copy.deepcopy(s_rowNodePrev)
            # print len(s_excelItem.xpath(SS_ROW)), startIndex
            beforeChild = None
            attr_indx = SS_INDEX
            #print SS_ROW_COUNT(s_excelItem)
            if SS_ROW_COUNT(s_excelItem) > startIndex:
                beforeChild = SS_ROW(s_excelItem, startIndex) # [startIndex + 1]
                prnt=s_rowNodePrev.getparent()
                prnt.insert(prnt.index(beforeChild), s_rowNodePrevClone)
                # print s_rowNodePrevClone.attrib
            try:
                del s_rowNodePrevClone.attrib[attr_indx]
            except KeyError:
                pass

        s_nodes = s_excelItem.xpath("ss:Row[position()>%d]" % (startIndex+1), namespaces=NS)
        for s_node in s_nodes:
            currentIndex = s_node.get(SS_INDEX)
            if currentIndex:
                s_node.set(SS_INDEX, str(int(currentIndex) + deltaRow))

    def findValue(self, s_dataItems):
        global s_mapItem, s_dataItem  # ?????
        s_sdNs_nodes = s_dataItem.xpath("sd:@*", namespaces=NS)
        for i in range(len(s_sdNs_nodes)):
            s_value = s_dataItems[i].get(s_mapItem.get(SD_NAME))

    def getValueNode(self, s_dataItem, s_dataName, s_requestString):
        if s_dataItem is None:
            return None
        # s_dataName + s_requestString - xpath строка запроса вида tag123456789987[@type='a']
        s_node = s_dataItem.xpath(s_dataName + s_requestString, namespaces=NS)
        if s_node:
            return s_node[0]
        return None

    def makeFormala(self, s_row, s_cell, s_count, s_mapItem):
        if s_cell is None:
            return
        s_function = s_mapItem.get("func")

        if not s_count and s_function:
            SS_DATA(s_cell).text = "0"
        elif s_function == 'sum':
            s_cell.set(SS_FORMULA, "=SUM(R[-" + s_count + "]C:R[-1]C)")
        elif s_function == 'avg':
            s_cell.set(SS_FORMULA, "=AVERAGE(R[-" + s_count + "]C:R[-1]C)")
        else:
            s_bottom = s_mapItem.get("bottom")
            if not s_bottom:
                s_bottom = ""
            # print etree.tostring(s_cell)
                SS_DATA(s_cell).text = s_bottom

            if s_bottom == "hidden":
                s_cell.parentNode.set(SS_HEIGHT, "0")

    def CharIn(self, chr):
        return chr in "-1234567890,."

    def roundNumber(self, s_value, s_round):
        if (s_round == None):
            return s_value
        ext = int(s_round) ** 10

        s_value = float(s_value)
        s_value = s_value * ext
        s_value = round(s_value)
        s_value = s_value / ext
        return s_value

    def isNumber(self, s_string):
        if not s_string:
            return False
        s_checkString = str(s_string)
        pointerCount = 0
        for i in range(len(s_checkString)):
            currentChar = s_checkString[i]
            if currentChar == '.' or currentChar == ',':
                pointerCount += 1
                if pointerCount > 1:
                    return False
                continue
            if (self.CharIn(currentChar) == False):
                return False
        return True

    def makeReport(self, dataXML):
        """
        excelXML as MSXML DOMDocument object - Шаблон отчета в формате XML-excel,
        mapXML as MSXML DOMDocument object - карта расположения Тэгов,
        dataXML as MSXML DOMDocument object - значения тэгов (<Data><Item><tagname>value</tagname>...</Item></Data>)
        """

        #self.mapXML.register_namespace(sd='{http://www.jgroup.com/2003/Excel/SpecialData}', dl='{http://www.jgroup.com/2003/Excel/DataLocation}')
        self.initReport()
        worksheets = self.excelXML.xpath("//ss:Workbook/ss:Worksheet", namespaces=NS)
        s_dataItems = dataXML.xpath("//*/Item")
        n_data = len(s_dataItems)

        for w, ws_item in enumerate(worksheets, 1):
            s_excelItem = ws_item.xpath("ss:Table[1]", namespaces=NS)
            if s_excelItem:
                s_excelItem = s_excelItem[0]
            else:
                continue
            # s_rowsCount = len(s_excelItem.xpath(SS_ROW))
            s_mapItems = self.mapXML.xpath("//*/Item[not(@ws) or @ws='1']") if w == 1 else self.mapXML.xpath("//*/Item[@ws='%d']"%w)
            s_lastInsertRow = -1
            s_deltaRow = 0
            for s_mapItem in s_mapItems:
                s_mapItemRange = str(s_mapItem.get(DL_STYLE)) == 'table'
                s_lastData = str(s_mapItem.get(DL_DATAPOS))
                s_rowIndex = int(s_mapItem.get(DL_ROWINDEX)) + s_deltaRow - 1
                s_cellIndex = int(s_mapItem.get(DL_CELLINDEX)) - 1
                s_rowIndex1 = s_rowIndex
                s_requestString = self.prepareString(s_mapItem)  # xpath строка запроса вида [@type='a']
                s_increase = str(s_mapItem.get(DL_OPER)) == 'inc'
                s_dataCount = 0
                # s_insertFlag = False

                if s_mapItemRange:
                    s_dataCount = n_data - 1

                    if s_lastInsertRow < s_rowIndex:
                        # s_insertFlag = True
                        s_lastInsertRow = s_rowIndex
                        s_lastInsertRow += s_dataCount + 2

                        self.reindexExcelXML(s_excelItem, s_rowIndex, s_dataCount + 1)
                        s_deltaRow += s_dataCount + 1
                    else:
                        s_rowIndex1 -= s_dataCount + 1

                addon = 2 if s_mapItemRange else 1
                s_prevValue = 0
                for j in xrange(s_dataCount + addon):
                    s_rowIndex = s_rowIndex1 + j
                    #print etree.tostring(s_excelItem)
                    s_rowNode = SS_ROW(s_excelItem, s_rowIndex)
                    s_cellNode = SS_CELL(s_rowNode, s_cellIndex)

                    if j < s_dataCount + 1:
                        if (self.callFunction(s_rowNode, s_cellNode, s_dataCount + 1, j, s_mapItem) == True):
                            continue

                        s_value = None
                        s_valueType = ""


                        # -------- start ------------
                        dataPosition = j
                        if s_mapItemRange is not True: dataPosition = 0
                        if s_lastData == 'last': dataPosition = n_data - 1
                        if s_lastData == 'first': dataPosition = 0
                        s_valueNode = self.getValueNode(
                            s_dataItems[dataPosition],
                            s_mapItem.get(SD_NAME),
                            s_requestString
                        )

                        # -------- end ------------
                        if s_valueNode is not None:
                            s_value = s_valueNode.text
                            s_valueType = s_valueNode.get("type")

                        if (not s_value and s_cellNode is not None):
                            s_cellNode.set(SS_STYLEID, "sErrorItem")
                            s_value = ""

                        if (s_valueType == "hand"):
                            s_cellNode.set(SS_STYLEID, "sHandMake")

                        if s_cellNode is not None:
                            data_cell = SS_DATA(s_cellNode)
                            if self.isNumber(s_value):
                                data_cell.set(SS_TYPE, "Number")
                                # multiplicator
                                s_mult = s_mapItem.get(DL_MULT)
                                if s_mult is not None and self.isNumber(s_mult):
                                    s_value = float(s_value) * float(s_mult)

                                s_prevValue += float(s_value)

                                if s_increase is True:
                                    s_data = self.roundNumber(s_prevValue, s_mapItem.get(DL_ROUND))
                                    data_cell.text = str(s_data)
                                else:
                                    s_data = self.roundNumber(s_value, s_mapItem.get(DL_ROUND))
                                    data_cell.text = str(s_data)
                            else:
                                SS_DATA(s_cellNode).text = s_value
                    else:
                        self.makeFormala(s_rowNode, s_cellNode, s_dataCount + 1, s_mapItem)
            s_rowsCount = int(s_excelItem.get(SS_EXPROWCOUNT))
            s_excelItem.set(SS_EXPROWCOUNT, str(s_rowsCount + s_deltaRow))

    def get_mirror_map(self):
        XMLScheme = self.mapXML
        s_nodes = X_DATA(XMLScheme)
        sd_ns = "{%s}" % NS.sd
        for currentNode in s_nodes:
            s_tag_id = currentNode.get("tagID")
            queryAddon = ""  # "".join([" and @%s='%s'" % (k.replace(sd_ns, ""), v) for k, v in currentNode.attrib.items() if sd_ns in k  and SD_NAME not in k])
            xpath = "object[@id='%s'%s][1]/value/text()" % (s_tag_id, queryAddon)
            s_row = int(currentNode.get(DL_FULLROWINDEX))
            s_cell = int(currentNode.get(DL_FULLCELLINDEX))
            yield Storage(tag=s_tag_id, xpath=xpath, row=s_row, cell=s_cell, )

    def get_mirror_data(self, XMLData=None):
        def get_value(xpath):
            s_value = XMLData.xpath(xpath)
            return s_value[0] if s_value else None

        if self.randomdata:
                get_value = lambda x: 100.0 * random()
        tag_map = self.get_mirror_map()
        return [(x.row, x.cell, get_value(x.xpath)) for x in tag_map]

    def getreport(self, ReportID, type, fromDate=None, toDate=None):
        dataXML = self.queryData(ReportID, type, fromDate, toDate)
        # print etree.tostring(dataXML)
        # print datetime.now() - self.t
        if dataXML.xpath("//result[1]/@type"):
            if dataXML.xpath("//result[1]/@type")[0].text == 'error':
                return
        self.mapXML = self.localLoadNewXML(os.path.join(self.reports_path, "Template_" + ReportID))
        if type == 'getMirror':
            return self.get_mirror_data(dataXML)
        self.excelXML = self.localLoadNewXML(os.path.join(self.reports_path, ReportID))
        #reportParamsXML = self.localLoadNewXML("data\\report_params.xml")
        self.makeReport(dataXML)
        return etree.tostring(self.excelXML, xml_declaration=True)
