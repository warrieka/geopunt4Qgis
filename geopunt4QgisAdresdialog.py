# -*- coding: utf-8 -*-
"""
/***************************************************************************
geopunt4qgisdialog
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
from __future__ import absolute_import
from qgis.PyQt.QtCore import Qt, QSettings, QCoreApplication, QTranslator, QStringListModel
from qgis.PyQt.QtWidgets import QDialog, QCompleter, QSizePolicy, QPushButton, QDialogButtonBox, QInputDialog, QMessageBox
from qgis.PyQt.QtGui import QColor
from .ui_geopunt4qgis import Ui_geopunt4Qgis
from qgis.gui import QgsMessageBar, QgsVertexMarker
from qgis.core import Qgis, QgsPointXY
import os, json, webbrowser
from .geopunt import Adres, basisregisters, internet_on
from .tools.geometry import geometryHelper
from .tools.settings import settings

class geopunt4QgisAdresDialog(QDialog):
    def __init__(self, iface):
        QDialog.__init__(self, None)
        self.setWindowFlags( self.windowFlags() & ~Qt.WindowContextHelpButtonHint )
        self.iface = iface
    
        # initialize locale
        locale = QSettings().value("locale/userLocale", "nl")
        if not locale: locale == 'nl' 
        else: locale = locale[0:2]
        localePath = os.path.join(os.path.dirname(__file__), 'i18n', 'geopunt4qgis_{}.qm'.format(locale))
        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)
            QCoreApplication.installTranslator(self.translator)
    
        self._initGui()

    def _initGui(self):
        """setup the user interface"""
        self.ui = Ui_geopunt4Qgis()
        self.ui.setupUi(self)
        
        #get settings
        self.s = QSettings()
        self.loadSettings()
        
        #setup geometryHelper object
        self.gh = geometryHelper(self.iface)
        
        #create graphicsLayer
        self.graphicsLayer = []

        self.firstShow = True
        
        self.completer = QCompleter(self)
        self.completerModel = QStringListModel(self)
        self.ui.gemeenteBox.setCompleter(self.completer )
        self.completer.setModel(self.completerModel )
        self.completer.setCaseSensitivity(False)

        #setup a message bar
        self.bar = QgsMessageBar() 
        self.bar.setSizePolicy( QSizePolicy.Minimum, QSizePolicy.Fixed )
        self.ui.verticalLayout.addWidget(self.bar)
        
        self.ui.buttonBox.addButton( QPushButton("Sluiten"), QDialogButtonBox.RejectRole )
        for btn in self.ui.buttonBox.buttons():
            btn.setAutoDefault(0)
            
        #event handlers 
        if self.adresSearchOnEnter:
          self.ui.zoekText.returnPressed.connect(self.onZoekActivated)
        else:
          self.ui.zoekText.textEdited.connect(self.onZoekActivated)
        self.ui.gemeenteBox.currentIndexChanged.connect(self.onZoekActivated)
        self.ui.resultLijst.itemDoubleClicked.connect(self.onItemActivated)
        self.ui.resultLijst.itemClicked.connect(self.onItemClick)
        self.ui.ZoomKnop.clicked.connect(self.onZoomKnopClick)
        self.ui.Add2mapKnop.clicked.connect(self.onAdd2mapKnopClick)
        self.ui.buttonBox.helpRequested.connect(self.openHelp)
        self.finished.connect(self.clean )
        
    def loadSettings(self):
        self.saveToFile = int( self.s.value("geopunt4qgis/adresSavetoFile" , 1))
        layerName =  self.s.value("geopunt4qgis/adreslayerText", "")
        if layerName :
           self.layerName= layerName
        self.adresSearchOnEnter = int( self.s.value("geopunt4qgis/adresSearchOnEnter" , 0))
        self.timeout =  int(  self.s.value("geopunt4qgis/timeout" ,15))

        s = settings()
        self.proxy = s.proxyUrl
        self.proxyInfo = s.proxyInfo

        self.startDir = self.s.value("geopunt4qgis/startDir", os.path.expanduser("~") )
        self.gp = Adres(self.timeout, self.proxy)
        
    # overwrite
    def show(self):
        QDialog.show(self)
        self.setWindowModality(0)

        QMessageBox.question(self.iface.mainWindow(), "DEBUG", str(self.proxyInfo), QMessageBox.Ok )    
           
        if self.firstShow: 
            self.am =  basisregisters.adresMatch(self.timeout, self.proxy)
            gemeenteNamen =  [n["Naam"] for n in self.am.gemeenten()]
            
            self.ui.gemeenteBox.addItems( gemeenteNamen )  
            self.completerModel.setStringList(gemeenteNamen )
            self.ui.gemeenteBox.setEditText(QCoreApplication.translate("geopunt4QgisAdresDialog", "gemeente"))
            self.ui.gemeenteBox.setStyleSheet('QComboBox {color: #808080}')
            self.ui.gemeenteBox.setFocus()
            self.firstShow = False
        
    def openHelp(self):
        webbrowser.open_new_tab("http://www.geopunt.be/voor-experts/geopunt-plug-ins/functionaliteiten/zoek-een-adres")
    
    def onZoekActivated(self):
        self._clearGraphicsLayer()
        self.bar.clearWidgets()
    
        gemeente = self.ui.gemeenteBox.currentText() 
        if gemeente != QCoreApplication.translate("geopunt4QgisAdresDialog","gemeente"):
          self.ui.gemeenteBox.setStyleSheet('QComboBox {color: #000000}')
    
          txt = self.ui.zoekText.text() +", "+ gemeente
    
          suggesties = self.gp.fetchSuggestion( txt , 25 )
      
          self.ui.resultLijst.clear()
          if type( suggesties ) is list and len(suggesties) != 0:
            self.ui.resultLijst.addItems(suggesties)
            if len(suggesties) == 1:
              self.ui.resultLijst.setCurrentRow(0)

    def onItemActivated( self, item):
        txt = item.text()
        self._zoomLoc(txt)
    
    def onItemClick(self, item):
        txt = item.text()
        streetNr = txt.split(",")[:-1]
        self.ui.zoekText.setText( ",".join(streetNr)  )
    
    def onZoomKnopClick(self):
        item = self.ui.resultLijst.currentItem()
        if item:
          self._zoomLoc(item.text())

    def onAdd2mapKnopClick(self):
        item = self.ui.resultLijst.currentItem()
        if item:
          self._addToMap(item.text())
      
    def _clearGraphicsLayer(self):
        for graphic in  self.graphicsLayer: 
          self.iface.mapCanvas().scene().removeItem(graphic)
        self.graphicsLayer = []
    
    def _zoomLoc(self, txt):
        self._clearGraphicsLayer()
        locations = self.gp.fetchLocation(txt)
        if type( locations ) is list and len(locations):
            loc = locations[0]
        
            LowerLeftX = loc['BoundingBox']['LowerLeft']['X_Lambert72']
            LowerLeftY = loc['BoundingBox']['LowerLeft']['Y_Lambert72']
            UpperRightX = loc['BoundingBox']['UpperRight']['X_Lambert72']
            UpperRightY = loc['BoundingBox']['UpperRight']['Y_Lambert72']
        
            self.gh.zoomtoRec(QgsPointXY(LowerLeftX,LowerLeftY),QgsPointXY(UpperRightX, UpperRightY), 31370)
        
            xlb, ylb = loc["Location"]["X_Lambert72"], loc["Location"]["Y_Lambert72"]
            x, y = self.gh.prjPtToMapCrs(QgsPointXY( xlb , ylb), 31370)
        
            m = QgsVertexMarker(self.iface.mapCanvas())
            self.graphicsLayer.append(m)
            m.setCenter(QgsPointXY(x,y))
            m.setColor(QColor(255,255,0))
            m.setIconSize(1)
            m.setIconType(QgsVertexMarker.ICON_BOX) 
            m.setPenWidth(9)
        
        elif type( locations ) is str:
          self.bar.pushMessage(
            QCoreApplication.translate("geopunt4QgisAdresDialog","Waarschuwing"), 
                locations, level=Qgis.Warning, duration=3)
        else:
          self.bar.pushMessage("Error", 
            QCoreApplication.translate("geopunt4QgisAdresDialog","onbekende fout"),
                level=Qgis.Critical, duration=3)
        
    def _addToMap(self, txt):
        if not self.layernameValid(): return
        locations = self.gp.fetchLocation(txt)
        if type( locations ) is list and len(locations):
            loc = locations[0]
            x, y = loc["Location"]["X_Lambert72"], loc["Location"]["Y_Lambert72"]
            adres = loc["FormattedAddress"]
            LocationType = loc["LocationType"]
        
            pt = self.gh.prjPtToMapCrs(QgsPointXY( x, y), 31370)
        
            self.gh.save_adres_point( pt, adres, typeAddress=LocationType, 
              layername=self.layerName, saveToFile=self.saveToFile, sender=self, 
              startFolder= os.path.join(self.startDir, self.layerName))
      
    def layernameValid(self):   
        if not hasattr(self, 'layerName'):
          layerName, accept = QInputDialog.getText(None,
              QCoreApplication.translate("geopunt4Qgis", 'Laag toevoegen'),
              QCoreApplication.translate("geopunt4Qgis", 'Geef een naam voor de laag op:') )
          if accept == False: 
             return False
          else: 
             self.layerName = layerName
        return True
      
    def clean(self):
        self.bar.clearWidgets()
        self.ui.resultLijst.clear()
        self.ui.zoekText.setText("")
        self.ui.gemeenteBox.setEditText(QCoreApplication.translate("geopunt4QgisAdresDialog" ,"gemeente"))
        self.ui.gemeenteBox.setStyleSheet('QComboBox {color: #808080}')
        self._clearGraphicsLayer()
    
