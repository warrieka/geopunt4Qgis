# -*- coding: utf-8 -*-
"""
/***************************************************************************
geopunt4QgisElevation
                A QGIS plugin
"Tool om geopunt in QGIS te gebruiken"
                -------------------
    begin                : 2014-07-02
    copyright            : (C) 2014 by Kay Warrie
    email                : kaywarrie@gmail.com
***************************************************************************/

/***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************/
"""
from __future__ import absolute_import
from qgis.PyQt.QtCore import Qt, QSettings, QTranslator, QCoreApplication 
from qgis.PyQt.QtWidgets import (QDialog, QPushButton, QDialogButtonBox, QFileDialog, QSizePolicy,
                                 QToolButton, QColorDialog, QInputDialog)
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.core import Qgis, QgsRasterLayer, QgsProject
from qgis.gui import  QgsMessageBar, QgsVertexMarker 
from .ui_geopunt4QgisElevation import Ui_elevationDlg

#mathplotlib
try:
  from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
  from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
  from matplotlib.figure import Figure
  import numpy as np
  mathplotlibWorks = True
except:
  mathplotlibWorks = False    
  
#other libs
import os, webbrowser, sys
from .tools.geometry import geometryHelper
from .tools.elevation import elevationHelper
from .tools.settings import settings
from .mapTools.elevationProfile import lineTool
from .geopunt import geopuntError, elevation

