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
import os.path, codecs
from PyQt4.QtCore import *
from PyQt4.QtGui import QFileDialog
from qgis.core import *

class batcGeoHelper:
  def __init__(self,iface, parent):
      self.iface = iface
      self.parent = parent
      self.canvas = iface.mapCanvas()
      self.adreslayer = None
      self.adreslayerid = ''
      self.adresProvider = None
   
  #def prjPtToMapCrs(self, xy , fromCRS=4326 ):
      #point = QgsPoint( xy[0], xy[1] )
      #fromCrs = QgsCoordinateReferenceSystem(fromCRS)
      #toCrs = self.iface.mapCanvas().mapRenderer().destinationCrs()
      #xform = QgsCoordinateTransform( fromCrs, toCrs )
      #return   xform.transform( point )
    
  def _createAttributeTable(self, tableDict, allString=True):
      attributeTable = []
      for name, var in tableDict.items():
	typeVar = QVariant.String
	if not allString and var.lstrip("-").isdigit():
	  typeVar = QVariant.Int 
	elif not allString and var.lstrip("-").replace(".","",1).isdigit():
	  typeVar = QVariant.Double
	attributeTable.append(QgsField(name, typeVar))
      return attributeTable
    
  def save_adres_point(self, point, address, typeAddress='', attritableDict={}, layername="Geopunt_adressen" ):
    
    mapcrs = self.canvas.mapRenderer().destinationCrs()
    
    if not QgsMapLayerRegistry.instance().mapLayer(self.adreslayerid):
      attributes = self._createAttributeTable( attritableDict )
      attributes += [QgsField("crabAdres", QVariant.String), QgsField("crabtype", QVariant.String)]
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
    fet['crabAdres'] = address
    fet['crabtype'] = typeAddress
    for name, var in attritableDict.items():
      field = self.adresProvider.fieldNameMap()[name]
      fet.setAttribute(field,var)
    self.adresProvider.addFeatures([ fet ])
    
    # update layer's extent when new features have been added
    # because change of extent in provider is not propagated to the layer
    self.adreslayer.updateExtents()
    
    #  set id, add to map, refresh
    self.adreslayerid = self.adreslayer.id()
    QgsMapLayerRegistry.instance().addMapLayer(self.adreslayer)
    self.canvas.refresh()
    
    
  def saveMem2file(self, layername ):
      if self.adresProvider is None or not self.adresProvider.name() == u'memory':
	return
      
      save = self._saveToFile( self.parent )
      if save:
	fpath, flType = save                
	error = QgsVectorFileWriter.writeAsVectorFormat(self.adreslayer, fpath, "utf-8", None, flType )
	if error == QgsVectorFileWriter.NoError:
	  QgsMapLayerRegistry.instance().removeMapLayer(self.adreslayerid)
	  self.adreslayer = QgsVectorLayer( fpath, layername, "ogr")
	  self.adresProvider = self.adreslayer.dataProvider()
	  self.adreslayerid = self.adreslayer.id()
	  QgsMapLayerRegistry.instance().addMapLayer(self.adreslayer)
	  self.canvas.refresh()
	else: 
	  return
      else: 
	return
  
  def clear(self):
      self.adreslayer = None
      self.adreslayerid = ''
      self.adresProvider = None
  
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
	