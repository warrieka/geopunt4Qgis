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
import os.path
from PyQt4 import QtCore, QtGui
from ui_geopunt4QgisBatchGeoCode import Ui_batchGeocodeDlg
import geopunt
import UnicodeCsvReader as csv

class batcGeoCodedialog(QtGui.QDialog):
    def __init__(self, iface):
	QtGui.QDialog.__init__(self)
	#set iface
	self.iface = iface

	# initialize locale
        locale = QtCore.QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(os.path.dirname(__file__), 'i18n', 
				  'geopunt4qgis_{}.qm'.format(locale))
        if os.path.exists(localePath):
            self.translator = QtCore.QTranslator()
            self.translator.load(localePath)
            if QtCore.qVersion() > '4.3.3': QtCore.QCoreApplication.installTranslator(self.translator)
	#load gui
	self._initGui()
	
    def _initGui(self):
      # Set up the user interface from Designer.
	self.ui = Ui_batchGeocodeDlg()
	self.ui.setupUi(self)
	
	#set vars
	self.csv = None
	self.delimiter = ';'
	self.headers = None
	self.gp = geopunt.Adres()
	
	self.ui.delimEdit.setEnabled(False)
	
	#event handlers 
	self.ui.inputBtn.clicked.connect(self.openInputCsv)
	self.ui.inputTxt.returnPressed.connect(self.loadTable)
	self.ui.delimSelect.activated.connect(self.setDelim) 
	self.ui.validateBtn.clicked.connect(self.validate)
	self.finished.connect(self.clean)
	
    def loadTable(self):
	#clear existing
	self.ui.outPutTbl.clearContents()
	self.ui.outPutTbl.setRowCount(0)
	self.ui.adresColSelect.clear()
	self.ui.huisnrSelect.clear()
	self.ui.gemeenteColSelect.clear()
	self.headers = {}
	
	if self.csv is None or not os.path.exists(self.csv):
	  self.ui.adresWgt.setDisabled(True)
	  return 
	
	csvReader = csv.UnicodeCsvReader(open( self.csv, 'rb'), delimiter=self.delimiter)
	header = csvReader.next()
	colCount = len(header)
	for i in range(colCount):
	  self.headers[header[i]]= i
	self.ui.outPutTbl.setColumnCount(colCount + 1)
	self.ui.outPutTbl.setHorizontalHeaderLabels(header + ["gevalideerd adres"])
	
	self.ui.adresColSelect.insertItems(0, header)
	self.ui.gemeenteColSelect.insertItems(0, header + ["<geen>"] )
	self.ui.gemeenteColSelect.setCurrentIndex(colCount)
	self.ui.huisnrSelect.insertItems(0, header + ["<geen>"])
	self.ui.huisnrSelect.setCurrentIndex(colCount)
	
	rowCount = 0
	for line in csvReader:
	  self.ui.outPutTbl.insertRow(rowCount)
	  for col in range(colCount):
	    self.ui.outPutTbl.setItem(rowCount, col, 
			       QtGui.QTableWidgetItem(line[col]))
	    
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
				"Andere separator", "Stel zelf een separator in: (Maximaal 1 karakter)")
	  if accept:
	    self.delimiter = str( delimiter.strip()[0])
	    self.ui.delimEdit.setText(self.delimiter)
	    self.loadTable()

    def validate(self):
	adresTxt = self.ui.adresColSelect.currentText()
	huisnrTxt = self.ui.huisnrSelect.currentText()
	gemeenteTxt = self.ui.gemeenteColSelect.currentText()
	
	adresCol = self.headers[adresTxt] 
	if gemeenteTxt != '<geen>':
	  gemeenteCol = self.headers[gemeenteTxt] 
	if huisnrTxt != '<geen>':
	  huisnrCol = self.headers[huisnrTxt] 
	  
	contoleCol = len( self.headers ) 
	
	#TODO: check if online before starting
	for rowIdx in range( self.ui.outPutTbl.rowCount()):
	  adres = self.ui.outPutTbl.item(rowIdx,adresCol).text()
	  if huisnrTxt != '<geen>':
	    adres += " " +  self.ui.outPutTbl.item(rowIdx, huisnrCol).text()
	  if gemeenteTxt != '<geen>': 
	    adres += ', ' + self.ui.outPutTbl.item(rowIdx, gemeenteCol).text()
	    
	  adres = " ".join( adres.split())  #remove too many spaces
	  validAdres = self.gp.fetchSuggestion(adres, 5)
	  if validAdres and validAdres.__class__ is list: 
	    validCombo = QtGui.QComboBox(self.ui.adresColSelect)
	    validCombo.addItems(validAdres)
	    self.ui.outPutTbl.setCellWidget(rowIdx, contoleCol, validCombo)
	    #out=> self.ui.outPutTbl.cellWidget(rowIdx,contoleCol).currentText()
	    
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

    def openInputCsv(self):
	fd = QtGui.QFileDialog()
	filter = "Comma separated value File (.csv) (*.csv);;Text Files (.txt) (*.txt);;Any File (*.*)"
        fd.setFileMode(QtGui.QFileDialog.AnyFile)
        #testdata:  /home/kay/projects/geopunt4Qgis/testData/vergunning2.csv
        fName = fd.getOpenFileName( self, "open file" , None, filter)
        if fName:
	    self.csv = fName
	    self.ui.inputTxt.setText(fName)
	    self.loadTable()

    def clean(self):
	#ui
	self.ui.inputTxt.setText("")
	self.ui.outPutTbl.clearContents()
	self.ui.outPutTbl.setRowCount(0)
	self.ui.outPutTbl.setColumnCount(0)
	self.ui.adresColSelect.clear()
	self.ui.huisnrSelect.clear()
	self.ui.gemeenteColSelect.clear()
	self.ui.adresWgt.setEnabled(False)
	#vars
	self.csv = None
	self.delimiter = ';'
	self.headers = None
	self.headers = {}