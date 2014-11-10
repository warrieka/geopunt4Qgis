# -*- coding: utf-8 -*-
"""
/***************************************************************************
batcGeoCodedialog 
                
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
import os.path, sys
from PyQt4 import QtCore, QtGui
from ui_geopunt4QgisBatchGeoCode import Ui_batchGeocodeDlg
import geopunt, geometryhelper, csv, unicodecsv, webbrowser
from batchGeoHelper import batcGeoHelper
from reverseAdresMapTool import reverseAdresMapTool

class geopunt4QgisBatcGeoCodeDialog(QtGui.QDialog):
    def __init__(self, iface):
        QtGui.QDialog.__init__(self, None)
        self.setWindowFlags( self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint )
        #self.setWindowFlags( self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        self.iface = iface
        
        # initialize locale
        locale = QtCore.QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(os.path.dirname(__file__), 'i18n', 
                      'geopunt4qgis_{}.qm'.format(locale))
        if os.path.exists(localePath):
            self.translator = QtCore.QTranslator()
            self.translator.load(localePath)
            if QtCore.qVersion() > '4.3.3': 
               QtCore.QCoreApplication.installTranslator(self.translator)
        #load gui
        self._initGui()
    
    def _initGui(self):
        "Set up the user interface"
        self.ui = Ui_batchGeocodeDlg()
        self.ui.setupUi(self)
    
        #settings
        self.s = QtCore.QSettings()
        self.loadSettings()
    
        #set vars
        self.csv = None
        self.delimiter = ';'
        self.headers = None
        self.graphicsLayer = []
        self.reverseAdresTool = None
        self.batcGeoHelper = batcGeoHelper(self.iface, self, startFolder=self.startDir )
        self.gh = geometryhelper.geometryHelper(self.iface)
    
        self.ui.delimEdit.setEnabled(False)
        self.ui.addToMapKnop.setEnabled(False)
        self.ui.tlFrame.setEnabled(False)
        
        self.ui.buttonBox.addButton( QtGui.QPushButton("Sluiten"), QtGui.QDialogButtonBox.RejectRole )
        for btn in self.ui.buttonBox.buttons():
            btn.setAutoDefault(0)
            
        #actions
        self.ui.outPutTbl.addAction( self.ui.actionValidateSelection)      
        self.ui.actionValidateSelection.triggered.connect(self.validateSelection)
        self.ui.outPutTbl.addAction( self.ui.actionZoomToSelection )
        self.ui.actionZoomToSelection.triggered.connect(self.zoomtoSelection)
        self.ui.outPutTbl.addAction(self.ui.adresFromMapAction)
        self.ui.adresFromMapAction.triggered.connect(self.adresFromMap)
    
        #event handlers 
        self.ui.inputBtn.clicked.connect(self.openInputCsv)
        self.ui.inputTxt.returnPressed.connect(self.loadTable)
        self.ui.delimSelect.activated.connect(self.setDelim) 
        self.ui.validateBtn.clicked.connect(self.validateAll)
        self.ui.validateSelBtn.clicked.connect(self.validateSelection)
        self.ui.addToMapKnop.clicked.connect(self.addToMap)
        self.ui.adresFromMapBtn.clicked.connect(self.adresFromMap)
        self.ui.singleLineChk.toggled.connect(self.on_singleLineToggled)
        self.ui.buttonBox.helpRequested.connect(self.openHelp)
        self.finished.connect(self.clean)
    
    def loadSettings(self): 
        self.maxRows = int( self.s.value("geopunt4qgis/batchMaxRows", 2000 ))
        self.saveToFile = int( self.s.value("geopunt4qgis/batchGeoCodeSavetoFile" , 1))
        layerName =  self.s.value("geopunt4qgis/batchLayerText", "")
        if layerName :
           self.layerName= layerName
        self.timeout =  int(self.s.value("geopunt4qgis/timeout" ,15))
        if int( self.s.value("geopunt4qgis/useProxy" , 0)):
            self.proxy = self.s.value("geopunt4qgis/proxyHost" ,"")
            self.port = self.s.value("geopunt4qgis/proxyPort" ,"")
        else:
            self.proxy = ""
            self.port = ""
        self.retrys = 3
        self.startDir = self.s.value("geopunt4qgis/startDir", os.path.dirname(__file__))
        self.gp = geopunt.Adres(self.timeout, self.proxy, self.port)

    #eventHandlers
    def openHelp(self):
        webbrowser.open_new_tab("http://www.geopunt.be/voor-experts/geopunt-plug-ins/functionaliteiten/csv-bestanden-geocoderen")

    def addToMap(self): 
        if not self.layernameValid(): return

        adresCol = self.ui.outPutTbl.columnCount() -1
        rowCount = self.ui.outPutTbl.rowCount()
    
        self.ui.statusProgress.setValue(0)
        self.ui.statusProgress.setMaximum(rowCount)
    
        retry = self.retrys
        row= 0
        while row < rowCount:
            attributes = {}
            self.ui.statusProgress.setValue(row)
            if self.ui.outPutTbl.cellWidget(row,adresCol):
                adres = self.ui.outPutTbl.cellWidget(row,adresCol).currentText()
                if not adres: continue
            else: 
                row  += 1
                continue

            for name, colIdx in self.headers.items():
                val= self.ui.outPutTbl.item(row, colIdx).text()
                attributes[name] = val
        
            if adres.split(",")[0].replace('.','').isdigit() and len(adres.split(","))==2:
                x,y = [float(n) for n in adres.split(",")]
                fakecrab = {"Location":{"X_Lambert72":x ,"Y_Lambert72":y }}
                fakecrab["LocationType"] = "manuele aanduiding"
                loc = [fakecrab]
            else:
                loc = self.gp.fetchLocation(adres,1)
        
            if loc and type( loc ) is list:
                xylb =  ( loc[0]["Location"]["X_Lambert72"], loc[0]["Location"]["Y_Lambert72"] )
                xyType = loc[0]["LocationType"]
                xymap = self.gh.prjPtToMapCrs(xylb, 31370)
                self.batcGeoHelper.save_adres_point(xymap, adres, xyType, attritableDict=attributes, 
                                layername=self.layerName )
            elif type( loc ) is str:
                if (loc == 'time out') & (retry > 0): 
                  retry -= 1                        #minus 1 retry
                  continue
                else:
                  self.ui.statusMsg.setText("<div style='color:red'>timeout after %s seconds</div>" 
                    % (self.timeout))
                  return
                self.ui.statusMsg.setText("<div style='color:red'>%s</div>" % loc)
                return
          
            retry = self.retrys
            row  += 1
        
        if self.saveToFile:
              self.batcGeoHelper.saveMem2file(self.layerName)
          
        self.accept()

    def layernameValid(self):   
        if not hasattr(self, 'layerName'):
          layerName, accept = QtGui.QInputDialog.getText(None,
              QtCore.QCoreApplication.translate("geopunt4Qgis", 'Laag toevoegen'),
              QtCore.QCoreApplication.translate("geopunt4Qgis", 'Geef een naam voor de laag op:') )
          if accept == False: 
            return False
          else: 
            self.layerName = layerName
        return True
        
    def adresFromMap(self):
        if self.getSelectedRows() == []: return
    
        self.reverseAdresTool = reverseAdresMapTool(self.iface, self._reverseAdresCallback) 
        self.iface.mapCanvas().setMapTool(self.reverseAdresTool)
        self.showMinimized()

    def on_singleLineToggled(self, toggled):
       if toggled:
         self.ui.adresColLbl.setText(QtCore.QCoreApplication.translate("batcGeoCodedialog", "Adres kolom:"))
       else:
         self.ui.adresColLbl.setText(QtCore.QCoreApplication.translate("batcGeoCodedialog", "Straatnaam kolom:"))
      
    def _reverseAdresCallback(self, point):
        'private callback for reverseAdresMapTool'
        self.iface.mapCanvas().unsetMapTool(self.reverseAdresTool)
        self.showNormal()
        self.activateWindow()
    
        x,y = self.gh.prjPtFromMapCrs(point, 31370)
        adres = str(x) +","+ str(y)
    
        validAdresCol = self.ui.outPutTbl.columnCount() -1
        rowIds= self.getSelectedRows()
        for rowIdx in rowIds:
            validCombo = QtGui.QComboBox(self.ui.adresColSelect)
            validCombo.addItems([adres])
            validCombo.setEnabled(False)
            self.ui.outPutTbl.setCellWidget(rowIdx, validAdresCol, validCombo)
            for col in range(validAdresCol):
                self.ui.outPutTbl.item(rowIdx,col).setBackgroundColor(QtGui.QColor("#DDFFDD"))
            self.ui.outPutTbl.clearSelection()
        
    def loadTable(self):
        self.ui.outPutTbl.clearContents()   #clear existing stuff
        self.ui.outPutTbl.setColumnCount(0)
        self.ui.outPutTbl.setRowCount(0)
        self.ui.adresColSelect.clear()
        self.ui.huisnrSelect.clear()
        self.ui.gemeenteColSelect.clear()
        self.ui.statusMsg.clear()
        self.clearGraphicsLayer()
        self.headers = {}
        
        self.csv = self.ui.inputTxt.text()
        
        if not self.csv :  #none or empty string
            self.ui.adresWgt.setDisabled(True)
            return
        elif not os.path.exists(self.csv):
            self.ui.statusMsg.setText(QtCore.QCoreApplication.translate("batcGeoCodedialog",
                                        "<div style='color:red'>%s bestaat niet</div>") % self.csv)
            self.ui.adresWgt.setDisabled(True)
            return 
      
        if self.ui.codecBox.currentText() == 'utf-8' :
           try: 
             csvReader = unicodecsv.reader(open( self.csv, 'rb'), delimiter=self.delimiter)
           except: 
              QtGui.QMessageBox.warning(self, "Error", 
              QtCore.QCoreApplication.translate("batcGeoCodedialog", 
                "Deze file kon niet correct worden ingelezen, probeer "+
                "eens in te laden als <strong>ANSI-file</strong>"))
        else:
            try: 
               csvReader = csv.reader(open( self.csv, 'r'), delimiter=self.delimiter)
            except: 
              QtGui.QMessageBox.warning(self, "Error", 
              QtCore.QCoreApplication.translate("batcGeoCodedialog", 
                "Deze file kon niet correct worden ingelezen, probeer " +
                " eens in te laden als <strong>UTF-8-file</strong>"))
        
        header = csvReader.next()
        colCount = len(header)
      
        for i in range(colCount):
          self.headers[header[i]]= i
      
        self.ui.outPutTbl.setColumnCount(colCount + 1)
        self.ui.outPutTbl.setColumnWidth(colCount, 250)
        self.ui.outPutTbl.setHorizontalHeaderLabels(header + [QtCore.QCoreApplication.translate(
                              "batcGeoCodedialog", "gevalideerd adres")])
        self.ui.adresColSelect.insertItems(0, header)
        self.ui.gemeenteColSelect.insertItems(0, header + [QtCore.QCoreApplication.translate(
                                    "batcGeoCodedialog", "<geen>")])
        self.ui.gemeenteColSelect.setCurrentIndex(colCount)
        self.ui.huisnrSelect.insertItems(0, header + [QtCore.QCoreApplication.translate(
                                    "batcGeoCodedialog", "<geen>")])
        self.ui.huisnrSelect.setCurrentIndex(colCount)
      
        rowCount = 0
        for line in csvReader:
          self.ui.outPutTbl.insertRow(rowCount)
          for col in range(colCount):
            self.ui.outPutTbl.setItem(rowCount, col, QtGui.QTableWidgetItem(line[col]))
          rowCount += 1
          if rowCount > self.maxRows:
              warnTitle = QtCore.QCoreApplication.translate("batcGeoCodedialog", 
              "%s heeft meer dan %s rijen") % (os.path.basename(self.csv), self.maxRows)
              warnMsg = "<div>" 
              warnMsg += QtCore.QCoreApplication.translate("batcGeoCodedialog", 
              "Je bestand heeft meer dan %s rijen.<br/>" ) % self.maxRows 
              warnMsg += QtCore.QCoreApplication.translate("batcGeoCodedialog",
              "Om de servers van agiv niet te zwaar te belasten is de toepassing beperkt tot %s rijen.<br/>" ) % self.maxRows 
              warnMsg += QtCore.QCoreApplication.translate("batcGeoCodedialog",
              "Deelnemers van GDI-vlaanderen kunnen gebruik maken van Crab Match om grote bestanden te valideren en geocoderen: <br/>" )
              warnMsg += QtCore.QCoreApplication.translate("batcGeoCodedialog", 
              "<a href='https://help.agiv.be/Categories/Details/213-Crab_Match_valideer_en_verrijk_je_adressenbestand'>Meer info</a>")
              warnMsg += "</div>"
          
              self.ui.statusMsg.setText("<div style='color:red'>"+ warnTitle +"</div>")
              QtGui.QMessageBox.warning(self, warnTitle, warnMsg )
              break
      
        self.ui.adresWgt.setDisabled(False)
        self.ui.tlFrame.setDisabled(False)

    def setDelim(self, idx):
        txt = self.ui.delimSelect.itemText(idx)
        accept = True
        if txt == 'Puntcomma':
            self.delimiter = ';'
            self.loadTable()
        elif txt == 'Comma':
            self.delimiter = ','
            self.loadTable()
        elif txt ==  'Tab':
            self.delimiter = '\t'
            self.loadTable()
        else:
            delimiter, accept = QtGui.QInputDialog.getText(self, 
                QtCore.QCoreApplication.translate("batcGeoCodedialog","Andere separator") , 
                QtCore.QCoreApplication.translate("batcGeoCodedialog","Stel zelf een separator in: (Maximaal 1 karakter)"))
            if accept:
                self.delimiter = str( delimiter.strip()[0])
                self.ui.delimEdit.setText(self.delimiter)
                self.loadTable()

    def validateSelection(self):
        if self.internet_on() != True: return
    
        rows = self.getSelectedRows()
    
        self.validateRows(rows)
        self.ui.addToMapKnop.setEnabled(True)

    def validateAll(self):
        if self.internet_on() != True: return
    
        rowCount = self.ui.outPutTbl.rowCount()
        rows = range(rowCount)
    
        self.validateRows(rows)
        self.ui.addToMapKnop.setEnabled(True)
    
    def validateRows(self , rowIds):
        if len(rowIds) == 0: return
        self.clearGraphicsLayer()
        adresTxt = self.ui.adresColSelect.currentText()
        huisnrTxt = self.ui.huisnrSelect.currentText()
        gemeenteTxt = self.ui.gemeenteColSelect.currentText()
      
        validAdresCol = self.ui.outPutTbl.columnCount() -1
        adresCol = self.headers[adresTxt] 
        if gemeenteTxt != QtCore.QCoreApplication.translate("batcGeoCodedialog", "<geen>"):
              gemeenteCol = self.headers[gemeenteTxt] 
        if huisnrTxt != QtCore.QCoreApplication.translate("batcGeoCodedialog", "<geen>"):
              huisnrCol = self.headers[huisnrTxt] 
    
        self.ui.statusProgress.setValue(0)
        self.ui.statusProgress.setMaximum(len(rowIds))
        self.ui.statusMsg.setText("vooruitgang: ")
    
        retry = self.retrys
        i= 0
        while i < len( rowIds):
              rowIdx = rowIds[i]
              #status Progress
              self.ui.statusProgress.setValue(i)

              adres = self.ui.outPutTbl.item(rowIdx, adresCol).text()
    
              if huisnrTxt != QtCore.QCoreApplication.translate("batcGeoCodedialog", "<geen>"):
                  adres += " " +  self.ui.outPutTbl.item(rowIdx, huisnrCol).text()
              if gemeenteTxt != QtCore.QCoreApplication.translate("batcGeoCodedialog", "<geen>"): 
                  adres = ",".join([adres, self.ui.outPutTbl.item(rowIdx, gemeenteCol).text()])
      
              adres = " ".join( adres.split())  #remove too many spaces
              validAdres = self.gp.fetchSuggestion(adres, 5)
          
              if validAdres and type( validAdres ) is str: 
                if (validAdres == 'time out') & (retry > 0): 
                  retry -= 1                        #minus 1 retry
                  continue
                elif retry == 0:
                  self.ui.statusMsg.setText("<div style='color:red'>timeout na %s seconden and %s pogingen</div>" % (self.timeout , self.retrys))
                  return
                self.ui.statusMsg.setText("<div style='color:red'>%s</div>" % validAdres)
                return
        
              elif validAdres and type( validAdres ) is list: 
                if len(validAdres) > 1 and len( validAdres[0].split(',')) == 2 and len(adres.strip()): 
                   resustNR =  validAdres[0].split(',')[0].split()[-1]
                   adresNR = adres.split(',')[0].split()[-1]
                   if adresNR == resustNR:
                      validAdres = [validAdres[0]]
                   
                validCombo = QtGui.QComboBox(self.ui.adresColSelect)
                validCombo.addItems(validAdres)
                self.ui.outPutTbl.setCellWidget(rowIdx, validAdresCol, validCombo)
    
              if len(validAdres) == 1:
                  self.ui.outPutTbl.cellWidget(rowIdx, validAdresCol).setEnabled(0)
                  for col in range(len(self.headers)):
                      self.ui.outPutTbl.item(rowIdx, col).setBackgroundColor(QtGui.QColor("#CCFFCC"))
              elif len(validAdres) > 1:
                  self.ui.outPutTbl.cellWidget(rowIdx, validAdresCol).addItem("")
                  for col in range(len(self.headers)):
                      self.ui.outPutTbl.item(rowIdx, col).setBackgroundColor(QtGui.QColor("#FFFFC8"))
                      
              elif len(validAdres) == 0:
                  self.ui.outPutTbl.setCellWidget(rowIdx, validAdresCol, None)
                  for col in range(len(self.headers)):
                      self.ui.outPutTbl.item(rowIdx, col).setBackgroundColor(QtGui.QColor("#FFBEBE"))
              i += 1
              retry = self.retrys

        #reset statusbar
        self.ui.statusMsg.setText("")
        self.ui.statusProgress.setValue(0)
        self.ui.outPutTbl.clearSelection()
        
    def zoomtoSelection(self):
        self.clearGraphicsLayer()
        rows = self.getSelectedRows()
        adresCol = self.ui.outPutTbl.columnCount() -1
        i = 0
        pts = []
        while i < len(rows):
          row = rows[i]
          adres = None
          if self.ui.outPutTbl.cellWidget(row,adresCol):
            adres = self.ui.outPutTbl.cellWidget(row,adresCol).currentText()
          if adres:
            loc = self.gp.fetchLocation(adres,1)
            if loc and type( loc ) is list:
                xylb = ( loc[0]["Location"]["X_Lambert72"], loc[0]["Location"]["Y_Lambert72"] )
                xyMap = self.gh.prjPtToMapCrs(xylb, 31370)
                pts.append(xyMap)
                graphic = self.gh.addPointGraphic(xyMap)
                self.graphicsLayer.append(graphic)
            elif type( loc ) is str:
                self.ui.statusMsg.setText("<div style='color:red'>%s</div>" % loc)
                self.clearGraphicsLayer()
            return
          i += 1
      
        bounds = None
        if len(pts) == 1:
          x,y = pts[0]
          bounds = self.gh.getBoundsOfPoint(x, y)
        elif len(pts) > 1:
          bounds = self.gh.getBoundsOfPointArray(pts)
      
        self.gh.zoomtoRec2(bounds)
    
    def openInputCsv(self):
        fd = QtGui.QFileDialog()
        filter = "Comma separated value File (.csv) (*.csv);;Text Files (.txt) (*.txt);;Any File (*.*)"
        fd.setFileMode(QtGui.QFileDialog.AnyFile)
        #testdata:  /home/kay/projects/geopunt4Qgis/testData/vergunning2.csv
        fName = fd.getOpenFileName( self, "open file" , self.startDir, filter)
        if fName:
            self.ui.inputTxt.setText(fName)
            self.loadTable()

    def internet_on(self):
        inet_on = geopunt.internet_on( timeout= self.timeout , proxyUrl= self.proxy , port= self.port  )
        if True != inet_on:
            self.ui.statusMsg.setText(
            QtCore.QCoreApplication.translate("batcGeoCodedialog", 
                                 "<div style='color:red'>Kon geen connectie maken met geopunt</div>"))
        return inet_on

    def getSelectedRows(self):
        selected = set( [sel.row() for sel in self.ui.outPutTbl.selectedIndexes()] )
        return list( selected )
    
    def clearGraphicsLayer(self):
        for graphic in  self.graphicsLayer: 
          self.iface.mapCanvas().scene().removeItem(graphic)
        self.graphicsLayer = []
      
    def clean(self):
        self.batcGeoHelper.clear()
        #ui
        self.ui.inputTxt.setText("")
        self.ui.delimSelect.setCurrentIndex(0)
        self.ui.outPutTbl.clearContents()
        self.ui.outPutTbl.setRowCount(0)
        self.ui.outPutTbl.setColumnCount(0)
        self.ui.adresColSelect.clear()
        self.ui.huisnrSelect.clear()
        self.ui.gemeenteColSelect.clear()
        self.ui.adresWgt.setEnabled(False)
        self.ui.addToMapKnop.setEnabled(False)
        self.ui.statusProgress.setValue(0)
        self.ui.statusMsg.setText("")
        #vars
        self.csv = None
        self.delimiter = ';'
        self.headers = None
        self.headers = {}
        self.clearGraphicsLayer()
        #unsetMapTool
        self.iface.mapCanvas().unsetMapTool(self.reverseAdresTool)