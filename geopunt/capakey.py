# -*- coding: utf-8 -*-
from .geopuntError import geopuntError
import urllib.request, urllib.error, urllib.parse, json, sys, datetime

class capakey(object):
    def __init__(self, timeout=15, proxyUrl=""):
      self.timeout = timeout
      self.baseUrl = "http://geoservices.informatievlaanderen.be/capakey/api/v1" 

      if isinstance(proxyUrl, str)  and proxyUrl != "":
        if proxyUrl.startswith("https"): proxy = urllib.request.ProxyHandler({'https': proxyUrl})
        else: proxy = urllib.request.ProxyHandler({'http': proxyUrl})
      else:
         proxy = urllib.request.ProxyHandler()
      auth = urllib.request.HTTPBasicAuthHandler()
      self.opener = urllib.request.build_opener(proxy, auth, urllib.request.HTTPHandler)

    def getMunicipalities(self):
        url = self.baseUrl + "/municipality/"
        try:
            response = self.opener.open(url, timeout=self.timeout)
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            raise geopuntError( e.reason )
        except:
            raise geopuntError( sys.exc_info()[1] )
        else:
            municipalities = json.load(response)
            if municipalities: return municipalities["municipalities"]
            else : return []

    def getMunicipalitieInfo(self, niscode, srs=31370, geometryType="no" ):
        data = {}
        if srs in [31370, 4326, 3857]: data["srs"] = srs
        if geometryType in ["no", "full", "bbox"]: data["geometry"] = geometryType
        values = urllib.parse.urlencode(data)
        
        url = "{0}/municipality/{1}?{2}".format( self.baseUrl, niscode, values )
        
        try:
            response = self.opener.open(url, timeout=self.timeout)
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
           raise geopuntError( e.reason )
        except:
           raise geopuntError( sys.exc_info()[1] )
        else:
            municipality = json.load(response)
            return municipality

    def getDepartments(self, niscode):
        url = "{0}/municipality/{1}/department/".format( self.baseUrl, niscode)

        try:
            response = self.opener.open(url, timeout=self.timeout)
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            raise geopuntError( e.reason )
        except:
            raise geopuntError( sys.exc_info()[1] )
        else:
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
        try:
            response = self.opener.open(url, timeout=self.timeout)
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            raise geopuntError( e.reason )
        except:
            raise geopuntError( sys.exc_info()[1] )
        else:
            department = json.load(response)
            return department

    def getSections(self, niscode, departmentCode):
        url = "{0}/municipality/{1}/department/{2}/section/".format( self.baseUrl, niscode, departmentCode)

        try:
            response = self.opener.open(url, timeout=self.timeout)
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            raise geopuntError( e.reason )
        except:
            raise geopuntError( sys.exc_info()[1] )
        else:
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
        try:
            response = self.opener.open(url, timeout=self.timeout)
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            raise geopuntError( e.reason )
        except:
            raise geopuntError( sys.exc_info()[1] )
        else:
            sectie = json.load(response)
            return sectie 

    def getParcels(self, niscode, departmentCode, sectieCode):
        url = "{0}/municipality/{1}/department/{2}/section/{3}/parcel".format( 
                              self.baseUrl, niscode, departmentCode, sectieCode)
        try:
            response = self.opener.open(url, timeout=self.timeout)
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            raise geopuntError( e.reason )
        except:
            raise geopuntError( sys.exc_info()[1] )
        else:
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
        try:
            response = self.opener.open(url, timeout=self.timeout)
        except (urllib.error.HTTPError, urllib.error.URLError) as e:
            raise geopuntError( e.reason )
        except:
            raise geopuntError( sys.exc_info()[1] )
        else:
            parcel = json.load(response)
            return parcel
