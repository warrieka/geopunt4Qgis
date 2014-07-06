# -*- coding: utf-8 -*-
"""
/***************************************************************************
geopunt4QgisSettingsdialog
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
import os.path

class geopunt4QgisSettingsdialog(QtGui.QDialog):
    def __init__(self):
      QtGui.QDialog.__init__(self)

      # initialize locale
      locale = QtCore.QSettings().value("locale/userLocale")[0:2]
      localePath = os.path.join(os.path.dirname(__file__), 'i18n', 'geopunt4qgis_{}.qm'.format(locale))
      if os.path.exists(localePath):
          self.translator = QtCore.QTranslator()
          self.translator.load(localePath)
          if QtCore.qVersion() > '4.3.3': QtCore.QCoreApplication.installTranslator(self.translator)

      self._initGui()
  
    def _initGui(self):
        ' Set up the user interface from Designer.'
        self.ui = Ui_settingsDlg()
        self.ui.setupUi(self)

        #get and load settings
        self.s = QtCore.QSettings()
        self.loadSettings()
            
        #event handlers, on accept:  save, on reject: return to previous 
        self.accepted.connect(self.saveSettings)	
        self.rejected.connect(self.loadSettings)

    def loadSettings(self):
        'geopunt4Qgis settings'
        #General
        useProxy = int( self.s.value("geopunt4qgis/useProxy" , 0))
            
        if useProxy:
            self.ui.proxyChk.setChecked(1)
            proxyHost = self.s.value("geopunt4qgis/proxyHost" ,"")
            self.ui.hostTxt.setText(proxyHost)
            self.ui.hostTxt.setEnabled(1)
            proxyPort = self.s.value("geopunt4qgis/proxyPort" ,"")
            self.ui.portTxt.setText(proxyPort)
            self.ui.portTxt.setEnabled(1)
        else:
            self.ui.proxyChk.setChecked(0)
          
            timeout = int(  self.s.value("geopunt4qgis/timeout" ,15))
            self.ui.timeOutBox.setValue(timeout)
        
        #geopunt4Qgis AdresDialog settings
        adresSearchOnEdit = int( self.s.value("geopunt4qgis/adresSearchOnEdit" , 1))
        self.ui.adresSearchOnEditChk.setChecked(adresSearchOnEdit)
        
        adresSearchOnEnter = int( self.s.value("geopunt4qgis/adresSearchOnEnter" , 0))
        self.ui.adresSearchOnEnterChk.setChecked(adresSearchOnEnter)
        
        adresSavetoFile = int( self.s.value("geopunt4qgis/adresSavetoFile" , 1))
        self.ui.adresSavetoFileChk.setChecked(adresSavetoFile)
        
        adresSaveMemory = int( self.s.value("geopunt4qgis/adresSaveMemory" , 0))
        self.ui.adresSaveMemoryChk.setChecked(adresSaveMemory)
        
        adreslayerText =  self.s.value("geopunt4qgis/adreslayerText", "geopunt_adres")
        self.ui.adresLayerTxt.setText(adreslayerText)
        
        #geopunt4Qgis ReverseAdres Settings
        reverseSavetoFile = int( self.s.value("geopunt4qgis/reverseSavetoFile", 1))
        self.ui.reverseSavetoFileChk.setChecked(reverseSavetoFile)
        
        reverseSaveMemory = int( self.s.value("geopunt4qgis/reverseSaveMemory", 0))
        self.ui.reverseSaveMemoryChk.setChecked(reverseSaveMemory)
        
        reverseLayerText =  self.s.value("geopunt4qgis/reverseLayerText", "geopunt_reverse_adres")
        self.ui.reverseLayerTxt.setText(reverseLayerText)
        
        #geopunt4Qgis batchGeoCode settings
        batchGeoCodeSavetoFile = int( self.s.value("geopunt4qgis/batchGeoCodeSavetoFile" , 1))
        self.ui.batchSavetoFileChk.setChecked(batchGeoCodeSavetoFile)
        
        batchGeoCodeSavetoMemory = int( self.s.value("geopunt4qgis/batchGeoCodeSavetoMemory", 0))
        self.ui.batchSaveMemoryChk.setChecked(batchGeoCodeSavetoMemory)
        
        batchLayerText = self.s.value("geopunt4qgis/batchLayerText", "adressen_csv")
        self.ui.batchLayerTxt.setText(batchLayerText)
        
        batchMaxRows = int( self.s.value("geopunt4qgis/batchMaxRows", 500 ))
        self.ui.maxRowsSpinBox.setValue(batchMaxRows)	
        
        #PoiDialog settings
        poiSavetoFile = int( self.s.value("geopunt4qgis/poiSavetoFile" , 1))
        self.ui.poiSavetoFileChk.setChecked(poiSavetoFile)
        
        poiSaveMemory = int( self.s.value("geopunt4qgis/poiSaveMemory" , 0))
        self.ui.poiSaveMemoryChk.setChecked(poiSaveMemory)
        
        poilayerText =  self.s.value("geopunt4qgis/poilayerText", "geopunt_poi")
        self.ui.poiLayerTxt.setText(poilayerText)
        
        #geopunt4Qgis gipod settngs
        gipodSavetoFile = int( self.s.value("geopunt4qgis/gipodSavetoFile" , 1))
        self.ui.gipodSavetoFileChk.setChecked(poiSavetoFile)
        
        gipodSaveMemory = int( self.s.value("geopunt4qgis/gipodSaveMemory" , 0))
        self.ui.gipodSaveMemoryChk.setChecked(poiSaveMemory)
        
        #geopunt4Qgis Elevation settings
        samplesSavetoFile = int( self.s.value("geopunt4qgis/samplesSavetoFile" , 1))
        self.ui.samplesSavetoFileChk.setChecked(samplesSavetoFile)
        
        samplesSaveMemory = int( self.s.value("geopunt4qgis/samplesSaveMemory", 0))
        self.ui.samplesSaveMemoryChk.setChecked(samplesSaveMemory)
        
        sampleLayerTxt = self.s.value("geopunt4qgis/sampleLayerTxt", "Elevation_samplepoints")
        self.ui.sampleLayerTxt.setText(sampleLayerTxt)
        
        profileLineSavetoFile = int( self.s.value("geopunt4qgis/profileLineSavetoFile" , 1))
        self.ui.profileLineSavetoFileChk.setChecked(profileLineSavetoFile)
        
        profileLineSaveMemory = int( self.s.value("geopunt4qgis/profileLineSaveMemory", 0))
        self.ui.profileLineSaveMemoryChk.setChecked(profileLineSaveMemory)
        
        profileLineLayerTxt = self.s.value("geopunt4qgis/profileLineLayerTxt", "Elevation_profiles")
        self.ui.profileLineLayerTxt.setText(profileLineLayerTxt)
        
    def saveSettings(self):
        'save all settings to registry'
        #General
        if self.ui.proxyChk.isChecked():
            proxyHost = self.ui.hostTxt.text()
            self.s.setValue("geopunt4qgis/proxyHost", proxyHost)
            proxyPort = self.ui.portTxt.text()
            self.s.setValue("geopunt4qgis/proxyPort" , proxyPort)
            self.s.setValue("geopunt4qgis/useProxy" , 1)
        else:
            self.s.setValue("geopunt4qgis/proxyHost", "")
            self.s.setValue("geopunt4qgis/proxyPort" , "")
            self.s.setValue("geopunt4qgis/useProxy" , 0)

        timeout =  self.ui.timeOutBox.value()
        self.s.setValue("geopunt4qgis/timeout" , timeout )
        
        #'save geopunt4QgisAdresDialog settings'
        adresSearchOnEdit = int( self.ui.adresSearchOnEditChk.isChecked())
        self.s.setValue("geopunt4qgis/adresSearchOnEdit" , adresSearchOnEdit)
        
        adresSearchOnEnter = int( self.ui.adresSearchOnEnterChk.isChecked())
        self.s.setValue("geopunt4qgis/adresSearchOnEnter" , adresSearchOnEnter)
        
        adresSavetoFile = int( self.ui.adresSavetoFileChk.isChecked())
        self.s.setValue("geopunt4qgis/adresSavetoFile" , adresSavetoFile)
        
        adresSaveMemory = int( self.ui.adresSaveMemoryChk.isChecked())
        self.s.setValue("geopunt4qgis/adresSaveMemory" , adresSaveMemory)
        
        adreslayerText =  self.ui.adresLayerTxt.text()
        self.s.setValue("geopunt4qgis/adreslayerText", adreslayerText)
        
        #geopunt4Qgis ReverseAdres Settings
        reverseSavetoFile = int( self.ui.reverseSavetoFileChk.isChecked())
        self.s.setValue("geopunt4qgis/reverseSavetoFile" , reverseSavetoFile)
        
        reverseSaveMemory = int( self.ui.reverseSaveMemoryChk.isChecked())
        self.s.setValue("geopunt4qgis/reverseSaveMemory" , reverseSaveMemory)
        
        reverseLayerText =  self.ui.reverseLayerTxt.text()
        self.s.setValue("geopunt4qgis/reverseLayerText", reverseLayerText)
        
        #batchGeoCode
        batchGeoCodeSavetoFile = int( self.ui.batchSavetoFileChk.isChecked())
        self.s.setValue("geopunt4qgis/batchGeoCodeSavetoFile" , batchGeoCodeSavetoFile)
        
        batchGeoCodeSavetoMemory = int( self.ui.batchSaveMemoryChk.isChecked())
        self.s.setValue("geopunt4qgis/batchGeoCodeSavetoMemory" , batchGeoCodeSavetoMemory)
        
        batchLayerText =  self.ui.batchLayerTxt.text()
        self.s.setValue("geopunt4qgis/batchLayerText", batchLayerText)	
        
        batchMaxRows = int( self.ui.maxRowsSpinBox.value())
        self.s.setValue("geopunt4qgis/batchMaxRows", batchMaxRows )
        
        #geopunt4QgisPoiDialog settings
        poiSavetoFile = int( self.ui.poiSavetoFileChk.isChecked())
        self.s.setValue("geopunt4qgis/poiSavetoFile" , poiSavetoFile)
        
        poiSaveMemory = int( self.ui.poiSaveMemoryChk.isChecked())
        self.s.setValue("geopunt4qgis/poiSaveMemory" , poiSaveMemory)
        
        poiLayerText =  self.ui.poiLayerTxt.text()
        self.s.setValue("geopunt4qgis/poiLayerText", poiLayerText)
        
        #gipod settings
        gipodSavetoFile = int( self.ui.gipodSavetoFileChk.isChecked())
        self.s.setValue("geopunt4qgis/gipodSavetoFile" , gipodSavetoFile)
        
        gipodSaveMemory = int( self.ui.gipodSaveMemoryChk.isChecked())
        self.s.setValue("geopunt4qgis/gipodSaveMemory" , gipodSaveMemory)
        
        #geopunt4Qgis Elevation settings
        samplesSavetoFile = int( self.ui.samplesSavetoFileChk.isChecked() )
        self.s.setValue("geopunt4qgis/samplesSavetoFile", samplesSavetoFile)
        
        samplesSaveMemory = int( self.ui.samplesSaveMemoryChk.isChecked() )
        self.s.value("geopunt4qgis/samplesSaveMemory", samplesSaveMemory)
        
        sampleLayerTxt = self.ui.sampleLayerTxt.text()
        self.s.setValue("geopunt4qgis/sampleLayerTxt", sampleLayerTxt)
        
        profileLineSavetoFile = int( self.ui.profileLineSavetoFileChk.isChecked() )
        self.s.setValue("geopunt4qgis/profileLineSavetoFile" , profileLineSavetoFile )
        
        profileLineSaveMemory = int( self.ui.profileLineSaveMemoryChk.isChecked() )
        self.s.setValue("geopunt4qgis/profileLineSaveMemory", profileLineSaveMemory )
        
        profileLineLayerTxt = self.ui.profileLineLayerTxt.text()
        self.s.setValue("geopunt4qgis/profileLineLayerTxt",  profileLineLayerTxt)
        