class geopunt4QgisElevationDialog(QDialog):
    def __init__(self, iface):
        QDialog.__init__(self, None)
        self.setWindowFlags( self.windowFlags() & ~Qt.WindowContextHelpButtonHint )

        self.iface = iface
    
        # initialize locale
        locale = QSettings().value("locale/userLocale", "en")
        if not locale: locale == 'en'
        else: locale = locale[0:2]
        localePath = os.path.join(os.path.dirname(__file__), 'i18n', 'geopunt4qgis_{}.qm'.format(locale))
        if os.path.exists(localePath):
            self.translator = QTranslator()
            self.translator.load(localePath)
            QCoreApplication.installTranslator(self.translator)
    
        self._initGui()

    def _initGui(self):
        """setup the user interface"""
        self.ui = Ui_elevationDlg()
        self.ui.setupUi(self)
                
        #get settings
        self.s = QSettings()
        self.loadSettings()

        self.gh = geometryHelper( self.iface )
        self.eh = elevationHelper( self.iface, self.startDir)
        
        #setup a message bar
        self.bar = QgsMessageBar() 
        self.bar.setSizePolicy( QSizePolicy.Minimum, QSizePolicy.Fixed )
        self.ui.verticalLayout.addWidget(self.bar)
        
        self.ui.buttonBox.addButton(QPushButton("Sluiten"), QDialogButtonBox.RejectRole )
        for btn in self.ui.buttonBox.buttons():
            btn.setAutoDefault(0)
                  
        ##graph global vars
        self.Rubberline =  None
        self.profile = None
        self.pt = None
        self.ax = None
        self.ano = None
        self.anoLbl = None
        self.counter = 0
        self.xscaleUnit = (1, "m")
        
        # a figure instance to plot on
        self.figure = Figure()

        #create the Canvas widget and toolbar and set graphWgt as parent
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        ###
        #self.ui.toolbar.layout().insertWidget(0, self.toolbar)
        self.ui.graphWgt.layout().addWidget(self.canvas)
        self.createCanvasToolbar()
        
        #events
        self.ui.drawBtn.clicked.connect(self.drawBtnClicked)
        self.figure.canvas.mpl_connect('motion_notify_event', self.showGraphMotion)
        self.ui.saveLineBtn.clicked.connect(self.saveLineClicked)
        self.ui.savePntBtn.clicked.connect(self.savePntClicked)
        self.ui.addDHMbtn.clicked.connect(self.addDHMasWMS) 
        self.ui.refreshBtn.clicked.connect( self.onRefresh )
        self.ui.buttonBox.helpRequested.connect(self.openHelp)
        
        self.rejected.connect(self.clean )

    def createCanvasToolbar (self):
        '''
        1 Reset original view
        2 Back to  previous view
        3 Forward to next view
        4 Pan axes with left mouse, zoom with right
        5 Zoom to rectangle
        6 Save the figure
        7 Edit curves line and axes parameters
        '''
        self.toolbar.setVisible(False)
        toolbarBtns = self.ui.toolbar.findChildren(QToolButton)
        self.ui.toolbar.setStyleSheet("""QToolButton {border-width: 2px; border-style: outset; 
                                                      border-color: #fbd837; border-radius: 5px ; background-color: white }
                                         QToolButton:pressed { border-style: inset;   background-color: grey } """)
        toolbarBtns[0].setToolTip(QCoreApplication.translate("geopunt4QgisElevationDialog", "Keer terug naar overzicht"))
        toolbarBtns[0].setIcon( QIcon(":/plugins/geopunt4Qgis/images/full_extent.png"))
        toolbarBtns[0].clicked.connect( self.toolbar.home )
        toolbarBtns[1].setToolTip(QCoreApplication.translate("geopunt4QgisElevationDialog", "Vorige"))
        toolbarBtns[1].setIcon( QIcon(":/plugins/geopunt4Qgis/images/previous.png")) 
        toolbarBtns[1].clicked.connect( self.toolbar.back )
        toolbarBtns[2].setToolTip(QCoreApplication.translate("geopunt4QgisElevationDialog", "Volgende"))
        toolbarBtns[2].setIcon( QIcon(":/plugins/geopunt4Qgis/images/next.png"))
        toolbarBtns[2].clicked.connect( self.toolbar.forward )
        toolbarBtns[3].setToolTip(QCoreApplication.translate("geopunt4QgisElevationDialog", "Pannen"))
        toolbarBtns[3].setIcon( QIcon(":/plugins/geopunt4Qgis/images/pan.png")) 
        toolbarBtns[3].clicked.connect( self.toolbar.pan )
        toolbarBtns[4].setToolTip(QCoreApplication.translate("geopunt4QgisElevationDialog", "Zoom naar rechthoek"))
        toolbarBtns[4].setIcon( QIcon(":/plugins/geopunt4Qgis/images/rectangleZoom.png"))  
        toolbarBtns[4].clicked.connect( self.toolbar.zoom )
        toolbarBtns[5].setToolTip(QCoreApplication.translate("geopunt4QgisElevationDialog", "Opslaan als afbeelding"))
        toolbarBtns[5].setIcon( QIcon(":/plugins/geopunt4Qgis/images/save.png"))
        toolbarBtns[5].clicked.connect( self.save_fig ) #semf.toolbar.save_figure
        toolbarBtns[6].setToolTip(QCoreApplication.translate("geopunt4QgisElevationDialog", "Vorm grafiek aanpassen"))
        toolbarBtns[6].setIcon( QIcon(":/plugins/geopunt4Qgis/images/wrench.png")) 
        toolbarBtns[6].clicked.connect( self.toolbar.edit_parameters)
        toolbarBtns[7].setIcon( QIcon(":/plugins/geopunt4Qgis/images/fill.png"))
        toolbarBtns[7].setToolTip( QCoreApplication.translate("geopunt4QgisElevationDialog", "Kies de vulkleur"))
        toolbarBtns[7].clicked.connect( self.setFill)
        
    def loadSettings(self):
        self.timeout =  int( self.s.value("geopunt4qgis/timeout" ,15))
        if settings().proxyUrl:
            self.proxy = settings().proxyUrl
        else:
            self.proxy = ""
        self.samplesSavetoFile = int( self.s.value("geopunt4qgis/samplesSavetoFile" , 1))
        sampleLayer = self.s.value("geopunt4qgis/sampleLayerTxt", "")
        if sampleLayer:  
           self.sampleLayerTxt = sampleLayer
        self.profileLineSavetoFile = int( self.s.value("geopunt4qgis/profileLineSavetoFile" , 1))
        profileLineLayer= self.s.value("geopunt4qgis/profileLineLayerTxt", "")
        if profileLineLayer:
           self.profileLineLayerTxt = profileLineLayer
        self.startDir = self.s.value("geopunt4qgis/startDir", os.path.expanduser("~"))        
        self.elevation = elevation(self.timeout, self.proxy )

    def resizeEvent(self, event):
        QDialog.resizeEvent(self, event)
        if self.ax: self.figure.tight_layout()

    #eventhandlers
    def save_fig(self):
        formats = (
        "Joint Photographic Experts Group (*.jpg) (*.jpg);;Scalable Vector Grapics (*.svg) (*.svg);;"+
        "Portable Document Format (*.pdf) (*.pdf);;Tagged Image File Format (*.tif) (*.tif)"+
        ";;Encapsulated Postscript (*.eps) (*.eps)")
      
        if not(sys.platform == 'win32'):
           formats += ";;Portable Network Graphics  (*.png) (*.png)"
      
        fileName, __ = QFileDialog.getSaveFileName( self , "Save File", self.startDir, formats);
        self.figure.savefig(fileName)
    
    def onRefresh(self):
        if self.ano: 
            self.ano.remove()
            self.ano = None
        if self.anoLbl: 
            self.anoLbl.remove()
            self.anoLbl = None
        self.plot()
    
    def onResize(self, event):
        self.figure.tight_layout()
    
    def openHelp(self):
        webbrowser.open_new_tab("http://www.geopunt.be/voor-experts/geopunt-plug-ins/functionaliteiten/hoogteprofiel")
    
    def drawBtnClicked(self):
        self.clean()
        #self.reSetFigure()
        self.tool = lineTool(self.iface, self.callBack )  
        self.iface.mapCanvas().setMapTool(self.tool)
        self.showMinimized()
        self.counter += 1
             
    def showGraphMotion(self, event):
        if self.ax == None: return
        
        if event.xdata != None and event.ydata != None:
          if self.ano != None: 
             self.ano.remove()
             self.ano = None
          if self.anoLbl != None: 
             self.anoLbl.remove()
             self.anoLbl = None
            
          xdata = np.array( [n[0] for n in self.profile ] ) * self.xscaleUnit[0]
          ydata = np.array( [n[3] for n in self.profile ] )# if n[3] > -9999 ]
          zx = np.interp( event.xdata, xdata, ydata )
          xmax = np.max( xdata ) 
          xmin = np.min( xdata )
          zmax = np.max( ydata )
          zmin = np.max( [n[3] for n in self.profile if n[3] > -9999 ] )
           
          if event.xdata <= xmax and event.xdata >= xmin  :
              self.ano = self.ax.arrow( event.xdata , -9999, 0, zx + 9999, fc="k", ec="k" )
              
              box_props = dict(boxstyle="Round,pad=0.3", fc="cyan", ec="b", lw=2)
              self.anoLbl = self.ax.annotate( str( round(zx, 2)) + " m",  xy= (event.xdata, zx ) , 
                          xytext= (event.xdata , zx + (0.2 * ( zmax - zmin )) ),
                          bbox=box_props )
              self.setMapPt( event.xdata / self.xscaleUnit[0] )
          else:
              self.setMapPt()
              
          event.canvas.draw()
        
    def saveLineClicked(self):
        if not hasattr(self, 'profileLineLayerTxt'):
           layerName, accept = QInputDialog.getText(None,
              QCoreApplication.translate("geopunt4Qgis", 'Laag toevoegen'),
              QCoreApplication.translate("geopunt4Qgis", 'Geef een naam voor de laag op:') )
           if accept == False: 
              return
           else:  
              self.profileLineLayerTxt = layerName
           
        if self.profile != None and self.Rubberline != None:
           title = self.ax.get_title()
           self.eh.save_profile( self.Rubberline.asGeometry(), self.profile, title,
                              self.profileLineLayerTxt, self.profileLineSavetoFile, sender=self )
        
    def savePntClicked(self):
        if not hasattr(self, 'sampleLayerTxt'):
           layerName, accept = QInputDialog.getText(None,
              QCoreApplication.translate("geopunt4Qgis", 'Laag toevoegen'),
              QCoreApplication.translate("geopunt4Qgis", 'Geef een naam voor de laag op:') )
           if accept == False: 
              return
           else:  
              self.sampleLayerTxt = layerName
      
        if self.profile != None:
           title = self.ax.get_title()
           self.eh.save_sample_points( self.profile, title, 
                                   self.sampleLayerTxt, self.samplesSavetoFile, sender=self )
    
    def setFill( self ):
        if self.profile == None: return
        if self.ax == None: return
        
        clr = QColorDialog.getColor( Qt.white, self, QCoreApplication.translate(
                  "geopunt4QgisElevationDialog", "Kies de vulkleur") )
        if clr.isValid():
          xdata = np.array( [n[0] for n in self.profile ] ) * self.xscaleUnit[0]
          ydata = np.array( [n[3] for n in self.profile ] )
          self.ax.fill_between( xdata, ydata, -9999, color=clr.name() )
    
    def addDHMasWMS(self):
        crs = self.gh.getGetMapCrs(self.iface).authid()
        if crs != 'EPSG:31370' or  crs != 'EPSG:3857' or  crs != 'EPSG:3043':
           crs = 'EPSG:31370' 
        dhmUrl =  "url=https://geoservices.informatievlaanderen.be/raadpleegdiensten/DHMV/wms&layers=DHMVII_DTM_1m&&format=image/png&styles=default&crs="+ crs

        try:
            rlayer = QgsRasterLayer(dhmUrl, 'Hoogtemodel', 'wms') 
            if rlayer.isValid():
               rlayer.renderer().setOpacity(0.8)
               QgsProject.instance().addMapLayer(rlayer)
            else: self.bar.pushMessage("Error", 
                QCoreApplication.translate("geopunt4QgisElevationDialog", "Kan WMS niet laden"), 
                level=Qgis.Critical, duration=10) 
        except: 
            self.bar.pushMessage("Error", str( sys.exc_info()[1] ), level=Qgis.Critical, duration=10)
            return 
        
    def plot(self):
        if self.Rubberline == None: return
      
        wgsLine = self.gh.prjLineFromMapCrs( self.Rubberline.asGeometry() )
        lineString = [ list(n) for n in wgsLine.asPolyline()]
        nrSamples = self.ui.nrOfSampleSpin.value()
        #try:
        self.profile = self.elevation.fetchElevaton( lineString, 4326, nrSamples)
        #except geopuntError as ge: 
        #    self.bar.pushMessage("Error", ge.message, level=Qgis.Critical, duration=10)
        #    return 
        
        if np.max( [n[0] for n in self.profile ] ) > 1000: self.xscaleUnit = (0.001 , "km" )
        else: self.xscaleUnit = (1 , "m" )
        
        xdata = np.array( [n[0] for n in self.profile ] ) * self.xscaleUnit[0]
        ydata = np.array( [n[3] for n in self.profile ] )
        
        #need at least 3 values
        if len(xdata) <= 2 or len([n for n in self.profile if n[3] > -9999 ]) <= 2:
           self.bar.pushMessage("Error", 
                QCoreApplication.translate(
                  "geopunt4QgisElevationDialog", "Er werd geen of onvoldoende data gevonden"),
                level=Qgis.Warning, duration=5)
           self.profile = None
           return 
        
        ymin = np.min( [n[3] for n in self.profile if n[3] > -9999 ] )
        ymax = np.max( ydata )
     
        # create an axis
        self.ax = self.figure.add_subplot(111)
        
        # discards the old graph
        self.ax.hold(False)

        # plot data
        self.ax.plot( xdata, ydata,'r*')
        self.ax.fill_between(xdata, ydata, -9999, color='#F8E6E0' )
        self.ax.set_ylim([ymin , ymax])
        self.ax.set_xlim([0 , None ])
        self.ax.set_ylabel("hoogte (m)")
        self.ax.set_xlabel("afstand (%s)" % self.xscaleUnit[1] )
        self.ax.set_title("Hoogteprofiel " + str( self.counter) )

        # refresh canvas
        self.figure.tight_layout()
        self.canvas.draw()
        
    def callBack(self, geom):
        self.iface.mapCanvas().unsetMapTool(self.tool)
        self.Rubberline = geom
        self.showNormal()
        self.activateWindow()
        self.plot()
        self.ui.saveWgt.setEnabled(True)

    def setMapPt(self, dist=None ):
        if self.pt: self.iface.mapCanvas().scene().removeItem(self.pt)
           
        if dist==None: return
        
        if self.Rubberline == None: return 

        # dist is measured in lambert 72 in meters
        lb72Line = self.gh.prjLineFromMapCrs( self.Rubberline.asGeometry() , 31370 )
        lb72pt = lb72Line.interpolate(dist).asPoint()
        pt = self.gh.prjPtToMapCrs(lb72pt, 31370)
        
        self.pt = QgsVertexMarker(self.iface.mapCanvas())
        self.pt.setCenter( pt )
        self.pt.setColor(QColor(0,255,250))
        self.pt.setIconSize(5)
        self.pt.setIconType(QgsVertexMarker.ICON_BOX ) # or ICON_CROSS, ICON_X
        self.pt.setPenWidth(7)
        
        if self.xscaleUnit[0] != 1:
           msg= "lengte= %s %s" %  (round( dist * self.xscaleUnit[0], 2) , self.xscaleUnit[1])
        else:
           msg= "lengte= %s %s" %  (int( dist * self.xscaleUnit[0]) , self.xscaleUnit[1])
        
        self.ui.mgsLbl.setText( msg )    
        
    def clean(self):
        if self.pt:
           self.iface.mapCanvas().scene().removeItem(self.pt)
        if self.Rubberline:
           self.iface.mapCanvas().scene().removeItem(self.Rubberline)
           
        if self.ano: 
           self.ano.remove()
           self.ano = None
        if self.anoLbl: 
           self.anoLbl.remove()
           self.anoLbl = None 
        if self.ax:  
           self.ax.hold(False)
           self.ax.clear()
           self.ax = None
        
        self.figure.clf()
              
        self.canvas.draw()
        self.ui.saveWgt.setEnabled(False)
        self.profile = None
        self.Rubberline = None
        self.ui.mgsLbl.setText("")
