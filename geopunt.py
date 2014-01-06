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
import urllib2, urllib, json, sys

class Adres:
  def __init__(self, timeout=15):
    self.timeout = timeout
    self._locUrl = "http://loc.api.geopunt.be/geolocation/Location?"
    self._sugUrl = "http://loc.api.geopunt.be/geolocation/Suggestion?"

  def _createLocationUrl(self, q, c=1):
      geopuntUrl = self._locUrl
      data = {}
      data["q"] = unicode(q).encode('utf-8')
      data["c"] = c
      values = urllib.urlencode(data)
      result = geopuntUrl + values
      return result

  def fetchLocation(self, q, c=1):
      url = self._createLocationUrl(q, c=1)
      try:
	    response = urllib2.urlopen(url, timeout=self.timeout)
      except (urllib2.HTTPError, urllib2.URLError) as e:
	    return str( e.reason )
      except:
	    return str( sys.exc_info()[1] )
      else:
	    LocationResult = json.load(response)
	    return LocationResult["LocationResult"]

  def _createSuggestionUrl(self, q, c=5):
      geopuntUrl = self._sugUrl
      data = {}
      data["q"] = unicode(q).encode('utf-8')
      data["c"] = c
      values = urllib.urlencode(data)
      result = geopuntUrl + values
      return result

  def fetchSuggestion(self, q, c=5):
      url = self._createSuggestionUrl(q,c)
      try:
	    response = urllib2.urlopen(url, timeout=self.timeout)
      except (urllib2.HTTPError, urllib2.URLError) as e:
	    return str( e.reason )
      except:
	    return  str( sys.exc_info()[1] )
      else:
	    suggestion = json.load(response)
	    return suggestion["SuggestionResult"]



class Poi:
  def __init__(self, timeout=15):
      self.timeout = timeout
      self._poiUrl = "http://poi.api.geopunt.be/core?"
      self.resultCount = 0
      
      #maxBounds srs 31370: x between 17736 and 297289, y between 23697 and 245375 
      #TODO: What if no Lambert coordinates as input???
      self.maxBounds = [17750,23720,297240,245340]  
      self.resultBounds = [17736,23697,297289,245375]
      self.PoiResult = []
      self.qeury = ""
      self.srs = 31370
      
  def _createPoiUrl(self , q, c=5, srs=31370 , maxModel=False, bbox=None ):
      poiUrl = self._poiUrl
      data = {}
      data["label"] = unicode(q).encode('utf-8')
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
    
  def fetchPoi(self, q,  c=5, srs=31370 , maxModel=True , updateResults=True, bbox=None ):
      url = self._createPoiUrl( q, c, srs, maxModel, bbox )
      try:
	  response = urllib2.urlopen(url, timeout=self.timeout)
      except urllib2.HTTPError as e:
	  return json.load(e)["Message"]
      except urllib2.URLError as e:
	  return str( e.reason )
      except:
	  return  str( sys.exc_info()[1] )
      else:
	poi = json.load(response)
	if updateResults:
	  self.resultCount =  int( poi["label"]["value"] )
	  if bbox:
	    self.resultBounds = bbox
	  else:
	    self.resultBounds = self._getBounds(poi["pois"])
	  self.PoiResult = poi["pois"]
	  self.qeury = q
	  self.srs = srs
	return poi["pois"]
  
  def poiSuggestion(self):
      if self.PoiResult:
	    sug = self.PoiResult
      else:
	    sug = self.fetchPoi( self.qeury, 25, 31370, 1, True, False)
      if sug.__class__ == str:
	    return sug
      else:
        labels = [(n["id"], n["categories"][0]['value'],n["labels"][0]["value"],
		     n['location']['address']["value"]) for n in sug ] 
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
	
      return [ minX, minY, maxX, maxY]
	  
def internet_on(timeout=15):
    try:
	response=urllib2.urlopen('http://loc.api.geopunt.be',timeout=timeout)
	return True
    except: 
	return False