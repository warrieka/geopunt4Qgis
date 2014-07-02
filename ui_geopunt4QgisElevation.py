# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_geopunt4QgisElevation.ui'
#
# Created: Wed Jul  2 17:28:37 2014
#      by: PyQt4 UI code generator 4.10.4
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

class Ui_elevationDlg(object):
    def setupUi(self, elevationDlg):
        elevationDlg.setObjectName(_fromUtf8("elevationDlg"))
        elevationDlg.resize(400, 300)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/geopunt4Qgis/images/geopuntElevationSmall.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        elevationDlg.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(elevationDlg)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.graphWgt = QtGui.QWidget(elevationDlg)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.graphWgt.sizePolicy().hasHeightForWidth())
        self.graphWgt.setSizePolicy(sizePolicy)
        self.graphWgt.setObjectName(_fromUtf8("graphWgt"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.graphWgt)
        self.verticalLayout_3.setMargin(0)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.verticalLayout.addWidget(self.graphWgt)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.drawBtn = QtGui.QPushButton(elevationDlg)
        self.drawBtn.setObjectName(_fromUtf8("drawBtn"))
        self.horizontalLayout.addWidget(self.drawBtn)
        self.mgsLbl = QtGui.QLabel(elevationDlg)
        self.mgsLbl.setText(_fromUtf8(""))
        self.mgsLbl.setObjectName(_fromUtf8("mgsLbl"))
        self.horizontalLayout.addWidget(self.mgsLbl)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.buttonBox = QtGui.QDialogButtonBox(elevationDlg)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(elevationDlg)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), elevationDlg.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), elevationDlg.reject)
        QtCore.QMetaObject.connectSlotsByName(elevationDlg)

    def retranslateUi(self, elevationDlg):
        elevationDlg.setWindowTitle(_translate("elevationDlg", "testPrf", None))
        self.drawBtn.setText(_translate("elevationDlg", "teken een lijn", None))

import resources_rc
