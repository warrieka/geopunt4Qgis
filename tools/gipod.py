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
from future import standard_library
standard_library.install_aliases()
import os.path 
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtWidgets import QFileDialog
from qgis.PyQt.QtGui import QColor
from qgis.core import QgsField, QgsCoordinateReferenceSystem, QgsVectorLayer, QgsVectorFileWriter, QgsCoordinateTransform, QgsPointXY, QgsFeature, QgsGeometry, QgsProject, QgsSymbol, QgsRendererCategory, QgsCategorizedSymbolRenderer

class gipodHelper(object):
    @staticmethod
    def openOutput(sender=None, startFolder=None):
        fd = QFileDialog()
        filter = "ESRI Shape File (*.shp);;Comma separated value File (excel) (*.csv);;geojson (*.geojson);;GML File (*.gml);;MapInfo TAB (*.tab);;SpatiaLite (*.sqlite);;KML (google earth) (*.kml)"
        fName = fd.getSaveFileName( sender, "open file", filter=filter, directory=startFolder)

        if fName:
            return fName[0]
        else:
            return None
      
    @staticmethod
    def checkFtype( file2check):
        fType = "ESRI Shapefile" #DEFAULT
        if file2check:
            if file2check.upper().endswith('SHP'):
                fType = "ESRI Shapefile"
            elif file2check.upper().endswith('GML'):
                fType = "GML"  
            elif file2check.upper().endswith('GEOJSON'):
                fType = "GeoJSON"  
            elif file2check.upper().endswith('CSV'):
                fType = "CSV"  
            elif file2check.upper().endswith('KML'):
                fType = "KML"  
            elif file2check.upper().endswith('SQLITE'):
                fType = "SQLite"  
            elif file2check.upper().endswith('TAB'):
                fType = "MapInfo File"  
            return fType
        else:
            return None


class gipodWriter(object):
    def __init__(self, iface, layername, CRS=31370, manifestation=False, KML="" ):
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.layername = layername
        self.CRS = CRS
        self.manifestation = manifestation
        if KML == "KML":
          self.KML = 1
        else:
          self.KML = 0
    
    def __enter__(self):
        attributes =[ QgsField("gipodId", QVariant.Int),
              QgsField("owner", QVariant.String) ,
              QgsField("description", QVariant.String),
              QgsField("beginDate", QVariant.String, "Date"),
              QgsField("endDate", QVariant.String, "Date"),         
              QgsField("hinder", QVariant.Int),
              QgsField("link", QVariant.String),
              QgsField("cities", QVariant.String)
            ]
        if self.manifestation:
           attributes += [QgsField("intiatief", QVariant.String), 
                      QgsField("patroon", QVariant.String)]
        if self.KML:
           attributes += [QgsField("begin", QVariant.String, "Date"), 
                  QgsField("end", QVariant.String, "Date"), 
                  QgsField("icon", QVariant.String)
                  ]
       
        self.gipodlayer = QgsVectorLayer("Point", self.layername, "memory")
        self.gipodProvider = self.gipodlayer.dataProvider()
        self.gipodProvider.addAttributes(attributes)
        self.gipodlayer.updateFields()
        self.fields= self.gipodlayer.fields()
        return self
    
    def saveGipod2file(self, filename, ftype="ESRI Shapefile" ):
        layerOptions = []
        datasourceOptions = []
        if ftype == "CSV": 
            layerOptions += ["GEOMETRY=AS_XY","SEPARATOR=SEMICOLON"]
        if ftype == "KML": 
            datasourceOptions += ["NameField=owner"]
        srs = QgsCoordinateReferenceSystem(self.CRS)
    
        fpath, name = os.path.split(filename)
    
        if fpath and os.path.exists(fpath):          
            error, errormsg = QgsVectorFileWriter.writeAsVectorFormat(self.gipodlayer , filename, "utf-8", self.gipodlayer.crs(), ftype, layerOptions= layerOptions, datasourceOptions= datasourceOptions )
            if error == QgsVectorFileWriter.NoError:
                if ftype == "CSV": 
                    uri =( "file:///%s?delimiter=%s&xField=%s&yField=%s&crs=%s" % ( 
                        filename, ";", "X", "Y", self.gipodlayer.crs().authid()) ).replace("\\","/")
                    self.gipodlayer = QgsVectorLayer(uri, self.layername, "delimitedtext")
                else:
                    self.gipodlayer = QgsVectorLayer( filename, self.layername, "ogr")
                    self.gipodProvider = self.gipodlayer.dataProvider()
            else:
                raise gipodError( str(error.hasError()) , errormsg )
        else:
            raise gipodError( fpath + " doesn't exist" )

    def _makeCRSpoint(self, xy):
        x,y = xy
        fromCrs = QgsCoordinateReferenceSystem(self.CRS)
        xform =   QgsCoordinateTransform( fromCrs, self.gipodlayer.crs(), QgsProject.instance() )
        return    xform.transform( QgsPointXY( x,y ))

    def writePoint(self, xy, gipodId, owner, description, startDateTime, endDateTime, importantHindrance, detail, cities=[], initiator=None, recurrencePattern=None):
        fet = QgsFeature(self.fields)
        fet['gipodId'] = gipodId
        fet['owner'] = owner
        fet['description'] = description
        if self.KML:
          fet['begin'] = startDateTime.split("T")[0]
          fet['end'] = endDateTime.split("T")[0]
          if importantHindrance: fet['icon'] = "http://api.gipod.vlaanderen.be/ws/v1/icon/workassignment?important=true"
          else: fet['icon'] = "http://api.gipod.vlaanderen.be/ws/v1/icon/workassignment?important=false"

        fet['beginDate'] = startDateTime
        fet['endDate'] = endDateTime
        fet['hinder'] = importantHindrance
        fet['link'] = detail
        fet['cities'] = ", ".join(cities)
        if initiator and self.manifestation:
          fet['intiatief'] = initiator
        if recurrencePattern and self.manifestation:
          fet['patroon'] = recurrencePattern
    
        prjPt = self._makeCRSpoint( xy )
        fet.setGeometry(QgsGeometry.fromPointXY(prjPt))
    
        self.gipodProvider.addFeatures([ fet ])
    
    def __exit__(self, type, value, traceback):
        ' add layer to map and clean up'
        render = gipodRender(self.gipodlayer, 'hinder' ).render
        self.gipodlayer.setRenderer(render)
        QgsProject.instance().addMapLayer(self.gipodlayer)
    
        # refresh and update extends
        self.gipodlayer.updateExtents()
        self.canvas.refresh()
        del self.gipodlayer, self.gipodProvider, self.fields
 
 
class gipodRender(object):
      def __init__(self, Layer, hinderAttr='hinder'):
          '1: in hinderAttr is veel hinder, 0: in hinderAttr is weinig hinder'
          hinderSymbol =  QgsSymbol.defaultSymbol( 0 ) #0=point
          noHinderSymbol =  QgsSymbol.defaultSymbol( 0 ) #Layer.geometryType()
          hinderSymbol.setColor(QColor('#FF0000'))
          noHinderSymbol.setColor(QColor('#FFFF00'))
          noHinder= QgsRendererCategory(0, noHinderSymbol ,'weinig hinder')
          hinder= QgsRendererCategory(1, hinderSymbol ,'veel hinder')
          self.render =  QgsCategorizedSymbolRenderer(hinderAttr,[noHinder,hinder])

class gipodError(Exception):
    def __init__(self, erro, message=''):
      self.message =  erro +" "+ message
    def __str__(self):
      return repr(self.message)
    
