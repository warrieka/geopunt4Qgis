# -*- coding: utf-8 -*-
import json, sys, datetime
from urllib.request import getproxies
import requests

class capakey(object):
    baseUrl = "https://geoservices.informatievlaanderen.be/capakey/api/v2" 

    def __init__(self, timeout=15, proxies=None):
        self.timeout = timeout
        self.proxy = proxies if proxies else getproxies()
      
    def getMunicipalities(self):
        url = "{0}/municipality/".format(self.baseUrl)
        response = requests.get(url, timeout=self.timeout , 
                            verify=False, proxies=self.proxy )
        municipalities = response.json()
        if municipalities: return municipalities["municipalities"]
        else : return []

    def getMunicipalitieInfo(self, niscode, srs=31370, geometryType="no" ):
        'srs is espg-code: 31370, 4326, 3857 and geometryType must be: "no", "full", "bbox"'
        data = {}
        if srs in [31370, 4326, 3857]: data["srs"] = srs
        if geometryType in ["no", "full", "bbox"]: data["geometry"] = geometryType
        
        url = "{0}/municipality/{1}".format( self.baseUrl, niscode )
        response = requests.get(url, params=data, timeout=self.timeout , 
                                         verify=False, proxies=self.proxy )
        municipality = response.json()
        return municipality

    def getDepartments(self, niscode):
        url = "{0}/municipality/{1}/department/".format( self.baseUrl, niscode)
        response = requests.get(url, timeout=self.timeout , 
                            verify=False, proxies=self.proxy )
        departments = response.json()
        if departments: return departments['departments']
        else : return []             

    def getDepartmentInfo(self, niscode, departmentCode, srs=31370, geometryType="no" ):
        'srs is espg-code: 31370, 4326, 3857 and geometryType must be: "no", "full", "bbox"'
        data = {}
        if srs in [31370, 4326, 3857]: data["srs"] = srs
        if geometryType in ["no", "full", "bbox"]: data["geometry"] = geometryType

        url = "{0}/municipality/{1}/department/{2}".format(self.baseUrl, niscode, departmentCode)
        response = requests.get(url, params=data, timeout=self.timeout , 
                            verify=False, proxies=self.proxy )
        department = response.json()
        return department

    def getSections(self, niscode, departmentCode):
        url = "{0}/municipality/{1}/department/{2}/section/".format( self.baseUrl, niscode, departmentCode)
        response = requests.get(url, timeout=self.timeout , 
                            verify=False, proxies=self.proxy )
        secties = response.json()
        if secties: return secties['sections']
        else : return []       

    def getSectionInfo(self, niscode, departmentCode, sectieCode, srs=31370, geometryType="no" ):
        'srs is espg-code: 31370, 4326, 3857 and geometryType must be: "no", "full", "bbox"'
        data = {}
        if srs in [31370, 4326, 3857]: data["srs"] = srs
        if geometryType in ["no", "full", "bbox"]: data["geometry"] = geometryType
      
        url = "{0}/municipality/{1}/department/{2}/section/{3}".format( 
                                  self.baseUrl, niscode, departmentCode, sectieCode)
        response = requests.get(url, params=data, timeout=self.timeout , 
                            verify=False, proxies=self.proxy )
        sectie = response.json()
        return sectie 

    def getParcels(self, niscode, departmentCode, sectieCode):
        url = "{0}/municipality/{1}/department/{2}/section/{3}/parcel".format( 
                              self.baseUrl, niscode, departmentCode, sectieCode)
        response = requests.get(url, timeout=self.timeout , 
                                  verify=False, proxies=self.proxy )
        parcels = response.json()
        if parcels: return parcels['parcels']
        else : return []       
          
    def getParcel(self, niscode, departmentCode, sectieCode, perceelnummer, srs=31370, geometryType="no"):
        'srs is espg-code: 31370, 4326, 3857 and geometryType must be: "no", "full", "bbox"'
        data = {}
        if srs in [31370, 4326, 3857]: data["srs"] = srs
        if geometryType in ["no", "full", "bbox"]: data["geometry"] = geometryType
  
        url = "{0}/municipality/{1}/department/{2}/section/{3}/parcel/{4}".format( 
                              self.baseUrl, niscode, departmentCode, sectieCode, perceelnummer)
        response = requests.get(url, params=data, timeout=self.timeout ,
                                         verify=False, proxies=self.proxy )
        parcel = response.json()
        return parcel
