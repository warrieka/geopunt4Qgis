# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_geopunt4qgisParcel.ui'
#
# Created: Tue Nov 24 11:49:53 2015
#      by: PyQt4 UI code generator 4.10.2
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

class Ui_geopunt4QgisParcelDlg(object):
    def setupUi(self, geopunt4QgisParcelDlg):
        geopunt4QgisParcelDlg.setObjectName(_fromUtf8("geopunt4QgisParcelDlg"))
        geopunt4QgisParcelDlg.resize(397, 280)
        geopunt4QgisParcelDlg.setMinimumSize(QtCore.QSize(0, 280))
        geopunt4QgisParcelDlg.setMaximumSize(QtCore.QSize(900, 280))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/geopunt4Qgis/images/geopuntParcelSmall.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        geopunt4QgisParcelDlg.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(geopunt4QgisParcelDlg)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.parcelWgt = QtGui.QWidget(geopunt4QgisParcelDlg)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.parcelWgt.sizePolicy().hasHeightForWidth())
        self.parcelWgt.setSizePolicy(sizePolicy)
        self.parcelWgt.setObjectName(_fromUtf8("parcelWgt"))
        self.formLayout = QtGui.QFormLayout(self.parcelWgt)
        self.formLayout.setMargin(0)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.municipalityLbl = QtGui.QLabel(self.parcelWgt)
        self.municipalityLbl.setObjectName(_fromUtf8("municipalityLbl"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.municipalityLbl)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.municipalityCbx = QtGui.QComboBox(self.parcelWgt)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.municipalityCbx.sizePolicy().hasHeightForWidth())
        self.municipalityCbx.setSizePolicy(sizePolicy)
        self.municipalityCbx.setEditable(True)
        self.municipalityCbx.setObjectName(_fromUtf8("municipalityCbx"))
        self.horizontalLayout.addWidget(self.municipalityCbx)
        self.ZoomKnop_muni = QtGui.QPushButton(self.parcelWgt)
        self.ZoomKnop_muni.setText(_fromUtf8(""))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/geopunt4Qgis/images/binocularsSmall.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.ZoomKnop_muni.setIcon(icon1)
        self.ZoomKnop_muni.setAutoDefault(True)
        self.ZoomKnop_muni.setFlat(False)
        self.ZoomKnop_muni.setObjectName(_fromUtf8("ZoomKnop_muni"))
        self.horizontalLayout.addWidget(self.ZoomKnop_muni)
        self.formLayout.setLayout(1, QtGui.QFormLayout.FieldRole, self.horizontalLayout)
        self.departmentLbl = QtGui.QLabel(self.parcelWgt)
        self.departmentLbl.setObjectName(_fromUtf8("departmentLbl"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.departmentLbl)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.departmentCbx = QtGui.QComboBox(self.parcelWgt)
        self.departmentCbx.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.departmentCbx.sizePolicy().hasHeightForWidth())
        self.departmentCbx.setSizePolicy(sizePolicy)
        self.departmentCbx.setEditable(True)
        self.departmentCbx.setObjectName(_fromUtf8("departmentCbx"))
        self.horizontalLayout_2.addWidget(self.departmentCbx)
        self.ZoomKnop_dep = QtGui.QPushButton(self.parcelWgt)
        self.ZoomKnop_dep.setText(_fromUtf8(""))
        self.ZoomKnop_dep.setIcon(icon1)
        self.ZoomKnop_dep.setAutoDefault(True)
        self.ZoomKnop_dep.setFlat(False)
        self.ZoomKnop_dep.setObjectName(_fromUtf8("ZoomKnop_dep"))
        self.horizontalLayout_2.addWidget(self.ZoomKnop_dep)
        self.formLayout.setLayout(3, QtGui.QFormLayout.FieldRole, self.horizontalLayout_2)
        self.sectionLbl = QtGui.QLabel(self.parcelWgt)
        self.sectionLbl.setObjectName(_fromUtf8("sectionLbl"))
        self.formLayout.setWidget(4, QtGui.QFormLayout.LabelRole, self.sectionLbl)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.sectionCbx = QtGui.QComboBox(self.parcelWgt)
        self.sectionCbx.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sectionCbx.sizePolicy().hasHeightForWidth())
        self.sectionCbx.setSizePolicy(sizePolicy)
        self.sectionCbx.setEditable(True)
        self.sectionCbx.setObjectName(_fromUtf8("sectionCbx"))
        self.horizontalLayout_3.addWidget(self.sectionCbx)
        self.ZoomKnop_sect = QtGui.QPushButton(self.parcelWgt)
        self.ZoomKnop_sect.setText(_fromUtf8(""))
        self.ZoomKnop_sect.setIcon(icon1)
        self.ZoomKnop_sect.setAutoDefault(True)
        self.ZoomKnop_sect.setFlat(False)
        self.ZoomKnop_sect.setObjectName(_fromUtf8("ZoomKnop_sect"))
        self.horizontalLayout_3.addWidget(self.ZoomKnop_sect)
        self.formLayout.setLayout(5, QtGui.QFormLayout.FieldRole, self.horizontalLayout_3)
        self.parcelLbl = QtGui.QLabel(self.parcelWgt)
        self.parcelLbl.setObjectName(_fromUtf8("parcelLbl"))
        self.formLayout.setWidget(6, QtGui.QFormLayout.LabelRole, self.parcelLbl)
        self.horizontalLayout_4 = QtGui.QHBoxLayout()
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.parcelCbx = QtGui.QComboBox(self.parcelWgt)
        self.parcelCbx.setEnabled(False)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.parcelCbx.sizePolicy().hasHeightForWidth())
        self.parcelCbx.setSizePolicy(sizePolicy)
        self.parcelCbx.setEditable(True)
        self.parcelCbx.setObjectName(_fromUtf8("parcelCbx"))
        self.horizontalLayout_4.addWidget(self.parcelCbx)
        self.ZoomKnop_parcel = QtGui.QPushButton(self.parcelWgt)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.ZoomKnop_parcel.sizePolicy().hasHeightForWidth())
        self.ZoomKnop_parcel.setSizePolicy(sizePolicy)
        self.ZoomKnop_parcel.setText(_fromUtf8(""))
        self.ZoomKnop_parcel.setIcon(icon1)
        self.ZoomKnop_parcel.setAutoDefault(True)
        self.ZoomKnop_parcel.setFlat(False)
        self.ZoomKnop_parcel.setObjectName(_fromUtf8("ZoomKnop_parcel"))
        self.horizontalLayout_4.addWidget(self.ZoomKnop_parcel)
        self.formLayout.setLayout(7, QtGui.QFormLayout.FieldRole, self.horizontalLayout_4)
        self.horizontalLayout_5 = QtGui.QHBoxLayout()
        self.horizontalLayout_5.setObjectName(_fromUtf8("horizontalLayout_5"))
        self.horizontalLayout_6 = QtGui.QHBoxLayout()
        self.horizontalLayout_6.setObjectName(_fromUtf8("horizontalLayout_6"))
        self.label = QtGui.QLabel(self.parcelWgt)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_6.addWidget(self.label)
        self.adresLine = QtGui.QLineEdit(self.parcelWgt)
        self.adresLine.setEnabled(True)
        self.adresLine.setFrame(False)
        self.adresLine.setReadOnly(True)
        self.adresLine.setObjectName(_fromUtf8("adresLine"))
        self.horizontalLayout_6.addWidget(self.adresLine)
        self.horizontalLayout_5.addLayout(self.horizontalLayout_6)
        self.formLayout.setLayout(9, QtGui.QFormLayout.SpanningRole, self.horizontalLayout_5)
        self.verticalLayout.addWidget(self.parcelWgt)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.widgetBtnsLayout = QtGui.QHBoxLayout()
        self.widgetBtnsLayout.setObjectName(_fromUtf8("widgetBtnsLayout"))
        self.saveBtn = QtGui.QPushButton(geopunt4QgisParcelDlg)
        self.saveBtn.setEnabled(False)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/geopunt4Qgis/images/addPointLayer.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.saveBtn.setIcon(icon2)
        self.saveBtn.setAutoDefault(False)
        self.saveBtn.setDefault(False)
        self.saveBtn.setObjectName(_fromUtf8("saveBtn"))
        self.widgetBtnsLayout.addWidget(self.saveBtn)
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.widgetBtnsLayout.addItem(spacerItem1)
        self.buttonBox = QtGui.QDialogButtonBox(geopunt4QgisParcelDlg)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonBox.sizePolicy().hasHeightForWidth())
        self.buttonBox.setSizePolicy(sizePolicy)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Help)
        self.buttonBox.setCenterButtons(False)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.widgetBtnsLayout.addWidget(self.buttonBox)
        self.verticalLayout.addLayout(self.widgetBtnsLayout)

        self.retranslateUi(geopunt4QgisParcelDlg)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), geopunt4QgisParcelDlg.close)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), geopunt4QgisParcelDlg.close)
        QtCore.QMetaObject.connectSlotsByName(geopunt4QgisParcelDlg)

    def retranslateUi(self, geopunt4QgisParcelDlg):
        geopunt4QgisParcelDlg.setWindowTitle(_translate("geopunt4QgisParcelDlg", "Zoek een perceel", None))
        self.municipalityLbl.setText(_translate("geopunt4QgisParcelDlg", "Gemeente:", None))
        self.ZoomKnop_muni.setToolTip(_translate("geopunt4QgisParcelDlg", "Zoom naar", None))
        self.ZoomKnop_muni.setStatusTip(_translate("geopunt4QgisParcelDlg", "Zoom naar", None))
        self.departmentLbl.setText(_translate("geopunt4QgisParcelDlg", "Departement:", None))
        self.ZoomKnop_dep.setToolTip(_translate("geopunt4QgisParcelDlg", "Zoom naar", None))
        self.ZoomKnop_dep.setStatusTip(_translate("geopunt4QgisParcelDlg", "Zoom naar", None))
        self.sectionLbl.setText(_translate("geopunt4QgisParcelDlg", "Sectie:", None))
        self.ZoomKnop_sect.setToolTip(_translate("geopunt4QgisParcelDlg", "Zoom naar", None))
        self.ZoomKnop_sect.setStatusTip(_translate("geopunt4QgisParcelDlg", "Zoom naar", None))
        self.parcelLbl.setText(_translate("geopunt4QgisParcelDlg", "Perceelnummer:", None))
        self.ZoomKnop_parcel.setToolTip(_translate("geopunt4QgisParcelDlg", "Zoom naar", None))
        self.ZoomKnop_parcel.setStatusTip(_translate("geopunt4QgisParcelDlg", "Zoom naar", None))
        self.label.setText(_translate("geopunt4QgisParcelDlg", "Adres:", None))
        self.saveBtn.setText(_translate("geopunt4QgisParcelDlg", "Toevoegen aan kaart", None))

import resources_rc
