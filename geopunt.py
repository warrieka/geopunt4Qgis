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

class geopunt:
  def __init__(self):
    self.locUrl = "http://loc.api.geopunt.be/geolocation/Location?"
    self.sugUrl = "http://loc.api.geopunt.be/geolocation/Suggestion?"

  def _createLocationUrl(self, q, c=1):
      geopuntUrl = self.locUrl
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
      geopuntUrl = self.sugUrl
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
      suggestion = json.load(response)
      return suggestion["SuggestionResult"]

