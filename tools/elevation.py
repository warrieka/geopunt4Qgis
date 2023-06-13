import os.path
import pathlib, locale
import numpy as np
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtWidgets import QFileDialog
from qgis.core import (QgsProject, QgsField, QgsVectorLayer, QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform, QgsGeometry, QgsVectorFileWriter, QgsFeature, QgsPointXY)
from .geometry import geometryHelper

class elevationHelper(object):
    def __init__(self , iface, startFolder=None ):
        self.iface= iface
        self.sampleslayerid = ''
        self.profilelayerId = ''
        self.startFolder= startFolder

    def save_sample_points(self, pointData, profileName="", layername="elevation_samples", saveToFile=None, sender=None):
        'save sample points als maplayer'
        attributes = [ QgsField("name", QVariant.String),
          QgsField("Dist", QVariant.Double), QgsField("z_taw", QVariant.Double) ]
    
        if not QgsProject.instance().mapLayer(self.sampleslayerid) :
            self.sampleslayer = QgsVectorLayer("Point", layername, "memory")
            self.samplesProvider = self.sampleslayer.dataProvider()
            self.samplesProvider.addAttributes(attributes)
            self.sampleslayer.updateFields()    
        
        fields= self.sampleslayer.fields()
        feats = []

        for point in pointData:
            #create the geometry
            pt = QgsPointXY( point[1], point[2] )

            # add a feature
            fet = QgsFeature(fields)

            #set geometry
            # fromCrs = QgsCoordinateReferenceSystem("EPSG:4326")
            # xform = QgsCoordinateTransform( fromCrs, self.sampleslayer.crs(), QgsProject.instance() )
            # prjPt = xform.transform( pt )
            fet.setGeometry(QgsGeometry.fromPointXY(pt))
      
            fet['name'] = profileName
            fet['dist'] =  point[0]
            if  point[3] > -9999 : fet['z_taw'] =  point[3]            
            feats.append(fet) 

        self.samplesProvider.addFeatures(feats) 
        self.sampleslayer.updateExtents()
    
        if saveToFile and not QgsProject.instance().mapLayer(self.sampleslayerid):
            save = self._saveToFile( sender, os.path.join( self.startFolder, layername))
            if save:
              fpath, flType = save
              error, _ = QgsVectorFileWriter.writeAsVectorFormat(layer=self.sampleslayer, 
                                              fileName=fpath, fileEncoding="utf-8", driverName=flType ) 
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
        QgsProject.instance().addMapLayer(self.sampleslayer) 

        # store layer id and refresh
        self.sampleslayerid = self.sampleslayer.id()
        self.iface.mapCanvas().refresh()

    def save_profile(self, lineGeom, pointData, profileName="", layername="elevation_line", saveToFile=None, sender=None):
        attributes = [  QgsField("name", QVariant.String), 
                        QgsField("maxZ", QVariant.Double), 
                        QgsField("meanZ", QVariant.Double), 
                        QgsField("minZ", QVariant.Double) ]
    
        if not QgsProject.instance().mapLayer(self.profilelayerId) :
            self.profilelayer = QgsVectorLayer("LineString", layername, "memory")
            self.profileProvider = self.profilelayer.dataProvider()
            self.profileProvider.addAttributes(attributes)
            self.profilelayer.updateFields()    
        
        fields= self.profilelayer.fields()

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
    
        if saveToFile and not QgsProject.instance().mapLayer(self.profilelayerId):
            save = self._saveToFile( sender, os.path.join( self.startFolder, layername ))
            if save:
              fpath, flType = save
              error, _ = QgsVectorFileWriter.writeAsVectorFormat(layer=self.profilelayer, 
                                    fileName=fpath, fileEncoding="utf-8", driverName=flType )
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
        QgsProject.instance().addMapLayer(self.profilelayer)

        # store layer id and refresh
        self.profilelayerId = self.profilelayer.id()
        self.iface.mapCanvas().refresh()


    def saveToCsv( self, sender, narray, title=''):
        filter = "Comma separated value File (excel) (*.csv);;TextFile (*.txt);;Any File (*.*)" 
        fName, _ = QFileDialog.getSaveFileName( sender, 
                "open file" , filter=filter, directory= os.path.join(self.startFolder, title))
        
        decimal_point = locale.localeconv()['decimal_point']
        sep = ";" if decimal_point == ',' else ','
        if fName:
          ext = os.path.splitext( fName )[1]
          if "TXT" in ext.upper(): sep = " "
          hdr = sep.join(['dist','x','y','z'])
          np.savetxt(fName, narray, delimiter=sep, header=hdr, fmt='%.2f' )
        else:
           return None

        if title == '':
           title=  os.path.basename(fName)

        uri =  pathlib.Path(fName).as_uri() + f"?delimiter={sep}&yField=y&xField=x&useHeader=yes"
        self.sampleslayer = QgsVectorLayer(uri, title , 'delimitedtext')
        QgsProject.instance().addMapLayer(self.sampleslayer)
        return self.sampleslayer

    def _saveToFile( self, sender, startFolder=None ):
        filter = "OGC GeoPackage (*.gpkg);;ESRI Shape Files (*.shp);;SpatiaLite (*.sqlite);;Geojson File (*.geojson);;GML ( *.gml);;Comma separated value File (excel) (*.csv);;MapInfo TAB (*.TAB);;Any File (*.*)" 
        fName, __ = QFileDialog.getSaveFileName( sender, "open file" , filter= filter, directory=startFolder)
        if fName:
          ext = os.path.splitext( fName )[1]
          if "GPKG" in ext.upper():
            flType = "GPKG"
          elif "SHP" in ext.upper():
            flType = "ESRI Shapefile"
          elif "SQLITE" in ext.upper():
            flType = "SQLite" 
          elif "GEOJSON" in ext.upper():#no update possible -> hidden
            flType = "GeoJSON"
          elif "GML" in ext.upper():    #no update possible -> hidden
            flType = "GML"
          elif 'TAB' in ext.upper():    #no update possible -> hidden
            flType = 'MapInfo File'
          elif 'CSV' in ext.upper():    #no update possible -> hidden
            flType = 'CSV'
          else:
            fName = fName + ".shp"
            flType = "ESRI Shapefile"
          return (fName , flType )
        else:
            return None
      
