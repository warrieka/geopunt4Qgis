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
from future import standard_library
standard_library.install_aliases()
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
      data["q"] = str(q).encode('utf-8')
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
      data["q"] = str(q).encode('utf-8')
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

class Poi(object):
  def __init__(self, timeout=15, proxyUrl=""):
      self.timeout = timeout
      self._poiUrl = "http://poi.api.geopunt.be/v1/core"
      self.resultCount = 0
      
      if isinstance(proxyUrl,str) and proxyUrl != "":
         proxy = urllib.request.ProxyHandler({'http': proxyUrl })
      else:
         proxy = urllib.request.ProxyHandler() 
      auth= urllib.request.HTTPBasicAuthHandler()
      self.opener = urllib.request.build_opener(proxy, auth, urllib.request.HTTPHandler)
      
      #REMARK: WGS coordinates as input!
      self.maxBounds = [1.17, 49.77, 7.29, 52.35]  
      self.resultBounds =  [1.17, 49.77, 7.29, 52.35]  
      self.PoiResult = []
      self.qeury = ""
      self.srs = 31370
      self.maxModel=True
     
  def listPoiThemes(self):
      url = self._poiUrl + "/themes"
      poithemes = None
      try:
          response = self.opener.open(url, timeout=self.timeout)
      except urllib.error.HTTPError as e:
         return json.load(e)["Message"]
      except urllib.error.URLError as e:
         return str( e.reason )
      except:
         return  str( sys.exc_info()[1] )
      else:
         poithemes = json.load(response)
      themes = [(  n["value"], n["term"]) for n in poithemes["categories"] ] #only need value and  term
      return themes
     
  def listPoiCategories(self, themeid=""):
      "http://{base}/{path}/themes/{themeid}/categories"
      if themeid:
        url = self._poiUrl + "/themes/" + themeid +"/categories"
      else:
        url = self._poiUrl + "/categories"
      
      poicategories = None
      try:
         response = self.opener.open(url, timeout=self.timeout)
      except urllib.error.HTTPError as e:
         return json.load(e)["Message"]
      except urllib.error.URLError as e:
         return str( e.reason )
      except:
         return  str( sys.exc_info()[1] )
      else:
         poicategories = json.load(response)
      categories = [(  n["value"], n["term"]) for n in poicategories["categories"] ]
      return categories
    
  def listPoitypes(self, themeid="", categoriename=""):
      if themeid and categoriename:
        url = self._poiUrl + "/themes/" + themeid + "/categories/" + categoriename +"/poitypes"
      else:
        url = self._poiUrl + "/poitypes"

      try:
         response = self.opener.open(url, timeout=self.timeout)
      except urllib.error.HTTPError as e:
         return json.load(e)["Message"]
      except urllib.error.URLError as e:
         return str( e.reason )
      except:
         return  str( sys.exc_info()[1] )
      else:
         poitypes = json.load(response)
      types = [(  n["value"], n["term"]) for n in poitypes["categories"] ]
      return types
    
  def _createPoiUrl(self, q, c=30, srs=31370, maxModel=False, bbox=None, theme='', category='', POItype='', region='', clustering=True):
      poiUrl = self._poiUrl
      data = {}
      if q : data["keyword"] = str(q).encode('utf-8')
      data["srsOut"] = srs
      data["srsIn"] = srs    
      data["maxcount"] = c
      data["theme"]  = theme
      data["category"]  = category
      data["POItype"]  = POItype
      data["region"] = str( region )
      
      if (not maxModel) and clustering:
         data["Clustering"] = "true"
      else: data["Clustering"] = "false"
      
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
    
      values = urllib.parse.urlencode(data)
      result = poiUrl + "?" + values
      return result
    
  def fetchPoi(self, q,  c=30, srs=31370, maxModel=True , updateResults=True,
               bbox=None,  theme='', category='', POItype='', region='', clustering=True):
        url = self._createPoiUrl( q, c, srs, maxModel, bbox, theme, category, POItype, region, clustering)

        try:
           response = self.opener.open(url, timeout=self.timeout)
        except urllib.error.HTTPError as e:
           error = e.read()
           errorjs =  json.loads(error)
           if "Message" in list(errorjs.keys()):
              return error["Message"]
           else: 
              return error
        except urllib.error.URLError as e:
           return str( e.reason )
        except:
           return  str( sys.exc_info()[1] )
        else:
          poi = json.load(response)
      
          if updateResults:
              self.resultCount =  int( poi["labels"][0]["value"] )
              if bbox:
                  self.resultBounds = bbox
              else:
                  self.resultBounds = self._getBounds(poi["pois"])
              self.PoiResult = poi["pois"]
              self.qeury = q
              self.srs = srs
              self.maxModel = maxModel           
          return poi
  
  def poiSuggestion(self):
      if self.PoiResult: 
        sug = self.PoiResult
      else: 
        return []
      
      if type( sug ) is str:
        return sug
      else:
        labels = []
        for n in sug:
          recID= n["id"]
          name= n["labels"][0]["value"]
          if "address" in n['location']: 
              if 'street' in n['location']["address"]:
                straat = n['location']["address"]["street"]
              else: 
                straat = ''
              if 'streetnumber' in n['location']["address"]:
                huisnr = n['location']["address"]["streetnumber"]
              else: 
                huisnr = ''
              if  'boxnumber' in n['location']["address"]:
                busnr = n['location']["address"]["boxnumber"]
              else: 
                busnr = ''
              if 'postalcode' in n['location']["address"]:
                postcode = n['location']["address"]["postalcode"]
              else: postcode = ''
              if 'municipality' in n['location']["address"]:
                gemeente = n['location']["address"]["municipality"]
              else: 
                gemeente = ''
                
          else: 
            straat, huisnr, busnr, postcode, gemeente = '', '', '', '', ''
          
          if self.maxModel: 
            Thema= n["categories"][0]["value"]
            Categorie = n["categories"][1]["value"]
            Type = n["categories"][2]["value"]
          else:
            Type = ["categories"][0]["value"]
            Thema, Categorie = "",""

          labels += [(recID, Thema, Categorie, Type , name , straat, huisnr, busnr, postcode, gemeente )] 
        
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
  
