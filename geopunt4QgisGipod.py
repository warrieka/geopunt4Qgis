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
from builtins import str
from qgis.PyQt.QtCore import Qt, QSettings, QTranslator, QCoreApplication 
from qgis.PyQt.QtWidgets import QDialog, QPushButton, QDialogButtonBox, QMessageBox
from qgis.PyQt.QtGui import QIcon
from .ui_geopunt4QgisGIPOD import Ui_gipodDlg
import os, json, webbrowser, sys
from .geopunt import  gipod, internet_on
from .tools.geometry import geometryHelper
from .tools.gipod import gipodHelper, gipodWriter
from .tools.settings import settings
from datetime import date, timedelta
from urllib.error import HTTPError

class geopunt4QgisGipodDialog(QDialog):
    def __init__(self, iface):
        QDialog.__init__(self, None)
        self.setWindowFlags( self.windowFlags() & ~Qt.WindowContextHelpButtonHint )

        self.iface = iface
        
        # initialize locale
        locale = QSettings().value("locale/userLocale", "en")
        if not locale: locale == 'en'
        else: locale = locale[0:2]
        localePath = os.path.join(os.path.dirname(__file__), 'i18n', 'geopunt4qgis_{}.qm'.format(locale))
        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)
            QCoreApplication.installTranslator(self.translator)
        self._initGui()
    
    def _initGui(self):
        "Set up the user interface"
        self.ui = Ui_gipodDlg()
        self.ui.setupUi(self)
            
        #get settings
        self.s = QSettings()
        self.loadSettings()

        self.gh = geometryHelper(self.iface)
        
        self.data = None
        
        self.ui.buttonBox.addButton( QPushButton("Sluiten"), QDialogButtonBox.RejectRole )
        self.ui.buttonBox.addButton( QPushButton( QIcon(":/plugins/geopunt4Qgis/images/addPointLayer.png" ),
                                                  "Voeg toe aan kaart"),  QDialogButtonBox.AcceptRole )         
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
    
    def loadSettings(self):
        self.timeout =  int(  self.s.value("geopunt4qgis/timeout" ,15))
        self.saveToFile = int( self.s.value("geopunt4qgis/gipodSavetoFile" , 1))

        s = settings()
        self.proxy = s.proxyUrl
        self.proxyInfo = s.proxyInfo

        self.startDir = self.s.value("geopunt4qgis/startDir", os.path.expanduser("~") )        
        self.gp = gipod(self.timeout, self.proxy)
    

    def show(self):
      QDialog.show(self)
      QMessageBox.question(self.iface.mainWindow(), "DEBUG", str(self.proxyInfo), QMessageBox.Ok ) 

      if  self.firstShow:
        try:
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
        except HTTPError:
            self.ui.mgsBox.setText( "<div style='color:red'>%s</div>" %  QCoreApplication.translate("geopunt4QgisGIPOD", 
              "<strong>Waarschuwing: </strong>kan niet verbinden met internet"))

    def endEditChanged(self, senderDate):
        self.ui.startEdit.setMaximumDate(senderDate)
    
    def okClicked(self):
        name= self.ui.lyrName.text()
        manifestation = self.ui.manifestationRadio.isChecked()
        self.data = self.fetchGIPOD()
          
        if self.data:
           fname, ftype= None , None
           if self.saveToFile:
              fname = gipodHelper.openOutput(self.iface.mainWindow(), os.path.join( self.startDir, name))
              if fname:
                ftype = gipodHelper.checkFtype(fname)
                if ftype == None:
                   ftype = "ESRI Shapefile"
              else:
                self.clean()
                return
              
           with gipodWriter( self.iface, name , 31370, manifestation, ftype ) as gipodOut:
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
                    
                  gipodOut.writePoint(xy, gipodId, owner, description, startDateTime, endDateTime,
                      importantHindrance, detail, cities, initiator, recurrencePattern )
              if self.saveToFile:
                  gipodOut.saveGipod2file(fname,ftype)
        else:
            QMessageBox.warning(self,
                    QCoreApplication.translate("geopunt4QgisGIPOD", "Waarschuwing"), 
                    QCoreApplication.translate("geopunt4QgisGIPOD", 
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
        try:
           if self.ui.workassignmentRadio.isChecked():
              return  self.gp.allWorkassignments(owner, startdate, enddate, city, province, srs, bbox)
           elif self.ui.manifestationRadio.isChecked():
              return self.gp.allManifestations(owner, eventtype, startdate, enddate, city, province, srs, bbox)
        except:      
           self.ui.mgsBox.setText( 
             "<div style='color:red'>%s</div>" % str( sys.exc_info()[1]) )
           return 
   
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
        webbrowser.open_new_tab("http://www.geopunt.be/voor-experts/geopunt-plug-ins/functionaliteiten/gipod")
    
    def clean(self):
        self.ui.lyrName.setText("GIPOD")
