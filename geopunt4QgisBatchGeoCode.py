# -*- coding: utf-8 -*-
import csv, webbrowser, os.path
from qgis.PyQt.QtCore import Qt, QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtWidgets import (QDialog, QDialogButtonBox, QPushButton, QInputDialog, 
                                 QComboBox, QMessageBox, QTableWidgetItem, QFileDialog)
from qgis.PyQt.QtGui import QColor, QBrush
from .ui_geopunt4QgisBatchGeoCode import Ui_batchGeocodeDlg
from .tools.batchGeo import batcGeoHelper
from .mapTools.reverseAdres import reverseAdresMapTool
from .geopunt import adresMatch
from .tools.settings import settings
from .tools.geometry import geometryHelper

class geopunt4QgisBatcGeoCodeDialog(QDialog):
    def __init__(self, iface):
        QDialog.__init__(self, None)
        self.setWindowFlags( self.windowFlags() & ~Qt.WindowContextHelpButtonHint )
        #self.setWindowFlags( self.windowFlags() |Qt.WindowStaysOnTopHint)
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
        #load gui
        self._initGui()
    
    def _initGui(self):
        "Set up the user interface"
        self.ui = Ui_batchGeocodeDlg()
        self.ui.setupUi(self)
    
        #settings
        self.s = QSettings()
        self.loadSettings()
        self.am = adresMatch()
    
        #set vars
        self.csv = None
        self.delimiter = ';'
        self.headers = None
        self.graphicsLayer = []
        self.reverseAdresTool = None
        self.batcGeoHelper = batcGeoHelper(self.iface, self, startFolder=self.startDir )
        self.gh = geometryHelper(self.iface)
    
        self.ui.delimEdit.setEnabled(False)
        self.ui.addToMapKnop.setEnabled(False)
        self.ui.tlFrame.setEnabled(False)
        
        self.ui.buttonBox.addButton( QPushButton("Sluiten"), QDialogButtonBox.RejectRole )
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
        self.ui.codecBox.currentIndexChanged.connect(self.loadTable)
        self.ui.validateBtn.clicked.connect(self.validateAll)
        self.ui.addToMapKnop.clicked.connect(self.addToMap)
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

        s = settings()
        self.proxy = s.proxy  
        self.startDir = self.s.value("geopunt4qgis/startDir", os.path.expanduser("~") )

    #eventHandlers
    def openHelp(self):
        webbrowser.open_new_tab("http://www.geopunt.be/voor-experts/geopunt-plug-ins/functionaliteiten/csv-bestanden-geocoderen")

    def addToMap(self): 
        if not self.layernameValid(): return

        adresCol = self.ui.outPutTbl.columnCount() -1
        rowCount = self.ui.outPutTbl.rowCount()
    
        self.ui.statusProgress.setValue(0)
        self.ui.statusProgress.setMaximum(rowCount)

        row= 0
        while row < rowCount:
            attributes = {}
            self.ui.statusProgress.setValue(row)
            if self.ui.outPutTbl.cellWidget(row,adresCol):
                adres = self.ui.outPutTbl.cellWidget(row,adresCol).currentText()
            else:
                row  += 1
                continue

            for name, colIdx in list(self.headers.items()):
                val= self.ui.outPutTbl.item(row, colIdx).text()
                attributes[name] = val
                
            row  += 1
            if adres.split(",")[0].replace('.','').isdigit() and len(adres.split(","))==2:
                xylb = [float(n) for n in adres.split(",")]
                xyType = "manuele aanduiding||0"
            else:
                loc = self.am.findMatchFromSingleLine(adres)
                if len(loc) == 0: continue
                xylb =  loc[0]["adresPositie"]["point"]["coordinates"]
                xyType = "|".join([ loc[0]["positieSpecificatie"], loc[0]["positieGeometrieMethode"], str(loc[0]["score"]) ])

            xymap = self.gh.prjPtToMapCrs(xylb, 31370)
            self.batcGeoHelper.save_adres_point(xymap, adres, xyType, attritableDict=attributes, layername=self.layerName )

        
        if self.saveToFile:
              self.batcGeoHelper.saveMem2file(self.layerName)
          
        self.accept()

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
        
    def adresFromMap(self):
        if self.getSelectedRows() == []: return
    
        self.reverseAdresTool = reverseAdresMapTool(self.iface, self._reverseAdresCallback) 
        self.iface.mapCanvas().setMapTool(self.reverseAdresTool)
        self.showMinimized()

    def on_singleLineToggled(self, toggled):
       self.ui.gemeenteChooseWgt.setVisible(not toggled)
       self.ui.huisnrLbl.setVisible(not toggled)
       self.ui.huisnrSelect.setVisible(not toggled)
       if toggled:
         self.ui.adresColLbl.setText(QCoreApplication.translate("batcGeoCodedialog", "Adres kolom [<straat>, <huisnr>, <postcode> <gemeente>]:"))
       else:
         self.ui.adresColLbl.setText(QCoreApplication.translate("batcGeoCodedialog", "Straatnaam kolom:"))
      
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
            validCombo = QComboBox(self.ui.adresColSelect)
            validCombo.addItems([adres])
            validCombo.setEnabled(False)
            self.ui.outPutTbl.setCellWidget(rowIdx, validAdresCol, validCombo)
            for col in range(validAdresCol):
                self.ui.outPutTbl.item(rowIdx,col).setBackground( QBrush( QColor("#DDFFDD")) )
            self.ui.outPutTbl.clearSelection()
    
    def loadTable(self):
        self.ui.outPutTbl.clearContents()   #clear existing stuff
        self.ui.outPutTbl.setColumnCount(0)
        self.ui.outPutTbl.setRowCount(0)
        self.ui.adresColSelect.clear()
        self.ui.huisnrSelect.clear()
        self.ui.pcColSelect.clear()
        self.ui.gemeenteColSelect.clear()
        self.ui.statusMsg.clear()
        self.clearGraphicsLayer()
        self.headers = {}
        
        self.csv = self.ui.inputTxt.text()
        
        if not self.csv :  #none or empty string
            self.ui.adresWgt.setDisabled(True)
            return
        elif not os.path.exists(self.csv):
            self.ui.statusMsg.setText(QCoreApplication.translate("batcGeoCodedialog",
                                        "<div style='color:red'>%s bestaat niet</div>") % self.csv)
            self.ui.adresWgt.setDisabled(True)
            return 
        
        enc = None
        if self.ui.codecBox.currentText() == 'utf-8' : enc = 'utf-8'
        elif self.ui.codecBox.currentText() == 'ansi latin1' : enc = 'latin-1'
        
        try: 
            csvReader = csv.reader(open( self.csv, 'r', encoding=enc,  newline=''), delimiter=self.delimiter)
        except: 
            QMessageBox.warning(self, "Error", QCoreApplication.translate("batcGeoCodedialog", 
            "Deze file kon niet correct worden ingelezen, probeer eens in te laden als een " +
            "<strong>ANSI latin-file</strong> of een <strong>UTF-8-file</strong>"))
        
        header = next(csvReader)
        colCount = len(header)
      
        for i in range(colCount):
          self.headers[header[i]]= i
      
        self.ui.outPutTbl.setColumnCount(colCount + 1)
        self.ui.outPutTbl.setColumnWidth(colCount, 250)
        
        self.ui.outPutTbl.setHorizontalHeaderLabels(header + [QCoreApplication.translate("batcGeoCodedialog", "gevalideerd adres")])
        
        self.ui.adresColSelect.insertItems(0, header)
        self.ui.huisnrSelect.insertItems(0, [QCoreApplication.translate("batcGeoCodedialog", "<geen>")]+ header )
        
        self.ui.pcColSelect.insertItems(0, header+ [QCoreApplication.translate("batcGeoCodedialog", "<geen>")]  )
        self.ui.pcColSelect.setCurrentIndex(colCount)
        self.ui.gemeenteColSelect.insertItems(0, header+ [QCoreApplication.translate("batcGeoCodedialog", "<geen>")] )
        self.ui.gemeenteColSelect.setCurrentIndex(colCount)
        
        rowCount = 0
        for line in csvReader:
          self.ui.outPutTbl.insertRow(rowCount)
          for col in range(colCount):
            self.ui.outPutTbl.setItem(rowCount, col, QTableWidgetItem(line[col]))
          rowCount += 1
          if rowCount > self.maxRows:
              warnTitle = QCoreApplication.translate("batcGeoCodedialog", 
              "%s heeft meer dan %s rijen") % (os.path.basename(self.csv), self.maxRows)
              warnMsg = "<div>" 
              warnMsg += QCoreApplication.translate("batcGeoCodedialog", 
              "Je bestand heeft meer dan %s rijen.<br/>" ) % self.maxRows 
              warnMsg += QCoreApplication.translate("batcGeoCodedialog",
              "Om de servers van agiv niet te zwaar te belasten is de toepassing beperkt tot %s rijen.<br/>" ) % self.maxRows 
              warnMsg += QCoreApplication.translate("batcGeoCodedialog",
              "Deelnemers van GDI-vlaanderen kunnen gebruik maken van Crab Match om grote bestanden te valideren en geocoderen: <br/>" )
              warnMsg += QCoreApplication.translate("batcGeoCodedialog", 
              "<a href='https://help.agiv.be/Categories/Details/213-Crab_Match_valideer_en_verrijk_je_adressenbestand'>Meer info</a>")
              warnMsg += "</div>"
          
              self.ui.statusMsg.setText("<div style='color:red'>"+ warnTitle +"</div>")
              QMessageBox.warning(self, warnTitle, warnMsg )
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
            delimiter, accept = QInputDialog.getText(self, 
                QCoreApplication.translate("batcGeoCodedialog","Andere separator") , 
                QCoreApplication.translate("batcGeoCodedialog","Stel zelf een separator in: (Maximaal 1 karakter)"))
            if accept:
                self.delimiter = str( delimiter.strip()[0])
                self.ui.delimEdit.setText(self.delimiter)
                self.loadTable()

    def validateSelection(self):
        rows = self.getSelectedRows()
    
        self.validateRows(rows)
        self.ui.addToMapKnop.setEnabled(True)

    def validateAll(self):
        rowCount = self.ui.outPutTbl.rowCount()
        rows = list(range(rowCount))
        self.validateRows(rows)
        self.ui.addToMapKnop.setEnabled(True)
    
    def validateRows(self , rowIds):
        if len(rowIds) == 0: return
    
        self.clearGraphicsLayer()
        adresTxt = self.ui.adresColSelect.currentText()
        huisnrTxt = self.ui.huisnrSelect.currentText()
        pcTxt = self.ui.pcColSelect.currentText()
        gemeenteTxt = self.ui.gemeenteColSelect.currentText()
        geenSymbol =  QCoreApplication.translate("batcGeoCodedialog", "<geen>")
        
        if gemeenteTxt == geenSymbol and pcTxt == geenSymbol and not self.ui.singleLineChk.isChecked():
            msg = QCoreApplication.translate("batcGeoCodedialog", "Je moet een postcode of gemeente kolom opgeven.")
            QMessageBox.warning(self, 'Warning', msg)
            return

        validAdresCol = self.ui.outPutTbl.columnCount() -1
        adresCol =    self.headers[adresTxt] 
        huisnrCol =   None if huisnrTxt == geenSymbol else self.headers[huisnrTxt] 
        gemeenteCol = None if gemeenteTxt == geenSymbol else self.headers[gemeenteTxt] 
        pcCol =       None if pcTxt == geenSymbol else self.headers[pcTxt]
        
        self.ui.statusProgress.setValue(0)
        self.ui.statusProgress.setMaximum(len(rowIds))
        self.ui.statusMsg.setText("")
    
        i= 0
        while i < len( rowIds):
            rowIdx = rowIds[i]
            #status Progress
            self.ui.statusProgress.setValue(i)

            adres = self.ui.outPutTbl.item(rowIdx, adresCol).text()  if adresCol else ''
            huisNr = self.ui.outPutTbl.item(rowIdx, huisnrCol).text()  if huisnrCol else ''
            pc = self.ui.outPutTbl.item(rowIdx, pcCol).text() if pcCol else ''
            muni = self.ui.outPutTbl.item(rowIdx, gemeenteCol).text() if gemeenteCol else ''
            if not self.ui.singleLineChk.isChecked():
                validAdres = self.am.findAdresSuggestions(municipality=muni, postalcode=pc, housenr=huisNr, streetname=adres)
            else:
                validAdres = self.am.findAdresSuggestions(single=adres)
            
            if type( validAdres ) is list: 
                if len(validAdres) > 1 and len( validAdres[0].split(',')) >= 2 and len(adres.strip()): 
                    resultNR =  validAdres[0].split(',')[0].split()[-1] if len(validAdres[0].split(',')[0].split()) > 0 else validAdres[0]
                    adresNR = adres.split(',')[0].split()[-1] if len(adres.split(',')[0].split()) > 0 else adres
                    if adresNR == resultNR: validAdres = [validAdres[0]]

                validCombo = QComboBox(self.ui.adresColSelect)
                validCombo.addItems(validAdres)
                self.ui.outPutTbl.setCellWidget(rowIdx, validAdresCol, validCombo)

            if len(validAdres) == 1:
                self.ui.outPutTbl.cellWidget(rowIdx, validAdresCol).setEnabled(0)
                for col in range(len(self.headers)):
                    self.ui.outPutTbl.item(rowIdx, col).setBackground( QBrush( QColor("#CCFFCC")) )
            elif len(validAdres) > 1:
                self.ui.outPutTbl.cellWidget(rowIdx, validAdresCol).addItem("")
                for col in range(len(self.headers)):
                    self.ui.outPutTbl.item(rowIdx, col).setBackground( QBrush( QColor("#FFFFC8")) )
                    
            elif len(validAdres) == 0:
                self.ui.outPutTbl.setCellWidget(rowIdx, validAdresCol, None)
                for col in range(len(self.headers)):
                    self.ui.outPutTbl.item(rowIdx, col).setBackground( QBrush( QColor("#FFBEBE")) )
            i += 1

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
            loc = self.am.findMatchFromSingleLine(adres)
            if len(loc):
                xylb = loc[0]["adresPositie"]["point"]["coordinates"]
                xyMap = self.gh.prjPtToMapCrs(xylb, 31370)
                pts.append(xyMap)
                graphic = self.gh.addPointGraphic(xyMap)
                self.graphicsLayer.append(graphic)
          i += 1
      
        bounds = None
        if len(pts) == 1:
          x,y = pts[0]
          bounds = self.gh.getBoundsOfPoint(x, y)
        elif len(pts) > 1:
          bounds = self.gh.getBoundsOfPointArray(pts)
      
        self.gh.zoomtoRec2(bounds)
    
    def openInputCsv(self):
        filter = "Comma separated value File (*.csv) (*.csv);;Text Files (*.txt) (*.txt);;Any File (*.*)"
        fName, _ = QFileDialog.getOpenFileName( self, "open file" , self.startDir, filter)
        if fName:
            self.ui.inputTxt.setText(fName)
            self.loadTable()

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
