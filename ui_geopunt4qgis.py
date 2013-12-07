# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_geopunt4qgis.ui'
#
# Created: Sat Dec  7 15:58:07 2013
#      by: PyQt4 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_geopunt4Qgis(object):
    def setupUi(self, geopunt4Qgis):
        geopunt4Qgis.setObjectName(_fromUtf8("geopunt4Qgis"))
        geopunt4Qgis.resize(480, 370)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/geopunt4Qgis/images/geopuntSmal.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        geopunt4Qgis.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(geopunt4Qgis)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.inputBox = QtGui.QGroupBox(geopunt4Qgis)
        self.inputBox.setObjectName(_fromUtf8("inputBox"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.inputBox)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.zoekText = QtGui.QLineEdit(self.inputBox)
        self.zoekText.setObjectName(_fromUtf8("zoekText"))
        self.horizontalLayout.addWidget(self.zoekText)
        self.zoekBtn = QtGui.QPushButton(self.inputBox)
        self.zoekBtn.setObjectName(_fromUtf8("zoekBtn"))
        self.horizontalLayout.addWidget(self.zoekBtn)
        self.verticalLayout.addWidget(self.inputBox)
        self.resultLijst = QtGui.QListWidget(geopunt4Qgis)
        self.resultLijst.setObjectName(_fromUtf8("resultLijst"))
        self.verticalLayout.addWidget(self.resultLijst)
        self.widget = QtGui.QWidget(geopunt4Qgis)
        self.widget.setObjectName(_fromUtf8("widget"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout(self.widget)
        self.horizontalLayout_2.setMargin(0)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.Add2mapKnop = QtGui.QPushButton(self.widget)
        self.Add2mapKnop.setObjectName(_fromUtf8("Add2mapKnop"))
        self.horizontalLayout_2.addWidget(self.Add2mapKnop)
        self.ZoomKnop = QtGui.QPushButton(self.widget)
        self.ZoomKnop.setObjectName(_fromUtf8("ZoomKnop"))
        self.horizontalLayout_2.addWidget(self.ZoomKnop)
        self.verticalLayout.addWidget(self.widget)

        self.retranslateUi(geopunt4Qgis)
        QtCore.QMetaObject.connectSlotsByName(geopunt4Qgis)

    def retranslateUi(self, geopunt4Qgis):
        geopunt4Qgis.setWindowTitle(_translate("geopunt4Qgis", "Geopunt zoeken op adres", None))
        self.inputBox.setTitle(_translate("geopunt4Qgis", "Geef een adres op:", None))
        self.zoekBtn.setText(_translate("geopunt4Qgis", "Valideer", None))
        self.Add2mapKnop.setText(_translate("geopunt4Qgis", "Toevoegen aan Kaart", None))
        self.ZoomKnop.setText(_translate("geopunt4Qgis", "Zoom naar", None))

import resources_rc
