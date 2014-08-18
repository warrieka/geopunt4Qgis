# -*- coding: utf-8 -*-
"""
/***************************************************************************
geopunt4QgisGipod
                                A QGIS plugin
"Tool om geopunt in QGIS te gebruiken"
                            -------------------
        begin                : 2013-12-08
        copyright            : (C) 2013 by Kay Warrie
        email                : kaywarrie@gmail.com
***************************************************************************/

/***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************/
"""
from PyQt4 import QtCore, QtGui
from PyQt4.QtGui import QFileDialog, QMessageBox
from ui_geopunt4QgisGIPOD import Ui_gipodDlg
import geopunt, geometryhelper, gipodHelper
import os, json, webbrowser
from  datetime import date, timedelta

class geopunt4QgisGipodDialog(QtGui.QDialog):
    def __init__(self, iface):
        QtGui.QDialog.__init__(self, None)
        self.setWindowFlags( self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint )
        #self.setWindowFlags( self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.iface = iface
        
        # initialize locale
        locale = QtCore.QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(os.path.dirname(__file__), 'i18n', 
                      'geopunt4qgis_{}.qm'.format(locale))
        if os.path.exists(localePath):
            self.translator = QtCore.QTranslator()
            self.translator.load(localePath)
            if QtCore.qVersion() > '4.3.3': 
              QtCore.QCoreApplication.installTranslator(self.translator)
        #load gui
        self._initGui()
    
    def _initGui(self):
        "Set up the user interface"
        self.ui = Ui_gipodDlg()
        self.ui.setupUi(self)
            
        #get settings
        self.s = QtCore.QSettings()
        self.loadSettings()
        
        self.gp = geopunt.gipod(self.timeout, self.proxy, self.port)
        self.gh = geometryhelper.geometryHelper(self.iface)
        
        self.data = None
        
        self.ui.buttonBox.addButton( QtGui.QPushButton("Sluiten"), QtGui.QDialogButtonBox.RejectRole )
        self.ui.buttonBox.addButton( QtGui.QPushButton(
                                QtGui.QIcon(":/plugins/geopunt4Qgis/images/addPointLayer.png" ),
                                "Voeg toe aan kaart"),  QtGui.QDialogButtonBox.AcceptRole )         
        self.firstShow = True
        
        #set calenders 
        now  = date.today()
        self.ui.endEdit.setDate(now + timedelta(30) )
        self.ui.endEdit.setMinimumDate(now)
        self.ui.startEdit.setDate(now)
        self.ui.startEdit.setMaximumDate( self.ui.endEdit.date() )
        
         #eventhandlers
        self.ui.endEdit.dateChanged.connect(self.endEditChanged)
        self.ui.buttonBox.helpRequested.connect(self.openHelp)
        self.ui.provinceCbx.currentIndexChanged.connect(self.provinceChanged)
        self.accepted.connect(self.okClicked )
        self.rejected.connect(self.clean )
      
    def show(self):
      QtGui.QDialog.show(self)
      if  self.firstShow:
        'exend show to load data'
        internet = geopunt.internet_on( proxyUrl=self.proxy, port=self.port, timeout=self.timeout )
        if internet:
            self.gemeentes = json.load( open(os.path.join(os.path.dirname(__file__), "data/gemeentenVL.json")) )
            #populate combo's
            self.ui.provinceCbx.clear()
            self.ui.provinceCbx.addItems(["","Antwerpen","Limburg","Oost-Vlaanderen","Vlaams-Brabant","West-Vlaanderen"])
            self.ui.cityCbx.clear()
            self.ui.cityCbx.addItems([n["Naam"] for n in self.gemeentes])
            self.ui.ownerCbx.clear()
            self.ui.ownerCbx.addItems([""] + self.gp.getOwner())
            self.ui.eventCbx.clear()
            self.ui.eventCbx.addItems([""] + self.gp.getEventType())
            self.ui.mgsBox.setText('')
            self.firstShow = False
        elif not internet:
            self.ui.mgsBox.setText( "<div style='color:red'>%s</div>" %  QtCore.QCoreApplication.translate("geopunt4QgisGIPOD", 
              "<strong>Waarschuwing: </strong>kan niet verbinden met internet"))
    
    def loadSettings(self):
        self.timeout =  int(  self.s.value("geopunt4qgis/timeout" ,15))
        self.saveToFile = int( self.s.value("geopunt4qgis/gipodSavetoFile" , 1))
        self.proxy = self.s.value("geopunt4qgis/proxyHost" ,"")
        self.port = self.s.value("geopunt4qgis/proxyPort" ,"")
        self.startDir = self.s.value("geopunt4qgis/startDir", os.path.dirname(__file__))
    
    def endEditChanged(self, senderDate):
        self.ui.startEdit.setMaximumDate(senderDate)
    
    def okClicked(self):
        name= self.ui.lyrName.text()
        manifestation = self.ui.manifestationRadio.isChecked()
        self.data = self.fetchGIPOD()
        fname, ftype= None , None
        if self.saveToFile:
            fname = gipodHelper.gipodeoHelper.openOutput(self.iface.mainWindow(), 
                                                     os.path.join( self.startDir, name))
            if fname:
              ftype = gipodHelper.gipodeoHelper.checkFtype(fname)
            else:
              self.clean()
              return
          
        if self.data:
           with gipodHelper.gipodWriter( self.iface, name , 31370, manifestation, ftype ) as gipodWriter:
              for row in self.data:
                  xy = row['coordinate']["coordinates"]
                  gipodId = int( row["gipodId"] )
                  owner = row["owner"]
                  description = row["description"]
                  startDateTime = row["startDateTime"]
                  endDateTime = row["endDateTime"]
                  detail= row["detail"]
                  importantHindrance = int( row["importantHindrance"] )
                  cities = row["cities"]
                  if manifestation:
                    initiator = row["initiator"]
                    recurrencePattern = row["recurrencePattern"]
                  else:
                    initiator, recurrencePattern = None, None
                    
                  gipodWriter.writePoint(xy, gipodId, owner, description, startDateTime, endDateTime,
                      importantHindrance, detail, cities, initiator, recurrencePattern )
              if self.saveToFile:
                  gipodWriter.saveGipod2file(fname,ftype)
        else:
            QMessageBox.warning(self,
                    QtCore.QCoreApplication.translate("geopunt4QgisGIPOD", "Waarschuwing"), 
                    QtCore.QCoreApplication.translate("geopunt4QgisGIPOD", 
                        "Deze bevraging had geen resultaten, er werd geen laag aangemaakt"))
        self.clean()
        
    def fetchGIPOD(self):
        owner= self.ui.ownerCbx.currentText()
        eventtype= self.ui.eventCbx.currentText()
        startdate= self.ui.startEdit.date().toPyDate()
        enddate= self.ui.endEdit.date().toPyDate()
        city= self.ui.cityCbx.currentText()
        province= self.ui.provinceCbx.currentText()
        srs=31370
        if self.ui.extendChk.isChecked():
            mapbbox = self.iface.mapCanvas().extent()
            minX, minY = self.gh.prjPtFromMapCrs([mapbbox.xMinimum(), mapbbox.yMinimum()], srs)
            maxX, maxY = self.gh.prjPtFromMapCrs([mapbbox.xMaximum(), mapbbox.yMaximum()], srs)
            bbox = [minX, minY, maxX, maxY]
        else:
            bbox=[]
        if self.ui.workassignmentRadio.isChecked():
            return  self.gp.allWorkassignments(owner, startdate, enddate, city, province, srs, bbox)
        elif self.ui.manifestationRadio.isChecked():
            return self.gp.allManifestations(owner, eventtype, startdate, enddate, city, province, srs, bbox)
   
    def provinceChanged(self):
        provText = self.ui.provinceCbx.currentText()
        if provText == "Antwerpen":
            self.ui.cityCbx.clear()
            self.ui.cityCbx.addItems( [""]  + 
                         [ n["Naam"] for n in self.gemeentes if n["Niscode"].startswith("1") ])
            return 
        if provText == "Limburg":
            self.ui.cityCbx.clear()
            self.ui.cityCbx.addItems( [""]  + 
                         [ n["Naam"] for n in self.gemeentes if n["Niscode"].startswith("7") ])
            return 
        if provText == "Oost-Vlaanderen":
            self.ui.cityCbx.clear()
            self.ui.cityCbx.addItems( [""]  + 
                         [ n["Naam"] for n in self.gemeentes if n["Niscode"].startswith("4") ])
            return 
        if provText == "Vlaams-Brabant":
            self.ui.cityCbx.clear()
            self.ui.cityCbx.addItems( [""] + 
                         [ n["Naam"] for n in self.gemeentes if n["Niscode"].startswith("2") ])
            return 
        if provText == "West-Vlaanderen":
            self.ui.cityCbx.clear()
            self.ui.cityCbx.addItems( [""] + 
                         [ n["Naam"] for n in self.gemeentes if n["Niscode"].startswith("3") ])
            return
        else:
            self.ui.cityCbx.clear()
            self.ui.cityCbx.addItems([ n["Naam"] for n in self.gemeentes ])
   
    def openHelp(self):
        webbrowser.open_new_tab("http://kgis.be/index.html#!geopuntGIPOD.md")
    
    def clean(self):
        self.ui.lyrName.setText("GIPOD")