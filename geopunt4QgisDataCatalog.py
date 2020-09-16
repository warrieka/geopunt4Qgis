# -*- coding: utf-8 -*-
from qgis.PyQt.QtCore import Qt, QSettings, QTranslator, QCoreApplication, QRegExp, QSortFilterProxyModel, QStringListModel
from qgis.PyQt.QtWidgets import QDialog, QPushButton, QDialogButtonBox, QCompleter, QInputDialog, QSizePolicy
from qgis.PyQt.QtGui import QStandardItem, QStandardItemModel
from .ui_geopunt4QgisDataCatalog import Ui_geopunt4QgisDataCatalogDlg
from qgis.core import Qgis, QgsProject, QgsRasterLayer, QgsVectorLayer
from qgis.gui import QgsMessageBar
import os, webbrowser, sys
from .geopunt.metadataParser import MDReader, MDdata, getWmsLayerNames, getWFSLayerNames, makeWFSuri
from .tools.geometry import geometryHelper
from .tools.settings import settings


class geopunt4QgisDataCatalog(QDialog):
    def __init__(self, iface):
        QDialog.__init__(self, None)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.iface = iface

        # initialize locale
        locale = QSettings().value("locale/userLocale", "en")
        if not locale: locale = 'en'
        else: locale = locale[0:2]
        localePath = os.path.join(os.path.dirname(__file__), 'i18n', 'geopunt4qgis_{}.qm'.format(locale))
        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)
            QCoreApplication.installTranslator(self.translator)

        self._initGui()

    def _initGui(self):
        """setup the user interface"""
        self.ui = Ui_geopunt4QgisDataCatalogDlg()
        self.ui.setupUi(self)

        # get settings
        self.s = QSettings()
        self.loadSettings()

        self.gh = geometryHelper(self.iface)

        # setup a message bar
        self.bar = QgsMessageBar()
        self.bar.setSizePolicy( QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.ui.verticalLayout.addWidget(self.bar)

        self.ui.buttonBox.addButton(QPushButton("Sluiten"), QDialogButtonBox.RejectRole)
        for btn in self.ui.buttonBox.buttons():
            btn.setAutoDefault(0)

        # vars
        self.firstShow = True
        self.wms = None
        self.wfs = None
        self.dl = None
        self.zoek = ''
        self.bronnen = None

        self.model = QStandardItemModel(self)
        self.proxyModel = QSortFilterProxyModel(self)
        self.proxyModel.setSourceModel(self.model)
        self.ui.resultView.setModel(self.proxyModel)

        self.completer = QCompleter(self)
        self.completerModel = QStringListModel(self)
        self.ui.zoekTxt.setCompleter(self.completer)
        self.completer.setModel(self.completerModel)

        # eventhandlers
        self.ui.zoekBtn.clicked.connect(self.onZoekClicked)
        self.ui.addWMSbtn.clicked.connect(self.addWMS)
        self.ui.addWFSbtn.clicked.connect(self.addWFS)
        self.ui.DLbtn.clicked.connect(lambda: self.openUrl(self.dl))
        self.ui.resultView.clicked.connect(self.resultViewClicked)
        self.ui.modelFilterCbx.currentIndexChanged.connect(self.modelFilterCbxIndexChanged)
        self.ui.filterWgt.setHidden(1)
        self.ui.buttonBox.helpRequested.connect(self.openHelp)
        self.finished.connect(self.clean)

    def loadSettings(self):
        self.timeout = int(self.s.value("geopunt4qgis/timeout", 15))

        s = settings()
        self.proxy = s.proxy
        self.md = MDReader(self.timeout, self.proxy)

    def openHelp(self):
        webbrowser.open_new_tab("http://www.geopunt.be/voor-experts/geopunt-plug-ins/functionaliteiten/catalogus")

    def _setModel(self, records):
        self.model.clear()
        records = sorted(records, key=lambda k: k['title']) 

        for rec in records:
            title = QStandardItem(rec['title'])  # 0
            wms = QStandardItem(rec['wms'])  # 1
            downloadLink = QStandardItem(rec['download'])  # 2
            id = QStandardItem(rec['uuid'])  # 3
            abstract = QStandardItem(rec['abstract'])  # 4
            wfs = QStandardItem(rec['wfs'])  # 5
            self.model.appendRow([title, wms, downloadLink, id, abstract, wfs])

    # overwrite
    def show(self):
        QDialog.show(self)
        self.setWindowModality(0)
        metadataUrl = "https://metadata.geopunt.be"

        if self.firstShow:
            self.ui.GDIThemaCbx.addItems([''] + self.md.list_GDI_theme())
            self.ui.organisatiesCbx.addItems([''] + self.md.list_organisations())
            keywords = sorted(self.md.list_suggestionKeyword())
            self.completerModel.setStringList(keywords)
            self.bronnen = self.md.list_bronnen()
            self.ui.bronCbx.addItems([''] + [n[1] for n in self.bronnen])
            self.ui.typeCbx.addItems([''] + [n[0] for n in self.md.dataTypes])

            self.ui.INSPIREannexCbx.addItems([''] + self.md.inspireannex)
            self.ui.INSPIREserviceCbx.addItems([''] + self.md.inspireServiceTypes)
            self.ui.INSPIREthemaCbx.addItems([''] + self.md.list_inspire_theme())
            self.firstShow = False


    # eventhandlers
    def resultViewClicked(self):
        if self.ui.resultView.selectedIndexes():
            row = self.ui.resultView.selectedIndexes()[0].row()

            title = self.proxyModel.data(self.proxyModel.index(row, 0))
            self.wms = self.proxyModel.data(self.proxyModel.index(row, 1))
            self.dl = self.proxyModel.data(self.proxyModel.index(row, 2))
            self.wfs = self.proxyModel.data(self.proxyModel.index(row, 5))
            uuid = self.proxyModel.data(self.proxyModel.index(row, 3))
            abstract = self.proxyModel.data(self.proxyModel.index(row, 4))

            self.ui.descriptionText.setText(
                """<h3>%s</h3><div>%s</div><br/><div>
             <a href='https://metadata.geopunt.be/zoekdienst/apps/tabsearch/index.html?uuid=%s'>
             Ga naar fiche</a></div>""" % (title, abstract, uuid))

            if self.wms:
                self.ui.addWMSbtn.setEnabled(1)
            else:
                self.ui.addWMSbtn.setEnabled(0)

            if self.wfs:
                self.ui.addWFSbtn.setEnabled(1)
            else:
                self.ui.addWFSbtn.setEnabled(0)

            if self.dl:
                self.ui.DLbtn.setEnabled(1)
            else:
                self.ui.DLbtn.setEnabled(0)

    def onZoekClicked(self):
        self.zoek = self.ui.zoekTxt.currentText()
        self.search()

    def modelFilterCbxIndexChanged(self):
        value = self.ui.modelFilterCbx.currentIndex()
        if value == 1:
            self.filterModel(1)
        elif value == 2:
            self.filterModel(5)
        elif value == 3:
            self.filterModel(2)
        else:
            self.filterModel()

    def filterModel(self, col=None):
        if col != None:
            self.proxyModel.setFilterKeyColumn(col)
            expr = QRegExp("?*", Qt.CaseInsensitive, QRegExp.Wildcard)
            self.proxyModel.setFilterRegExp(expr)
        else:
            self.proxyModel.setFilterRegExp(None)

    def search(self):
        try:
            if self.ui.filterBox.isChecked():
                themekey = self.ui.GDIThemaCbx.currentText()
                orgName = self.ui.organisatiesCbx.currentText()
                dataTypes = [n[1] for n in self.md.dataTypes if n[0] == self.ui.typeCbx.currentText()]
                if dataTypes != []:
                    dataType = dataTypes[0]
                else:
                    dataType = ''
                siteIds = [n[0] for n in self.bronnen if n[1] == self.ui.bronCbx.currentText()]
                if siteIds != []:
                    siteId = siteIds[0]
                else:
                    siteId = ''
                inspiretheme = self.ui.INSPIREthemaCbx.currentText()
                inspireannex = self.ui.INSPIREannexCbx.currentText()
                inspireServiceType = self.ui.INSPIREserviceCbx.currentText()
                searchResult = MDdata(self.md.searchAll(
                    self.zoek, themekey, orgName, dataType, siteId, inspiretheme, inspireannex, inspireServiceType))
            else:
                searchResult = MDdata(self.md.searchAll(self.zoek))
        except:
            self.bar.pushMessage("Error", str(sys.exc_info()[1]), level=Qgis.Critical, duration=3)
            return

        self.ui.countLbl.setText("Aantal gevonden: %s" % searchResult.count)
        self.ui.descriptionText.setText('')
        self._setModel(searchResult.records)
        if searchResult.count == 0:
            self.bar.pushMessage(
                QCoreApplication.translate("geopunt4QgisPoidialog", "Waarschuwing "),
                QCoreApplication.translate("geopunt4QgisPoidialog",
                                                  "Er werden geen resultaten gevonde voor deze zoekopdracht"),
                duration=5)

    def openUrl(self, url):
        if url: webbrowser.open_new_tab(url.encode("utf-8"))

    def addWMS(self):
        if self.wms == None: return

        crs = self.gh.getGetMapCrs(self.iface).authid()
        if crs != 'EPSG:31370' or crs != 'EPSG:3857' or crs != 'EPSG:3043':
            crs = 'EPSG:31370'
        try:
            lyrs = getWmsLayerNames(self.wms, self.proxy)
        except:
            self.bar.pushMessage("Error", str(sys.exc_info()[1]), level=Qgis.Critical, duration=10)
            return
        if len(lyrs) == 0:
            self.bar.pushMessage("WMS",
                                 QCoreApplication.translate("geopunt4QgisDataCatalog",
                                                                   "Kan geen lagen vinden in: %s" % self.wms),
                                 level=Qgis.Warning, duration=10)
            return
        elif len(lyrs) == 1:
            layerTitle = lyrs[0][1]
        else:
            layerTitle, accept = QInputDialog.getItem(self, "WMS toevoegen",
                                                            "Kies een laag om toe te voegen", [n[1] for n in lyrs],
                                                            editable=0)
            if not accept: return

        layerName = [n[0] for n in lyrs if n[1] == layerTitle][0]
        style = [n[2] for n in lyrs if n[1] == layerTitle][0]
        if not style: style = ""
        
        url = self.wms.split('?')[0]

        if crs != 'EPSG:31370' or crs != 'EPSG:3857':
            crs = 'EPSG:31370'
        wmsUrl = "contextualWMSLegend=0&dpiMode=7&url=%s&layers=%s&format=image/png&styles=%s&crs=%s" % (
                                                                         url, layerName, style, crs)

        try:
            rlayer = QgsRasterLayer(wmsUrl, layerTitle, 'wms')
            if rlayer.isValid():
                QgsProject.instance().addMapLayer(rlayer)
            else:
                self.bar.pushMessage("Error",
                                     QCoreApplication.translate("geopunt4QgisDataCatalog", "Kan WMS niet laden"),
                                     level=Qgis.Critical, duration=10)
        except:
            self.bar.pushMessage("Error", str(sys.exc_info()[1]), level=Qgis.Critical, duration=10)
            return

    def addWFS(self):
        if self.wfs == None: return
        try:
            lyrs = getWFSLayerNames(self.wfs, self.proxy)
        except:
            self.bar.pushMessage("Error", str(sys.exc_info()[1]), level=Qgis.Critical, duration=10)
            return
        if len(lyrs) == 0:
            self.bar.pushMessage("WFS",
                 QCoreApplication.translate("geopunt4QgisDataCatalog",
                 "Kan geen lagen vinden in: %s" % self.wfs), level=Qgis.Warning, duration=10)
            return
        elif len(lyrs) == 1:
            layerTitle = lyrs[0][1]
        else:
            layerTitle, accept = QInputDialog.getItem(self, "WFS toevoegen",
                                                            "Kies een laag om toe te voegen", [n[1] for n in lyrs],
                                                            editable=0)
            if not accept: return

        layerName = [n[0] for n in lyrs if n[1] == layerTitle][0]
        crs = [n[2] for n in lyrs if n[1] == layerTitle][0]
        url = self.wfs.split('?')[0]

        wfsUri = makeWFSuri(url, layerName, crs )

        try:
          vlayer = QgsVectorLayer(wfsUri, layerTitle, "WFS")
          QgsProject.instance().addMapLayer(vlayer)
        except:
            self.bar.pushMessage("Error", str(sys.exc_info()[1]), level=Qgis.Critical, duration=10)
            return

    def clean(self):
        self.model.clear()
        self.wms = None
        self.wfs = None
        self.dl = None
        self.ui.zoekTxt.setCurrentIndex(0)
        self.ui.descriptionText.setText('')
        self.ui.countLbl.setText("")
        self.ui.msgLbl.setText("")
        self.ui.DLbtn.setEnabled(0)
        self.ui.addWFSbtn.setEnabled(0)
        self.ui.addWMSbtn.setEnabled(0)
        self.ui.modelFilterCbx.setCurrentIndex(0)
