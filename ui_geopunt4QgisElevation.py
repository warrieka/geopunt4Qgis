# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_geopunt4QgisElevation.ui'
#
# Created: Sun Jul  6 10:23:53 2014
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
        elevationDlg.resize(581, 419)
        elevationDlg.setMinimumSize(QtCore.QSize(300, 200))
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
        self.nrOfsampleLbl = QtGui.QLabel(elevationDlg)
        self.nrOfsampleLbl.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.nrOfsampleLbl.setObjectName(_fromUtf8("nrOfsampleLbl"))
        self.horizontalLayout.addWidget(self.nrOfsampleLbl)
        self.nrOfSampleSpin = QtGui.QSpinBox(elevationDlg)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.nrOfSampleSpin.sizePolicy().hasHeightForWidth())
        self.nrOfSampleSpin.setSizePolicy(sizePolicy)
        self.nrOfSampleSpin.setSuffix(_fromUtf8(""))
        self.nrOfSampleSpin.setMinimum(10)
        self.nrOfSampleSpin.setMaximum(500)
        self.nrOfSampleSpin.setSingleStep(10)
        self.nrOfSampleSpin.setProperty("value", 50)
        self.nrOfSampleSpin.setObjectName(_fromUtf8("nrOfSampleSpin"))
        self.horizontalLayout.addWidget(self.nrOfSampleSpin)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.saveLineBtn = QtGui.QPushButton(elevationDlg)
        self.saveLineBtn.setObjectName(_fromUtf8("saveLineBtn"))
        self.horizontalLayout_2.addWidget(self.saveLineBtn)
        self.savePntBtn = QtGui.QPushButton(elevationDlg)
        self.savePntBtn.setObjectName(_fromUtf8("savePntBtn"))
        self.horizontalLayout_2.addWidget(self.savePntBtn)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.mgsLbl = QtGui.QLabel(elevationDlg)
        self.mgsLbl.setText(_fromUtf8(""))
        self.mgsLbl.setObjectName(_fromUtf8("mgsLbl"))
        self.horizontalLayout_3.addWidget(self.mgsLbl)
        spacerItem = QtGui.QSpacerItem(389, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem)
        self.buttonBox = QtGui.QDialogButtonBox(elevationDlg)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Help)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.horizontalLayout_3.addWidget(self.buttonBox)
        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.retranslateUi(elevationDlg)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), elevationDlg.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), elevationDlg.reject)
        QtCore.QMetaObject.connectSlotsByName(elevationDlg)

    def retranslateUi(self, elevationDlg):
        elevationDlg.setWindowTitle(_translate("elevationDlg", "Hoogteprofiel", None))
        self.drawBtn.setText(_translate("elevationDlg", "Teken een lijn", None))
        self.nrOfsampleLbl.setText(_translate("elevationDlg", "Aantal samples:", None))
        self.saveLineBtn.setText(_translate("elevationDlg", "Profiellijn opslaan ", None))
        self.savePntBtn.setText(_translate("elevationDlg", "Samples opslaan", None))

import resources_rc
