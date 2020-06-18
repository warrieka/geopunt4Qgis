# -*- coding: utf-8 -*-
from .geopuntError import geopuntError
import urllib.request, urllib.error, urllib.parse, json, sys, datetime, ssl

from qgis.PyQt.QtWidgets import QMessageBox 

class elevation(object):
  def __init__(self, timeout=15, proxyUrl=""):
      self.timeout = timeout
      self.baseUri = 'https://dhm.agiv.be/api/elevation/v1/DHMVMIXED/request'
      
      QMessageBox.warning( None , "elevation" , proxyUrl)
      
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

  def _createElevationRequest(self, LineString, srs=31370, samples=50 ):
      geojson = {}
      geojson["SrsIn"] = srs
      geojson["SrsOut"] = srs 
      geojson["LineString"] = {"coordinates": LineString , "type":"LineString" }
      geojson["Samples"] = samples
      data =  json.dumps(geojson)
      req = urllib.request.Request(self.baseUri , data.encode('utf-8'),
                                   {'Content-Type': 'application/json'})
      return req
  
  def fetchElevaton(self, LineString, srs=31370, samples=50 ):
      "LineString= a serie of points in form [[4.2,51.27],[4.7,51.2],...], srs=ESPGcode, samples=nummer to return"
      req = self._createElevationRequest( LineString, srs, samples )
      response = urllib.request.urlopen(req, timeout= self.timeout, context=self.ctx)
      elevationJson = json.load(response)
      return elevationJson
