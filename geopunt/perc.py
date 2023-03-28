# -*- coding: utf-8 -*-
import json
from ..tools.web import getUrlData

class perc(object):
   def __init__(self):
      self._esriCapaServer= "https://geoservices.informatievlaanderen.be/ArcGIS/rest/services/adp/MapServer/0/query" 
      self._locUrl = "https://geo.api.vlaanderen.be/geolocation/v2/Location"
      self._sugUrl = "https://geo.api.vlaanderen.be/geolocation/v2/Suggestion"

   def fetchLocation(self, q, c=1):
      geopuntUrl = self._locUrl
      data = {"capakey": q, "c":c}
      LocationResult = getUrlData(geopuntUrl, params=data)
      return json.loads(LocationResult)["LocationResult"]

   def fetchSuggestion(self, q, c=5):
      geopuntUrl = self._sugUrl
      data = {"capakey": q, "c": c}
      suggestion =  getUrlData(geopuntUrl, params=data)
      return json.loads(suggestion)["SuggestionResult"]
         
   def getPercGeom(self, capakey, srs=31370):
      capaUrl = self._esriCapaServer
      data = {"f": "geojson"}
      data["where"] = str( "CAPAKEY LIKE '{}'".format( capakey ) )
      data["outSR"] = srs
      response = getUrlData(capaUrl, params=data)
      return json.loads(response)
         
   def getPercAtXY(self, x, y, srs=31370):
      capaUrl = self._esriCapaServer
      data = {"f": "geojson", "geometryType":"esriGeometryPoint"}
      data["geometry"] = str(x) +","+ str(y)
      data["inSR"] = srs
      data["outSR"] = srs
      response = getUrlData(capaUrl, params=data)
      return json.loads(response)
         
