# -*- coding: utf-8 -*-
from .geopuntError import geopuntError
import urllib.request, urllib.error, urllib.parse, json, sys, datetime

class Adres(object):
  def __init__(self, timeout=15, proxyUrl=""):
      self.timeout = timeout
      self._locUrl = "http://loc.api.geopunt.be/v3/Location?"
      self._sugUrl = "http://loc.api.geopunt.be/v3/Suggestion?"
      if isinstance(proxyUrl, str)  and proxyUrl != "":
         proxy = urllib.request.ProxyHandler({'http': proxyUrl })
      else:
         proxy = urllib.request.ProxyHandler()
      auth = urllib.request.HTTPBasicAuthHandler()
      self.opener = urllib.request.build_opener(proxy, auth, urllib.request.HTTPHandler)

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
      try:
            response = self.opener.open(url, timeout=self.timeout)
      except (urllib.error.HTTPError, urllib.error.URLError) as e:
            raise geopuntError( str( e.reason ) )
      except:
            raise geopuntError( sys.exc_info()[1] )
      else:
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
          response = self.opener.open(url, timeout=self.timeout)
      except (urllib.error.HTTPError, urllib.error.URLError) as e:
          raise geopuntError( str( e.reason ))
      except:
          raise geopuntError( sys.exc_info()[1] )
      else:
          suggestion = json.load(response)
          return suggestion["SuggestionResult"]