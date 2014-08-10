# -*- coding: utf-8 -*-
"""
/***************************************************************************
poiHelper
                                A QGIS plugin
"Tool om geopunt in QGIS te gebruiken"
                            -------------------
        begin                : 2014-08-06
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
import os

class poiHelper:
    def __init__(self , iface ):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.poilayerid = ''
        self.minPoilayerid =  ''

    def save_minPois_points(self, points, layername="Geopunt_poi", saveToFile=None, sender=None, startFolder=None ):       
        attributes = [ QgsField("id", QVariant.Int),
            QgsField("type", QVariant.String),
            QgsField("name", QVariant.String),
            QgsField("link", QVariant.String),
            QgsField("count", QVariant.Int) ]
    
        if not QgsMapLayerRegistry.instance().mapLayer(self.minPoilayerid) :
            self.minpoilayer = QgsVectorLayer("Point", layername, "memory")
            self.minpoiProvider = self.minpoilayer.dataProvider()
            self.minpoiProvider.addAttributes(attributes)
            self.minpoilayer.updateFields()    
        
        fields=self.minpoilayer.pendingFields()
        
        for point in points["pois"]:
            pt = QgsPoint( point['location']['points'][0]['Point']['coordinates'][0], 
                           point['location']['points'][0]['Point']['coordinates'][1]  )
            poiId = point["id"]
            if "categories" in point and len(point["categories"]) > 0: poiType = point["categories"][0]['value']
            else: poiType = ''
            name = point["labels"][0]["value"]
            if "links" in point: link = point["links"][0]['href']
            else: link = ""

            # add a feature
            fet = QgsFeature(fields)

            #set geometry
            fromCrs = QgsCoordinateReferenceSystem(4326)
            xform = QgsCoordinateTransform( fromCrs, self.minpoilayer.crs() )
            prjPt = xform.transform( pt )
            fet.setGeometry(QgsGeometry.fromPoint(prjPt))
      
            fet['id'] = int( poiId )
            fet['type'] = poiType
            fet['name'] = name
            fet['link'] = link

            self.minpoiProvider.addFeatures([ fet ])
            
        for point in points["clusters"]:
            pt = QgsPoint( point['point']['Point']['coordinates'][0], 
                           point['point']['Point']['coordinates'][1]  )
            poiType = point['point']['type']
            count = point['count']

            # add a feature
            fet = QgsFeature(fields)

            #set geometry
            fromCrs = QgsCoordinateReferenceSystem(4326)
            xform = QgsCoordinateTransform( fromCrs, self.minpoilayer.crs() )
            prjPt = xform.transform( pt )
            fet.setGeometry(QgsGeometry.fromPoint(prjPt))

            fet['type'] = poiType
            fet['count'] = count

            self.minpoiProvider.addFeatures([ fet ])
        
        if saveToFile and not QgsMapLayerRegistry.instance().mapLayer(self.minPoilayerid):
            save = self._saveToFile( sender, startFolder )
            if save:
              fpath, flType = save
              error = QgsVectorFileWriter.writeAsVectorFormat(self.minpoilayer, fpath, "utf-8", None, flType, )
              if error == QgsVectorFileWriter.NoError:
                  self.minpoilayer = QgsVectorLayer( fpath , layername, "ogr")
                  self.minpoiProvider = self.minpoilayer.dataProvider()
              else: 
                  del self.minpoilayer, self.minpoiProvider 
                  return 
            else:
              del self.minpoilayer, self.minpoiProvider 
              return 

        # add layer if not already
        QgsMapLayerRegistry.instance().addMapLayer(self.minpoilayer)

        # store layer id and refresh
        self.minPoilayerid = self.minpoilayer.id()
        self.minpoilayer.updateExtents()
        self.canvas.refresh()
    
    def save_pois_points(self, points, layername="Geopunt_poi", saveToFile=None, sender=None, startFolder=None ):       
        attributes = [ QgsField("id", QVariant.Int),
            QgsField("thema", QVariant.String),
            QgsField("category", QVariant.String),
            QgsField("type", QVariant.String),
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
            pt = QgsPoint( point['location']['points'][0]['Point']['coordinates'][0], 
                           point['location']['points'][0]['Point']['coordinates'][1]  )
            poiId = point["id"]
            if "categories" in point and len(point["categories"]) > 0: theme =     point["categories"][0]['value']
            else: theme = ''
            if "categories" in  point and len(point["categories"]) > 1: category = point["categories"][1]['value']
            else: category = ''
            if "categories" in  point and len(point["categories"]) > 2: poiType =  point["categories"][2]['value']
            else: poiType = ''
            name = point["labels"][0]["value"]
            adres = point['location']['address']["value"].replace("<br />",", ").replace("<br/>",", ")
            if "links" in point: link = point["links"][0]['href']
            else: link = ""
            tijd =  point["updated"] 
            if "authors" in point: owner = point["authors"][0]["value"]
            else: owner= ""

            # add a feature
            fet = QgsFeature(fields)

            #set geometry
            fromCrs = QgsCoordinateReferenceSystem(4326)
            xform = QgsCoordinateTransform( fromCrs, self.poilayer.crs() )
            prjPt = xform.transform( pt )
            fet.setGeometry(QgsGeometry.fromPoint(prjPt))
      
            fet['id'] = int( poiId )
            fet['thema'] = theme
            fet['category'] = category
            fet['type'] = poiType
            fet['name'] = name
            fet['adres'] = adres
            fet['link'] = link
            fet['lastupdate'] = tijd
            fet['owner'] = owner
      
            self.poiProvider.addFeatures([ fet ])
            self.poilayer.updateExtents()
    
        if saveToFile and not QgsMapLayerRegistry.instance().mapLayer(self.poilayerid):
            save = self._saveToFile( sender, startFolder )
            if save:
              fpath, flType = save
              error = QgsVectorFileWriter.writeAsVectorFormat(self.poilayer, fpath, "utf-8", None, flType, )
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
        palyr = QgsPalLayerSettings() 
        palyr.readFromLayer( self.poilayer ) 
        palyr.enabled = True 
        palyr.fieldName = 'name' 
        palyr.placement= QgsPalLayerSettings.Free 
        palyr.dist = 1
        palyr.bufferSize = 1
        palyr.bufferDraw = 1
        palyr.setDataDefinedProperty(QgsPalLayerSettings.Size,True,True,'8','') 
        palyr.writeToLayer( self.poilayer ) 
        
        self.poilayer.setEditType( 6, QgsVectorLayer.WebView) 
        
        # add layer if not already
        QgsMapLayerRegistry.instance().addMapLayer(self.poilayer)

        # store layer id and refresh
        self.poilayerid = self.poilayer.id()
        self.canvas.refresh()
    
    def _saveToFile( self, sender, startFolder=None ):
        'save to file'
        #"Shape Files (*.shp);;Geojson File (*.geojson);;GML ( *.gml);;Comma separated value File (excel) (*.csv);;MapInfo TAB (*.TAB);;Any File (*.*)"
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
      