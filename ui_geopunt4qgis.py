# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_geopunt4qgis.ui'
#
# Created: Sun Mar 22 21:59:40 2015
#      by: PyQt4 UI code generator 4.11.2
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
        geopunt4Qgis.resize(604, 352)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/geopunt4Qgis/images/geopuntAddressSmall.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        geopunt4Qgis.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(geopunt4Qgis)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.inputBox = QtGui.QGroupBox(geopunt4Qgis)
        self.inputBox.setObjectName(_fromUtf8("inputBox"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.inputBox)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.gemeenteBox = QtGui.QComboBox(self.inputBox)
        self.gemeenteBox.setEditable(True)
        self.gemeenteBox.setObjectName(_fromUtf8("gemeenteBox"))
        self.horizontalLayout.addWidget(self.gemeenteBox)
        self.zoekText = QtGui.QLineEdit(self.inputBox)
        self.zoekText.setObjectName(_fromUtf8("zoekText"))
        self.horizontalLayout.addWidget(self.zoekText)
        self.verticalLayout.addWidget(self.inputBox)
        self.resultLijst = QtGui.QListWidget(geopunt4Qgis)
        self.resultLijst.setObjectName(_fromUtf8("resultLijst"))
        self.verticalLayout.addWidget(self.resultLijst)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.Add2mapKnop = QtGui.QPushButton(geopunt4Qgis)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/geopunt4Qgis/images/addPointLayer.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.Add2mapKnop.setIcon(icon1)
        self.Add2mapKnop.setAutoDefault(False)
        self.Add2mapKnop.setObjectName(_fromUtf8("Add2mapKnop"))
        self.horizontalLayout_2.addWidget(self.Add2mapKnop)
        self.ZoomKnop = QtGui.QPushButton(geopunt4Qgis)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/geopunt4Qgis/images/binocularsSmall.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ZoomKnop.setIcon(icon2)
        self.ZoomKnop.setDefault(True)
        self.ZoomKnop.setObjectName(_fromUtf8("ZoomKnop"))
        self.horizontalLayout_2.addWidget(self.ZoomKnop)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.label = QtGui.QLabel(geopunt4Qgis)
        self.label.setMinimumSize(QtCore.QSize(120, 0))
        self.label.setFrameShape(QtGui.QFrame.Panel)
        self.label.setFrameShadow(QtGui.QFrame.Sunken)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_3.addWidget(self.label)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.buttonBox = QtGui.QDialogButtonBox(geopunt4Qgis)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Help)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout_3.addWidget(self.buttonBox)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.laraLbl = QtGui.QLabel(geopunt4Qgis)
        self.laraLbl.setAlignment(QtCore.Qt.AlignBottom|QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing)
        self.laraLbl.setMargin(-1)
        self.laraLbl.setOpenExternalLinks(True)
        self.laraLbl.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse)
        self.laraLbl.setObjectName(_fromUtf8("laraLbl"))
        self.verticalLayout.addWidget(self.laraLbl)

        self.retranslateUi(geopunt4Qgis)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), geopunt4Qgis.close)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), geopunt4Qgis.close)
        QtCore.QMetaObject.connectSlotsByName(geopunt4Qgis)

    def retranslateUi(self, geopunt4Qgis):
        geopunt4Qgis.setWindowTitle(_translate("geopunt4Qgis", "Zoek een adres via Geopunt ", None))
        self.inputBox.setTitle(_translate("geopunt4Qgis", "Selecteer een gemeente. Geef een straat (+nr) op en selecteer dan een suggestie ", None))
        self.zoekText.setPlaceholderText(_translate("geopunt4Qgis", "straat huisnummer", None))
        self.Add2mapKnop.setText(_translate("geopunt4Qgis", "Toevoegen aan kaart", None))
        self.ZoomKnop.setText(_translate("geopunt4Qgis", "Zoom naar", None))
        self.label.setText(_translate("geopunt4Qgis", "  ", None))
        self.laraLbl.setText(_translate("geopunt4Qgis", "<small><a href=\"http://crab.agiv.be/Lara\">Foute adressen kunt u melden via LARA</a></small>", None))

import resources_rc
