Notities
-------
 
parse CSW
---------

	import urllib2 , sys
	import xml.etree.ElementTree as ET
	
	url = "https://metadata.geopunt.be/zoekdienst/srv/dut/q?fast=index&from=1&to=100&any=vlaams"
	
	response = urllib2.urlopen(url, timeout=50)
	tree  = ET.ElementTree(file=response )
	root = tree.getroot()
	recs = root.findall("metadata")
	
	for rec in recs:
	ll =  "|".join( [ n.text for n in rec.findall("link") ] ) 
	title = rec.find("title")
	l=  [n for n in ll.split('|') if ("request=GetCapabilities" in n) & ("service=wms" in n)]
	for n in l: 
	print title.text +" "+ n 

 
Loading WMS: 
-----------

	urlWithParams =  "url=http://geo.agiv.be/inspire/wms/hydrografie&layers=Deelbekken&format=image/png&styles=default&crs=EPSG:31370"
	
	rlayer = QgsRasterLayer(urlWithParams, 'some layer name', 'wms')
	
	if rlayer.isValid():
	QgsMapLayerRegistry.instance().addMapLayer(rlayer)


Find layer names in getcapabilties
----------

	layerNames = [n.text for n in root.findall( ".//{http://www.opengis.net/wms}Layer/{http://www.opengis.net/wms}CRS" )]
  
  
create a graph with mathplotlib
------------

  from PyQt4 import QtGui
  import numpy as np

  from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
  from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
  import matplotlib.pyplot as plt

  import random

  class Window(QtGui.QDialog):
      def __init__(self, parent=None):
	  super(Window, self).__init__(parent)

	  # a figure instance to plot on
	  self.figure = plt.figure()
	  plt.ylabel("hoogte (m)")
	  plt.xlabel("afstand")

	  # this is the Canvas Widget that displays the `figure`
	  # it takes the `figure` instance as a parameter to __init__
	  self.canvas = FigureCanvas(self.figure)

	  # this is the Navigation widget
	  # it takes the Canvas widget and a parent
	  self.toolbar = NavigationToolbar(self.canvas, self)

	  # Just some button connected to `plot` method
	  self.button = QtGui.QPushButton('Plot')
	  self.button.clicked.connect(self.plot)

	  # set the layout
	  layout = QtGui.QVBoxLayout()
	  layout.addWidget(self.toolbar)
	  layout.addWidget(self.canvas)
	  layout.addWidget(self.button)
	  self.setLayout(layout)

      def plot(self):
	  ''' plot some random stuff '''
	  # random data
	  data = [random.random() for i in range(10)]

	  # create an axis
	  ax = self.figure.add_subplot(111)

	  # discards the old graph
	  ax.hold(False)

	  # plot data
	  ax.plot(data, '*-')

	  # refresh canvas
	  self.canvas.draw()

  if __name__ == '__main__':
      app = QtGui.QApplication(sys.argv)

      main = Window()
      main.show()

      sys.exit(app.exec_())
    
