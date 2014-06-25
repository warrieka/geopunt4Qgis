# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_geopunt4QgisAbout.ui'
#
# Created: Mon Jun 16 19:30:04 2014
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

class Ui_aboutDlg(object):
    def setupUi(self, aboutDlg):
        aboutDlg.setObjectName(_fromUtf8("aboutDlg"))
        aboutDlg.resize(440, 428)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/geopunt4Qgis/images/geopuntSmal.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        aboutDlg.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(aboutDlg)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.aboutText = QtGui.QTextBrowser(aboutDlg)
        self.aboutText.setHtml(_fromUtf8("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Ubuntu\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.aboutText.setTextInteractionFlags(QtCore.Qt.LinksAccessibleByKeyboard|QtCore.Qt.LinksAccessibleByMouse|QtCore.Qt.TextBrowserInteraction|QtCore.Qt.TextSelectableByKeyboard|QtCore.Qt.TextSelectableByMouse)
        self.aboutText.setSearchPaths(['images', '../images'])
        self.aboutText.setOpenExternalLinks(True)
        self.aboutText.setOpenLinks(True)
        self.aboutText.setObjectName(_fromUtf8("aboutText"))
        self.verticalLayout.addWidget(self.aboutText)
        self.buttonBox = QtGui.QDialogButtonBox(aboutDlg)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(aboutDlg)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), aboutDlg.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), aboutDlg.reject)
        QtCore.QMetaObject.connectSlotsByName(aboutDlg)

    def retranslateUi(self, aboutDlg):
        aboutDlg.setWindowTitle(_translate("aboutDlg", "Over Geopunt4QGIS", None))

import resources_rc
