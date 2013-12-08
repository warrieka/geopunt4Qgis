# -*- coding: utf-8 -*-
"""
/***************************************************************************
 geopunt
                                 
 "bibliotheek om geopunt in python te gebruiken"
                             -------------------
        begin                : 2013-12-05
        copyright            : (C) 2013 by Kay Warrie
        email                : kaywarrie@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import urllib2, urllib, json

class geopuntAdres:
  def __init__(self):
    self._locUrl = "http://loc.api.geopunt.be/geolocation/Location?"
    self._sugUrl = "http://loc.api.geopunt.be/geolocation/Suggestion?"

  def _createLocationUrl(self, q, c=1):
      geopuntUrl = self._locUrl
      data = {}
      data["q"] = q
      data["c"] = c
      values = urllib.urlencode(data)
      result = geopuntUrl + values
      return result

  def fetchLocation(self, q, c=1):
      url = self._createLocationUrl(q, c=1)
      try:
	  response = urllib2.urlopen(url)
      except:
	  return "could not connect to geopunt"
      LocationResult = json.load(response)["LocationResult"]
      return LocationResult

  def _createSuggestionUrl(self, q, c=5):
      geopuntUrl = self._sugUrl
      data = {}
      data["q"] = q
      data["c"] = c
      values = urllib.urlencode(data)
      result = geopuntUrl + values
      return result

  def fetchSuggestion(self, q, c=5):
      url = self._createSuggestionUrl(q,c)
      try:
	  response = urllib2.urlopen(url)
      except:
	  return "could not connect to geopunt"
      suggestion = json.load(response)["SuggestionResult"]
      return suggestion


class geopuntPoi:
  def __init__(self):
      self._poiUrl = "http://poi.api.geopunt.be/core?"
      
  def _createPoiUrl(self , q, c=5, srs=31370 , maxModel=True ):
      poiUrl = self._poiUrl
      data = {}
      data["label"] = q
      data["srsOut"] = srs
      data["maxcount"] = c
      if maxModel:
	data["maxModel"] = "true"
      else:
	data["maxModel"] = "false"
      values = urllib.urlencode(data)
      result = poiUrl + values
      return result
    
  def fetchPoi(self, q,  c=5, srs=31370 , maxModel=False ):
      url = self._createPoiUrl( q, c, srs, maxModel )
      try:
	  response = urllib2.urlopen(url)
      except:
	  return "could not connect to geopunt"
      poi = json.load(response)["pois"]
      return poi
  
  def poiSuggestion(self, q, srs=31370 ):
      sug = self.fetchPoi( q, 25, srs )
      result = [n["labels"][0]["value"] for n in sug ]
      return result