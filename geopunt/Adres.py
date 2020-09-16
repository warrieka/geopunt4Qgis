# -*- coding: utf-8 -*-
import json, sys, datetime, urllib.parse
from urllib.request import getproxies
import requests

class Adres(object):
  _locUrl = "https://loc.api.geopunt.be/v4/Location?"
  _sugUrl = "https://loc.api.geopunt.be/v4/Suggestion?"

  def __init__(self, timeout=15, proxies=None):
      self.timeout = timeout
      self.proxy = proxies if proxies else getproxies()
      
  def _createLocationUrl(self, q, c=1):
      geopuntUrl = self._locUrl
      data = {}
      data["q"] = q
      data["c"] = c
      values = urllib.parse.urlencode(data)
      result = geopuntUrl + values 
      return result

  def fetchLocation(self, q, c=1):
      url = self._createLocationUrl(q, c=1)
      response = requests.get(url, timeout=self.timeout, verify=False, proxies=self.proxy )
      LocationResult = response.json()
      return LocationResult["LocationResult"]

  def _createSuggestionUrl(self, q, c=5):
      geopuntUrl = self._sugUrl
      data = {}
      data["q"] = q
      data["c"] = c
      values = urllib.parse.urlencode(data)
      result = geopuntUrl + values
      return result

  def fetchSuggestion(self, q, c=5):
      url = self._createSuggestionUrl(q,c)
      response = requests.get(url, timeout=self.timeout, verify=False, proxies=self.proxy )
      suggestion = response.json()
      return suggestion["SuggestionResult"]
