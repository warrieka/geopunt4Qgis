# -*- coding: utf-8 -*-
from .geopuntError import geopuntError
import urllib.request, urllib.error, urllib.parse, json, sys, datetime

class gipod(object):
  def __init__(self, timeout=15, proxyUrl=""):
      self.timeout = timeout
      self.baseUri = 'http://api.gipod.vlaanderen.be/ws/v1/'
      
      if (isinstance(proxyUrl, str) or isinstance(proxyUrl, str)) and proxyUrl != "":
         proxy = urllib.request.ProxyHandler({'http': proxyUrl })
      else:
         proxy = urllib.request.ProxyHandler()
      auth = urllib.request.HTTPBasicAuthHandler() 
      self.opener =  urllib.request.build_opener(proxy, auth, urllib.request.HTTPHandler)
  
  def getCity(self, q="" ):
      query = urllib.parse.quote(q)
      url = self.baseUri + "referencedata/city/" + query 
      try:
         response = self.opener.open(url, timeout=self.timeout)
      except (urllib.error.HTTPError, urllib.error.URLError) as e:
         raise geopuntError(str( e.reason ))
      except:
         raise geopuntError( str( sys.exc_info()[1] ))
      else:
         city = json.load(response)
         return city

  def getProvince(self, q="" ):
      query = urllib.parse.quote(q)
      url = self.baseUri + "referencedata/province/" + query
      try:
         response = self.opener.open(url, timeout=self.timeout)
      except (urllib.error.HTTPError, urllib.error.URLError) as e:
         raise geopuntError(str( e.reason ))
      except:
         raise geopuntError( str( sys.exc_info()[1] ))
      else:
         province = json.load(response)
         return province

  def getEventType(self, q="" ):
      query = urllib.parse.quote(q)
      url = self.baseUri + "referencedata/eventtype/" + query
      try:
         response = self.opener.open(url, timeout=self.timeout)
      except (urllib.error.HTTPError, urllib.error.URLError) as e:
         raise geopuntError( str( e.reason ))
      except:
         raise geopuntError( str( sys.exc_info()[1] ))
      else:
         eventtype = json.load(response)
         return eventtype

  def getOwner(self, q=''):
      query = urllib.parse.quote(q)
      url = self.baseUri + "referencedata/owner/" + query
      try:
         response = self.opener.open(url, timeout=self.timeout)
      except (urllib.error.HTTPError, urllib.error.URLError) as e:
         raise geopuntError( str( e.reason ))
      except:
         raise geopuntError( str( sys.exc_info()[1] )) 
      else:
         owner = json.load(response)
         return owner

  def _createWorkassignmentUrl(self, owner="", startdate=None, enddate=None, city="", province="", srs=31370, bbox=[], c=50, offset=0 ):
      "startdate and enddate are datetime.date\n bbox is [xmin,ymin,xmax,ymax]"
      endpoint = self.baseUri + 'workassignment?'
      data = {}
      data['limit'] = c
      if offset:
         data["offset"] = offset
      if owner:
         data['owner'] = owner
      if startdate and isinstance(startdate, datetime.date): 
         data["startdate"] = startdate.__str__()
      if enddate and isinstance(enddate, datetime.date): 
         data["enddate"] = enddate.__str__()
      if city:
         data['city'] = city
      if province:
         data['province'] = province
      if srs in [31370,4326,3857]:
         data['CRS'] = srs
      if bbox and isinstance(bbox,(list,tuple)) and len(bbox) == 4:
         xmin,ymin,xmax,ymax = bbox
         xymin = str(xmin) +','+ str(ymin)
         xymax = str(xmax) +','+ str(ymax)
         data["bbox"] = '|'.join([xymin,xymax])
      values = urllib.parse.urlencode(data)
      result = endpoint + values
      return result

  def fetchWorkassignment(self,owner="", startdate=None, enddate=None, city="", province="", srs=31370, bbox=[], c=50, offset=0 ):
      url = self._createWorkassignmentUrl(owner, startdate, enddate, city, province, srs, bbox, c, offset )
      try:
         response = self.opener.open(url, timeout=self.timeout)
      except  (urllib.error.HTTPError, urllib.error.URLError) as e:
         raise geopuntError( str( e.reason ))
      except:
         raise geopuntError( str( sys.exc_info()[1] ))
      else:
         workassignment = json.load(response)
         return workassignment
      
  def allWorkassignments(self, owner="", startdate=None, enddate=None, city="", province="", srs=31370, bbox=[]):
      counter = 0
      wAs = self.fetchWorkassignment(owner, startdate, enddate, city, province, srs, bbox, 100, counter )
      wAlen = len(wAs)
      while wAlen == 100:
        counter += 100
        wA = self.fetchWorkassignment(owner, startdate, enddate, city, province, srs, bbox, 100, counter )
        wAs += wA
        wAlen = len(wA)
      return wAs

  def _createManifestationUrl(self, owner="", eventtype="", startdate=None, enddate=None, city="", province="", srs=31370, bbox=[], c=50, offset=0 ):
      endpoint = self.baseUri + "manifestation?"
      data = {}
      data['limit'] = c
      if offset:
        data["offset"] = offset
      if owner:
        data['owner'] = owner
      if eventtype:
        data['eventtype'] = eventtype
      if startdate and isinstance(startdate, datetime.date): 
        data["startdate"] = startdate.__str__()
      if enddate and isinstance(enddate, datetime.date): 
        data["enddate"] = enddate.__str__()
      if city:
        data['city'] = city
      if province:
        data['province'] = province
      if srs in [31370,4326,3857]:
        data['CRS'] = srs
      if bbox and isinstance(bbox,(list,tuple)) and len(bbox) == 4:
        xmin,ymin,xmax,ymax = bbox
        xymin = str(xmin) +','+ str(ymin)
        xymax = str(xmax) +','+ str(ymax)
        data["bbox"] = '|'.join([xymin,xymax])
      values = urllib.parse.urlencode(data)
      result = endpoint + values
      return result
  
  def fetchManifestation(self, owner="", eventtype="", startdate=None, enddate=None, city="", province="", srs=31370, bbox=[], c=50, offset=0 ):
      url = self._createManifestationUrl(owner, eventtype, startdate, enddate, city, province, srs, bbox, c, offset )
      try:
        response = self.opener.open(url, timeout=self.timeout)
      except  (urllib.error.HTTPError, urllib.error.URLError) as e:
        raise geopuntError( str( e.reason ))
      except:
        raise geopuntError( str( sys.exc_info()[1] ))
      else:
        manifestation = json.load(response)
        return manifestation
        
  def allManifestations(self, owner="", eventtype="", startdate=None, enddate=None, city="", province="", srs=31370, bbox=[]):
      counter = 0
      mAs = self.fetchManifestation(owner, eventtype, startdate, enddate, city, province, srs, bbox, 100, counter)
      mAlen = len(mAs)
      while mAlen == 100:
          counter += 100
          mA = self.fetchManifestation(owner, eventtype, startdate, enddate, city, province, srs, bbox, 100, counter)
          mAs += mA
          mAlen = len(mA)
      return mAs
  