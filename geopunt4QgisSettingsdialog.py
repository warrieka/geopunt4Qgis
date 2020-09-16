# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import Qt, QSettings, QTranslator, QCoreApplication 
from qgis.PyQt.QtWidgets import QDialog, QPushButton, QDialogButtonBox, QFileDialog
from .ui_geopunt4QgisSettings import Ui_settingsDlg
import os

class geopunt4QgisSettingsDialog(QDialog):
    def __init__(self):
      QDialog.__init__(self, None)
      self.setWindowFlags( self.windowFlags() & ~Qt.WindowContextHelpButtonHint )
      self.setWindowFlags( self.windowFlags() | Qt.WindowStaysOnTopHint)
        
      # initialize locale
      locale = QSettings().value("locale/userLocale", "nl")
      if not locale: locale == 'en'
      else: locale = locale[0:2]
      localePath = os.path.join(os.path.dirname(__file__), 'i18n', 'geopunt4qgis_{}.qm'.format(locale))
      if os.path.exists(localePath):
          self.translator = QTranslator()
          self.translator.load(localePath)
          QCoreApplication.installTranslator(self.translator)

      self._initGui()
  
    def _initGui(self):
        ' Set up the user interface from Designer.'
        self.ui = Ui_settingsDlg()
        self.ui.setupUi(self)

        #get and load settings
        self.s = QSettings()
        self.loadSettings()
        
        self.ui.buttonBox.addButton( QPushButton("Sluiten"), QDialogButtonBox.RejectRole  )
        self.ui.buttonBox.addButton( QPushButton("Opslaan"), QDialogButtonBox.AcceptRole  )
            
        #event handlers, on accept:  save, on reject: return to previous 
        self.accepted.connect(self.saveSettings)
        self.rejected.connect(self.loadSettings)
        self.ui.dirSelBtn.clicked.connect(self.setDir )

    def loadSettings(self):
        'geopunt4Qgis settings'
        timeout = int(self.s.value("geopunt4qgis/timeout", 15))
        self.ui.timeOutBox.setValue(timeout)
        home = os.path.expanduser("~")
        startDir = self.s.value("geopunt4qgis/startDir", home)
        
        if isinstance(startDir, str): 
            self.ui.startDirTxt.setText(startDir)                                   
        
        #proxysettings
        proxyOverwiteEnabled = int( self.s.value("geopunt4qgis/proxyOverwiteEnabled" , 0))
        self.ui.proxyChk.setChecked(proxyOverwiteEnabled)

        proxyText = self.s.value("geopunt4qgis/proxyUrl", "")
        if isinstance(proxyText, str): self.ui.proxyText.setText(proxyText)
        
        #geopunt4Qgis AdresDialog settings
        adresSearchOnEdit = int( self.s.value("geopunt4qgis/adresSearchOnEdit" , 1))
        self.ui.adresSearchOnEditChk.setChecked(adresSearchOnEdit)
        
        adresSearchOnEnter = int( self.s.value("geopunt4qgis/adresSearchOnEnter" , 0))
        self.ui.adresSearchOnEnterChk.setChecked(adresSearchOnEnter)
        
        adresSavetoFile = int( self.s.value("geopunt4qgis/adresSavetoFile" , 1))
        self.ui.adresSavetoFileChk.setChecked(adresSavetoFile)
        
        adresSaveMemory = int( self.s.value("geopunt4qgis/adresSaveMemory" , 0))
        self.ui.adresSaveMemoryChk.setChecked(adresSaveMemory)
        
        adreslayerText =  self.s.value("geopunt4qgis/adreslayerText", "")
        if isinstance(adreslayerText, str): self.ui.adresLayerTxt.setText(adreslayerText)
        
        #geopunt4Qgis ReverseAdres Settings
        reverseSavetoFile = int( self.s.value("geopunt4qgis/reverseSavetoFile", 1))
        self.ui.reverseSavetoFileChk.setChecked(reverseSavetoFile)
        
        reverseSaveMemory = int( self.s.value("geopunt4qgis/reverseSaveMemory", 0))
        self.ui.reverseSaveMemoryChk.setChecked(reverseSaveMemory)
        
        reverseLayerText =  self.s.value("geopunt4qgis/reverseLayerText", "")
        if isinstance(reverseLayerText, str): self.ui.reverseLayerTxt.setText(reverseLayerText)
        
        #geopunt4Qgis batchGeoCode settings
        batchGeoCodeSavetoFile = int( self.s.value("geopunt4qgis/batchGeoCodeSavetoFile" , 1))
        self.ui.batchSavetoFileChk.setChecked(batchGeoCodeSavetoFile)
        
        batchGeoCodeSavetoMemory = int(self.s.value("geopunt4qgis/batchGeoCodeSavetoMemory", 0))
        self.ui.batchSaveMemoryChk.setChecked(batchGeoCodeSavetoMemory)
        
        batchLayerText = self.s.value("geopunt4qgis/batchLayerText", "")
        if isinstance(batchLayerText, str): self.ui.batchLayerTxt.setText(batchLayerText)
        
        batchMaxRows = int( self.s.value("geopunt4qgis/batchMaxRows", 500 ))
        self.ui.maxRowsSpinBox.setValue(batchMaxRows)	
        
        #PoiDialog settings
        poiSavetoFile = int( self.s.value("geopunt4qgis/poiSavetoFile" , 1))
        self.ui.poiSavetoFileChk.setChecked(poiSavetoFile)
        
        poiSaveMemory = int( self.s.value("geopunt4qgis/poiSaveMemory" , 0))
        self.ui.poiSaveMemoryChk.setChecked(poiSaveMemory)
        
        poilayerText =  self.s.value("geopunt4qgis/poilayerText", "")
        if isinstance(poilayerText, str): self.ui.poiLayerTxt.setText(poilayerText)
        
        #geopunt4Qgis gipod settngs
        gipodSavetoFile = int( self.s.value("geopunt4qgis/gipodSavetoFile" , 1))
        self.ui.gipodSavetoFileChk.setChecked(poiSavetoFile)
        
        gipodSaveMemory = int( self.s.value("geopunt4qgis/gipodSaveMemory" , 0))
        self.ui.gipodSaveMemoryChk.setChecked(poiSaveMemory)
        
        gipodLayerTxt = self.s.value("geopunt4qgis/gipodLayerTxt", "GIPOD")        
        if isinstance(gipodLayerTxt, str): self.ui.gipodLayerTxt.setText(gipodLayerTxt)
        
        #geopunt4Qgis Elevation settings
        samplesSavetoFile = int( self.s.value("geopunt4qgis/samplesSavetoFile" , 1))
        self.ui.samplesSavetoFileChk.setChecked(samplesSavetoFile)
        
        samplesSaveMemory = int( self.s.value("geopunt4qgis/samplesSaveMemory", 0))
        self.ui.samplesSaveMemoryChk.setChecked(samplesSaveMemory)
        
        sampleLayerTxt = self.s.value("geopunt4qgis/sampleLayerTxt", "")
        if isinstance(sampleLayerTxt, str): self.ui.sampleLayerTxt.setText(sampleLayerTxt)
        
        profileLineSavetoFile = int( self.s.value("geopunt4qgis/profileLineSavetoFile" , 1))
        self.ui.profileLineSavetoFileChk.setChecked(profileLineSavetoFile)
        
        profileLineSaveMemory = int( self.s.value("geopunt4qgis/profileLineSaveMemory", 0))
        self.ui.profileLineSaveMemoryChk.setChecked(profileLineSaveMemory)
        
        profileLineLayerTxt = self.s.value("geopunt4qgis/profileLineLayerTxt", "")
        if isinstance(profileLineLayerTxt, str): self.ui.profileLineLayerTxt.setText(profileLineLayerTxt)
        
        #geopunt4Qgis parcel settings
        parcelSavetoFile = int( self.s.value("geopunt4qgis/parcelSavetoFile", 1))
        self.ui.parcelSavetoFileChk.setChecked(parcelSavetoFile)
        
        parcelSaveMemory = int( self.s.value("geopunt4qgis/parcelSaveMemory", 0))
        self.ui.parcelSaveMemoryChk.setChecked(parcelSaveMemory)
        
        parcelLayerText =  self.s.value("geopunt4qgis/parcelLayerText", "")
        if isinstance(parcelLayerText, str): self.ui.parcelLayerTxt.setText(parcelLayerText)
            
 
    def saveSettings(self):
        'save all settings to registry'
        timeout =  self.ui.timeOutBox.value()
        self.s.setValue("geopunt4qgis/timeout" , timeout )
        startDir = self.ui.startDirTxt.text()
        self.s.setValue("geopunt4qgis/startDir", startDir)           
        
        #proxysettings
        proxyOverwiteEnabled = int( self.ui.proxyChk.isChecked() )
        self.s.setValue("geopunt4qgis/proxyOverwiteEnabled" , proxyOverwiteEnabled)

        if proxyOverwiteEnabled:
            proxyText = self.ui.proxyText.text()
            self.s.setValue("geopunt4qgis/proxyUrl" , proxyText)

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
        
        gipodLayerTxt = self.ui.gipodLayerTxt.text()
        self.s.setValue("geopunt4qgis/gipodLayerTxt", gipodLayerTxt)        
        
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
        
        #geopunt4Qgis parcel settings
        parcelSavetoFile = int( self.ui.parcelSavetoFileChk.isChecked() )
        self.s.setValue("geopunt4qgis/parcelSavetoFile", parcelSavetoFile)
        
        parcelSaveMemory = int( self.ui.parcelSaveMemoryChk.isChecked() )
        self.s.setValue("geopunt4qgis/parcelSaveMemory", parcelSaveMemory)
        
        parcelLayerText =  self.ui.parcelLayerTxt.text()
        self.s.setValue("geopunt4qgis/parcelLayerText",  parcelLayerText)
        
    def setDir(self):
        dirpath = QFileDialog.getExistingDirectory()
        if dirpath == None: return
        self.ui.startDirTxt.setText(dirpath)

