# -*- coding: utf-8 -*-
"""
/***************************************************************************
elevationHelper
                A QGIS plugin
"Tool om geopunt in QGIS te gebruiken"
                -------------------
    begin                : 2014-07-02
    copyright            : (C) 2014 by Kay Warrie
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
from PyQt4.QtCore import *
from PyQt4.QtGui import QFileDialog
from qgis.core import *
import numpy as np
from geometryhelper import geometryHelper

class elevationHelper:
    def __init__(self , iface, startFolder=None ):
        self.iface= iface
        self.sampleslayerid = ''
        self.profilelayerId = ''
        self.startFolder= startFolder

    def save_sample_points(self, pointData, profileName="", layername="elevation_samples", saveToFile=None, sender=None):
        ''
        attributes = [    QgsField("name", QVariant.String),
          QgsField("Dist", QVariant.Double), QgsField("z_taw", QVariant.Double) ]
    
        if not QgsMapLayerRegistry.instance().mapLayer(self.sampleslayerid) :
            self.sampleslayer = QgsVectorLayer("Point", layername, "memory")
            self.samplesProvider = self.sampleslayer.dataProvider()
            self.samplesProvider.addAttributes(attributes)
            self.sampleslayer.updateFields()    
        
        fields= self.sampleslayer.pendingFields()
        
        for point in pointData:
            #create the geometry
            pt = QgsPoint( point[1], point[2] )

            # add a feature
            fet = QgsFeature(fields)

            #set geometry
            fromCrs = QgsCoordinateReferenceSystem(4326)
            xform = QgsCoordinateTransform( fromCrs, self.sampleslayer.crs() )
            prjPt = xform.transform( pt )
            fet.setGeometry(QgsGeometry.fromPoint(prjPt))
      
            fet['name'] = profileName
            fet['dist'] =  point[0]
            if  point[3] > -9999 : fet['z_taw'] =  point[3]            
      
            self.samplesProvider.addFeatures([ fet ])
            self.sampleslayer.updateExtents()
    
        if saveToFile and not QgsMapLayerRegistry.instance().mapLayer(self.sampleslayerid):
            save = self._saveToFile( sender, os.path.join( self.startFolder, layername))
            if save:
              fpath, flType = save
              error = QgsVectorFileWriter.writeAsVectorFormat(self.sampleslayer, fpath, "utf-8", None, flType, )
              if error == QgsVectorFileWriter.NoError:
                  self.sampleslayer = QgsVectorLayer( fpath , layername, "ogr")
                  self.samplesProvider = self.sampleslayer.dataProvider()
              else: 
                  del self.sampleslayer, self.samplesProvider 
                  return 
            else:
              del self.sampleslayer, self.samplesProvider 
              return 

        # add layer if not already
        QgsMapLayerRegistry.instance().addMapLayer(self.sampleslayer)

        # store layer id and refresh
        self.sampleslayerid = self.sampleslayer.id()
        self.iface.mapCanvas().refresh()

    def save_profile(self, lineGeom, pointData, profileName="", layername="elevation_line", saveToFile=None, sender=None):
        attributes = [  QgsField("name", QVariant.String), 
                        QgsField("maxZ", QVariant.Double), 
                        QgsField("meanZ", QVariant.Double), 
                        QgsField("minZ", QVariant.Double) ]
    
        if not QgsMapLayerRegistry.instance().mapLayer(self.profilelayerId) :
            self.profilelayer = QgsVectorLayer("LineString", layername, "memory")
            self.profileProvider = self.profilelayer.dataProvider()
            self.profileProvider.addAttributes(attributes)
            self.profilelayer.updateFields()    
        
        fields= self.profilelayer.pendingFields()

        # add the feature
        fet = QgsFeature(fields)

        #set geometry
        gh = geometryHelper( self.iface )
        prjGeom = gh.prjLineFromMapCrs(lineGeom, self.profilelayer.crs() )
        fet.setGeometry( prjGeom )
  
        zdata =  [n[3] for n in pointData if n[3] > -9999 ]
        fet["name"] = profileName
        fet['maxZ'] = float( np.max( zdata ) )
        fet['meanZ'] = float( np.mean( zdata ) )
        fet['minZ'] = float( np.min( zdata ) )
  
        self.profileProvider.addFeatures([ fet ])
        self.profilelayer.updateExtents()
    
        if saveToFile and not QgsMapLayerRegistry.instance().mapLayer(self.profilelayerId):
            save = self._saveToFile( sender, os.path.join( self.startFolder, layername ))
            if save:
              fpath, flType = save
              error = QgsVectorFileWriter.writeAsVectorFormat(self.profilelayer, fpath, "utf-8", None, flType, )
              if error == QgsVectorFileWriter.NoError:
                  self.profilelayer = QgsVectorLayer( fpath , layername, "ogr")
                  self.profileProvider = self.profilelayer.dataProvider()
              else: 
                  del self.profilelayer, self.profileProvider 
                  return 
            else:
              del self.profilelayer, self.profileProvider 
              return 

        # add layer if not already
        QgsMapLayerRegistry.instance().addMapLayer(self.profilelayer)

        # store layer id and refresh
        self.profilelayerId = self.profilelayer.id()
        self.iface.mapCanvas().refresh()

    def _saveToFile( self, sender, startFolder=None ):
        filter = "ESRI Shape Files (*.shp);;SpatiaLite (*.sqlite);;Any File (*.*)" #show only formats with update capabilty
        Fdlg = QFileDialog()
        Fdlg.setFileMode(QFileDialog.AnyFile)
        fName = Fdlg.getSaveFileName( sender, "open file" , filter= filter, directory=startFolder)
        if fName:
          ext = os.path.splitext( fName )[1]
          if "SHP" in ext.upper():
            flType = "ESRI Shapefile"
          elif "SQLITE" in ext.upper():
            flType = "SQLite" 
          elif "GEOJSON" in ext.upper():#no update possible -> hidden
            flType = "GeoJSON"
          elif "GML" in ext.upper():    #no update possible -> hidden
            flType = "GML"
          elif 'TAB' in ext.upper():    #no update possible -> hidden
            flType = 'MapInfo File'
          elif 'KML' in ext.upper():    #no update possible -> hidden
            flType = 'KML'
          else:
            fName = fName + ".shp"
            flType = "ESRI Shapefile"
          return (fName , flType )
        else:
            return None
      