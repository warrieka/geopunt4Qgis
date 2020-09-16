# -*- coding: utf-8 -*-
import sys, datetime
from urllib.request import getproxies
import requests

class elevation(object):
  baseUri = 'https://dhm.agiv.be/api/elevation/v1/DHMVMIXED/request'

  def __init__(self, timeout=15, proxies=None):
      self.timeout = timeout
      self.proxy = proxies if proxies else getproxies()

  def fetchElevaton(self, LineString, srs=31370, samples=50 ):
      geojson = {}
      geojson["SrsIn"] = srs
      geojson["SrsOut"] = srs 
      geojson["LineString"] = {"coordinates": LineString , "type":"LineString" }
      geojson["Samples"] = samples
      #data =  json.dumps(geojson)
      req = requests.post(self.baseUri, timeout= self.timeout, json=geojson, 
                                                verify=False, proxies=self.proxy )
      return req.json()

