from typing import Tuple, Iterator, Sequence
import numpy as np
from qgis.core import ( QgsRectangle, QgsProject, QgsCoordinateTransform,
         QgsPointXY, QgsRasterLayer, QgsRaster, QgsStyle, QgsRasterShader,
         QgsColorRampShader, QgsSingleBandPseudoColorRenderer, QgsGeometry)

URL_DHM = "https://geo.api.vlaanderen.be/el-dtm/wcs"

class dhm:
    def __init__(self) -> None:
        self.dhmlayer =  self.dhmLayer()
        self.crs =self.dhmlayer.crs()
        self.dhmProvider = self.dhmlayer.dataProvider()
        self.nodata = self.dhmProvider.sourceNoDataValue(1)

    @staticmethod
    def dhmLayer(dtm_url=URL_DHM) -> QgsRasterLayer:
        f"""
        Create new Raster layer the DHM-WCS of Flanders: {URL_DHM}

        Returns:
            QgsRasterLayer: A instance of the DTM or if it can't connect None
        """
        url = dtm_url+"?IgnoreAxisOrientation=1&dpiMode=7&identifier=EL.GridCoverage.DTM&url="+dtm_url
        dhmlayer = QgsRasterLayer(url, 'Hoogtemodel', 'wcs') 
        dhmProvider = dhmlayer.dataProvider()
        if dhmlayer.isValid():
            colorRamp = QgsStyle().defaultStyle().colorRamp('Turbo')
            fnc = QgsColorRampShader(0,200)
            fnc.setColorRampType(QgsColorRampShader.Interpolated)
            fnc.setSourceColorRamp(colorRamp)
            fnc.classifyColorRamp(15)

            shader = QgsRasterShader()
            shader.setRasterShaderFunction(fnc)

            renderer = QgsSingleBandPseudoColorRenderer(dhmProvider, 1, shader)
            renderer.setClassificationMin(0)
            renderer.setClassificationMax(200)
            renderer.setOpacity(0.8)

            dhmlayer.setRenderer(renderer)
            # dhmlayer.triggerRepaint()
            return dhmlayer
        return None

        
    def identify(self, xy:QgsPointXY, bbox:QgsRectangle=QgsRectangle(), w:int=0, h:int=0) -> Tuple[float, float, float]:
        """Identify a point on the DHM.
           if xy does not overlap with the DHM, then (x,y, None) is returned.

        Returns:
            Tuple[float, float, float]: a tuple containing the x,y,z coordinates
        """
        _xy= self.t.transform(xy)
        _bbox= self.t.transformBoundingBox( bbox )

        ident = self.dhmProvider.identify(_xy, QgsRaster.IdentifyFormatValue, boundingBox=_bbox, width=w, height=h)

        if ident.isValid():
           z= ident.results()[1]
           if z != self.nodata: 
                return ( xy.x() , xy.y() , z )
           print(z)
        return ( xy.x() , xy.y() , None )
    
    
    def identifyLine(self, geom: QgsGeometry, dist:float=50, count:int=None) -> Iterator[Tuple[float, float, float]]:
        """Identify a series of points along a line. 

        Args:
            geom (QgsGeometry): A line geometry
            dist (float, optional): The distance at along the line to interpolate a point, ignored if count is set. Defaults to 50.
            count (int, optional): The number of points to interpolate. Defaults to None.

        Yields:
            Iterator[Tuple[float, float, float]]: A list of points interpolated on the line, 
        """
        if geom.wkbType() != 2: 
            raise Exception("only QgsGeometry of type Line is allowed")
        if count is not None:
            dist = geom.length() / count
        else:
            count = geom.length() // dist

        print(dist, count)
        line = geom.densifyByDistance(dist)
        bbox = self.t.transformBoundingBox( geom.boundingBox() )
        print(line)
        for pnt in line.asPolyline():
            print(pnt)
            yield self.identify(pnt, bbox)

    def fetchAsArray(self, geom: QgsGeometry, d:float=50, c:int=None) -> Sequence:
        """Identify a series of points along a line. Result is numpy array.

        Args:
            geom (QgsGeometry): A line geometry
            d (float, optional):. The distance at along the line to interpolate a point, ignored if count is set. Defaults to 50.
            c (int, optional): The number of points to interpolate. Defaults to None.

        Returns:
            List: a 4 by c array in form [[d,x,y,z],**] 
        """
        if geom.wkbType() != 2: 
            raise Exception("only QgsGeometry of type Line is allowed")

        if c is not None:
            dist = geom.length() / c
        else:
            dist = d

        self.t = QgsCoordinateTransform( QgsProject.instance().crs(), self.crs, QgsProject.instance())

        line = geom.densifyByDistance(dist).asPolyline()
        pnt0 = line[0]
        x0, y0, z0 = self.identify(pnt0, geom.boundingBox() )
        data = [[0, x0, y0, z0]] 

        for pnt in line[1:]:
            x,y,z = self.identify(pnt)
            r = np.sqrt( (x-x0)**2 + (y-y0)**2 )
            x0, y0, z0 = (x,y,z0)
            data.append([r,x,y,z])
        return data 