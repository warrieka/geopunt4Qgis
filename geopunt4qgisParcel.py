# -*- coding: utf-8 -*-
"""
/***************************************************************************
geopunt4qgisdialog
                A QGIS plugin
"Tool om geopunt in QGIS te gebruiken"
                -------------------
    begin                : 2014-11-08
    copyright            : (C) 2014 by Kay Warrie
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
from ui_geopunt4qgisParcel import Ui_geopunt4QgisParcelDlg
from qgis.core import *
from qgis.gui import  QgsMessageBar, QgsVertexMarker, QgsRubberBand
import geopunt, os, json, webbrowser
from geometryhelper import geometryHelper
from parcelHelper import parcelHelper

class geopunt4QgisParcelDlg(QtGui.QDialog):
    def __init__(self, iface):
        QtGui.QDialog.__init__(self, None)
        self.setWindowFlags( self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint )
        #self.setWindowFlags( self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.iface = iface
    
        # initialize locale
        locale = QtCore.QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(os.path.dirname(__file__), 'i18n', 'geopunt4qgis_{}.qm'.format(locale))
        if os.path.exists(localePath):
            self.translator = QtCore.QTranslator()
            self.translator.load(localePath)
            if QtCore.qVersion() > '4.3.3': QtCore.QCoreApplication.installTranslator(self.translator)
        
        self._initGui()

    def _initGui(self):
        """setup the user interface"""
        self.ui = Ui_geopunt4QgisParcelDlg()
        self.ui.setupUi(self)
        self.ui.buttonBox.addButton( QtGui.QPushButton("Sluiten"), QtGui.QDialogButtonBox.RejectRole  )

        #get settings
        self.s = QtCore.QSettings()
        self.loadSettings()

        #setup geometryHelper object
        self.gh = geometryHelper(self.iface)
        self.ph = parcelHelper(self.iface)
        
        #variables
        self.firstShow = True 
        self.municipalities = []
        self.departments = []
        self.sections = []
        self.parcels = []
        self.graphics = []
        
        #setup a message bar
        self.bar = QgsMessageBar() 
        self.bar.setSizePolicy( QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed )
        self.ui.verticalLayout.addWidget(self.bar)
        
        #event handlers 
        self.ui.municipalityCbx.currentIndexChanged.connect(self.municipalityChanged)
        self.ui.departmentCbx.currentIndexChanged.connect( self.departmentChanged )
        self.ui.sectionCbx.currentIndexChanged.connect(self.sectionChanged)
        self.ui.parcelCbx.currentIndexChanged.connect(self.parcelChanged)
        self.ui.ZoomKnop_muni.clicked.connect(self.zoomTo)
        self.ui.ZoomKnop_dep.clicked.connect(self.zoomTo)
        self.ui.ZoomKnop_sect.clicked.connect(self.zoomTo)
        self.ui.ZoomKnop_parcel.clicked.connect(self.zoomTo)
        self.ui.buttonBox.helpRequested.connect(self.openHelp)
        self.ui.saveBtn.clicked.connect(self.saveParcel)
        self.finished.connect( self.clean)
        
    def loadSettings(self):
        self.saveToFile = int( self.s.value("geopunt4qgis/parcelSavetoFile" , 1))
        layerName =  self.s.value("geopunt4qgis/parcelLayerText", "")
        if layerName :
           self.layerName= layerName   
        self.timeout =  int( self.s.value("geopunt4qgis/timeout" ,15))
        if int( self.s.value("geopunt4qgis/useProxy" , 0)):
            self.proxy = self.s.value("geopunt4qgis/proxyHost" ,"")
            self.port = self.s.value("geopunt4qgis/proxyPort" ,"")
        else:
            self.proxy = ""
            self.port = ""
        self.startDir = self.s.value("geopunt4qgis/startDir", os.path.dirname(__file__))    
        self.parcel = geopunt.parcel(self.timeout, self.proxy, self.port )
        
    def show(self):
        QtGui.QDialog.show(self)
        if self.firstShow:
             inet =  geopunt.internet_on( proxyUrl=self.proxy, port=self.port, timeout=self.timeout )
             if inet:
                self.firstShow = False
                
                self.municipalities = self.parcel.getMunicipalities()
                self.ui.municipalityCbx.clear()
                muniNames = [n['municipalityName'] for n in self.municipalities]
                self.ui.municipalityCbx.addItems( [''] + muniNames )
                self.setCompleter( muniNames, self.ui.municipalityCbx )
             else:
                self.bar.pushMessage(
                  QtCore.QCoreApplication.translate("geopunt4QgisParcelDlg", "Waarschuwing "), 
                  QtCore.QCoreApplication.translate("geopunt4QgisParcelDlg", 
                    "Kan geen verbing maken met het internet."), level=QgsMessageBar.WARNING, duration=5)

    def saveParcel(self):
        if not self.layernameValid(): return
        municipality= self.ui.municipalityCbx.currentText()
        department = self.ui.departmentCbx.currentText()
        
        niscodes = [n['municipalityCode'] for n in self.municipalities if n['municipalityName'] == municipality ]
        niscode = (niscodes[0] if len(niscodes) else '')
        departmentcodes = [n['departmentCode'] for n in self.departments if n['departmentName'] == department ]
        departmentcode = (departmentcodes[0] if len( departmentcodes) else '')
            
        section = self.ui.sectionCbx.currentText()
        parcelNr = self.ui.parcelCbx.currentText()
        
        if '' in (niscode, departmentcode, section, parcelNr): return
        
        try:
          if municipality != '' or department != '' or section != '' or parcelNr != '':
              parcelInfo = self.parcel.getParcel( niscode, departmentcode, section, parcelNr, 31370, 'full') 
              shape = json.loads( parcelInfo['geometry']['shape'])
              pts = [n.asPolygon() for n in self.PolygonsFromJson( shape )]
              mPolygon = QgsGeometry.fromMultiPolygon( pts )  
              self.ph.save_parcel_polygon(mPolygon, parcelInfo, self.layerName, self.saveToFile,
                                        self, os.path.join(self.startDir, self.layerName))
        except geopunt.geopuntError as e:
          self.bar.pushMessage("Error", str( e.message) , level=QgsMessageBar.WARNING, duration=5)
          return
        except Exception as e:
          self.bar.pushMessage("Error", str( e.message) , level=QgsMessageBar.CRITICAL)
          return

    def municipalityChanged(self):
        municipality= self.ui.municipalityCbx.currentText()
        
        if municipality == '': return
      
        niscodes = [n['municipalityCode'] for n in self.municipalities if n['municipalityName'] == municipality ]
        niscode = (niscodes[0] if len(niscodes) else '')
        if niscode == '': return
        
        try:
          self.departments = self.parcel.getDepartments(niscode)
        except geopunt.geopuntError as e:
          self.bar.pushMessage("Error", str( e.message) , level=QgsMessageBar.WARNING, duration=5)
          return
        except Exception as e:
          self.bar.pushMessage("Error", str( e.message) , level=QgsMessageBar.CRITICAL)
          return
        self.ui.departmentCbx.setEnabled(1) 
        self.ui.departmentCbx.clear()
        depNames = [n['departmentName'] for n in self.departments]
        self.ui.departmentCbx.addItems([''] + depNames )
        self.setCompleter( depNames, self.ui.departmentCbx)
        self.ui.sectionCbx.setEnabled(0)
        self.ui.parcelCbx.setEnabled(0)
        self.ui.saveBtn.setEnabled(0)
  
    def departmentChanged(self):
        department = self.ui.departmentCbx.currentText()
        municipality= self.ui.municipalityCbx.currentText()

        if municipality == '' or department == '': return

        niscodes = [n['municipalityCode'] for n in self.municipalities if n['municipalityName'] == municipality ]
        niscode = (niscodes[0] if len(niscodes) else '')
        departmentcodes = [n['departmentCode'] for n in self.departments if n['departmentName'] == department ]
        departmentcode = (departmentcodes[0] if len( departmentcodes) else '')
        
        if niscode == '' or departmentcode == '': return

        try:
          self.sections = [n['sectionCode'] for n in self.parcel.getSections(niscode, departmentcode)]
        except geopunt.geopuntError as e:
          self.bar.pushMessage("Error", str( e.message) , level=QgsMessageBar.WARNING, duration=5)
          return
        except Exception as e:
          self.bar.pushMessage("Error", str( e.message) , level=QgsMessageBar.CRITICAL)
          return

        self.ui.sectionCbx.clear()
        self.ui.sectionCbx.setEnabled(1)
        self.ui.sectionCbx.addItems([''] + self.sections )
        self.setCompleter( self.sections, self.ui.sectionCbx ) 
        self.ui.parcelCbx.setEnabled(0)
        self.ui.saveBtn.setEnabled(0)

    def sectionChanged(self):
        municipality= self.ui.municipalityCbx.currentText()
        department = self.ui.departmentCbx.currentText()
        section = self.ui.sectionCbx.currentText()
        
        if municipality == '' or department == '' or section == '': return
        
        niscodes = [n['municipalityCode'] for n in self.municipalities if n['municipalityName'] == municipality ]
        niscode = (niscodes[0] if len(niscodes) else '')
        departmentcodes = [n['departmentCode'] for n in self.departments if n['departmentName'] == department ]
        departmentcode = (departmentcodes[0] if len( departmentcodes) else '')
        
        if niscode == '' or departmentcode == '': return
      
        try:
          self.parcels = self.parcel.getParcels( niscode, departmentcode, section )
        except geopunt.geopuntError as e:
          self.bar.pushMessage("Error", str( e.message) , level=QgsMessageBar.WARNING, duration=5)
          return
        except Exception as e:
          self.bar.pushMessage("Error", str( e.message) , level=QgsMessageBar.CRITICAL)
          return
        
        self.ui.parcelCbx.clear()
        self.ui.parcelCbx.setEnabled(1)
        parcelNrs = [n['perceelnummer'] for n in self.parcels]
        self.ui.parcelCbx.addItems([''] + parcelNrs)
        self.setCompleter( parcelNrs, self.ui.parcelCbx ) 
        self.ui.saveBtn.setEnabled(0)

    def parcelChanged(self):
        self.ui.saveBtn.setEnabled( self.ui.parcelCbx.currentText() != '' )

    def zoomTo(self):
        sender = self.sender()
        municipality= self.ui.municipalityCbx.currentText()
        department = self.ui.departmentCbx.currentText()
        
        niscodes = [n['municipalityCode'] for n in self.municipalities if n['municipalityName'] == municipality ]
        niscode = (niscodes[0] if len(niscodes) else '')
        departmentcodes = [n['departmentCode'] for n in self.departments if n['departmentName'] == department ]
        departmentcode = (departmentcodes[0] if len( departmentcodes) else '')
            
        section = self.ui.sectionCbx.currentText()
        parcelNr = self.ui.parcelCbx.currentText()
        
        try:
            if sender is self.ui.ZoomKnop_muni and municipality != '':
                muniInfo = self.parcel.getMunicipalitieInfo( niscode, 31370, 'full') 
                if muniInfo == []: return
                bbox= json.loads( muniInfo['geometry']['boundingBox'])['coordinates'][0]
                self.clearGraphics()
                self.gh.zoomtoRec( bbox[0], bbox[2], 31370 )        
                shape = json.loads( muniInfo['geometry']['shape'])
                for n in self.PolygonsFromJson( shape ):  self.addGraphic(n)
                return
            if sender is self.ui.ZoomKnop_dep and municipality != '' and department != '':
                depInfo = self.parcel.getDepartmentInfo( niscode, departmentcode, 31370, 'full') 
                if depInfo == []: return
                bbox= json.loads( depInfo['geometry']['boundingBox'])['coordinates'][0]
                self.clearGraphics()
                self.gh.zoomtoRec( bbox[0], bbox[2], 31370 )
                shape = json.loads( depInfo['geometry']['shape'])
                for n in self.PolygonsFromJson( shape ):  self.addGraphic(n)
                return
            if sender is self.ui.ZoomKnop_sect and municipality != '' and department != '' and section != '':
                sectInfo = self.parcel.getSectionInfo( niscode, departmentcode, section, 31370, 'full') 
                if sectInfo == []: return
                bbox= json.loads( sectInfo['geometry']['boundingBox'])['coordinates'][0]
                self.clearGraphics()
                self.gh.zoomtoRec( bbox[0], bbox[2], 31370 )
                shape = json.loads( sectInfo['geometry']['shape'])
                for n in self.PolygonsFromJson( shape ):  self.addGraphic(n)
                return
            if sender is self.ui.ZoomKnop_parcel and municipality != '' and department != '' and section != '' and parcelNr != '':
                parcelInfo = self.parcel.getParcel( niscode, departmentcode, section, parcelNr, 31370, 'full') 
                if parcelInfo == []: return
                bbox= json.loads( parcelInfo['geometry']['boundingBox'])['coordinates'][0]
                self.clearGraphics()
                self.gh.zoomtoRec( bbox[0], bbox[2], 31370 )
                shape = json.loads( parcelInfo['geometry']['shape'])
                for n in self.PolygonsFromJson( shape ):  self.addGraphic(n)
                return
        except geopunt.geopuntError as e:
          self.bar.pushMessage("Error", str( e.message) , level=QgsMessageBar.WARNING, duration=5)
          return
        except Exception as e:
          self.bar.pushMessage("Error", str( e.message) , level=QgsMessageBar.CRITICAL)
          return

    def openHelp(self):
        webbrowser.open_new_tab("http://www.geopunt.be/voor-experts/geopunt-plugins/functionaliteiten")

    def layernameValid(self):   
        if not hasattr(self, 'layerName'):
          layerName, accept = QtGui.QInputDialog.getText(None,
              QtCore.QCoreApplication.translate("geopunt4Qgis", 'Laag toevoegen'),
              QtCore.QCoreApplication.translate("geopunt4Qgis", 'Geef een naam voor de laag op:') )
          if accept == False: 
             return False
          else: 
             self.layerName = layerName
        return True

    def PolygonsFromJson(self, geojson ):
        geoType= geojson['type']
        Polygons = []
        
        if geoType == "Polygon":
           rings = geojson['coordinates']
           mPolygon = [ rings ]
        if geoType == "MultiPolygon":
           mPolygon = geojson['coordinates']
           print  len( mPolygon)
           
        for rings in mPolygon:
            prjPolygon = []
            for ring in rings:
              prjRing = self.gh.prjLineToMapCrs( ring, 31370 )
              prjPolygon.append( prjRing.asPolyline() )
            
            gPolygon = QgsGeometry.fromPolygon( prjPolygon )
            Polygons.append( gPolygon )
        
        return Polygons

    def addGraphic(self, geom ):
        canvas = self.iface.mapCanvas()      
        rBand = QgsRubberBand(canvas, True) 
        self.graphics.append( rBand )
        rBand.setToGeometry( geom, None )
        rBand.setColor(QtGui.QColor(0,0,255, 70))
        rBand.setBorderColor( QtGui.QColor(70,70,70, 220) )
        rBand.setWidth(3)

    def clearGraphics(self):
        canvas = self.iface.mapCanvas()
        for g in self.graphics:
            canvas.scene().removeItem(g)
  
    def setCompleter(self, values, wgt):
        completer = QtGui.QCompleter( self )
        completerModel = QtGui.QStringListModel( self )
        wgt.setCompleter( completer )
        completer.setModel( completerModel )
        completer.setCaseSensitivity(False)
        completerModel.setStringList( values )
  
    def clean(self):
        self.clearGraphics()
        self.ui.municipalityCbx.setCurrentIndex(0)
        self.ui.departmentCbx.clear()
        self.ui.sectionCbx.clear()
        self.ui.parcelCbx.clear()
        self.ui.departmentCbx.setDisabled(1)
        self.ui.sectionCbx.setDisabled(1)
        self.ui.parcelCbx.setDisabled(1)
        