class elevation(object):
  def __init__(self, timeout=15, proxyUrl=""):
      self.timeout = timeout
      self.baseUri = 'http://dhm.agiv.be/api/elevation/v1/DHMVMIXED/request'
      
      if isinstance(proxyUrl, str) and proxyUrl != "":
          proxy = urllib.request.ProxyHandler({'http': proxyUrl})
      else:
          proxy = urllib.request.ProxyHandler()
      auth = urllib.request.HTTPBasicAuthHandler()   
      self.opener = urllib.request.build_opener(proxy, auth, urllib.request.HTTPHandler)

  def _createElevationRequest(self, LineString, srs=31370, samples=50 ):
      geojson = {}
      geojson["SrsIn"] = srs
      geojson["SrsOut"] = srs 
      geojson["LineString"] = {"coordinates": LineString , "type":"LineString" }
      geojson["Samples"] = samples
      data =  json.dumps(geojson)
      req = urllib.request.Request(self.baseUri , data.encode('utf-8'), {'Content-Type': 'application/json'})
      return req
  
  def fetchElevaton(self, LineString, srs=31370, samples=50 ):
      "LineString= a serie of points in form [[4.2,51.27],[4.7,51.2],...], srs=ESPGcode, samples=nummer to return"
      req = self._createElevationRequest( LineString, srs, samples )
      try:
         response = self.opener.open(req, timeout= self.timeout)
      except  (urllib.error.HTTPError, urllib.error.URLError) as e:
         raise geopuntError( str( e.reason ))
      except:
         raise geopuntError( str( sys.exc_info()[1] ))
      else:
         elevationJson = json.load(response)
         return elevationJson

