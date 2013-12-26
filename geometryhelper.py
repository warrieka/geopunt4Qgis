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
from PyQt4.QtGui import QFileDialog
import os

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


    def save_adres_point(self, point, address, typeAddress='', layername="Geopunt_adres", saveToFile=None, sender=None):
        attributes = [QgsField("adres", QVariant.String), QgsField("type", QVariant.String)]
        mapcrs = self.canvas.mapRenderer().destinationCrs()
        
        if not QgsMapLayerRegistry.instance().mapLayer(self.adreslayerid):
	    self.adreslayer = QgsVectorLayer("Point", layername, "memory")
	    self.adresProvider = self.adreslayer.dataProvider()
	    self.adresProvider.addAttributes(attributes)
	    self.adreslayer.updateFields()

        # add a feature
        fields= self.adreslayer.pendingFields()
        fet = QgsFeature(fields)

        #set geometry and project from mapCRS
        xform = QgsCoordinateTransform( mapcrs, self.adreslayer.crs() )
        prjPoint = xform.transform( point )
        fet.setGeometry(QgsGeometry.fromPoint(prjPoint))

	    #populate fields
        fet['adres'] = address
        fet['type'] = typeAddress
        self.adresProvider.addFeatures([ fet ])
        
        # update layer's extent when new features have been added
	# because change of extent in provider is not propagated to the layer
	self.adreslayer.updateExtents()
        
        if saveToFile and not QgsMapLayerRegistry.instance().mapLayer(self.adreslayerid): 
	  save = self._saveToFile( sender )
	  if save:
	    fpath, flType = save                
	    error = QgsVectorFileWriter.writeAsVectorFormat(self.adreslayer, fpath, "utf-8", None, flType)
	    if error == QgsVectorFileWriter.NoError:
	      self.adreslayer = QgsVectorLayer( fpath, layername, "ogr")
	      self.adresProvider = self.adreslayer.dataProvider()
	    else: 
	      del self.adreslayer, self.adresProvider 
	      return
	  else: 
	    del self.adreslayer, self.adresProvider 
	    return
	  
	#  set id, add to map, Labels on, refresh
	self.adreslayerid = self.adreslayer.id()
	QgsMapLayerRegistry.instance().addMapLayer(self.adreslayer)
	label = self.adreslayer.label()
	labelField = self.adresProvider.fieldNameMap()["adres"]
	label.setLabelField(QgsLabel.Text, labelField)
	self.adreslayer.enableLabels(True)
	self.canvas.refresh()
        
    def save_pois_points(self, points, layername="Geopunt_poi", saveToFile=None, sender=None ):
        mapcrs = self.canvas.mapRenderer().destinationCrs()
        attributes = [  QgsField("id", QVariant.Int),
			QgsField("category", QVariant.String),
			QgsField("name", QVariant.String),
			QgsField("adres", QVariant.String),
			QgsField("link", QVariant.String),
			QgsField("lastupdate", QVariant.String, "DateTime"),
			QgsField("owner", QVariant.String)  ]
	
        if not QgsMapLayerRegistry.instance().mapLayer(self.poilayerid) :
		self.poilayer = QgsVectorLayer("Point", layername, "memory")
		self.poiProvider = self.poilayer.dataProvider()
		self.poiProvider.addAttributes(attributes)
		self.poilayer.updateFields()    
	  
        fields=self.poilayer.pendingFields()
        
        for point in points:
            #get values
            pt = QgsPoint( point['location']['points'][0]['Point']['coordinates'][0], 
                           point['location']['points'][0]['Point']['coordinates'][1] )
            poiId = point["id"]
            if "categories" in  point: category =  point["categories"][0]['value']
            else: category = ''
            name = point["labels"][0]["value"]
            adres = point['location']['address']["value"].replace("<br />",", ").replace("<br/>",", ")
            if "links" in point: link = point["links"][0]['href']
            else: link = ""
            tijd =  point["updated"] 
            #tijd = QDateTime().fromString( point["updated"] , "yyyy-MM-ddTHH:mm:ss")
            if "authors" in point: owner = point["authors"][0]["value"]
            else: owner= ""

            # add a feature
            fet = QgsFeature(fields)

            #set geometry
            fromCrs = QgsCoordinateReferenceSystem(31370)
            xform = QgsCoordinateTransform( fromCrs, self.poilayer.crs() )
            prjPt = xform.transform( pt )
            fet.setGeometry(QgsGeometry.fromPoint(prjPt))
	  
            fet['id'] = int( poiId )
            fet['category'] = category
            fet['name'] = name
            fet['adres'] = adres
            fet['link'] = link
            fet['lastupdate'] = tijd
            fet['owner'] = owner
	  
            self.poiProvider.addFeatures([ fet ])
	    self.poilayer.updateExtents()
	
	if saveToFile and not QgsMapLayerRegistry.instance().mapLayer(self.poilayerid):
	      save = self._saveToFile( sender )
	      if save:
		fpath, flType = save
		error = QgsVectorFileWriter.writeAsVectorFormat(self.poilayer, fpath, "utf-8", None, flType)
		if error == QgsVectorFileWriter.NoError:
		    self.poilayer = QgsVectorLayer( fpath , layername, "ogr")
		    self.poiProvider = self.poilayer.dataProvider()
		else: 
		    del self.poilayer, self.poiProvider 
		    return 
	      else: 
		del self.poilayer, self.poiProvider 
		return 

	# add Labels
	label = self.poilayer.label()   
	labelField = self.poiProvider.fieldNameMap()["name"]
	label.setLabelField(QgsLabel.Text, labelField) 
	self.poilayer.enableLabels(True) 
	
	# add layer if not already
	QgsMapLayerRegistry.instance().addMapLayer(self.poilayer)

	# store layer id and refresh
	self.poilayerid = self.poilayer.id()
        self.canvas.refresh()
	
    def _saveToFile( self, sender ):
        filter = "Shape Files (*.shp);;Geojson File (*.geojson);;GML ( *.gml);;Any File (*.*)"
        Fdlg = QFileDialog()
        Fdlg.setFileMode(QFileDialog.AnyFile)
        fName = Fdlg.getSaveFileName( sender, "open file" , None, filter)
        if fName:
	    ext = os.path.splitext( fName )[1]
	    if "SHP" in ext.upper():
		flType = "ESRI Shapefile"
	    elif "GEOJSON" in ext.upper():
		flType = "GeoJSON"
	    elif "GML" in ext.upper():
		flType = "GML"
	    else:
		fName = fName + ".shp"
		flType = "ESRI Shapefile"
	    return (fName , flType )
        else:
            return None

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