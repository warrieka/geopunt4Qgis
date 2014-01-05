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
from qgis.gui import  QgsMessageBar
# Initialize Qt resources from file resources.py
import resources_rc
# Import the code for the dialogs
from geopunt4qgisAdresdialog import geopunt4QgisAdresDialog
from geopunt4QgisPoidialog import geopunt4QgisPoidialog
from reverseAdresMapTool import reverseAdresMapTool
from geopunt4QgisAbout import geopunt4QgisAboutdialog
from geopunt4QgisSettingsdialog import geopunt4QgisSettingsdialog
from geopunt4QgisBatchGeoCode import geopunt4QgisBatcGeoCodedialog
#import from libraries
import geopunt, geometryhelper
import os.path, time

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
        self.settingsDlg = geopunt4QgisSettingsdialog()
        self.aboutDlg = geopunt4QgisAboutdialog()
        
        self.batchgeoDlg = geopunt4QgisBatcGeoCodedialog(self.iface) 
        
        #geopunt adres and geometry object
        self.adres = geopunt.Adres()
        self.gh = geometryhelper.geometryHelper(self.iface)

    def initGui(self):
        #get settings
        self.s = QSettings()
        self.loadSettings()
        
        # Create actions that will start plugin configuration
        self.adresAction = QAction(
            QIcon(":/plugins/geopunt4Qgis/images/geopuntAddress.png"),
            QCoreApplication.translate( "geopunt4Qgis" , u"Zoek een Adres"), self.iface.mainWindow())
	self.reverseAction = QAction( 
	    QIcon(":/plugins/geopunt4Qgis/images/geopuntReverse.png"),
            QCoreApplication.translate("geopunt4Qgis", u"Prik een Adres op kaart"), 
            self.iface.mainWindow())
	self.batchAction = QAction(QIcon(":/plugins/geopunt4Qgis/images/geopuntBatchgeocode.png"),
	    QCoreApplication.translate("geopunt4Qgis", u"CSV-adresbestanden geocoderen"),
	    self.iface.mainWindow())
	self.poiAction = QAction(
            QIcon(":/plugins/geopunt4Qgis/images/geopuntPoi.png"),
            QCoreApplication.translate("geopunt4Qgis" , u"Zoek een Plaats - interesse punt"), 
	    self.iface.mainWindow())
	self.settingsAction = QAction(
            QIcon(":/plugins/geopunt4Qgis/images/geopuntSettings.png"),
            QCoreApplication.translate("geopunt4Qgis" , u"Instellingen"), self.iface.mainWindow())
	self.aboutAction = QAction(
            QIcon(":/plugins/geopunt4Qgis/images/geopunt.png"),
            QCoreApplication.translate("geopunt4Qgis" , u"Over geopunt4Qgis"), self.iface.mainWindow())
	
        # connect the action to the run method
        self.adresAction.triggered.connect(self.runAdresDlg)
        self.reverseAction.triggered.connect( self.reverse )
        self.batchAction.triggered.connect(self.runBatch)
        self.poiAction.triggered.connect(self.runPoiDlg)
        self.settingsAction.triggered.connect(self.runSettingsDlg)
        self.aboutAction.triggered.connect(self.runAbout)

        # Add to toolbar button
        self.iface.addToolBarIcon(self.adresAction)
        self.iface.addToolBarIcon(self.reverseAction)
        self.iface.addToolBarIcon(self.batchAction)
        self.iface.addToolBarIcon(self.poiAction)
        
        # Add to Menu
        self.iface.addPluginToMenu(u"&geopunt4Qgis", self.adresAction)
        self.iface.addPluginToMenu(u"&geopunt4Qgis", self.reverseAction)
        self.iface.addPluginToMenu(u"&geopunt4Qgis", self.batchAction)
        self.iface.addPluginToMenu(u"&geopunt4Qgis", self.poiAction)
        self.iface.addPluginToMenu(u"&geopunt4Qgis", self.settingsAction)
        self.iface.addPluginToMenu(u"&geopunt4Qgis", self.aboutAction)


    def unload(self):
        # Remove the plugin menu items and icons
        self.iface.removePluginMenu(u"&geopunt4Qgis", self.adresAction)
        self.iface.removeToolBarIcon(self.adresAction)
        self.iface.removePluginMenu(u"&geopunt4Qgis", self.poiAction)
        self.iface.removeToolBarIcon(self.poiAction)
        self.iface.removePluginMenu(u"&geopunt4Qgis", self.reverseAction)
	self.iface.removeToolBarIcon(self.reverseAction)
	self.iface.removePluginMenu(u"&geopunt4Qgis", self.batchAction)
	self.iface.removeToolBarIcon(self.batchAction)
        self.iface.removePluginMenu(u"&geopunt4Qgis", self.aboutAction)
        self.iface.removePluginMenu(u"&geopunt4Qgis", self.settingsAction)
	
    def loadSettings(self):
	self.saveToFile_reverse = int( self.s.value("geopunt4qgis/reverseSavetoFile", 0))
        self.layerName_reverse  = self.s.value("geopunt4qgis/reverseLayerText", "geopunt_reverse_adres")
        
    def runSettingsDlg(self):
      # show the dialog
	self.settingsDlg.show()
	# Run the dialog event loop
        result = self.settingsDlg.exec_()
	if result:
	  self.loadSettings()
	  self.adresdlg.loadSettings()
	  self.poiDlg.loadSettings()
	  self.batchgeoDlg.loadSettings()
        
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
        
    def runBatch(self):
	# show the dialog
	self.batchgeoDlg.show()
	# Run the dialog event loop
        self.batchgeoDlg.exec_()
	  
    def runAbout(self):
	# show the dialog
        self.aboutDlg.show()
        # Run the dialog event loop
        result = self.aboutDlg.exec_()
        
    def reverse(self):
	self.iface.messageBar().pushMessage(
	  QCoreApplication.translate("geopunt4Qgis" ,"Zoek een Adres: "), 
	  QCoreApplication.translate("geopunt4Qgis" ,"Klik op de kaart om het adres op te vragen")
				     ,level=QgsMessageBar.INFO)
        reverseAdresTool = reverseAdresMapTool( self.iface, self._reverseAdresCallback ) 
        self.iface.mapCanvas().setMapTool(reverseAdresTool)
        
    def _reverseAdresCallback(self, point):
	lam72 = QgsCoordinateReferenceSystem(31370)
	mapCrs = self.iface.mapCanvas().mapRenderer().destinationCrs()
	xform = QgsCoordinateTransform( mapCrs, lam72 )
	lam72pt = xform.transform( point )
	
	#to clear or not clear that is the question
	self.iface.messageBar().clearWidgets()

	#fetch Location from geopunt
	adres = self.adres.fetchLocation(lam72pt.x().__str__() +","+ lam72pt.y().__str__(), 1)
	
	if len(adres) and adres.__class__ is list:
	  #only one result in list, was set in request
	  FormattedAddress = adres[0]["FormattedAddress"]
	  
	  #add a button to the messageBar widget
	  widget = self.iface.messageBar().createMessage(
	    QCoreApplication.translate("geopunt4Qgis" ,"Resultaat: "), FormattedAddress)
	  button = QPushButton(widget)
	  button.clicked.connect(lambda: self._addReverse( adres[0] ) )
	  button.setText("Voeg toe")
	  widget.layout().addWidget(button)
	  self.iface.messageBar().clearWidgets()
	  self.iface.messageBar().pushWidget( widget, level=QgsMessageBar.INFO)
	
	elif len(adres) == 0:
	  self.iface.messageBar().pushMessage( 
	    QCoreApplication.translate("geopunt4Qgis","Waarschuwing"),
	    QCoreApplication.translate("geopunt4Qgis","Geen resultaten gevonden"), 
		        level=QgsMessageBar.INFO, duration=3)
	  
	elif adres.__class__ is str:
	  self.iface.messageBar().pushMessage(
	    QCoreApplication.translate("geopunt4Qgis","Waarschuwing"),
			adres, level=QgsMessageBar.WARNING)
	else:
	  self.iface.messageBar().pushMessage("Error", 
	    QCoreApplication.translate("geopunt4Qgis","onbekende fout"),
			level=QgsMessageBar.CRITICAL)
	  
    def _addReverse(self, adres):
	formattedAddress, locationType = adres["FormattedAddress"] , adres["LocationType"]
	xlam72, ylam72 = adres["Location"]["X_Lambert72"] , adres["Location"]["Y_Lambert72"]
	
	xy = self.gh.prjPtToMapCrs([xlam72, ylam72], 31370)
	self.gh.save_adres_point(xy, formattedAddress, locationType, layername=self.layerName_reverse,
			  saveToFile=self.saveToFile_reverse , sender=self.iface.mainWindow()  )
	self.iface.messageBar().popWidget()	
        