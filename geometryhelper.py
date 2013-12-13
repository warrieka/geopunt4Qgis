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
	self.adreslayerid = ''
	self.poilayerid = ''
        
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
        if not QgsMapLayerRegistry.instance().mapLayer(self.adreslayerid) :
            # create layer with same CRS as map canvas
            self.adreslayer = QgsVectorLayer("Point", layername, "memory")
            self.adresProvider = self.adreslayer.dataProvider()
            self.adreslayer.setCrs(self.canvas.mapRenderer().destinationCrs())

            # add fields
            self.adresProvider.addAttributes([QgsField("adres", QVariant.String), 
					      QgsField("type", QVariant.String)])
            self.adreslayer.updateFields()

            # Labels on
            label = self.adreslayer.label()
            label.setLabelField(QgsLabel.Text, 0)
            self.adreslayer.enableLabels(True)

            # add layer if not already
            QgsMapLayerRegistry.instance().addMapLayer(self.adreslayer)

            # store layer id
            self.adreslayerid = self.adreslayer.id()

        # add a feature
        fields=self.adreslayer.pendingFields()
        fet = QgsFeature(fields)
        fet.setGeometry(QgsGeometry.fromPoint(point))

	#populate fields
        fet['adres'] = address
        fet['type'] = typeAddress

        self.adresProvider.addFeatures([ fet ])

        # update layer's extent when new features have been added
        # because change of extent in provider is not propagated to the layer
        self.adreslayer.updateExtents()
        self.canvas.refresh()
        
    def save_pois_points(self, points, layername="Geopunt_place" ):
	if not QgsMapLayerRegistry.instance().mapLayer(self.poilayerid) :
	  self.poilayer = QgsVectorLayer("Point", layername, "memory")
	  self.poiProvider = self.poilayer.dataProvider()
	  self.poilayer.setCrs(self.canvas.mapRenderer().destinationCrs())
	  
	  # add fields
	  self.poiProvider.addAttributes([ 
	    QgsField("id", QVariant.Int),
	    QgsField("category", QVariant.String),
	    QgsField("name", QVariant.String),
	    QgsField("adres", QVariant.String)])
	  self.poilayer.updateFields()           
	  
	  label = self.poilayer.label()        
	  label.setLabelField(QgsLabel.Text, 2) #2 = name
	  self.poilayer.enableLabels(True)    # Labels on

	  # add layer if not already
	  QgsMapLayerRegistry.instance().addMapLayer(self.poilayer)

	  # store layer id
	  self.poilayerid = self.poilayer.id()
	  
	fields=self.poilayer.pendingFields()
	for point in points:
	  pt = self.prjPtToMapCrs( point['location']['points'][0]['Point']['coordinates'], 31370)
	  
	  poiId = point["id"]
	  category =  point["categories"][0]['value']
	  name = point["labels"][0]["value"]
	  adres = point['location']['address']["value"].replace("<br />",", ").replace("<br/>",", ")
	  
	  # add a feature
	  fet = QgsFeature(fields)
	  fet.setGeometry(QgsGeometry.fromPoint(pt))
	  
	  fet['id'] = int( poiId )
	  fet['category'] = category
	  fet['name'] = name
	  fet['adres'] = adres
	  
	  self.poiProvider.addFeatures([ fet ])
	  
	self.poilayer.updateExtents()
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