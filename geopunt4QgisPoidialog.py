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
        
    def onZoekActivated(self):
	txt = self.ui.poiText.text()
	suggesties = self.poi.poiSuggestion(txt)
	self.ui.resultLijst.clear()
	self.ui.resultLijst
	self.ui.resultLijst.addItems(suggesties)
	
	#self.bar.pushMessage("Fout",txt, level=QgsMessageBar.CRITICAL, duration=3)
      
      