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
import geopunt 

class geopunt4QgisPoidialog(QtGui.QDialog):
    def __init__(self, iface):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.ui = Ui_geopunt4QgisPoiDlg()
        self.ui.setupUi(self)
        
        #setup a message bar
        self.bar = QgsMessageBar() 
        self.bar.setSizePolicy( QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed )
        self.ui.verticalLayout.addWidget(self.bar)
        
        self.iface = iface
        
        self.graphicsLayer = []
        
        #setup geopunt and geometryHelper objects
        self.poi = geopunt.Poi()
        self.gh = gh.geometryHelper(iface)
        
        #table ui
        self.ui.resultLijst.hideColumn(0)
        
        #event handlers 
        self.ui.poiText.returnPressed.connect(self.onZoekActivated)
        self.ui.zoekKnop.clicked.connect(self.onZoekActivated)
        self.ui.zoomSelKnop.clicked.connect(self.onZoomSelClicked)
        self.ui.resultLijst.itemSelectionChanged.connect(self.onSelectionChanged)
        self.finished.connect(self.clean )
        
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
	  self.bar.pushMessage("Geen resultaten gevonden voor", txt, level=QgsMessageBar.INFO, duration=3)
	elif suggesties.__class__ == str:
	  self.bar.pushMessage("Waarschuwing", suggesties, level=QgsMessageBar.WARNING, duration=3)
	else:
	  self.bar.pushMessage("Fout", "onbekende fout", level=QgsMessageBar.CRITICAL, duration=3)

    def onZoomSelClicked(self):
	selPois = self._getSelectedPois()
	if len(selPois) <= 0 :
	  self.bar.pushMessage("Merk op", "Er niets om naar te zoomen" ,level=QgsMessageBar.INFO, duration=3)
	elif len(selPois) >= 2:
	  pts = [n['location']['points'][0]['Point']['coordinates'] for n in selPois ] 
	  bounds = self.gh.getBoundsOfPointArray(pts)
	  self.gh.zoomtoRec(bounds[:2], bounds[2:4], 31370)
	elif len(selPois) == 1:
	  x,  y = selPois[0]['location']['points'][0]['Point']['coordinates']
	  bounds = self.gh.getBoundsOfPoint(x,y)
	  print bounds.__str__()
	  self.gh.zoomtoRec(bounds[:2], bounds[2:4], 31370)
	
	        	        
    def onSelectionChanged(self):
	selPois = self._getSelectedPois()
	canvas = self.iface.mapCanvas()
	self._clearGraphicsLayer()
	
	pts = [ self.gh.prjPtToMapCrs( n['location']['points'][0]['Point']['coordinates'], 31370)
			       for n in selPois ] 
	for pt in pts:
	  x,y = pt
	  m = QgsVertexMarker(canvas)
	  self.graphicsLayer.append(m)
	  m.setCenter(QgsPoint(x,y))
	  m.setColor(QtGui.QColor(255,255,0))
	  m.setIconSize(5)
	  m.setIconType(QgsVertexMarker.ICON_BOX) 
	  m.setPenWidth(3)
	
    def clean(self):
	self.ui.poiText.setText("")
	self.ui.resultLijst.clearContents()
	self.ui.resultLijst.setRowCount(0)
	self._clearGraphicsLayer()
	
    def _getSelectedPois(self):
	pois =  self.poi.PoiResult
	selPois = []
	selRows = set( [sel.row() for sel in self.ui.resultLijst.selectedIndexes()] )
	for row in  selRows:
	  itemID = self.ui.resultLijst.item(row,0).text()
	  selPois += [i for i in pois if i["id"] == itemID]
	return selPois
      
    def _clearGraphicsLayer(self):
      for graphic in  self.graphicsLayer: 
	self.iface.mapCanvas().scene().removeItem(graphic)
      self.graphicsLayer = []
      