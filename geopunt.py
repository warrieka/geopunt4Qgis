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

class Adres:
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
      LocationResult = json.load(response)
      return LocationResult["LocationResult"]

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
      suggestion = json.load(response)
      return suggestion["SuggestionResult"]


class Poi:
  def __init__(self):
      self._poiUrl = "http://poi.api.geopunt.be/core?"
      self.resultCount = 0
      self.resultBounds = [17736,23697,297289,245375]
      self.resultPoi = []
      #maxBounds srs 31370: x between 17736 and 297289, y between 23697 and 245375 
      #TODO: What if no Lambert coordinates as input???
      self.maxBounds = [17736,23697,297289,245375]

      
  def _createPoiUrl(self , q, c=5, srs=31370 , maxModel=False, bbox=[] ):
      poiUrl = self._poiUrl
      data = {}
      data["label"] = q
      data["srsOut"] = srs
      data["srsIn"] = srs    #i am asuming srsIn wil alwaysbe = srsOut
      data["maxcount"] = c
      if maxModel:
	data["maxModel"] = "true"
      else:
	data["maxModel"] = "false"
      if bbox:
	if bbox[0] < self.maxBounds[0]: 
	   bbox[0] = self.maxBounds[0]
	if bbox[1] < self.maxBounds[1]:
	   bbox[1] = self.maxBounds[1]
	if bbox[2] > self.maxBounds[2]:
	   bbox[2] = self.maxBounds[2]
	if bbox[3] > self.maxBounds[3]:
	   bbox[3] = self.maxBounds[3]
	data["bbox"] = "|".join([str(b) for b in bbox])
	
      values = urllib.urlencode(data)
      result = poiUrl + values
      return result
    
  def fetchPoi(self, q,  c=5, srs=31370 , maxModel=False , updateResults=True, bbox=None ):
      url = self._createPoiUrl( q, c, srs, maxModel, bbox )
      try:
	  response = urllib2.urlopen(url)
      except:
	  return "could not connect to geopunt"
      poi = json.load(response)
      if updateResults:
	self.resultCount =  int( poi["label"]["value"] )
	self.resultBounds = self._getBounds(poi["pois"])
	self.resultPoi = poi["pois"]
      return poi["pois"]
  
  def poiSuggestion(self, q, bbox=None ):
      if bbox: mm=1
      else: mm=0
      sug = self.fetchPoi( q, 25, 31370, mm, 1, bbox)
      #categories = [n["categories"][0]['value'] for n in sug ] 
      labels = [n["labels"][0]["value"] for n in sug ] 
      labels.sort()
      return labels
    
  def _getBounds(self, poiResult ):
      minX = 1.7976931348623157e+308
      maxX = -1.7976931348623157e+308
      minY = 1.7976931348623157e+308
      maxY = -1.7976931348623157e+308
      
      points =  [n['location']['points'][0]['Point']['coordinates'] for n in poiResult ]
      for xy in points:
	x, y = xy
	if x > maxX: maxX = x
	elif x < minX: minX = x
	if y > maxY: maxY = y
	elif y < minY: minY = y
	
      return [maxX,maxY, minX, minY]
	  


