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
from qgis.PyQt.QtCore import QVariant
from qgis.core import QgsField, QgsProject, QgsVectorLayer, QgsPoint, QgsFeature, QgsCoordinateReferenceSystem, QgsCoordinateTransform, QgsGeometry, QgsVectorFileWriter, QgsPalLayerSettings
from qgis.PyQt.QtWidgets import QFileDialog
from qgis.PyQt.QtGui import QColor
import os

class poiHelper(object):
    def __init__(self , iface ):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.poilayerid = ''
        self.minPoilayerid =  ''

    def save_minPois_points(self, points, layername="Geopunt_poi", saveToFile=None, sender=None, startFolder=None ):       
        attributes = [ QgsField("id", QVariant.Int),
            QgsField("type", QVariant.String),
            QgsField("name", QVariant.String),
            QgsField("straat", QVariant.String),
            QgsField("huisnr", QVariant.String),
            QgsField("busnr", QVariant.String),
            QgsField("postcode", QVariant.String),
            QgsField("gemeente", QVariant.String),
            QgsField("link", QVariant.String),
            QgsField("count", QVariant.Int) ]
    
        if not QgsProject.instance().mapLayer(self.minPoilayerid) :
            self.minpoilayer = QgsVectorLayer("Point", layername, "memory")
            self.minpoiProvider = self.minpoilayer.dataProvider()
            self.minpoiProvider.addAttributes(attributes)
            self.minpoilayer.updateFields()    
        
        fields=self.minpoilayer.fields()
        
        for point in points["pois"]:
            pt = QgsPoint( point['location']['points'][0]['Point']['coordinates'][0], 
                           point['location']['points'][0]['Point']['coordinates'][1]  )
            poiId = point["id"]
            
            if "address" in point['location']: 
              if "street" in point['location']["address"]: 
                straat = point['location']["address"]["street"]
              else:  straat = ''
              if "streetnumber" in point['location']["address"]: 
                huisnr = point['location']["address"]["streetnumber"]
              else:  huisnr = ''
              if "boxnumber" in point['location']["address"]: 
                busnr = point['location']["address"]["boxnumber"]
              else:  busnr = ''
              postcode = point['location']["address"]["postalcode"]
              gemeente = point['location']["address"]["municipality"]
            else: 
              straat = ""
              huisnr = ""
              busnr = ""
              postcode = ""
              gemeente = ""
              
            if "categories" in point and len(point["categories"]) > 0: 
              poiType = point["categories"][0]["value"]
            else: poiType = ''
            if "labels" in point and len(point["labels"]) > 0:
              name = point["labels"][0]["value"]
            else: name = ''
            if "links" in point: 
              link = point["links"][0]["href"]
            else: link = ''

            # add a feature
            fet = QgsFeature(fields)

            #set geometry
            fromCrs = QgsCoordinateReferenceSystem(4326)
            xform = QgsCoordinateTransform( fromCrs, self.minpoilayer.crs(), QgsProject.instance() )
            prjPt = xform.transform( pt )
            fet.setGeometry(QgsGeometry.fromPoint(prjPt))
      
            fet['id'] = int( poiId )
            fet['straat'] = straat
            fet['huisnr'] = huisnr
            fet['busnr'] = busnr
            fet['postcode'] = postcode
            fet['gemeente'] = gemeente
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
            xform = QgsCoordinateTransform( fromCrs, self.minpoilayer.crs(), QgsProject.instance() )
            prjPt = xform.transform( pt )
            fet.setGeometry(QgsGeometry.fromPoint(prjPt))

            fet['type'] = poiType
            fet['count'] = count

            self.minpoiProvider.addFeatures([ fet ])
        
        if saveToFile and not QgsProject.instance().mapLayer(self.minPoilayerid):
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
        QgsProject.instance().addMapLayer(self.minpoilayer)

        # store layer id and refresh
        self.minPoilayerid = self.minpoilayer.id()
        self.minpoilayer.updateExtents()
        self.canvas.refresh()
    
    def save_pois_points(self, points, layername="Geopunt_poi", saveToFile=None, sender=None, startFolder=None ):       
        attributes = [ QgsField("id", QVariant.Int),
            QgsField("thema", QVariant.String), 
            QgsField("categorie", QVariant.String),
            QgsField("type", QVariant.String),

            QgsField("naam", QVariant.String),
            QgsField("telefoon", QVariant.String),  
            QgsField("email", QVariant.String) ,
            #address
            QgsField("straat", QVariant.String),
            QgsField("huisnr", QVariant.String),
            QgsField("busnr", QVariant.String),
            QgsField("postcode", QVariant.String),
            QgsField("gemeente", QVariant.String),
            
            QgsField("link", QVariant.String),
            QgsField("lastupdate", QVariant.String),
            QgsField("owner", QVariant.String) ]
    
        if not QgsProject.instance().mapLayer(self.poilayerid) :
            self.poilayer = QgsVectorLayer("Point", layername, "memory")
            self.poiProvider = self.poilayer.dataProvider()
            self.poiProvider.addAttributes(attributes)
            self.poilayer.updateFields()    
        
        fields=self.poilayer.fields()
        
        for point in points:
            pt = QgsPoint( point['location']['points'][0]['Point']['coordinates'][0], 
                           point['location']['points'][0]['Point']['coordinates'][1]  )
            poiId = point["id"]
            if "categories" in list(point.keys()) and len(point["categories"]) > 0: 
               theme = point["categories"][0]['value']
            else: theme = ''
            if "categories" in  list(point.keys()) and len(point["categories"]) > 1: 
               category = point["categories"][1]['value']
            else: category = ''
            if "categories" in  point and len(point["categories"]) > 2: 
               poiType =  point["categories"][2]['value']
            else: poiType = ''
            
            name = point["labels"][0]["value"]
            if "phone" in list(point.keys()): 
               phone = point["phone"]
            else: phone= ""
            if "email" in list(point.keys()): 
               email = point["email"]
            else: email= ""
            #address
            if "address" in list(point['location'].keys()): 
              if "street" in list(point['location']["address"].keys()): 
                 straat = point['location']["address"]["street"]
              else:  straat = ''
              if "streetnumber" in list(point['location']["address"].keys()): 
                 huisnr = point['location']["address"]["streetnumber"]
              else:  huisnr = ''
              if "boxnumber" in list(point['location']["address"].keys()): 
                 busnr = point['location']["address"]["boxnumber"]
              else:  boxnr = ''
              postcode = point['location']["address"]["postalcode"]
              gemeente = point['location']["address"]["municipality"]
            else: 
              straat = ""
              huisnr = ""
              busnr = ""
              postcode = ""
              gemeente = ""
            
            if "links" in point: 
              link = point["links"][0]['href']
            else: link = ""
            tijd =  point["updated"] 
            if "authors" in point: 
              owner = point["authors"][0]["value"]
            else: owner= ""
            
            # add a feature
            fet = QgsFeature(fields)

            #set geometry
            fromCrs = QgsCoordinateReferenceSystem(4326)
            xform = QgsCoordinateTransform( fromCrs, self.poilayer.crs(), QgsProject.instance() )
            prjPt = xform.transform( pt )
            fet.setGeometry(QgsGeometry.fromPoint(prjPt))
      
            fet['id'] = int( poiId )
            fet['thema'] = theme
            fet['categorie'] = category
            fet['type'] = poiType
            fet['naam'] = name
            fet["email"] = email
            fet["telefoon"] = phone
            #address
            fet['straat'] = straat
            fet['huisnr'] = huisnr
            fet['busnr'] = busnr
            fet['postcode'] = postcode
            fet['gemeente'] = gemeente
            
            fet['link'] = link
            fet['lastupdate'] = tijd
            fet['owner'] = owner
      
            self.poiProvider.addFeatures([ fet ])
            self.poilayer.updateExtents()
    
        if saveToFile and not QgsProject.instance().mapLayer(self.poilayerid):
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
        QgsProject.instance().addMapLayer(self.poilayer)

        # store layer id and refresh
        self.poilayerid = self.poilayer.id()
        self.canvas.refresh()
    
    def _saveToFile( self, sender, startFolder=None ):
        'save to file'
        #"Shape Files (*.shp);;Geojson File (*.geojson);;GML ( *.gml);;Comma separated value File (excel) (*.csv);;MapInfo TAB (*.TAB);;Any File (*.*)"
        filter = "ESRI Shape Files (*.shp);;SpatiaLite (*.sqlite);;Any File (*.*)" #show only formats with update capabilty
        Fdlg = QFileDialog()
        Fdlg.setFileMode(QFileDialog.AnyFile)
        fName, __, __ = QFileDialog.getSaveFileName(sender, "open file", filter=filter, directory=startFolder)
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
      