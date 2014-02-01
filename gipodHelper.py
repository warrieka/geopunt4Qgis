# -*- coding: utf-8 -*-
"""
/***************************************************************************
gipodeoHelper
				A QGIS plugin
"Tool om geopunt in QGIS te gebruiken"
			    -------------------
	begin                : 2013-12-08
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
import os.path, datetime
from PyQt4.QtCore import *
from qgis.core import *

class gipodWriter:
    def __init__(self, iface, layername, CRS=31370):
	self.iface = iface
	self.canvas = iface.mapCanvas()
	self.layername = layername
	self.CRS = CRS
	
    def __enter__(self):
        attributes =[ QgsField("gipodId", QVariant.Int),
		      QgsField("owner", QVariant.String) ,
		      QgsField("description", QVariant.String),
		      QgsField("startDateTime", QVariant.String, "DateTime"),
		      QgsField("endDateTime", QVariant.String, "DateTime"),			QgsField("importantHindrance", QVariant.Int),
		      #QgsField("link", QVariant.String),
		    ]
	self.gipodlayer = QgsVectorLayer("Point", self.layername, "memory")
	self.gipodProvider = self.gipodlayer.dataProvider()
	self.gipodProvider.addAttributes(attributes)
	self.gipodlayer.updateFields()
	self.fields= self.gipodlayer.pendingFields()
        return self
        
    def saveGipodPoint(self, fname, ftype="ESRI Shapefile" ):
	options = []
	if self.ftype == "CSV": 
	    options += ["GEOMETRY=AS_XY","SEPARATOR=SEMICOLON"]
	srs = QgsCoordinateReferenceSystem(self.CRS)
	
    def writePoint(self, xy, gipodId, owner, description, startDateTime, endDateTime, importantHindrance ):
	fet = QgsFeature(self.fields)
	fet['gipodId'] = gipodId
	fet['owner'] = owner
	fet['description'] = description
	fet['startDateTime'] = startDateTime
	fet['endDateTime'] = endDateTime
	fet['importantHindrance'] = importantHindrance
	
	x,y = xy
	fromCrs = QgsCoordinateReferenceSystem(self.CRS)
	xform =   QgsCoordinateTransform( fromCrs, self.gipodlayer.crs() )
	prjPt =   xform.transform( QgsPoint( x,y ))
	fet.setGeometry(QgsGeometry.fromPoint(prjPt))
	
	self.gipodProvider.addFeatures([ fet ])
	
    def __exit__(self, type, value, traceback):
      	# add layer to map
	QgsMapLayerRegistry.instance().addMapLayer(self.gipodlayer)
	
	# refresh and update extends
	self.gipodlayer.updateExtents()
        self.canvas.refresh()