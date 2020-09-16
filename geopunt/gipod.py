# -*- coding: utf-8 -*-
import json, sys, datetime, urllib.parse
from urllib.request import getproxies
import requests

class gipod(object):
  baseUri = 'https://api.gipod.vlaanderen.be/ws/v1/'

  def __init__(self, timeout=15,  proxies=None):
      self.timeout = timeout
      self.proxy = proxies if proxies else getproxies()
  
  def getCity(self, q="" ):
      query = urllib.parse.quote(q)
      url = self.baseUri + "referencedata/city/" + query 
      response = requests.get(url, timeout=self.timeout , verify=False , proxies=self.proxy )
      return response.json()

  def getProvince(self, q="" ):
      query = urllib.parse.quote(q)
      url = self.baseUri + "referencedata/province/" + query
      response = requests.get(url, timeout=self.timeout , verify=False , proxies=self.proxy )
      return response.json()

  def getEventType(self, q="" ):
      query = urllib.parse.quote(q)
      url = self.baseUri + "referencedata/eventtype/" + query
      response = requests.get(url, timeout=self.timeout , verify=False , proxies=self.proxy )
      return response.json()

  def getOwner(self, q=''):
      query = urllib.parse.quote(q)
      url = self.baseUri + "referencedata/owner/" + query
      response = requests.get(url, timeout=self.timeout , verify=False , proxies=self.proxy )
      return response.json()

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
      response = requests.get(url, timeout=self.timeout , verify=False , proxies=self.proxy )
      return response.json()
      
  def allManifestations(self, owner="", startdate=None, enddate=None, city="", province="", srs=31370, bbox=[]):
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
      response = requests.get(url, timeout=self.timeout , verify=False , proxies=self.proxy )
      return response.json()
        
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
  
