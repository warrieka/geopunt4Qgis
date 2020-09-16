# -*- coding: utf-8 -*-
import json, sys, datetime
from urllib.request import getproxies
import requests

class perc(object):
   _esriCapaServer= "https://geoservices.informatievlaanderen.be/ArcGIS/rest/services/adp/MapServer/0/query?" 
   _locUrl = "https://perc.geopunt.be/Perceel/Location?"
   _sugUrl = "https://perc.geopunt.be/Perceel/Suggestion?"

   def __init__(self, timeout=15,  proxies=None):
      self.timeout = timeout
      self.proxy = proxies if proxies else getproxies()
      
   def fetchLocation(self, q, c=1):
      geopuntUrl = self._locUrl
      data = {"q": q, "c":c}
      LocationResult = requests.get(geopuntUrl, params=data, timeout=self.timeout , verify=False, proxies=self.proxy )
      return LocationResult.json()["LocationResult"]

   def fetchSuggestion(self, q, c=5):
      geopuntUrl = self._sugUrl
      data = {"q": q, "c": c}
      suggestion = requests.get(geopuntUrl, params=data, timeout=self.timeout , verify=False, proxies=self.proxy )
      return suggestion.json()["SuggestionResult"]
         
   def getPercGeom(self, capakey, srs=31370):
      capaUrl = self._esriCapaServer
      data = {"f": "geojson"}
      data["where"] = str( "CAPAKEY LIKE '{}'".format( capakey ) )
      data["outSR"] = srs
      response = requests.get(capaUrl, params=data, timeout=self.timeout , verify=False, proxies=self.proxy )
      return response.json()
         
   def getPercAtXY(self, x, y, srs=31370):
      capaUrl = self._esriCapaServer
      data = {"f": "geojson", "geometryType":"esriGeometryPoint"}
      data["geometry"] = str(x) +","+ str(y)
      data["inSR"] = srs
      data["outSR"] = srs
      response = requests.get(capaUrl, params=data, timeout=self.timeout , verify=False, proxies=self.proxy )
      return response.json() 

