# -*- coding: utf-8 -*-
"""
/***************************************************************************
batcGeoHelper
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
import os.path
from .geometry import geometryHelper
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtWidgets import QFileDialog
from qgis.core import QgsField, QgsVectorLayer, QgsProject, QgsFeature, QgsCoordinateTransform, QgsGeometry, QgsVectorFileWriter

class batcGeoHelper(object):
  def __init__(self,iface, parent, startFolder="" ):
      self.iface = iface
      self.parent = parent
      self.canvas = iface.mapCanvas()
      self.adreslayer = None
      self.adreslayerid = ''
      self.adresProvider = None
      self.startFolder = startFolder
    
  def _createAttributeTable(self, tableDict, allString=True):
      attributeTable = []
      for name, var in list(tableDict.items()):
        typeVar = QVariant.String
        if not allString and var.lstrip("-").isdigit():
             typeVar = QVariant.Int 
        elif not allString and var.lstrip("-").replace(".","",1).isdigit():
             typeVar = QVariant.Double
       
        attributeTable.append(QgsField(name, typeVar))
      return attributeTable
    
  def save_adres_point(self, point, address, typeAddress='', attritableDict={}, layername="Geopunt_adressen" ):
    
    mapcrs = geometryHelper.getGetMapCrs( self.iface )
    
    if not QgsProject.instance().mapLayer(self.adreslayerid):
        attributes = self._createAttributeTable( attritableDict )
        attributes += [QgsField("fullAdres", QVariant.String), QgsField("quality", QVariant.String)]
        self.adreslayer = QgsVectorLayer("Point", layername, "memory")
        self.adresProvider = self.adreslayer.dataProvider()
        self.adresProvider.addAttributes(attributes)
        self.adreslayer.updateFields()

    # add a feature
    fields= self.adreslayer.fields()
    fet = QgsFeature(fields)

    #set geometry and project from mapCRS
    xform = QgsCoordinateTransform( mapcrs, self.adreslayer.crs(), QgsProject.instance() )
    prjPoint = xform.transform( point )
    fet.setGeometry(QgsGeometry.fromPointXY(prjPoint))

    #populate fields
    fet['fullAdres'] = address
    fet['quality'] = typeAddress
    for name, var in list(attritableDict.items()):
       field = self.adresProvider.fieldNameMap()[name]
       fet.setAttribute(field,var)
    self.adresProvider.addFeatures([ fet ])
    
    # update layer's extent when new features have been added
    # because change of extent in provider is not propagated to the layer
    self.adreslayer.updateExtents()
    
    #  set id, add to map, refresh
    self.adreslayerid = self.adreslayer.id()
    QgsProject.instance().addMapLayer(self.adreslayer)
    self.canvas.refresh()
    
    
  def saveMem2file(self, layername ):
      if self.adresProvider is None or not self.adresProvider.name() == 'memory': return
      
      save = self._saveToFile( self.parent, os.path.join( self.startFolder, layername ))
      if save:
        fpath, flType = save    
        error, msg = QgsVectorFileWriter.writeAsVectorFormat(self.adreslayer, fileName=fpath, fileEncoding="utf-8", driverName=flType)
        if error == QgsVectorFileWriter.NoError:
          QgsProject.instance().removeMapLayer(self.adreslayerid)
          self.adreslayer = QgsVectorLayer( fpath, layername, "ogr")
          self.adresProvider = self.adreslayer.dataProvider()
          self.adreslayerid = self.adreslayer.id()
          QgsProject.instance().addMapLayer(self.adreslayer)
          self.canvas.refresh()
        else: 
            raise Exception(msg)
      else: return
  
  def clear(self):
      self.adreslayer = None
      self.adreslayerid = ''
      self.adresProvider = None
  
  def _saveToFile( self, sender , startFolder=None):
     'save to file'
     filter = "OGC GeoPackage (*.gpkg);;ESRI Shape Files (*.shp);;SpatiaLite (*.sqlite);;Geojson File (*.geojson);;GML ( *.gml);;Comma separated value File (excel) (*.csv);;MapInfo TAB (*.TAB);;Any File (*.*)" 
     fName, __ = QFileDialog.getSaveFileName( sender, "open file" , filter=filter, directory=startFolder)

     if fName: ext = os.path.splitext( fName )[1]
     else: return 

     if "GPKG" in ext.upper():
         flType = "GPKG"
     elif "SHP" in ext.upper():
         flType = "ESRI Shapefile"
     elif "SQLITE" in ext.upper():
         flType = "SQLite" 
     elif "GEOJSON" in ext.upper():
         flType = "GeoJSON"
     elif "GML" in ext.upper():
         flType = "GML"
     elif "CSV" in ext.upper():
         ftType = "CSV"
     elif 'TAB' in ext.upper():
         flType = 'MapInfo File'
     elif 'CSV' in ext.upper():
         flType = 'CSV'
     else:
         fName = fName + ".shp"
         flType = "ESRI Shapefile"

     return (fName , flType )
