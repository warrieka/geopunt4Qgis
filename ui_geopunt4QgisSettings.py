# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_geopunt4QgisSettings.ui'
#
# Created: Thu Dec 26 16:17:05 2013
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

class Ui_settingsDlg(object):
    def setupUi(self, settingsDlg):
        settingsDlg.setObjectName(_fromUtf8("settingsDlg"))
        settingsDlg.resize(392, 301)
        self.verticalLayout = QtGui.QVBoxLayout(settingsDlg)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.settingsTab = QtGui.QToolBox(settingsDlg)
        self.settingsTab.setObjectName(_fromUtf8("settingsTab"))
        self.adresTab = QtGui.QWidget()
        self.adresTab.setObjectName(_fromUtf8("adresTab"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.adresTab)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.groupBox = QtGui.QGroupBox(self.adresTab)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.savetoFileAdresChk = QtGui.QRadioButton(self.groupBox)
        self.savetoFileAdresChk.setObjectName(_fromUtf8("savetoFileAdresChk"))
        self.verticalLayout_2.addWidget(self.savetoFileAdresChk)
        self.saveMemoryAdresChk = QtGui.QRadioButton(self.groupBox)
        self.saveMemoryAdresChk.setChecked(True)
        self.saveMemoryAdresChk.setObjectName(_fromUtf8("saveMemoryAdresChk"))
        self.verticalLayout_2.addWidget(self.saveMemoryAdresChk)
        self.verticalLayout_3.addWidget(self.groupBox)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem)
        self.settingsTab.addItem(self.adresTab, _fromUtf8(""))
        self.reverseTab = QtGui.QWidget()
        self.reverseTab.setObjectName(_fromUtf8("reverseTab"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.reverseTab)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.groupBox_2 = QtGui.QGroupBox(self.reverseTab)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.verticalLayout_4 = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_4.setObjectName(_fromUtf8("verticalLayout_4"))
        self.savetoFileReverseChk = QtGui.QRadioButton(self.groupBox_2)
        self.savetoFileReverseChk.setObjectName(_fromUtf8("savetoFileReverseChk"))
        self.verticalLayout_4.addWidget(self.savetoFileReverseChk)
        self.saveMemoryReverseChk = QtGui.QRadioButton(self.groupBox_2)
        self.saveMemoryReverseChk.setChecked(True)
        self.saveMemoryReverseChk.setObjectName(_fromUtf8("saveMemoryReverseChk"))
        self.verticalLayout_4.addWidget(self.saveMemoryReverseChk)
        self.verticalLayout_5.addWidget(self.groupBox_2)
        spacerItem1 = QtGui.QSpacerItem(20, 75, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_5.addItem(spacerItem1)
        self.settingsTab.addItem(self.reverseTab, _fromUtf8(""))
        self.poiTab = QtGui.QWidget()
        self.poiTab.setObjectName(_fromUtf8("poiTab"))
        self.verticalLayout_7 = QtGui.QVBoxLayout(self.poiTab)
        self.verticalLayout_7.setObjectName(_fromUtf8("verticalLayout_7"))
        self.groupBox_3 = QtGui.QGroupBox(self.poiTab)
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.verticalLayout_6 = QtGui.QVBoxLayout(self.groupBox_3)
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.savetoFileReverseChk_2 = QtGui.QRadioButton(self.groupBox_3)
        self.savetoFileReverseChk_2.setObjectName(_fromUtf8("savetoFileReverseChk_2"))
        self.verticalLayout_6.addWidget(self.savetoFileReverseChk_2)
        self.saveMemoryReverseChk_2 = QtGui.QRadioButton(self.groupBox_3)
        self.saveMemoryReverseChk_2.setChecked(True)
        self.saveMemoryReverseChk_2.setObjectName(_fromUtf8("saveMemoryReverseChk_2"))
        self.verticalLayout_6.addWidget(self.saveMemoryReverseChk_2)
        self.verticalLayout_7.addWidget(self.groupBox_3)
        spacerItem2 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout_7.addItem(spacerItem2)
        self.settingsTab.addItem(self.poiTab, _fromUtf8(""))
        self.verticalLayout.addWidget(self.settingsTab)
        self.buttonBox = QtGui.QDialogButtonBox(settingsDlg)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Save)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(settingsDlg)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), settingsDlg.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), settingsDlg.reject)
        QtCore.QMetaObject.connectSlotsByName(settingsDlg)

    def retranslateUi(self, settingsDlg):
        settingsDlg.setWindowTitle(_translate("settingsDlg", "Instellingen", None))
        self.groupBox.setTitle(_translate("settingsDlg", "Toevoegen punten aan de kaart", None))
        self.savetoFileAdresChk.setText(_translate("settingsDlg", "Opslaan naar bestand ", None))
        self.saveMemoryAdresChk.setText(_translate("settingsDlg", "Opslaan naar tijdelijke laag", None))
        self.settingsTab.setItemText(self.settingsTab.indexOf(self.adresTab), _translate("settingsDlg", "Zoek naar adres", None))
        self.groupBox_2.setTitle(_translate("settingsDlg", "Toevoegen punten aan de kaart", None))
        self.savetoFileReverseChk.setText(_translate("settingsDlg", "Opslaan naar bestand ", None))
        self.saveMemoryReverseChk.setText(_translate("settingsDlg", "Opslaan naar tijdelijke laag", None))
        self.settingsTab.setItemText(self.settingsTab.indexOf(self.reverseTab), _translate("settingsDlg", "Prikken van een adres", None))
        self.groupBox_3.setTitle(_translate("settingsDlg", "Toevoegen punten aan de kaart", None))
        self.savetoFileReverseChk_2.setText(_translate("settingsDlg", "Opslaan naar bestand ", None))
        self.saveMemoryReverseChk_2.setText(_translate("settingsDlg", "Opslaan naar tijdelijke laag", None))
        self.settingsTab.setItemText(self.settingsTab.indexOf(self.poiTab), _translate("settingsDlg", "Zoeken naar plaatsen", None))

