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
import geopunt, os, webbrowser

class geopunt4QgisPoidialog(QtGui.QDialog):
    def __init__(self, iface):
	    QtGui.QDialog.__init__(self)
	    self.iface = iface

	    # initialize locale
	    locale = QtCore.QSettings().value("locale/userLocale")[0:2]
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
        self.poi = geopunt.Poi(self.timeout, self.proxy, self.port)
        self.gh = gh.geometryHelper(self.iface)
        
        #create the graphicsLayer
        self.graphicsLayer = []
	
        #setup a message bar
        self.bar = QgsMessageBar() 
        self.bar.setSizePolicy( QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed )
        self.ui.verticalLayout.addWidget(self.bar)
	
        #table ui
        self.ui.resultLijst.hideColumn(0)
	
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
        self.ui.buttonBox.helpRequested.connect(self.openHelp)
        self.finished.connect(self.clean )
	
    def loadSettings(self):
        self.saveToFile = int( self.s.value("geopunt4qgis/poiSavetoFile" , 1))
        self.layerName =  self.s.value("geopunt4qgis/poilayerText", "geopunt_poi")
        self.timeout =  int(  self.s.value("geopunt4qgis/timeout" ,15))
	self.proxy = self.s.value("geopunt4qgis/proxyHost" ,"")
        self.port = self.s.value("geopunt4qgis/proxyPort" ,"")
	
    def openHelp(self):
	webbrowser.open_new_tab("http://warrieka.github.io/index.html#!geopuntPoi.md")
	
    def onZoekActivated(self):
	    txt = self.ui.poiText.text()
	    self.ui.resultLijst.clearContents()
	    self.ui.resultLijst.setRowCount(0)
	
	    if self.ui.currentBoundsVink.isChecked():
	      bbox = self.iface.mapCanvas().extent()
	      minX, minY = self.gh.prjPtFromMapCrs([bbox.xMinimum(),bbox.yMinimum()], 31370)
	      maxX, maxY = self.gh.prjPtFromMapCrs([bbox.xMaximum(),bbox.yMaximum()], 31370)
	      lam72Box = [minX, minY, maxX, maxY]
	      self.poi.fetchPoi( txt, c=25, srs=31370 , maxModel=True, updateResults=True, bbox=lam72Box )
	    else:
	      self.poi.fetchPoi( txt, c=25, srs=31370 , maxModel=True, updateResults=True, bbox=None )
	  
	    suggesties = self.poi.poiSuggestion()
	
	    if suggesties.__class__ == list and len(suggesties) > 0:
	      #prevent sorting every time an item is added
	      self.ui.resultLijst.setSortingEnabled(False)
	      row =0
	      for sug in suggesties:
	        id = QtGui.QTableWidgetItem( sug[0] )
	        categorie = QtGui.QTableWidgetItem( sug[1] )
	        naam = QtGui.QTableWidgetItem( sug[2], 0 )
	        adres = QtGui.QTableWidgetItem( sug[3].replace("<br />",", ").replace("<br/>",", "), 0)
	        self.ui.resultLijst.insertRow(row)
	        self.ui.resultLijst.setItem(row, 0, id)
	        self.ui.resultLijst.setItem(row, 1, categorie)
	        self.ui.resultLijst.setItem(row, 2, naam)
	        self.ui.resultLijst.setItem(row, 3, adres)
	        row += 1
	      self.ui.resultLijst.setSortingEnabled(True)
	  
	    elif len(suggesties) == 0:
	      self.bar.pushMessage(
	        QtCore.QCoreApplication.translate("geopunt4QgisPoidialog", "Geen resultaten gevonden voor: "), 
	        txt, level=QgsMessageBar.INFO, duration=3)
	    elif suggesties.__class__ == str:
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
	      self.gh.zoomtoRec(bounds[:2], bounds[2:4], 31370)
	    elif len(selPois) == 1:
	      x,  y = selPois[0]['location']['points'][0]['Point']['coordinates']
	      bounds = self.gh.getBoundsOfPoint(x,y)
	      self.gh.zoomtoRec(bounds[:2], bounds[2:4], 31370)
	
    def onSelectionChanged(self):
	    selPois = self._getSelectedPois()
	    canvas = self.iface.mapCanvas()
	    self.clearGraphicsLayer()
	
	    pts = [ self.gh.prjPtToMapCrs( n['location']['points'][0]['Point']['coordinates'], 31370)
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
	    self.clearGraphicsLayer()
	    pts = self._getSelectedPois()
	    self.gh.save_pois_points( pts ,  layername=self.layerName, 
			      saveToFile=self.saveToFile, sender=self )

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
      
    def clean(self):
        self.bar.clearWidgets()
        self.ui.poiText.setText("")
        self.ui.resultLijst.clearContents()
        self.ui.resultLijst.setRowCount(0)
        self.clearGraphicsLayer()