# -*- coding: utf-8 -*-
"""
/***************************************************************************
batcGeoCodedialog 
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
#TODO: create triggers, validate selected, zoom to selected
import os.path
from PyQt4 import QtCore, QtGui
from ui_geopunt4QgisBatchGeoCode import Ui_batchGeocodeDlg
import geopunt
import UnicodeCsvReader as csv
from batchGeoHelper import batcGeoHelper

class geopunt4QgisBatcGeoCodedialog(QtGui.QDialog):
    def __init__(self, iface):
	QtGui.QDialog.__init__(self)
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
      # Set up the user interface from Designer.
	self.ui = Ui_batchGeocodeDlg()
	self.ui.setupUi(self)
	
	#settings
	self.s = QtCore.QSettings()
	self.loadSettings()
	
	#set vars
	self.csv = None
	self.delimiter = ';'
	self.headers = None
	self.gp = geopunt.Adres()
	self.batcGeoHelper = batcGeoHelper(self.iface, self)
	
	self.ui.delimEdit.setEnabled(False)
	self.ui.addToMapKnop.setEnabled(False)
	
	#actions
	self.ui.outPutTbl.addAction( self.ui.actionValidateSelection )
	self.ui.outPutTbl.addAction( self.ui.actionValidateAll)
	self.ui.outPutTbl.addAction( self.ui.actionAddValidToMap )
	
	#event handlers 
	self.ui.inputBtn.clicked.connect(self.openInputCsv)
	self.ui.inputTxt.returnPressed.connect(self.loadTable)
	self.ui.delimSelect.activated.connect(self.setDelim) 
	self.ui.validateBtn.clicked.connect(self.validateAll)
	self.ui.validateSelBtn.clicked.connect(self.validateSelection)
	self.ui.addToMapKnop.clicked.connect(self.addToMap)
	self.finished.connect(self.clean)
	
    def loadSettings(self): 
	self.maxRows = int( self.s.value("geopunt4qgis/batchMaxRows", 100 ))
	self.saveToFile = int( self.s.value("geopunt4qgis/poiSavetoFile" , 0))
	self.layerName = self.s.value("geopunt4qgis/poilayerText", "geopunt_poi")
	
    def addToMap(self):
	adresCol = len( self.headers ) 
	rowCount = self.ui.outPutTbl.rowCount()
	
	self.ui.statusProgress.setValue(0)
	self.ui.statusProgress.setMaximum(rowCount)
	
	for row in range(rowCount):
	  attributes = {}
	  self.ui.statusProgress.setValue(row)
	  if self.ui.outPutTbl.cellWidget(row,adresCol):
	    adres = self.ui.outPutTbl.cellWidget(row,adresCol).currentText()
	  else: 
	    continue
	  for name, colIdx in self.headers.items():
	    val= self.ui.outPutTbl.item(row, colIdx).text()
	    attributes[name] = val
	  
	  loc = self.gp.fetchLocation(adres,1)
	  if loc and loc.__class__ is list:
	    xylb = ( loc[0]["Location"]["X_Lambert72"], loc[0]["Location"]["Y_Lambert72"] )
	    xyType = loc[0]["LocationType"]
	    xymap = self.batcGeoHelper.prjPtToMapCrs(xylb, 31370)
	    self.batcGeoHelper.save_adres_point(xymap, adres, xyType, attritableDict=attributes, 
					 layername=self.layerName )
	  elif loc.__class__ is str:
	    self.ui.statusMsg.setText("<div style='color:red'>%s</div>" % loc)
	    
	if self.saveToFile:
	  self.batcGeoHelper.saveMem2file(self.layerName)
	    
	self.accept()
	
    def loadTable(self):
	#clear existing
	self.ui.outPutTbl.clearContents()
	self.ui.outPutTbl.setColumnCount(0)
	self.ui.outPutTbl.setRowCount(0)
	self.ui.adresColSelect.clear()
	self.ui.huisnrSelect.clear()
	self.ui.gemeenteColSelect.clear()
	self.ui.statusMsg.clear()
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
	
	csvReader = csv.UnicodeCsvReader(open( self.csv, 'rb'), delimiter=self.delimiter)
	header = csvReader.next()
	colCount = len(header)
	
	for i in range(colCount):
	  self.headers[header[i]]= i
	  
	self.ui.outPutTbl.setColumnCount(colCount + 1)
	self.ui.outPutTbl.setHorizontalHeaderLabels(header +  [QtCore.QCoreApplication.translate(
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
	    "Deelnemers van GDI-vlaanderen kunnen gebruik maken van Crab Match om grote bestanden te valideren en geocoderen: <br/>"  )
	    warnMsg += QtCore.QCoreApplication.translate("batcGeoCodedialog", 
	    "<a href='https://help.agiv.be/Categories/Details/213-Crab_Match_valideer_en_verrijk_je_adressenbestand'>Meer info</a>")
	    warnMsg += "</div>"
	    
	    self.ui.statusMsg.setText("<div style='color:red'>"+ warnTitle +"</div>")
	    QtGui.QMessageBox.warning(self, warnTitle, warnMsg )
	    break
	    
	self.ui.adresWgt.setDisabled(False)

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
	#check if online before starting
	if True != self.internet_on():
	  return
	
	rows = self.getSelectedRows()
	
	self.validateRows(rows)
	self.ui.addToMapKnop.setEnabled(True)

    def validateAll(self):
        #check if online before starting
	if True != self.internet_on():
	  return
	
	rowCount = self.ui.outPutTbl.rowCount()
	rows = range(rowCount)
	
	self.validateRows(rows)
	self.ui.addToMapKnop.setEnabled(True)
	
    def validateRows(self , rowIds):
	adresTxt = self.ui.adresColSelect.currentText()
	huisnrTxt = self.ui.huisnrSelect.currentText()
	gemeenteTxt = self.ui.gemeenteColSelect.currentText()
      
	contoleCol = len( self.headers ) 
	adresCol = self.headers[adresTxt] 
	if gemeenteTxt != QtCore.QCoreApplication.translate("batcGeoCodedialog", "<geen>"):
	  gemeenteCol = self.headers[gemeenteTxt] 
	if huisnrTxt != QtCore.QCoreApplication.translate("batcGeoCodedialog", "<geen>"):
	  huisnrCol = self.headers[huisnrTxt] 
	
	self.ui.statusProgress.setValue(0)
	self.ui.statusProgress.setMaximum(len(rowIds))
	self.ui.statusMsg.setText("vooruitgang: ")
	
	for rowIdx in rowIds:
	  #status Progress
	  self.ui.statusProgress.setValue(rowIdx)

	  adres = self.ui.outPutTbl.item(rowIdx, adresCol).text()
	  
	  if huisnrTxt != QtCore.QCoreApplication.translate("batcGeoCodedialog", "<geen>"):
	    adres += " " +  self.ui.outPutTbl.item(rowIdx, huisnrCol).text()
	  if gemeenteTxt != QtCore.QCoreApplication.translate("batcGeoCodedialog", "<geen>"): 
	    adres = ",".join([adres, self.ui.outPutTbl.item(rowIdx, gemeenteCol).text()])
	    
	  adres = " ".join( adres.split())  #remove too many spaces
	  #self.ui.statusMsg.setText(adres)
	  validAdres = self.gp.fetchSuggestion(adres, 5)
	  if validAdres and validAdres.__class__ is list: 
	    validCombo = QtGui.QComboBox(self.ui.adresColSelect)
	    validCombo.addItems(validAdres)
	    self.ui.outPutTbl.setCellWidget(rowIdx, contoleCol, validCombo)
	    
	    if len(validAdres) == 1:
	      for col in range(len(self.headers)):
		self.ui.outPutTbl.item(rowIdx, col).setBackgroundColor(QtGui.QColor(204,255,204))
	    if len(validAdres) > 1:
	      for col in range(len(self.headers)):
		self.ui.outPutTbl.item(rowIdx, col).setBackgroundColor(QtGui.QColor(255,255,200))
	    
	  else:
	    self.ui.outPutTbl.setCellWidget(rowIdx, contoleCol, None)
	    for col in range(len(self.headers)):
	      self.ui.outPutTbl.item(rowIdx, col).setBackgroundColor(QtGui.QColor(255,190,190))
	  
	  #reset statusbar
	self.ui.statusMsg.setText("")
	self.ui.statusProgress.setValue(0)

    def openInputCsv(self):
	fd = QtGui.QFileDialog()
	filter = "Comma separated value File (.csv) (*.csv);;Text Files (.txt) (*.txt);;Any File (*.*)"
	fd.setFileMode(QtGui.QFileDialog.AnyFile)
	#testdata:  /home/kay/projects/geopunt4Qgis/testData/vergunning2.csv
	fName = fd.getOpenFileName( self, "open file" , None, filter)
	if fName:
	    self.ui.inputTxt.setText(fName)
	    self.loadTable()

    def internet_on(self):
	inet_on = geopunt.internet_on()
	if True != inet_on:
	  self.ui.statusMsg.setText(
	    QtCore.QCoreApplication.translate("batcGeoCodedialog", "<div style='color:red'>Kon geen connectie maken met geopunt</div>"))
	return inet_on

    def getSelectedRows(self):
	selected = set( [sel.row() for sel in self.ui.outPutTbl.selectedIndexes()] )
	return selected

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