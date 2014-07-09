Notities
-------
 
parse metadata
---------

docs: http://geonetwork-opensource.org/manuals/2.8.0/eng/developer/xml_services/metadata_xml_search_retrieve.html

```python
	import urllib2, sys
	import xml.etree.ElementTree as ET
	
	url = "https://metadata.geopunt.be/zoekdienst/srv/dut/q?fast=index&from=1&to=20&orgName=%22databank%20ondergrond%20vlaanderen%22&inspiretheme=Bodem&hitsperpage=20"
	
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
```

metadata keywords:
  
 **GDI-Vlaanderen-trefwoorden:** https://metadata.geopunt.be/zoekdienst/srv/dut/xml.search.keywords?pNewSearch=true&pTypeSearch=1&pKeyword=*&pThesauri=external.theme.GDI-Vlaanderen-trefwoorden
  
 **inspire-thema's:** https://metadata.geopunt.be/zoekdienst/srv/dut/xml.search.keywords?pNewSearch=true&pTypeSearch=1&pKeyword=*&pThesauri=external.theme.inspire-theme
 
 **orgnisaties:** https://metadata.geopunt.be/zoekdienst/srv/dut/main.search.suggest?field=orgName
 
 **bronnen:** https://metadata.geopunt.be/zoekdienst/srv/dut/xml.info?type=sources
 
 **autocomplete:** https://metadata.geopunt.be/zoekdienst/srv/dut/main.search.suggest?field=any&q=<...>
 
 
Loading WMS: 
-----------

```python
	urlWithParams =  "url=http://geo.agiv.be/inspire/wms/hydrografie&layers=Deelbekken&format=image/png&styles=default&crs=EPSG:31370"
	
	rlayer = QgsRasterLayer(urlWithParams, 'some layer name', 'wms')
	
	if rlayer.isValid():
		QgsMapLayerRegistry.instance().addMapLayer(rlayer)
```
  

Find layer names in WMS getcapabilties
----------

```python
	layerNames = [n.text for n in root.findall( ".//{http://www.opengis.net/wms}Layer/{http://www.opengis.net/wms}Name" )]
```
  
  
using the elevation service
--------------------------

```python
    import urllib2
    url = 'http://ws.agiv.be/elevation/dhmv1/search'
    data = json.dumps({"SrsIn":"4326","SrsOut":"4326","LineString":{"coordinates":[[4.287999804111748,51.2705874472921],[4.787877733799225,51.25340043028034],[4.837316210361721,51.098427963862875],[4.529699022861737,51.39071668493124],[4.952672655674216,51.380432223771166]],"type":"LineString"},"Samples":50})
    req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
    f = urllib2.urlopen(req)
    elvJson = json.load( f )
```
  
create a graph with mathplotlib
------------

```python
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
```
  
