# -*- coding: utf-8 -*-
"""
/***************************************************************************
 geometryHelper
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
from PyQt4.QtCore import *
from qgis.core import *

class geometryHelper:
    def __init__(self , iface ):
	self.iface = iface
	self.canvas = iface.mapCanvas()
	self.layerid = ''
        
    def prjPtToMapCrs( self, xy , fromCRS=4326 ):
	point = QgsPoint( xy[0], xy[1] )
	fromCrs = QgsCoordinateReferenceSystem(fromCRS)
	toCrs = self.iface.mapCanvas().mapRenderer().destinationCrs()
	xform = QgsCoordinateTransform( fromCrs, toCrs )
	return   xform.transform( point )
    
    def prjPtFromMapCrs( self, xy , toCRS=31370 ):
	point = QgsPoint( xy[0], xy[1] )
	toCrs = QgsCoordinateReferenceSystem(toCRS)
	fromCrs = self.iface.mapCanvas().mapRenderer().destinationCrs()
	xform = QgsCoordinateTransform( fromCrs, toCrs )
	return   xform.transform( point )
    
    def zoomtoRec(self, xyMin, xyMax, crs ):
	maxpoint = QgsPoint(xyMax[0], xyMax[1])
        minpoint = QgsPoint(xyMin[0], xyMin[1])
        
        pmaxpoint = self.prjPtToMapCrs(maxpoint, crs)
        pminpoint = self.prjPtToMapCrs(minpoint, crs)
      
        # Create a rectangle to cover the new extent
        rect = QgsRectangle( pmaxpoint, pminpoint )
	
        # Set the extent to our new rectangle
        self.iface.mapCanvas().setExtent(rect)
        # Refresh the map
        self.iface.mapCanvas().refresh()

#some code shamelessly copied from qgis-geocoding by Alessandro Pasotti: 
# -> https://github.com/elpaso/qgis-geocoding/blob/master/GeoCoding.py
    def save_adres_point(self, point, address, typeAddress='', layername="Geopunt_adres" ):
        if not QgsMapLayerRegistry.instance().mapLayer(self.layerid) :
            # create layer with same CRS as map canvas
            self.layer = QgsVectorLayer("Point", layername, "memory")
            self.provider = self.layer.dataProvider()
            self.layer.setCrs(self.canvas.mapRenderer().destinationCrs())

            # add fields
            self.provider.addAttributes([QgsField("adres", QVariant.String, len=128), 
					 QgsField("type", QVariant.String, len=64)])

            self.layer.updateFields()

            # Labels on
            label = self.layer.label()
            label.setLabelField(QgsLabel.Text, 0)
            self.layer.enableLabels(True)

            # add layer if not already
            QgsMapLayerRegistry.instance().addMapLayer(self.layer)

            # store layer id
            self.layerid = self.layer.id()


        # add a feature
        fields=self.layer.pendingFields()
        fet = QgsFeature(fields)
        fet.setGeometry(QgsGeometry.fromPoint(point))

	#populate fields
        fet['adres'] = address
        fet['type'] = typeAddress

        self.provider.addFeatures([ fet ])

        # update layer's extent when new features have been added
        # because change of extent in provider is not propagated to the layer
        self.layer.updateExtents()

        self.canvas.refresh()
      
    def getBoundsOfPointArray( self, pointArray):
	minX = 1.7976931348623157e+308
	maxX = -1.7976931348623157e+308
	minY = 1.7976931348623157e+308
	maxY = -1.7976931348623157e+308
	
	for xy in pointArray:
	  x, y = list(xy)[:2]
	  if x > maxX: maxX = x
	  if x < minX: minX = x
	  if y > maxY: maxY = y
	  if y < minY: minY = y
	   
	Xdelta = (maxX - minX) /100
	Ydelta = (maxY - minY) /100
	    
	return [ minX - Xdelta, minY - Ydelta, maxX + Xdelta, maxY + Ydelta]
    
    def getBoundsOfPoint( self , x, y):
      if x >= 360:
	delta = 300 #x bigger then 360 -> meters
      else:
	delta = 0.0025 #x smaller then 360 -> degrees
	
      xmax = x + delta
      xmin = x - delta
      ymax = y + delta
      ymin = y - delta
      
      return [xmin, ymin, xmax,ymax]