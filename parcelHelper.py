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
from PyQt4.QtGui import QFileDialog, QColor
from qgis.gui import QgsVertexMarker
import os

class parcelHelper:
    def __init__(self, iface, parent= None, startFolder="" ):
      self.iface = iface
      self.parent = parent
      self.canvas = iface.mapCanvas()
      self.parcellayer = None
      self.parcellayerid = ''
      self.parcelProvider = None
      self.startFolder = startFolder
      
      
    def save_parcel_polygon(self, polygon, parcelInfo, layername="perceel", saveToFile=False, sender=None, startFolder=None ):
        attributes =[ QgsField("macht", QVariant.Int),
              QgsField("bisnummer", QVariant.Int) ,
              QgsField("exponent", QVariant.String),
              QgsField("adres", QVariant.String),
              QgsField("capakey", QVariant.String),         
              QgsField("grondnr", QVariant.Int),
              QgsField("type", QVariant.String),
              QgsField("perceelnr", QVariant.String) ]
  
        if not QgsMapLayerRegistry.instance().mapLayer(self.parcellayerid):
            self.parcellayer = QgsVectorLayer("MultiPolygon", layername, "memory")
            self.parcelProvider = self.parcellayer.dataProvider()
            self.parcelProvider.addAttributes(attributes)
            self.parcellayer.updateFields()
        
        # add a feature
        fields= self.parcellayer.pendingFields()
        fet = QgsFeature(fields)

        #set geometry and project from mapCRS
        fet.setGeometry(polygon)

        #populate fields
        fet['macht'] = parcelInfo['macht']
        fet['bisnummer'] = parcelInfo['bisnummer']
        fet['exponent'] = parcelInfo['exponent']
        fet['adres'] = "; ".join( parcelInfo['adres'] )
        fet['capakey'] = parcelInfo['capakey']
        fet['grondnr'] = parcelInfo['grondnummer']
        fet['type'] = parcelInfo['type']
        fet['perceelnr'] = parcelInfo['perceelnummer']   
        
        self.parcelProvider.addFeatures([ fet ])
        ""
        # update layer's extent when new features have been added
        # because change of extent in provider is not propagated to the layer
        self.parcellayer.updateExtents()

        # save memoryLAYER to file and replace all references    
        if saveToFile and not QgsMapLayerRegistry.instance().mapLayer(self.parcellayerid): 
          save = self._saveToFile( sender, startFolder )
          if save:
            fpath, flType = save                
            error = QgsVectorFileWriter.writeAsVectorFormat(self.parcellayer, fpath, "utf-8", None, flType)
            if error == QgsVectorFileWriter.NoError:
              self.parcellayer = QgsVectorLayer( fpath, layername, "ogr")
              self.parcelProvider = self.parcellayer.dataProvider()
            else: 
              del self.parcellayer, self.parcelProvider 
              return
          else: 
            del self.parcellayer, self.parcelProvider 
            return

        #  add to map
        QgsMapLayerRegistry.instance().addMapLayer(self.parcellayer)
        
        # store layer id and refresh      
        self.parcellayerid = self.parcellayer.id()
        self.canvas.refresh()
        
    def _saveToFile( self, sender, startFolder=None ):
        filter = "ESRI Shape Files (*.shp);;SpatiaLite (*.sqlite);;Any File (*.*)" #show only formats with update capabilty
        Fdlg = QFileDialog()
        Fdlg.setFileMode(QFileDialog.AnyFile)
        fName = QFileDialog.getSaveFileName(sender, "open file", filter=filter, directory=startFolder)
        if fName:
          ext = os.path.splitext( fName )[1]
          if "SHP" in ext.upper():
            flType = "ESRI Shapefile"
          elif "SQLITE" in ext.upper():
            flType = "SQLite" 
          elif "GEOJSON" in ext.upper():  #no update possible -> hidden
            flType = "GeoJSON"
          elif "GML" in ext.upper():
            flType = "GML"
          elif 'TAB' in ext.upper():
            flType = 'MapInfo File'
          elif 'KML' in ext.upper():
            flType = 'KML'
          else:
            fName = fName + ".shp"
            flType = "ESRI Shapefile"
          return (fName , flType )
        else:
            return None
