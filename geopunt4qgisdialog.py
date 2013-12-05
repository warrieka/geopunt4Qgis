# -*- coding: utf-8 -*-
"""
/***************************************************************************
 geopunt4QgisDialog
                                 A QGIS plugin
 "Tool om geopunt in QGIS te gebruiken"
                             -------------------
        begin                : 2013-12-05
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
from ui_geopunt4qgis import Ui_geopunt4Qgis

import geopunt 


class geopunt4QgisDialog(QtGui.QDialog):
    def __init__(self, iface):
        QtGui.QDialog.__init__(self)
        # Set up the user interface from Designer.
        self.ui = Ui_geopunt4Qgis()
        self.ui.setupUi(self)
        
        self.gp = geopunt.geopunt()
        
       # self.ui.zoekText.textEdited.connect(self.onZoekActivated)
        self.ui.zoekText.returnPressed.connect(self.onZoekActivated)
        self.ui.zoekBtn.clicked.connect(self.onZoekActivated)
        
        self.ui.resultLijst.itemDoubleClicked.connect(self.onItemActivated)
        
    def onZoekActivated(self):
        txt = self.ui.zoekText.text()
        suggesties = self.gp.fetchSuggestion( txt , 12 )
        self.ui.resultLijst.clear()
        self.ui.resultLijst.addItems(suggesties)
        
    def onItemActivated( self , item):
	 txt = item.text()
	 loc = self.gp.fetchLocation(txt)[0]
	 x,y,adres = loc['x'], loc['y'], loc['adres']
	 
	 msgBox = QtGui.QMessageBox()
	 msgBox.setText(adres + " at: "+ str(x) +','+ str(y) )
	 msgBox.setWindowTitle("Gevonden")
	 msgBox.show()
	 msgBox.exec_()       
        
        