class capakey(object):
    def __init__(self, timeout=15, proxyUrl=""):
      self.timeout = timeout
      self.baseUrl = "http://geoservices.informatievlaanderen.be/capakey/api/v1" 

      if isinstance(proxyUrl, str)  and proxyUrl != "":
         proxy = urllib.request.ProxyHandler({'http': proxyUrl })
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

class perc(object):
   def __init__(self, timeout=15, proxyUrl=""):
      self.timeout = timeout

      self._esriCapaServer= "http://geoservices.informatievlaanderen.be/ArcGIS/rest/services/adp/MapServer/0/query?" 
      self._locUrl = "http://perc.geopunt.be/Perceel/Location?"
      self._sugUrl = "http://perc.geopunt.be/Perceel/Suggestion?"
      if (isinstance(proxyUrl, str) or isinstance(proxyUrl, str)) and proxyUrl != "":
         proxy = urllib.request.ProxyHandler({'http': proxyUrl })
      else:
         proxy = urllib.request.ProxyHandler()
      auth = urllib.request.HTTPBasicAuthHandler()
      self.opener = urllib.request.build_opener(proxy, auth, urllib.request.HTTPHandler)

   def _createLocationUrl(self, q, c=1):
      geopuntUrl = self._locUrl
      data = {}
      data["q"] = str(q).encode('utf-8')
      data["c"] = c
      values = urllib.parse.urlencode(data)
      result = geopuntUrl + values 
      return result

   def fetchLocation(self, q, c=1):
      url = self._createLocationUrl(q, c=1)
      try:
          response = self.opener.open(url, timeout=self.timeout)
      except (urllib.error.HTTPError, urllib.error.URLError) as e:
          return str( e.reason )
      except:
          return  str( sys.exc_info()[1] )
      else:
          LocationResult = json.load(response)
          return LocationResult["LocationResult"]

   def _createSuggestionUrl(self, q, c=5):
      geopuntUrl = self._sugUrl
      data = {}
      data["q"] = str(q).encode('utf-8')
      data["c"] = c
      values = urllib.parse.urlencode(data)
      result = geopuntUrl + values
      return result

   def fetchSuggestion(self, q, c=5):
      url = self._createSuggestionUrl(q,c)
      try:
         response = self.opener.open(url, timeout=self.timeout)
      except (urllib.error.HTTPError, urllib.error.URLError) as e:
         return str( e.reason )
      except:
         return  str( sys.exc_info()[1] )
      else:
         suggestion = json.load(response)
         return suggestion["SuggestionResult"]

   def getPercGeom(self, capakey, srs=31370):
      capaUrl = self._esriCapaServer
      data = {"f": "json"}
      data["where"] = str( "CAPAKEY LIKE '{}'".format( capakey ) ).encode('utf-8')
      data["outSR"] = srs
      values = urllib.parse.urlencode(data)
      url = capaUrl + values 

      try:
            response = self.opener.open(url, timeout=self.timeout)
      except (urllib.error.HTTPError, urllib.error.URLError) as e:
            return str( e.reason )
      except:
            return  str( sys.exc_info()[1] )
      else:
            LocationResult = json.load(response)
            return LocationResult["features"]

class geopuntError(Exception):
    def __init__(self, message):
      self.message = message
    def __str__(self):
      return repr(self.message)

def internet_on( proxyUrl="", timeout=15 ):
    opener = None
    if isinstance(proxyUrl, str) and proxyUrl != "":
        proxy =  urllib.request.ProxyHandler({'http': proxyUrl })
        auth =   urllib.request.HTTPBasicAuthHandler()
        opener = urllib.request.build_opener(proxy, auth, urllib.request.HTTPHandler)
    else: 
       proxy =  urllib.request.ProxyHandler()
       auth =   urllib.request.HTTPBasicAuthHandler()
       opener = urllib.request.build_opener(proxy, auth, urllib.request.HTTPHandler)

    if opener:
        opener.open( 'http://loc.api.geopunt.be/v2/Suggestion', timeout=timeout )
        return True
    else:
        urllib.request.urlopen('http://loc.api.geopunt.be/v2/Suggestion', timeout=timeout)
        return True