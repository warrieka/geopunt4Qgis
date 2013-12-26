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
from ui_geopunt4QgisSettings import Ui_settingsDlg

class geopunt4QgisSettingsdialog(QtGui.QDialog):
    def __init__(self, iface):
	QtGui.QDialog.__init__(self)
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
	
	# Set up the user interface from Designer.
	self.ui = Ui_geopunt4QgisPoiDlg()
	self.ui.setupUi(self)
	
	self.loadSettings()
	
	#event handlers 
	self.accepted.connect(self.saveSettings)
	
    def loadSettings(self):
      pass
	
    def saveSettings(self):
      pass