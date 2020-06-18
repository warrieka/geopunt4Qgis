# -*- coding: utf-8 -*-
from .geopuntError import geopuntError
import urllib.request, urllib.error, urllib.parse, json, sys, datetime, ssl

class Adres(object):
  def __init__(self, timeout=15, proxyUrl=""):
      self.timeout = timeout
      self._locUrl = "https://loc.api.geopunt.be/v3/Location?"
      self._sugUrl = "https://loc.api.geopunt.be/v3/Suggestion?"
      
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
      response = urllib.request.urlopen(url, timeout=self.timeout, context=self.ctx)
      LocationResult = json.load(response)
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
      try:
          response = urllib.request.urlopen(url, timeout=self.timeout, context=self.ctx)
      except (urllib.error.HTTPError, urllib.error.URLError) as e:
          raise geopuntError( str( e.reason ))
      except:
          raise geopuntError( sys.exc_info()[1] )
      else:
          suggestion = json.load(response)
          return suggestion["SuggestionResult"]
