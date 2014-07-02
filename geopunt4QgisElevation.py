# -*- coding: utf-8 -*-
"""
/***************************************************************************
geopunt4qgisdialog
                A QGIS plugin
"Tool om geopunt in QGIS te gebruiken"
                -------------------
    begin                : 2013-12-05
    copyright            : (C) 2013 by Kay Warrie
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
        
        #vars
        self.elevation = geopunt.elevation(self.timeout, self.proxy, self.port )
        
        ##graph global vars
        self.Rubberline =  None
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
        self.rejected.connect(self.clean )

    def loadSettings(self):
        self.timeout =  int(  self.s.value("geopunt4qgis/timeout" ,15))
        self.proxy = self.s.value("geopunt4qgis/proxyHost" ,"")
        self.port = self.s.value("geopunt4qgis/proxyPort" ,"")
       
    def plot(self):
        
        wgsLine = self._prjLine2wgs( self.Rubberline.asGeometry() )
        lineString = [ list(n) for n in wgsLine.asPolyline()]
        self.profile = self.elevation.fetchElevaton( lineString, 4326, 50  )

        ''' plot some random stuff '''
        #lengh = self.Rubberline.asGeometry().length()
        #self.ydata = [random.uniform(0,20) for i in range(10)]
        #self.xdata = np.arange(0, lengh, (lengh * 1.1 )/ 10)
        
        self.xdata = [n[0] for n in self.profile if n[3] > -9999 ]
        self.ydata = [n[3] for n in self.profile if n[3] > -9999 ]
        # create an axis
        self.ax = self.figure.add_subplot(111)

        # discards the old graph
        self.ax.hold(False)

        # plot data
        self.ax.plot(self.xdata, self.ydata,'r*-')
        plt.ylabel("hoogte (m)")
        plt.xlabel("afstand (m)")

        # refresh canvas
        self.canvas.draw()

    def showGraphPt(self, event):
        if self.ax == None: return
        
        if event.xdata != None and event.ydata != None:
          if self.ano: 
            self.ano.remove()
            self.ano = None
          if self.anoLbl: 
            self.anoLbl.remove()
            self.anoLbl = None
            
          zx= np.interp( event.xdata, self.xdata,  self.ydata )
          self.ano = self.ax.arrow( event.xdata, 0, 0,  zx, fc="k", ec="k" )
          self.anoLbl = self.ax.annotate( str( round(zx, 2)) ,  xy= (event.xdata, zx ) , xytext= (event.xdata, zx ) )
          self.setMapPt( event.xdata )
          event.canvas.draw()
       
    def callBack(self, geom):
        self.iface.mapCanvas().unsetMapTool(self.tool)
        self.Rubberline = geom
        self.setMapPt( 0 )
        self.plot()

    def setMapPt(self, dist ):
        if self.Rubberline == None: return 
        
        if self.pt:
           self.iface.mapCanvas().scene().removeItem(self.pt)
      
        pt = self.Rubberline.asGeometry().interpolate(dist).asPoint()
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
        
    def _prjLine2wgs(self, lineString, toSrsID=4326 ):
        fromCrs = self.iface.mapCanvas().mapRenderer().destinationCrs()
        toCrs = QgsCoordinateReferenceSystem(toSrsID)
        xform = QgsCoordinateTransform(fromCrs, toCrs)
        wgsLine = [ xform.transform( xy ) for xy in  lineString.asPolyline()]
        return QgsGeometry.fromPolyline( wgsLine )