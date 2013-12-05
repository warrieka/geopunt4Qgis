# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_testpod.ui'
#
# Created: Thu Dec  5 01:02:55 2013
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

class Ui_testPod(object):
    def setupUi(self, testPod):
        testPod.setObjectName(_fromUtf8("testPod"))
        testPod.resize(515, 356)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/testpod/geopunt.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        testPod.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(testPod)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.inputBox = QtGui.QGroupBox(testPod)
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
        self.resultLijst = QtGui.QListWidget(testPod)
        self.resultLijst.setObjectName(_fromUtf8("resultLijst"))
        self.verticalLayout.addWidget(self.resultLijst)

        self.retranslateUi(testPod)
        QtCore.QMetaObject.connectSlotsByName(testPod)

    def retranslateUi(self, testPod):
        testPod.setWindowTitle(_translate("testPod", "Geopunt", None))
        self.inputBox.setTitle(_translate("testPod", "Geef een adres op:", None))
        self.zoekBtn.setText(_translate("testPod", "Zoek", None))

import resources_rc
