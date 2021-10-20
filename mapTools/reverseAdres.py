from qgis.gui import QgsMapTool

class reverseAdresMapTool(QgsMapTool):
    def __init__(self, iface, callback):
        QgsMapTool.__init__(self,iface.mapCanvas())
        self.iface      = iface
        self.callback   = callback
        self.canvas     = iface.mapCanvas()
        return None

    def canvasReleaseEvent(self,e):
        """Raise the Callback to return point to sender"""
        point = self.toMapCoordinates(e.pos())
        self.callback(point)
        return None

