# -*- coding: utf-8 -*-
import json
from ..tools import getUrlData

class elevation(object):
  def __init__(self):
      self.baseUri = 'https://dhm.agiv.be/api/elevation/v1/DHMV2'

  def fetchElevaton(self, LineString, srs=31370, samples=50 ):
      locations = "|".join( ["{},{}".format(*f) for f in LineString ] )
      data = {}
      data["SrsIn"] = srs
      data["SrsOut"] = srs 
      data["Locations"] = locations
      data["Samples"] = samples
      resp = getUrlData(self.baseUri, params=data )
      return json.loads( resp )

