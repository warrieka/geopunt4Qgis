# -*- coding: utf-8 -*-
from .geopuntError import geopuntError
import urllib.request, urllib.error, urllib.parse, json, sys, datetime, ssl


class perc(object):
   def __init__(self, timeout=15, proxyUrl=""):
      self.timeout = timeout

      self._esriCapaServer= "https://geoservices.informatievlaanderen.be/ArcGIS/rest/services/adp/MapServer/0/query?" 
      self._locUrl = "https://perc.geopunt.be/Perceel/Location?"
      self._sugUrl = "https://perc.geopunt.be/Perceel/Suggestion?"

      self.ctx = ssl.create_default_context()
      self.ctx.check_hostname = False
      self.ctx.verify_mode = ssl.CERT_NONE
      
      if isinstance(proxyUrl, str)  and proxyUrl != "":
         if proxyUrl.startswith("https"): 
            proxy = urllib.request.ProxyHandler({'https': proxyUrl})
         else: 
            proxy = urllib.request.ProxyHandler({'http': proxyUrl})
         opener = urllib.request.build_opener(proxy, urllib.request.HTTPSHandler, urllib.request.HTTPHandler)
         urllib.request.install_opener(opener)

      
   def fetchLocation(self, q, c=1):
      geopuntUrl = self._locUrl
      data = {"q": q, "c":c}
      values = urllib.parse.urlencode(data).encode('utf-8')
      response = urllib.request.urlopen(geopuntUrl, values, timeout=self.timeout, context=self.ctx)
      LocationResult = json.load(response)
      return LocationResult["LocationResult"]

   def fetchSuggestion(self, q, c=5):
      geopuntUrl = self._sugUrl
      data = {"q": q, "c": c}
      values = urllib.parse.urlencode(data).encode('utf-8')
      response = urllib.request.urlopen(geopuntUrl, values, timeout=self.timeout, context=self.ctx)
      suggestion = json.load(response)
      return suggestion["SuggestionResult"]
         
   def getPercGeom(self, capakey, srs=31370):
      capaUrl = self._esriCapaServer
      data = {"f": "geojson"}
      data["where"] = str( "CAPAKEY LIKE '{}'".format( capakey ) )
      data["outSR"] = srs
      values = urllib.parse.urlencode(data).encode('utf-8')
      response = urllib.request.urlopen(capaUrl, values, timeout=self.timeout, context=self.ctx)
      return json.load(response)
         
   def getPercAtXY(self, x, y, srs=31370):
      capaUrl = self._esriCapaServer
      data = {"f": "geojson", "geometryType":"esriGeometryPoint"}
      data["geometry"] = str(x), +","+ str(y)
      data["inSR"] = srs
      data["outSR"] = srs
      values = urllib.parse.urlencode(data).encode('utf-8')
      response = urllib.request.urlopen(capaUrl, values, timeout=self.timeout, context=self.ctx)
      return json.load(response)

