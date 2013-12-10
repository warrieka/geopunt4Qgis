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
from qgis.gui import QgsMessageBar
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
        
        #setup geopunt
        self.poi = geopunt.Poi()
        self.gh = gh.geometryHelper(iface)
        
        #event handlers 
        self.ui.poiText.returnPressed.connect(self.onZoekActivated)
        self.ui.zoekKnop.clicked.connect(self.onZoekActivated)
        self.ui.zoomSelKnop.clicked.connect(self.zoomSelClicked)
        self.finished.connect(self.clean )
        
    def onZoekActivated(self):
	txt = self.ui.poiText.text()
	if self.ui.currentBoundsVink.isChecked():
	  bbox = self.iface.mapCanvas().extent()
	  minX, minY = self.gh.prjPtFromMapCrs([bbox.xMinimum(),bbox.yMinimum()], 31370)
	  maxX, maxY = self.gh.prjPtFromMapCrs([bbox.xMaximum(),bbox.yMaximum()], 31370)
	  lam72Box = [minX, minY, maxX, maxY]
	  suggesties = self.poi.poiSuggestion(txt, lam72Box, True)
	else:
	  suggesties = self.poi.poiSuggestion(txt, None, True)
	
	self.ui.resultLijst.clearContents()
	self.ui.resultLijst.setRowCount(0)
	if suggesties.__class__ == list and len(suggesties) > 0:
	  
	  #prevent sorting every time an item is added
	  self.ui.resultLijst.setSortingEnabled(False)
	  row =0
	  for sug in suggesties:
	    categorie = QtGui.QTableWidgetItem( sug[0] )
	    naam = QtGui.QTableWidgetItem( sug[1], 0 )
	    adres = QtGui.QTableWidgetItem( sug[2].replace("<br />",", ").replace("<br/>",", "), 0)
	    self.ui.resultLijst.insertRow(row)
	    self.ui.resultLijst.setItem(row, 0, categorie)
	    self.ui.resultLijst.setItem(row, 1, naam)
	    self.ui.resultLijst.setItem(row, 2, adres)
	    row += 1
	  self.ui.resultLijst.setSortingEnabled(True)
	  
	elif len(suggesties) == 0:
	  self.bar.pushMessage("Geen resultaten gevonden voor", txt, level=QgsMessageBar.INFO, duration=3)
	elif suggesties.__class__ == str:
	  self.bar.pushMessage("Waarschuwing", suggesties, level=QgsMessageBar.WARNING, duration=3)
	else:
	  self.bar.pushMessage("Fout", "onbekende fout", level=QgsMessageBar.ERROR, duration=3)

    def zoomSelClicked(self):
	pois =  self.poi.resultPoi
	if self.ui.resultLijst.rowCount() <= 0 :
	  self.bar.pushMessage("Merk op", "Er niets om naar te zoomen" ,level=QgsMessageBar.INFO, duration=3)
	  return
	elif self.ui.resultLijst.rowCount() > 2:
	  pts = [n['location']['points'][0]['Point']['coordinates'] for n in pois ] 
	  bounds = self.gh.getBoundsOfPointArray(pts)
	elif  self.ui.resultLijst.rowCount() == 1:
	  x,  y = pois[0]['location']['points'][0]['Point']['coordinates']
	  bounds = self.gh.getBoundsOfPoint(x,y)
	  
	self.gh.zoomtoRec(bounds[:2], bounds[2:4], 31370)
	        	        
	        
    def clean(self):
	self.ui.poiText.setText("")
	self.ui.resultLijst.setRowCount(0)