from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

class lineTool(QgsMapTool):
    def __init__(self, iface, callback):
        QgsMapTool.__init__(self,iface.mapCanvas())
        self.iface  = iface
        self.canvas = iface.mapCanvas()
        self.cursor = QCursor(Qt.CrossCursor)
        self.callback   = callback
        
        self.rubberBand = QgsRubberBand(self.canvas, False)
        self.points  = []
        self.rubberBand.setColor(Qt.red)
        self.rubberBand.setWidth(1.6)

    def canvasReleaseEvent(self,event):
        if event.button() == Qt.RightButton:
          self.points.append( self.toMapCoordinates(event.pos()) )
          if len(self.points) <= 1 :return
        
          self.rubberBand.setToGeometry( QgsGeometry.fromPolyline(self.points), None )
          self.callback( self.rubberBand )
          QgsMapTool.deactivate(self)
        else:
          self.points.append( self.toMapCoordinates(event.pos()) )
          if len(self.points) <= 1 : return
          
          self.rubberBand.setToGeometry( QgsGeometry.fromPolyline(self.points), None )

    def canvasDoubleClickEvent(self,event):
        self.points.append( self.toMapCoordinates(event.pos()) )
        if len(self.points) <= 1 : return
      
        self.rubberBand.setToGeometry( QgsGeometry.fromPolyline(self.points), None )
        self.callback( self.rubberBand )
        QgsMapTool.deactivate(self)
    
    def activate(self):
      QgsMapTool.activate(self)
      self.canvas.setCursor(self.cursor)

    def isZoomTool(self):
        return False

    def setCursor(self,cursor):
        self.cursor = QCursor(cursor)
        