# -*- coding: utf-8 -*-
"""
/***************************************************************************
 geopunt4Qgis
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
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.utils import showPluginHelp
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialog
from geopunt4qgisAdresdialog import geopunt4QgisAdresDialog
from geopunt4QgisPoidialog import geopunt4QgisPoidialog
from about import geopunt4QgisAboutdialog
import os.path


class geopunt4Qgis:
    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(self.plugin_dir, 'i18n', 'geopunt4qgis_{}.qm'.format(locale))
        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)
            if qVersion() > '4.3.3': QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.adresdlg = geopunt4QgisAdresDialog(self.iface)
        self.poiDlg = geopunt4QgisPoidialog(self.iface)
        self.aboutDlg = geopunt4QgisAboutdialog()

    def initGui(self):
        # Create actions that will start plugin configuration
        self.adresAction = QAction(
            QIcon(":/plugins/geopunt4Qgis/images/geopuntAddress.png"),
            QCoreApplication.translate( "geopunt4Qgis" , u"Zoek een Adres"), self.iface.mainWindow())
	self.poiAction = QAction(
            QIcon(":/plugins/geopunt4Qgis/images/geopuntPoi.png"),
            QCoreApplication.translate("geopunt4Qgis" , u"Zoek een Plaats - interesse punt"), self.iface.mainWindow())
	self.aboutAction = QAction(
            QIcon(":/plugins/geopunt4Qgis/images/geopunt.png"),
            QCoreApplication.translate("geopunt4Qgis" , u"Over geopunt4Qgis"), self.iface.mainWindow())
	
        # connect the action to the run method
        self.adresAction.triggered.connect(self.runAdresDlg)
        self.poiAction.triggered.connect(self.runPoiDlg)
        self.aboutAction.triggered.connect(self.runAbout)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.adresAction)
        self.iface.addToolBarIcon(self.poiAction)
        self.iface.addPluginToMenu(u"&geopunt4Qgis", self.adresAction)
        self.iface.addPluginToMenu(u"&geopunt4Qgis", self.poiAction)
        self.iface.addPluginToMenu(u"&geopunt4Qgis", self.aboutAction)

    def unload(self):
        # Remove the plugin menu items and icons
        self.iface.removePluginMenu(u"&geopunt4Qgis", self.adresAction)
        self.iface.removeToolBarIcon(self.adresAction)
        self.iface.removePluginMenu(u"&geopunt4Qgis", self.poiAction)
        self.iface.removeToolBarIcon(self.poiAction)
        self.iface.removePluginMenu(u"&geopunt4Qgis", self.aboutAction)

    def runAdresDlg(self):
        # show the dialog
        self.adresdlg.show()
        # Run the dialog event loop
        result = self.adresdlg.exec_()
        
    def runPoiDlg(self):
	# show the dialog
        self.poiDlg.show()
        # Run the dialog event loop
        result = self.poiDlg.exec_()
        
    def runAbout(self):
	# show the dialog
        self.aboutDlg.show()
        # Run the dialog event loop
        result = self.aboutDlg.exec_()
        