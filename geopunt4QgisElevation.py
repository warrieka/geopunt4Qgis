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
from PyQt4 import QtCore, QtGui
from ui_geopunt4QgisElevation import Ui_elevationDlg
from qgis.core import *
from qgis.gui import  QgsMessageBar, QgsVertexMarker
#mathplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
import matplotlib.pyplot as plt
import numpy as np
#other libs
from geometryhelper import geometryHelper
from elevtionHelper import elevationHelper
from elevationProfileMapTool import lineTool
import geopunt, os, json, webbrowser, random

class geopunt4QgisElevationDialog(QtGui.QDialog):
    def __init__(self, iface):
        QtGui.QDialog.__init__(self)
        self.iface = iface
    
        # initialize locale
        locale = QtCore.QSettings().value("locale/userLocale")[0:2]
        localePath = os.path.join(os.path.dirname(__file__), 'i18n', 'geopunt4qgis_{}.qm'.format(locale))
        if os.path.exists(localePath):
            self.translator = QtCore.QTranslator()
            self.translator.load(localePath)
            if QtCore.qVersion() > '4.3.3': QtCore.QCoreApplication.installTranslator(self.translator)
    
        self._initGui()

    def _initGui(self):
        """setup the user interface"""
        self.ui = Ui_elevationDlg()
        self.ui.setupUi(self)
                
        #get settings
        self.s = QtCore.QSettings()
        self.loadSettings()
        
        self.firstShow = True 
        
        #vars
        self.elevation = geopunt.elevation(self.timeout, self.proxy, self.port )
        self.gh = geometryHelper( self.iface )
        self.eh = elevationHelper( self.iface )
        
        #setup a message bar
        self.bar = QgsMessageBar() 
        self.bar.setSizePolicy( QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed )
        self.ui.verticalLayout.addWidget(self.bar)
        
        ##graph global vars
        self.Rubberline =  None
        self.profile = None
        self.pt = None
        self.ax = None
        self.ano = None
        self.anoLbl = None
        
        # a figure instance to plot on
        self.figure = plt.figure()

        #create the Canvas widget and toolbar and set graphWgt as parent
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.toolbar.findChildren(QtGui.QLabel)[0].setParent(None) #disable position label 
        self.ui.graphWgt.layout().addWidget(self.canvas)
        self.ui.graphWgt.layout().addWidget(self.toolbar)
        
        #events
        self.ui.drawBtn.clicked.connect(self.draw)
        self.figure.canvas.mpl_connect('motion_notify_event', self.showGraphPt)
        self.ui.saveLineBtn.clicked.connect(self.saveLineClicked)
        self.ui.savePntBtn.clicked.connect(self.savePntClicked)
        self.rejected.connect(self.clean )

    def loadSettings(self):
        self.timeout =  int(  self.s.value("geopunt4qgis/timeout" ,15))
        self.proxy = self.s.value("geopunt4qgis/proxyHost" ,"")
        self.port = self.s.value("geopunt4qgis/proxyPort" ,"")       
       
    #eventhandlers
    def showGraphPt(self, event):
        if self.ax == None: return
        
        if event.xdata != None and event.ydata != None:
          if self.ano: 
             self.ano.remove()
             self.ano = None
          if self.anoLbl: 
             self.anoLbl.remove()
             self.anoLbl = None
            
          xdata = [n[0] for n in self.profile if n[3] > -9999 ]
          ydata = [n[3] for n in self.profile if n[3] > -9999 ]
          zx = np.interp( event.xdata, xdata, ydata )
          xmax = np.max( xdata ) 
          xmin = np.min( xdata )
          
          if event.xdata <= xmax and event.xdata >= xmin  :
              self.ano = self.ax.arrow( event.xdata , 0, 0,  zx, fc="k", ec="k" )
              box_props = dict(boxstyle="Round,pad=0.3", fc="cyan", ec="b", lw=2)
              self.anoLbl = self.ax.annotate( str( round(zx, 2)) + " m" ,  xy= (event.xdata , zx ) , 
                                            xytext= (event.xdata , zx ), bbox=box_props )
              self.setMapPt( event.xdata )
          else:
              self.setMapPt()
              
          event.canvas.draw()
        
    def saveLineClicked(self):
        if self.profile != None and self.Rubberline != None:
           self.eh.save_profile( self.Rubberline.asGeometry(), self.profile, "elevation_profile", False, sender=self )
        
    def savePntClicked(self):
        if self.profile != None:
           self.eh.save_sample_points( self.profile, "elevation_samples", True, sender=self )
        
    def plot(self):
        wgsLine = self.gh.prjLineFromMapCrs( self.Rubberline.asGeometry() )
        lineString = [ list(n) for n in wgsLine.asPolyline()]
        nrSamples = self.ui.nrOfSampleSpin.value()
        self.profile = self.elevation.fetchElevaton( lineString, 4326, nrSamples)
        
        xdata = [n[0] for n in self.profile if n[3] > -9999 ]
        ydata = [n[3] for n in self.profile if n[3] > -9999 ]
        # create an axis
        self.ax = self.figure.add_subplot(111)

        # discards the old graph
        self.ax.hold(False)

        # plot data
        self.ax.plot( xdata, ydata,'r*-')
        plt.ylabel("hoogte (m)")
        plt.xlabel("afstand (m)")

        # refresh canvas
        self.canvas.draw()

    def callBack(self, geom):
        self.iface.mapCanvas().unsetMapTool(self.tool)
        self.Rubberline = geom
        self.plot()

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
        self.pt.setColor(QtGui.QColor(0,255,250))
        self.pt.setIconSize(5)
        self.pt.setIconType(QgsVertexMarker.ICON_BOX ) # or ICON_CROSS, ICON_X
        self.pt.setPenWidth(7)

        self.ui.mgsLbl.setText("lengte= %s" % dist )    
        
    def draw(self):
        self.clean()
        
        self.tool = lineTool(self.iface, self.callBack )  
        self.iface.mapCanvas().setMapTool(self.tool)
             
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
          self.ax = None
          
        self.canvas.draw()
        
