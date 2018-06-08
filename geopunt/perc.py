# -*- coding: utf-8 -*-
from .geopuntError import geopuntError
import urllib.request, urllib.error, urllib.parse, json, sys, datetime


class perc(object):
   def __init__(self, timeout=15, proxyUrl=""):
      self.timeout = timeout

      self._esriCapaServer= "http://geoservices.informatievlaanderen.be/ArcGIS/rest/services/adp/MapServer/0/query?" 
      self._locUrl = "http://perc.geopunt.be/Perceel/Location?"
      self._sugUrl = "http://perc.geopunt.be/Perceel/Suggestion?"
      if (isinstance(proxyUrl, str) or isinstance(proxyUrl, str)) and proxyUrl != "":
         proxy = urllib.request.ProxyHandler({'http': proxyUrl })
      else:
         proxy = urllib.request.ProxyHandler()
      auth = urllib.request.HTTPBasicAuthHandler()
      self.opener = urllib.request.build_opener(proxy, auth, urllib.request.HTTPHandler)
      
   def fetchLocation(self, q, c=1):
      geopuntUrl = self._locUrl
      data = {"q": q, "c":c}
      values = urllib.parse.urlencode(data).encode('utf-8')
      response = self.opener.open(geopuntUrl, values, timeout=self.timeout)
      LocationResult = json.load(response)
      return LocationResult["LocationResult"]

   def fetchSuggestion(self, q, c=5):
      geopuntUrl = self._sugUrl
      data = {"q": q, "c": c}
      values = urllib.parse.urlencode(data).encode('utf-8')
      response = self.opener.open(geopuntUrl, values, timeout=self.timeout)
      suggestion = json.load(response)
      return suggestion["SuggestionResult"]
         
   def getPercGeom(self, capakey, srs=31370):
      capaUrl = self._esriCapaServer
      data = {"f": "geojson"}
      data["where"] = str( "CAPAKEY LIKE '{}'".format( capakey ) )
      data["outSR"] = srs
      values = urllib.parse.urlencode(data).encode('utf-8')
      response = self.opener.open(capaUrl, values, timeout=self.timeout)
      return json.load(response)
         
   def getPercAtXY(self, x, y, srs=31370):
      capaUrl = self._esriCapaServer
      data = {"f": "geojson", "geometryType":"esriGeometryPoint"}
      data["geometry"] = str(x), +","+ str(y)
      data["inSR"] = srs
      data["outSR"] = srs
      values = urllib.parse.urlencode(data).encode('utf-8')
      response = self.opener.open(capaUrl, values, timeout=self.timeout)
      return json.load(response)

