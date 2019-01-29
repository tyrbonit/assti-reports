# -*- coding: utf-8 -*-
from cStringIO import StringIO
from gluon.fileutils import read_file
from gluon.storage import Storage
import os, re

def index():
    return dict()

bridge.testdata = read_file("C:\\YandexDisk\\PycharmProjects\\asstireports\\responsepage268.xml")

def report():
    args = request.args
    if args:
        response.headers['Content-Type'] = 'text/xml'
        param = Storage(request.vars)
        if args[0] == 'view':
            stream = StringIO(
                re.sub("\$\$tag[^<>]+", "",
                       read_file(os.path.join(request.folder, 'static', 'reports', request.args[1]))
                      ))
        elif args[0] == 'load':
            stream = StringIO(bridge.getreport(args[1], param.type, param.startdate, param.enddate))
        else:
            stream = StringIO(read_file(os.path.join(request.folder, 'static', 'reports', request.args[1])))

        if param.htmldata:
            import win32com.client as wc
            xlApp = wc.Dispatch('OWC11.Spreadsheet.11')
            xlApp.DataType = "XMLData"
            xlApp.load(stream.getvalue())
            return StringIO(xlApp.HTMLData).getvalue()
        else:
            return stream.getvalue()
    else:
        return "None"

@cache.action(time_expire=300, cache_model=cache.ram, quick='SVP')
def htmlreport():
    return XML(bridge.getreport("page268.xml", "10", "23.12.2018 07:50:00", "23.12.2018 07:51:00"))
    import win32com.client as wc
    xlApp = wc.Dispatch('OWC11.Spreadsheet.11')
    xlApp.DataType = "XMLURL"
    xlApp.XMLURL = "http://127.0.0.1:8000/reports/page/report/view/page203.xml"
    return xlApp.HTMLData

def getmirror():
    if request.args:
        bridge.randomdata=True
        return response.json(bridge.getreport(request.args[0], "getMirror"))
    else:
        return response.json(dict(error="No report id"))
