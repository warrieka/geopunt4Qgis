# -*- coding: utf-8 -*-
import json
from ..tools import getUrlData

class Adres(object):
  def __init__(self):
      self.locUrl = "https://loc.geopunt.be/v4/Location"
      self.sugUrl = "https://loc.geopunt.be/v4/Suggestion"
      
  def fetchLocation(self, q: str, c=1):
      LocationResult = json.loads( getUrlData(self.locUrl, params={"q": q, "c": c} ) )
      return LocationResult["LocationResult"]

  def fetchSuggestion(self, q: str, c=5):
      suggestion =  json.loads( getUrlData(self.sugUrl, params={"q": q, "c": c} ) )
      return suggestion["SuggestionResult"]
