# -*- coding: utf-8 -*-
from .geopuntError import geopuntError
import urllib.request, urllib.error, urllib.parse, json, sys, datetime, ssl

from qgis.PyQt.QtWidgets import QMessageBox 

class capakey(object):
    def __init__(self, timeout=15, proxyUrl=""):
      self.timeout = timeout
      self.baseUrl = "https://geoservices.informatievlaanderen.be/capakey/api/v1" 
      
      QMessageBox.warning( None , "capakey" , proxyUrl)
      
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
      
    def getMunicipalities(self):
        url = self.baseUrl + "/municipality/"
        response = urllib.request.urlopen(url, timeout=self.timeout, context=self.ctx)
        municipalities = json.load(response)
        if municipalities: return municipalities["municipalities"]
        else : return []

    def getMunicipalitieInfo(self, niscode, srs=31370, geometryType="no" ):
        data = {}
        if srs in [31370, 4326, 3857]: data["srs"] = srs
        if geometryType in ["no", "full", "bbox"]: data["geometry"] = geometryType
        values = urllib.parse.urlencode(data)
        
        url = "{0}/municipality/{1}?{2}".format( self.baseUrl, niscode, values )
        response = urllib.request.urlopen(url, timeout=self.timeout, context=self.ctx)
        municipality = json.load(response)
        return municipality

    def getDepartments(self, niscode):
        url = "{0}/municipality/{1}/department/".format( self.baseUrl, niscode)
        response = urllib.request.urlopen(url, timeout=self.timeout, context=self.ctx)
        departments = json.load(response)
        if departments: return departments['departments']
        else : return []             

    def getDepartmentInfo(self, niscode, departmentCode, srs=31370, geometryType="no" ):
        data = {}
        if srs in [31370, 4326, 3857]: data["srs"] = srs
        if geometryType in ["no", "full", "bbox"]: data["geometry"] = geometryType
        values = urllib.parse.urlencode(data)

        url = "{0}/municipality/{1}/department/{2}?{3}".format( 
                                    self.baseUrl, niscode, departmentCode, values)
        response = urllib.request.urlopen(url, timeout=self.timeout, context=self.ctx)
        department = json.load(response)
        return department

    def getSections(self, niscode, departmentCode):
        url = "{0}/municipality/{1}/department/{2}/section/".format( self.baseUrl, niscode, departmentCode)
        response = urllib.request.urlopen(url, timeout=self.timeout, context=self.ctx)
        secties = json.load(response)
        if secties: return secties['sections']
        else : return []       

    def getSectionInfo(self, niscode, departmentCode, sectieCode, srs=31370, geometryType="no" ):
        data = {}
        if srs in [31370, 4326, 3857]: data["srs"] = srs
        if geometryType in ["no", "full", "bbox"]: data["geometry"] = geometryType
        values = urllib.parse.urlencode(data)
      
        url = "{0}/municipality/{1}/department/{2}/section/{3}?{4}".format( 
                                  self.baseUrl, niscode, departmentCode, sectieCode, values)
        response = urllib.request.urlopen(url, timeout=self.timeout, context=self.ctx)
        sectie = json.load(response)
        return sectie 

    def getParcels(self, niscode, departmentCode, sectieCode):
        url = "{0}/municipality/{1}/department/{2}/section/{3}/parcel".format( 
                              self.baseUrl, niscode, departmentCode, sectieCode)
        response = urllib.request.urlopen(url, timeout=self.timeout, context=self.ctx)
        parcels = json.load(response)
        if parcels: return parcels['parcels']
        else : return []       
          
    def getParcel(self, niscode, departmentCode, sectieCode, perceelnummer, srs=31370, geometryType="no"):
        data = {}
        if srs in [31370, 4326, 3857]: data["srs"] = srs
        if geometryType in ["no", "full", "bbox"]: data["geometry"] = geometryType
        values = urllib.parse.urlencode(data)
  
        url = "{0}/municipality/{1}/department/{2}/section/{3}/parcel/{4}?{5}".format( 
                              self.baseUrl, niscode, departmentCode, sectieCode, perceelnummer, values)
        response = urllib.request.urlopen(url, timeout=self.timeout, context=self.ctx)
        parcel = json.load(response)
        return parcel
