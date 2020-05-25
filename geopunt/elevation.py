# -*- coding: utf-8 -*-
from .geopuntError import geopuntError
import urllib.request, urllib.error, urllib.parse, json, sys, datetime

class elevation(object):
  def __init__(self, timeout=15, proxyUrl=""):
      self.timeout = timeout
      self.baseUri = 'http://dhm.agiv.be/api/elevation/v1/DHMVMIXED/request'
      
      if isinstance(proxyUrl, str) and proxyUrl != "":
        if proxyUrl.startswith("https"): proxy = urllib.request.ProxyHandler({'https': proxyUrl})
        else: proxy = urllib.request.ProxyHandler({'http': proxyUrl})
      else:
          proxy = urllib.request.ProxyHandler()
      auth = urllib.request.HTTPBasicAuthHandler()   
      self.opener = urllib.request.build_opener(proxy, auth, urllib.request.HTTPHandler)

  def _createElevationRequest(self, LineString, srs=31370, samples=50 ):
      geojson = {}
      geojson["SrsIn"] = srs
      geojson["SrsOut"] = srs 
      geojson["LineString"] = {"coordinates": LineString , "type":"LineString" }
      geojson["Samples"] = samples
      data =  json.dumps(geojson)
      req = urllib.request.Request(self.baseUri , data.encode('utf-8'), {'Content-Type': 'application/json'})
      return req
  
  def fetchElevaton(self, LineString, srs=31370, samples=50 ):
      "LineString= a serie of points in form [[4.2,51.27],[4.7,51.2],...], srs=ESPGcode, samples=nummer to return"
      req = self._createElevationRequest( LineString, srs, samples )
      try:
         response = self.opener.open(req, timeout= self.timeout)
      except  (urllib.error.HTTPError, urllib.error.URLError) as e:
         raise geopuntError( str( e.reason ))
      except:
         raise geopuntError( str( sys.exc_info()[1] ))
      else:
         elevationJson = json.load(response)
         return elevationJson
