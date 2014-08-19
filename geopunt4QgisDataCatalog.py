# -*- coding: utf-8 -*-
"""
/***************************************************************************
geopunt4QgisDataCatalog
                A QGIS plugin
"Tool om geopunt in QGIS te gebruiken"
                -------------------
    begin                : 2014-07-15
    copyright            : (C) 2014 by Kay Warrie
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
from ui_geopunt4QgisDataCatalog import Ui_geopunt4QgisDataCatalogDlg
from qgis.core import *
from qgis.gui import QgsMessageBar 
from geopunt import internet_on
import metadata, os, json, webbrowser, sys
import geometryhelper as gh

class geopunt4QgisDataCatalog(QtGui.QDialog):
    def __init__(self, iface):
        QtGui.QDialog.__init__(self, None)
        self.setWindowFlags( self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint )
        #self.setWindowFlags( self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
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
        """setup the user interface"""
        self.ui = Ui_geopunt4QgisDataCatalogDlg()
        self.ui.setupUi(self)
        
        #get settings
        self.s = QtCore.QSettings()
        self.loadSettings()

        self.gh = gh.geometryHelper( self.iface )
        
        #setup a message bar
        self.bar = QgsMessageBar() 
        self.bar.setSizePolicy( QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed )
        self.ui.verticalLayout.addWidget(self.bar)
        
        self.ui.buttonBox.addButton( QtGui.QPushButton("Sluiten"), QtGui.QDialogButtonBox.RejectRole )
        
        #vars
        self.firstShow = True
        self.wms = None
        self.wfs = None
        self.dl = None
        self.zoek = ''
        self.bronnen = None 
        
        self.model = QtGui.QStandardItemModel( self )
        self.proxyModel = QtGui.QSortFilterProxyModel(self)
        self.proxyModel.setSourceModel(self.model)
        self.ui.resultView.setModel( self.proxyModel )
        
        self.completer = QtGui.QCompleter( self )
        self.completerModel = QtGui.QStringListModel( self)
        self.ui.zoekTxt.setCompleter( self.completer )
        self.completer.setModel( self.completerModel )
        
        #eventhandlers 
        self.ui.zoekBtn.clicked.connect(self.onZoekClicked)
        self.ui.addWMSbtn.clicked.connect(self.addWMS)
        self.ui.addWFSbtn.clicked.connect(self.addWFS)
        self.ui.DLbtn.clicked.connect(lambda: self.openUrl(self.dl))
        self.ui.resultView.clicked.connect(self.resultViewClicked)
        self.ui.modelFilterCbx.currentIndexChanged.connect(self.modelFilterCbxIndexChanged)
        self.ui.filterWgt.setHidden(1)
        
        self.finished.connect(self.clean)

    def loadSettings(self):
        self.timeout =  int( self.s.value("geopunt4qgis/timeout" ,15))
        if int( self.s.value("geopunt4qgis/useProxy" , 0)):
            self.proxy = self.s.value("geopunt4qgis/proxyHost" ,"")
            self.port = self.s.value("geopunt4qgis/proxyPort" ,"")
        else:
            self.proxy = ""
            self.port = ""
        self.md = metadata.MDReader( self.timeout, self.proxy, self.port )
            

    def _setModel(self, records):   
        self.model.clear()
         
        for rec in records:
            title = QtGui.QStandardItem( rec['title'] )         #0
            wms = QtGui.QStandardItem( rec['wms'] )             #1
            downloadLink = QtGui.QStandardItem(rec['download']) #2
            id = QtGui.QStandardItem( rec['uuid'] )             #3
            abstract  = QtGui.QStandardItem( rec['abstract'] )  #4
            wfs =     QtGui.QStandardItem( rec['wfs'] )         #5
            self.model.appendRow([title,wms,downloadLink,id,abstract,wfs])

    #overwrite
    def show(self):
        QtGui.QDialog.show(self)
        self.setWindowModality(0)
        if self.firstShow:
             inet = internet_on( proxyUrl=self.proxy, port=self.port, timeout=self.timeout )
             if inet:
                self.ui.GDIThemaCbx.addItems( ['']+ self.md.list_GDI_theme() )
                self.ui.organisatiesCbx.addItems( ['']+ self.md.list_organisations() )
                keywords = sorted( self.md.list_suggestionKeyword() ) 
                self.completerModel.setStringList( keywords )
                self.bronnen = self.md.list_bronnen()
                self.ui.bronCbx.addItems( ['']+ [ n[1] for n in self.bronnen] )
                self.ui.typeCbx.addItems(['']+  [ n[0] for n in self.md.dataTypes])                
                
                self.ui.INSPIREannexCbx.addItems( ['']+ self.md.inspireannex )
                self.ui.INSPIREserviceCbx.addItems( ['']+ self.md.inspireServiceTypes )
                self.ui.INSPIREthemaCbx.addItems( ['']+ self.md.list_inspire_theme() )
                self.firstShow = False      
             else:
                self.bar.pushMessage(
                  QtCore.QCoreApplication.translate("geopunt4QgisPoidialog", "Waarschuwing "), 
                  QtCore.QCoreApplication.translate("geopunt4QgisPoidialog", 
                    "Kan geen verbing maken met het internet."), level=QgsMessageBar.WARNING, duration=3)
      
    #eventhandlers
    def resultViewClicked(self):
        if self.ui.resultView.selectedIndexes(): 
           row = self.ui.resultView.selectedIndexes()[0].row()  
           
           title    = self.proxyModel.data( self.proxyModel.index( row, 0) )
           self.wms = self.proxyModel.data( self.proxyModel.index( row, 1) )
           self.dl  = self.proxyModel.data( self.proxyModel.index( row, 2) )
           self.wfs = self.proxyModel.data( self.proxyModel.index( row, 5) )
           uuid     = self.proxyModel.data( self.proxyModel.index( row, 3) )
           abstract = self.proxyModel.data( self.proxyModel.index( row, 4) )
           
           self.ui.descriptionText.setText(
             """<h3>%s</h3><div>%s</div><br/><br/>
             <a href='https://metadata.geopunt.be/zoekdienst/apps/tabsearch/index.html?uuid=%s'>
             Ga naar fiche</a>""" %  (title , abstract, uuid ))
           
           if self.wms: self.ui.addWMSbtn.setEnabled(1)
           else: self.ui.addWMSbtn.setEnabled(0)
           
           if self.wfs: self.ui.addWFSbtn.setEnabled(1)
           else: self.ui.addWFSbtn.setEnabled(0)
           
           if self.dl: self.ui.DLbtn.setEnabled(1)
           else: self.ui.DLbtn.setEnabled(0)
        
    def onZoekClicked(self):
        self.zoek = self.ui.zoekTxt.currentText()
        self.search()  
      
    def modelFilterCbxIndexChanged(self):
        value = self.ui.modelFilterCbx.currentIndex()
        if value == 1:
           self.filterModel(1)
        elif value == 2:
           self.filterModel(5)
        elif value == 3:
           self.filterModel(2)
        else:
          self.filterModel()
          
    def filterModel(self, col=None):
        if col != None:
           self.proxyModel.setFilterKeyColumn(col)
           expr = QtCore.QRegExp("?*", QtCore.Qt.CaseInsensitive, QtCore.QRegExp.Wildcard )
           self.proxyModel.setFilterRegExp(expr)
        else:
           self.proxyModel.setFilterRegExp(None)
        
    def search(self):       
        if self.ui.filterBox.isChecked():
            themekey= self.ui.GDIThemaCbx.currentText()
            orgName= self.ui.organisatiesCbx.currentText()
            dataTypes= [ n[1] for n in self.md.dataTypes if n[0] == self.ui.typeCbx.currentText()] 
            if dataTypes != []: dataType= dataTypes[0]
            else: dataType=''
            siteIds = [ n[0] for n in self.bronnen if n[1] == self.ui.bronCbx.currentText() ]
            if siteIds != []: siteId= siteIds[0]
            else: siteId =''
            inspiretheme= self.ui.INSPIREthemaCbx.currentText()
            inspireannex= self.ui.INSPIREannexCbx.currentText()
            inspireServiceType= self.ui.INSPIREserviceCbx.currentText()
            searchResult = metadata.MDdata( 
              self.md.searchAll(self.zoek, themekey, orgName, dataType, siteId, inspiretheme, inspireannex, inspireServiceType))
        else:
            searchResult = metadata.MDdata( self.md.searchAll( self.zoek ))
        
        self.ui.countLbl.setText( "Aantal gevonden: %s" % searchResult.count  )
        self.ui.descriptionText.setText('')
        self._setModel(searchResult.records)
        if searchResult.count == 0:
           self.bar.pushMessage(
             QtCore.QCoreApplication.translate("geopunt4QgisPoidialog", "Waarschuwing "), 
             QtCore.QCoreApplication.translate("geopunt4QgisPoidialog", "Er werden geen resultaten gevonde voor deze zoekopdracht"),
                duration=5)

    def openUrl(self, url):
        if url: webbrowser.open_new_tab( url.encode("utf-8") )

    def addWMS(self):
        if self.wms == None: return
      
        crs = self.iface.mapCanvas().mapRenderer().destinationCrs().authid()
        if crs != 'EPSG:31370' or  crs != 'EPSG:3857' or  crs != 'EPSG:3043':
           crs = 'EPSG:31370' 
        try:   
          lyrs =  metadata.getWmsLayerNames( self.wms , self.proxy, self.port) 
        except:
          self.bar.pushMessage( "Error", str( sys.exc_info()[1]), level=QgsMessageBar.CRITICAL, duration=10)
          return 
        if len(lyrs) == 0:
            self.bar.pushMessage("WMS", 
            QtCore.QCoreApplication.translate("geopunt4QgisDataCatalog", 
                      "Kan geen lagen vinden in: %s" % self.wms ), level=QgsMessageBar.WARNING, duration=10)
            return 
        elif len(lyrs) == 1:
            layerTitle = lyrs[0][1]
        else:
            layerTitle, accept = QtGui.QInputDialog.getItem(self, "WMS toevoegen", 
                                              "Kies een laag om toe te voegen", [n[1] for n in lyrs], editable=0) 
            if not accept: return
        
        layerName = [n[0] for n in lyrs if n[1] == layerTitle ][0]
        style = [n[2] for n in lyrs if n[1] == layerTitle ][0]
        url= self.wms.split('?')[0]

        if crs != 'EPSG:31370' or  crs != 'EPSG:3857' : 
           crs = 'EPSG:31370' 
        wmsUrl = "url=%s&layers=%s&format=image/png&styles=%s&crs=%s" % (url, layerName, style , crs) 
        
        try:
            rlayer = QgsRasterLayer(wmsUrl, layerTitle, 'wms') 
            if rlayer.isValid():
               rlayer.renderer().setOpacity(0.8)
               QgsMapLayerRegistry.instance().addMapLayer(rlayer)
            else:  
                self.bar.pushMessage("Error", 
                QtCore.QCoreApplication.translate("geopunt4QgisDataCatalog", "Kan WMS niet laden"), 
                level=QgsMessageBar.CRITICAL, duration=10) 
        except: 
            self.bar.pushMessage("Error", str( sys.exc_info()[1] ), level=QgsMessageBar.CRITICAL, duration=10)
            return 
      
    def addWFS(self):    
        if self.wfs == None: return
        try:
            lyrs =  metadata.getWFSLayerNames( self.wfs, self.proxy, self.port)
        except:
            self.bar.pushMessage( "Error", str( sys.exc_info()[1]), level=QgsMessageBar.CRITICAL, duration=10)
            return 
        if len(lyrs) == 0:
            self.bar.pushMessage("WFS", 
            QtCore.QCoreApplication.translate("geopunt4QgisDataCatalog", 
                      "Kan geen lagen vinden in: %s" % self.wfs ), level=QgsMessageBar.WARNING, duration=10)
            return
        elif len(lyrs) == 1:
            layerTitle = lyrs[0][1]
        else:
            layerTitle, accept = QtGui.QInputDialog.getItem(self, "WFS toevoegen", 
                                "Kies een laag om toe te voegen", [n[1] for n in lyrs], editable=0) 
            if not accept: return
          
        layerName = [n[0] for n in lyrs if n[1] == layerTitle ][0]
        crs = [n[2] for n in lyrs if n[1] == layerTitle ][0]
        url =  self.wfs.split('?')[0]
        wfsUri = metadata.makeWFSuri( url, layerName, crs )
        
        try:
            vlayer = QgsVectorLayer( wfsUri, layerTitle , "WFS")
            QgsMapLayerRegistry.instance().addMapLayer(vlayer)
        except: 
            self.bar.pushMessage("Error", str( sys.exc_info()[1] ), level=QgsMessageBar.CRITICAL, duration=10)
            return 
          
    def clean(self):
        self.model.clear()
        self.wms = None
        self.wfs = None
        self.dl = None
        self.ui.zoekTxt.setCurrentIndex(0)
        self.ui.descriptionText.setText('')
        self.ui.countLbl.setText( "")
        self.ui.msgLbl.setText("" )
        self.ui.DLbtn.setEnabled(0)
        self.ui.addWFSbtn.setEnabled(0)
        self.ui.addWMSbtn.setEnabled(0)