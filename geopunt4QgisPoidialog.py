# -*- coding: utf-8 -*-
"""
/***************************************************************************
geopunt4QgisPoiDialog
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
from qgis.core import *
from qgis.gui import QgsMessageBar, QgsVertexMarker
from ui_geopunt4QgisPoi import Ui_geopunt4QgisPoiDlg
import geometryhelper as gh
from poiHelper import poiHelper
import geopunt, os, webbrowser, json

class geopunt4QgisPoidialog(QtGui.QDialog):
    def __init__(self, iface):
        QtGui.QDialog.__init__(self, None)
        self.setWindowFlags( self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint )
        #self.setWindowFlags( self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.iface = iface

        # initialize locale
        locale = QtCore.QSettings().value("locale/userLocale", "nl")
        if not locale: locale == 'nl' 
        else: locale = locale[0:2]
        localePath = os.path.join(os.path.dirname(__file__), 'i18n', 'geopunt4qgis_{}.qm'.format(locale))
        if os.path.exists(localePath):
            self.translator = QtCore.QTranslator()
            self.translator.load(localePath)
            if QtCore.qVersion() > '4.3.3': 
               QtCore.QCoreApplication.installTranslator(self.translator)
        self._initGui()
    
    def _initGui(self):
        'Set up the user interface from Designer.'
        self.ui = Ui_geopunt4QgisPoiDlg()
        self.ui.setupUi(self)	
    
        #get settings
        self.s = QtCore.QSettings()
        self.loadSettings()

        #setup geopunt and geometryHelper objects
        self.gh = gh.geometryHelper(self.iface)
        self.ph = poiHelper( self.iface)
        
        #create the graphicsLayer
        self.graphicsLayer = []
    
        #setup a message bar
        self.bar = QgsMessageBar() 
        self.bar.setSizePolicy( QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed )
        self.ui.verticalLayout.addWidget(self.bar)
    
        self.ui.buttonBox.addButton( QtGui.QPushButton("Sluiten"), QtGui.QDialogButtonBox.RejectRole  )
        for btn in self.ui.buttonBox.buttons():
            btn.setAutoDefault(0)
            
        #table ui
        self.ui.resultLijst.hideColumn(0)
       
        # filters
        self.firstShow = True
        self.poiTypes = {}
        self.poiCategories = {}
        self.poiThemes = {}
    
        #actions
        self.ui.resultLijst.addAction( self.ui.actionZoomtoSelection )
        self.ui.actionZoomtoSelection.triggered.connect( self.onZoomSelClicked)
        self.ui.resultLijst.addAction( self.ui.actionAddTSeltoMap )
        self.ui.actionAddTSeltoMap.triggered.connect( self.onAddSelClicked)
    
        #event handlers 
        self.ui.zoekKnop.clicked.connect(self.onZoekActivated)
        self.ui.zoomSelKnop.clicked.connect(self.onZoomSelClicked)
        self.ui.resultLijst.itemDoubleClicked.connect(self.onZoomSelClicked )
        self.ui.resultLijst.itemSelectionChanged.connect(self.onSelectionChanged)
        self.ui.addToMapKnop.clicked.connect(self.onAddSelClicked)
        self.ui.addMinModelBtn.clicked.connect( self.addMinModel )
        self.ui.poiText.textChanged.connect( self.searchTxtChanged )
        self.ui.buttonBox.helpRequested.connect(self.openHelp)
        
        self.finished.connect(self.clean )
    
    def loadSettings(self):
        self.saveToFile = int( self.s.value("geopunt4qgis/poiSavetoFile" , 1))
        layerName =  self.s.value("geopunt4qgis/poilayerText", "")
        if layerName: self.layerName= layerName
        self.timeout =  int(  self.s.value("geopunt4qgis/timeout" ,15))
        if int( self.s.value("geopunt4qgis/useProxy" , 0)):
            self.proxy = self.s.value("geopunt4qgis/proxyHost" ,"")
            self.port = self.s.value("geopunt4qgis/proxyPort" ,"")
        else:
            self.proxy = ""
            self.port = ""
        self.startDir = self.s.value("geopunt4qgis/startDir", os.path.dirname(__file__))
        self.poi = geopunt.Poi(self.timeout, self.proxy, self.port)
    
    def show(self):
        QtGui.QDialog.show(self)
        self.setWindowModality(0)
        if self.firstShow:
             inet = geopunt.internet_on( proxyUrl=self.proxy, port=self.port, timeout=self.timeout )
             #filters
             if inet:
                self.poiThemes = dict( self.poi.listPoiThemes() )
                poiThemes = [""] + self.poiThemes.keys()
                poiThemes.sort()
                self.ui.filterPoiThemeCombo.addItems( poiThemes )
                self.poiCategories = dict( self.poi.listPoiCategories() )
                poiCategories = [""] + self.poiCategories.keys()
                poiCategories.sort()
                self.ui.filterPoiCategoryCombo.addItems( poiCategories )
                self.poiTypes = dict( self.poi.listPoitypes() )
                poiTypes = [""] + self.poiTypes.keys()
                poiTypes.sort()
                self.ui.filterPoiTypeCombo.addItems(  poiTypes )
                gemeentes = json.load( open(os.path.join(os.path.dirname(__file__), "data/gemeentenVL.json")) )
                self.NIScodes= { n["Naam"] : n["Niscode"] for n in gemeentes }
                gemeenteNamen = [n["Naam"] for n in gemeentes]
                gemeenteNamen.sort()
                self.ui.filterPoiNIS.addItems( gemeenteNamen )            
                #connect when inet on
                self.ui.filterPoiThemeCombo.activated.connect(self.onThemeFilterChange)
                self.ui.filterPoiCategoryCombo.activated.connect(self.onCategorieFilterChange)
                
                self.firstShow = False      
             else:
                self.bar.pushMessage(
                  QtCore.QCoreApplication.translate("geopunt4QgisPoidialog", "Waarschuwing "), 
                  QtCore.QCoreApplication.translate("geopunt4QgisPoidialog", "Kan geen verbing maken met het internet."), 
                  level=QgsMessageBar.WARNING, duration=3)
      
    def openHelp(self):
        webbrowser.open_new_tab("http://www.geopunt.be/voor-experts/geopunt-plug-ins/functionaliteiten/poi")
    
    def onZoekActivated(self):
        txt = self.ui.poiText.text()
        self.ui.resultLijst.clearContents()
        self.ui.resultLijst.setRowCount(0)
        self.ui.msgLbl.setText("")
        
        ##filters:
        poithemeText = self.ui.filterPoiThemeCombo.currentText()
        if poithemeText != "": poitheme = self.poiThemes[ poithemeText ]
        else: poitheme = ""
        poiCategorieText = self.ui.filterPoiCategoryCombo.currentText() 
        if poiCategorieText != "": poiCategorie = self.poiCategories[ poiCategorieText ]
        else: poiCategorie = ""
        poiTypeText =  self.ui.filterPoiTypeCombo.currentText() 
        if poiTypeText!= "": poiType = self.poiTypes[ poiTypeText ]
        else: poiType = ""
        NISText= self.ui.filterPoiNIS.currentText()
        if NISText != "" and not self.ui.currentBoundsVink.isChecked(): Niscode = self.NIScodes[NISText]
        else: Niscode = ""
        
        if self.ui.currentBoundsVink.isChecked():
            bbox = self.iface.mapCanvas().extent()
            minX, minY = self.gh.prjPtFromMapCrs([bbox.xMinimum(),bbox.yMinimum()], 4326)
            maxX, maxY = self.gh.prjPtFromMapCrs([bbox.xMaximum(),bbox.yMaximum()], 4326)
            xyBox = [minX, minY, maxX, maxY]
            self.poi.fetchPoi( txt, c=32, srs=4326 , maxModel=True, updateResults=True, bbox=xyBox, 
                               theme=poitheme , category=poiCategorie, POItype=poiType )
        else:
            self.poi.fetchPoi( txt, c=32, srs=4326 , maxModel=True, updateResults=True, bbox=None, 
                               theme=poitheme , category=poiCategorie, POItype=poiType, region=Niscode )
      
        suggesties = self.poi.poiSuggestion()
    
        if type(suggesties) is list and len(suggesties) > 0:
          #prevent sorting every time an item is added
          self.ui.resultLijst.setSortingEnabled(False)
          row =0
          for sug in suggesties:
              id = QtGui.QTableWidgetItem( sug[0], 0 )
              theme = QtGui.QTableWidgetItem( sug[1], 0 )
              categorie = QtGui.QTableWidgetItem( sug[2], 0 )
              PoiType = QtGui.QTableWidgetItem( sug[3], 0 )
              naam = QtGui.QTableWidgetItem( sug[4], 0 )
              adres = QtGui.QTableWidgetItem( sug[5].replace("<br />",", ").replace("<br/>",", "), 0)
              self.ui.resultLijst.insertRow(row)
              self.ui.resultLijst.setItem(row, 0, id)
              self.ui.resultLijst.setItem(row, 1, theme)
              self.ui.resultLijst.setItem(row, 2, categorie)
              self.ui.resultLijst.setItem(row, 3, PoiType)
              self.ui.resultLijst.setItem(row, 4, naam)
              self.ui.resultLijst.setItem(row, 5, adres)
              row += 1
          self.ui.resultLijst.setSortingEnabled(True)
          
          if txt == "":
            self.ui.msgLbl.setText(QtCore.QCoreApplication.translate("geopunt4QgisPoidialog", 
            "Aantal getoond: %s gevonden: %s" % ( self.ui.resultLijst.rowCount() , self.poi.resultCount ) ))
          else:
            self.ui.msgLbl.setText(QtCore.QCoreApplication.translate("geopunt4QgisPoidialog", 
            "Aantal getoond: %s" % ( self.ui.resultLijst.rowCount() ) ))
        
        elif len(suggesties) == 0:
          self.bar.pushMessage(
            QtCore.QCoreApplication.translate("geopunt4QgisPoidialog", "Geen resultaten gevonden voor deze  zoekopdracht"), 
            txt, level=QgsMessageBar.INFO, duration=5)
        elif type( suggesties ) is str:
          self.bar.pushMessage(
            QtCore.QCoreApplication.translate("geopunt4QgisPoidialog","Waarschuwing"), 
            suggesties, level=QgsMessageBar.WARNING)
        else:
          self.bar.pushMessage("Error",
            QtCore.QCoreApplication.translate("geopunt4QgisPoidialog","onbekende fout"),
            level=QgsMessageBar.CRITICAL)
    
    def onZoomSelClicked(self):
        selPois = self._getSelectedPois()
        if len(selPois) <= 0 :
          self.bar.pushMessage( QtCore.QCoreApplication.translate("geopunt4QgisPoidialog", "Merk op"), 
                QtCore.QCoreApplication.translate("geopunt4QgisPoidialog", "Er niets om naar te zoomen"),
                level=QgsMessageBar.INFO, duration=3)
        elif len(selPois) >= 2:
            pts = [n['location']['points'][0]['Point']['coordinates'] for n in selPois ] 
            bounds = self.gh.getBoundsOfPointArray(pts)
            self.gh.zoomtoRec(bounds[:2], bounds[2:4], 4326)
        elif len(selPois) == 1:
            x,  y = selPois[0]['location']['points'][0]['Point']['coordinates']
            bounds = self.gh.getBoundsOfPoint(x,y)
            self.gh.zoomtoRec(bounds[:2], bounds[2:4], 4326)
    
    def onSelectionChanged(self):
        selPois = self._getSelectedPois()
        canvas = self.iface.mapCanvas()
        self.clearGraphicsLayer()
    
        pts = [ self.gh.prjPtToMapCrs( n['location']['points'][0]['Point']['coordinates'], 4326)
                      for n in selPois ] 
        for pt in pts:
            x,y = pt
            m = QgsVertexMarker(canvas)
            self.graphicsLayer.append(m)
            m.setCenter(QgsPoint(x,y))
            m.setColor(QtGui.QColor(255,255,0))
            m.setIconSize(1)
            m.setIconType(QgsVertexMarker.ICON_BOX) 
            m.setPenWidth(10)

    def onAddSelClicked(self):
        if not self.layernameValid(): return
        self.clearGraphicsLayer()
        pts = self._getSelectedPois()
        self.ph.save_pois_points( pts ,  layername=self.layerName, startFolder= os.path.join(self.startDir, self.layerName),
                  saveToFile=self.saveToFile, sender=self )

    def onThemeFilterChange(self): 
        poithemeText = self.ui.filterPoiThemeCombo.currentText()
        
        if poithemeText != "": 
           poithemeID = self.poiThemes[ poithemeText ]
           poiCategories = [""] + [n[0] for n in self.poi.listPoiCategories(poithemeID)]
           poiCategories.sort()
           self.ui.filterPoiCategoryCombo.clear()
           self.ui.filterPoiTypeCombo.clear()
           self.ui.filterPoiCategoryCombo.addItems( poiCategories )
        else:
          self.ui.filterPoiCategoryCombo.addItems([""] + self.poiCategories.keys())
          self.ui.filterPoiTypeCombo.addItems([""] + self.poiTypes.keys())

    def onCategorieFilterChange(self):
        poithemeText = self.ui.filterPoiThemeCombo.currentText()
        poiCategorieText = self.ui.filterPoiCategoryCombo.currentText() 
        
        if poiCategorieText != "" and poithemeText != "": 
           poiCategorieID = self.poiCategories[ poiCategorieText ]
           poithemeID = self.poiThemes[ poithemeText ]
           poiTypes = [""] + [n[0] for n in self.poi.listPoitypes(poithemeID, poiCategorieID)]
           poiTypes.sort()          
           self.ui.filterPoiTypeCombo.clear()
           self.ui.filterPoiTypeCombo.addItems( poiTypes )

    def addMinModel(self):
        if not self.layernameValid(): return
        self.clearGraphicsLayer()
        txt = self.ui.poiText.text()

        poithemeText = self.ui.filterPoiThemeCombo.currentText()
        if poithemeText != "": poitheme = self.poiThemes[ poithemeText ]
        else: poitheme = ""
        poiCategorieText = self.ui.filterPoiCategoryCombo.currentText() 
        if poiCategorieText != "": poiCategorie = self.poiCategories[ poiCategorieText ]
        else: poiCategorie = ""
        poiTypeText =  self.ui.filterPoiTypeCombo.currentText() 
        if poiTypeText!= "": poiType = self.poiTypes[ poiTypeText ]
        else: poiType = ""
        NISText= self.ui.filterPoiNIS.currentText()
        if NISText != "" and not self.ui.currentBoundsVink.isChecked(): Niscode = self.NIScodes[NISText]
        else: Niscode = ""
      
        if self.ui.currentBoundsVink.isChecked():
            bbox = self.iface.mapCanvas().extent()
            minX, minY = self.gh.prjPtFromMapCrs([bbox.xMinimum(),bbox.yMinimum()], 4326)
            maxX, maxY = self.gh.prjPtFromMapCrs([bbox.xMaximum(),bbox.yMaximum()], 4326)
            xyBox = [minX, minY, maxX, maxY]
            pts= self.poi.fetchPoi( txt, c=1024, srs=4326 , maxModel=0, updateResults=0,
                                   bbox=xyBox, theme=poitheme , category=poiCategorie,
                                   POItype=poiType )
        else:
            pts= self.poi.fetchPoi( txt, c=1024, srs=4326 , maxModel=0, updateResults=0,
                                   bbox=None,  theme=poitheme , category=poiCategorie,
                                   POItype=poiType, region=Niscode )

        if type( pts ) == str:
            self.bar.pushMessage( QtCore.QCoreApplication.translate("geopunt4QgisPoidialog","Waarschuwing"),
                                  pts, level=QgsMessageBar.WARNING, duration=5)
        elif type( pts ) == list or type( pts )  == dict:            
            self.ph.save_minPois_points(pts, layername=self.layerName, startFolder= os.path.join(self.startDir, self.layerName), saveToFile=self.saveToFile, sender=self )
            self.close()

    def searchTxtChanged(self):
        txt= self.ui.poiText.text()
        if txt != "":
           msg = QtCore.QCoreApplication.translate("geopunt4QgisPoidialog",
                                                   "Voeg meer punten toe")
        else:
           msg = QtCore.QCoreApplication.translate("geopunt4QgisPoidialog",
                                                   "Voeg alle punten toe" )
        self.ui.addMinModelBtn.setText(msg)   

    def _getSelectedPois(self):
        pois =  self.poi.PoiResult
        selPois = []
        selRows = set( [sel.row() for sel in self.ui.resultLijst.selectedIndexes()] )
        for row in  selRows:
            itemID = self.ui.resultLijst.item(row,0).text()
            selPois += [i for i in pois if i["id"] == itemID]
        return selPois
      
    def clearGraphicsLayer(self):
      for graphic in  self.graphicsLayer: 
          self.iface.mapCanvas().scene().removeItem(graphic)
      self.graphicsLayer = []

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
      
    def clean(self):
        self.bar.clearWidgets()
        self.ui.poiText.setText("")
        self.ui.msgLbl.setText("")
        self.ui.resultLijst.clearContents()
        self.ui.resultLijst.setRowCount(0)
        self.clearGraphicsLayer()