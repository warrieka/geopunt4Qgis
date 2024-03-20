from qgis.PyQt.QtCore import (Qt, QSettings, QTranslator, QCoreApplication)
from qgis.PyQt.QtWidgets import (QDialog, QPushButton, QDialogButtonBox,
                                 QInputDialog, QSizePolicy)
from qgis.PyQt.QtGui import QStandardItem, QStandardItemModel
from .ui_geopunt4QgisDataCatalog import Ui_geopunt4QgisDataCatalogDlg
from qgis.core import Qgis, QgsProject, QgsRasterLayer, QgsVectorLayer
from qgis.gui import QgsMessageBar
from .geopunt.metadataParser import (getWmsLayerNames, getWFSLayerNames, get_ogc_api_collections,
                                     getWCSlayerNames, makeWFSuri, makeWCSuri, makeOGCAPIuri)
from .geopunt.datavindPlaats import datavindPlaats
from .tools.geometry import geometryHelper
import os, webbrowser, sys

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
        self.dvp = datavindPlaats()
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
        self.bronnen = None

        self.resultModel = QStandardItemModel(self)
        self.ui.resultView.setModel(self.resultModel)

        # eventhandlers
        self.ui.zoekBtn.clicked.connect(self.onZoekClicked)
        self.ui.addWMSbtn.clicked.connect(self.addWMS)
        self.ui.addWFSbtn.clicked.connect(self.addWFS)
        self.ui.addWCSbtn.clicked.connect(self.addWCS)
        self.ui.ogcAPIbtn.clicked.connect(self.add_ogcapi)

        self.ui.resultView.clicked.connect(self.resultViewClicked)
        self.ui.buttonBox.helpRequested.connect(lambda: webbrowser.open_new_tab(
            "https://www.vlaanderen.be/geopunt/plug-ins/qgis-plug-in/functionaliteiten-qgis-plug-in/geopunt-catalogus-in-qgis"))
        self.finished.connect(self.clean)

    def _setModel(self, records):
        self.resultModel.clear()
        # records = sorted(records, key=lambda k: k['title']) 

        for rec in records:
            title = QStandardItem(rec['title'])                 # 0
            identifier = QStandardItem(rec["identifier"])       # 1
            description =  QStandardItem(rec["description"])    # 2
            date_modified = QStandardItem(rec["modified"])      # 3
            accessRights = QStandardItem(rec["accessRights"])   # 4
            self.resultModel.appendRow([title,identifier,description,date_modified,accessRights])

    def show(self):
        QDialog.show(self)
        self.setWindowModality(0)
        if self.firstShow:
            self.firstShow = False

    # eventhandlers
    def resultViewClicked(self):
        self.wms = self.wfs = self.wcs = self.ogcfeats = None

        if self.ui.resultView.selectedIndexes():
            row = self.ui.resultView.selectedIndexes()[0].row()

            title = self.resultModel.data(self.resultModel.index(row, 0))
            identifier = self.resultModel.data(self.resultModel.index(row, 1))
            abstract = self.resultModel.data(self.resultModel.index(row, 2))
            msg = f"""<h2>{title}</h2>
            <div>{abstract}</div><br/>""" 

            links = self.dvp.findLinks(identifier)
            if len(links):
                msg += '<div>Links:</div><br/>'
                for link in links:
                    name = link['name']
                    url = link['url']
                    urltype = link['type']

                    if urltype == 'wms':
                        self.wms = url
                        self.ui.addWMSbtn.setEnabled(1)
                    else:
                        self.ui.addWMSbtn.setEnabled(0)

                    if urltype == 'wfs':
                        self.wfs = url
                        self.ui.addWFSbtn.setEnabled(1)
                    else:
                        self.ui.addWFSbtn.setEnabled(0)

                    if urltype == 'wcs':
                        self.wcs = url
                        self.ui.addWCSbtn.setEnabled(1)
                    else:
                        self.ui.addWCSbtn.setEnabled(0)

                    if urltype == 'ogc-api':
                        self.ogcfeats = url
                        self.ui.ogcAPIbtn.setEnabled(1)
                    else:
                        self.ui.ogcAPIbtn.setEnabled(0)

                    msg += f"<a target='_blank' href='{url}'>{name}</a> ({urltype})<br/>"

            msg += f"""<div>
             <a href='https://metadata.vlaanderen.be/srv/dut/catalog.search#/metadata/{identifier}'>
             Ga naar metadata fiche</a></div>"""

            self.ui.descriptionText.setText(msg)

    def onZoekClicked(self):
        self.zoek = self.ui.zoekTxt.text()
        dataType = None
        if  self.ui.typeCbx.currentText() == 'Service' :
            dataType = 'type/service'
        elif  self.ui.typeCbx.currentText() == 'Dataset' :
            dataType = 'type/dataset'
        data = self.dvp.findAllItems(self.zoek, taxonomy=dataType)
        self.parse_searchResults(data)

    def parse_searchResults(self, data):
        if len(data) == 0:
            self.bar.pushMessage(
                QCoreApplication.translate("geopunt4QgisPoidialog", "Waarschuwing "),
                QCoreApplication.translate("geopunt4QgisPoidialog",
                        "Er werden geen resultaten gevonde voor deze zoekopdracht"), duration=5)
            return

        self.ui.countLbl.setText(f"Aantal gevonden: {len(data)}" )
        self.ui.descriptionText.setText('')
        self._setModel( data )

    def addWMS(self):
        if self.wms is None: return
        lyrs = getWmsLayerNames(self.wms)

        if len(lyrs) == 0:
            self.bar.pushMessage("WMS",
                QCoreApplication.translate("geopunt4QgisDataCatalog", 
                                    f"Kan geen lagen vinden in: {self.wms}" ),
                level=Qgis.Warning, duration=10)
            return
        elif len(lyrs) == 1:
            layerTitle = lyrs[0][1]
            layerName  = lyrs[0][0]
        else: 
            layerTitle, accept = QInputDialog.getItem(self, "WMS toevoegen",
                            "Kies een laag om toe te voegen", [n[1] for n in lyrs], editable=0)
            if not accept: return
            layerName = [n[0] for n in lyrs if n[1] == layerTitle][0]
        
        crs = self.gh.getGetMapCrs(self.iface).authid()
        if  crs != 'EPSG:31370' or crs != 'EPSG:3857' or crs != 'EPSG:3043':
            crs = 'EPSG:31370'

        url = self.wms.split('?')[0]

        if crs != 'EPSG:31370' or crs != 'EPSG:3857': crs = 'EPSG:31370'
        wmsUrl = f"contextualWMSLegend=0&dpiMode=7&url={url}&layers={layerName}&styles=&format=image/png&crs={crs}"
        rlayer = QgsRasterLayer(wmsUrl, layerTitle, 'wms')
        if rlayer.isValid():
            QgsProject.instance().addMapLayer(rlayer)
        else:
            self.bar.pushMessage("Error",
                 QCoreApplication.translate("geopunt4QgisDataCatalog", "Kan WMS niet laden"),
                 level=Qgis.Critical, duration=10)

    def addWFS(self):
        if self.wfs is None: return
        lyrs, version = getWFSLayerNames(self.wfs)

        if len(lyrs) == 0:
            self.bar.pushMessage("WFS",
                 QCoreApplication.translate("geopunt4QgisDataCatalog",
                 "Kan geen lagen vinden in: %s" % self.wfs), level=Qgis.Warning, duration=10)
            return
        elif len(lyrs) == 1:
            layerName = lyrs[0][0]
            layerTitle = lyrs[0][1]
        else:
            layerTitle, accept = QInputDialog.getItem(self, "WFS toevoegen",
                    "Kies een laag om toe te voegen", [n[1] for n in lyrs], editable=0)
            if not accept: 
                return
            layerName = [n[0] for n in lyrs if n[1] == layerTitle][0]
        crs =  [n[2] for n in lyrs if n[0] == layerName][0]
        wfsUri = makeWFSuri(self.wfs, layerName, srsname=crs, version=version )

        try:
          vlayer = QgsVectorLayer(wfsUri, layerTitle, "WFS")
          QgsProject.instance().addMapLayer(vlayer)
        except:
            self.bar.pushMessage("Error", str(sys.exc_info()[1]), level=Qgis.Critical, duration=10)
            return

    def addWCS(self):
        if self.wcs is None: return
        lyrs = getWCSlayerNames(self.wcs) 

        if len(lyrs) == 0:
            self.bar.pushMessage("WCS",
                 QCoreApplication.translate("geopunt4QgisDataCatalog",
                 "Kan geen lagen vinden in: %s" % self.wcs), level=Qgis.Warning, duration=10)
            return
        elif len(lyrs) == 1:
            layerName = lyrs[0][0]
            layerTitle = lyrs[0][1]
        else:
            layerTitle, accept = QInputDialog.getItem(self, "WCS toevoegen",
                    "Kies een laag om toe te voegen", [n[1] for n in lyrs], editable=0)
            if not accept: 
                return
            layerName = [n[0] for n in lyrs if n[1] == layerTitle][0]
        format =  [n[2] for n in lyrs if n[0] == layerName][0]
        url = self.wcs.split('?')[0]

        wcsUri = makeWCSuri(url, layerName, format=format)

        try:
          vlayer = QgsRasterLayer(wcsUri, layerTitle, "wcs")
          QgsProject.instance().addMapLayer(vlayer)
        except:
            self.bar.pushMessage("Error", str(sys.exc_info()[1]), level=Qgis.Critical, duration=10)
            return

    def add_ogcapi(self):
        if self.ogcfeats is None: return
        lyrs = get_ogc_api_collections(self.ogcfeats) 
        
        if len(lyrs) == 0:
            self.bar.pushMessage("OGC-API",
                 QCoreApplication.translate("geopunt4QgisDataCatalog",
                 "Kan geen lagen vinden in: %s" % self.ogcfeats), level=Qgis.Warning, duration=10)
            return
        elif len(lyrs) == 1:
            layerName = lyrs[0][0]
            layerTitle = lyrs[0][1]
        else:
            layerTitle, accept = QInputDialog.getItem(self, "OGC laag toevoegen",
                    "Kies een laag om toe te voegen", [n[1] for n in lyrs], editable=0)
            if not accept: 
                return
            layerName = [n[0] for n in lyrs if n[1] == layerTitle][0]

        ogcUri = makeOGCAPIuri(self.ogcfeats, layerName)
        print(ogcUri)
        try:
            vlayer = QgsVectorLayer(ogcUri, layerTitle, "OAPIF")
            QgsProject.instance().addMapLayer(vlayer)
        except:
            self.bar.pushMessage("Error", str(sys.exc_info()[1]), level=Qgis.Critical, duration=10)
            return

    def clean(self):
        self.resultModel.clear()
        self.wms = None
        self.wfs = None
        self.wcs = None
        self.ogcfeats = None
        self.ui.zoekTxt.clear()
        self.ui.descriptionText.setText('')
        self.ui.countLbl.setText("")
        self.ui.msgLbl.setText("")
        self.ui.addWMSbtn.setEnabled(0)
        self.ui.addWFSbtn.setEnabled(0)
        self.ui.addWMSbtn.setEnabled(0)