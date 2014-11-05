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
import urllib2, urllib, json, sys, os.path, datetime

class Adres:
  def __init__(self, timeout=15, proxyUrl="", port="" ):
      self.timeout = timeout
      self._locUrl = "http://loc.api.geopunt.be/geolocation/Location?"
      self._sugUrl = "http://loc.api.geopunt.be/geolocation/Suggestion?"
      if (isinstance( proxyUrl, unicode ) or isinstance( proxyUrl, str )) & proxyUrl.startswith("http://"):
         netLoc = proxyUrl.strip() + ":" + port
         proxy = urllib2.ProxyHandler({'http': netLoc })
         self.opener = urllib2.build_opener(proxy)
      else:
         self.opener = None

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
          if self.opener: response = self.opener.open(url, timeout=self.timeout)
          else: response = urllib2.urlopen(url, timeout=self.timeout)
      except (urllib2.HTTPError, urllib2.URLError) as e:
            return str( e.reason )
      except:
            return  str( sys.exc_info()[1] )
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
        if self.opener: response = self.opener.open(url, timeout=self.timeout)
        else: response = urllib2.urlopen(url, timeout=self.timeout)
      except (urllib2.HTTPError, urllib2.URLError) as e:
        return str( e.reason )
      except:
          return  str( sys.exc_info()[1] )
      else:
          suggestion = json.load(response)
          return suggestion["SuggestionResult"]

class Poi:
  def __init__(self, timeout=15, proxyUrl="", port=""):
      self.timeout = timeout
      self._poiUrl = "http://poi.beta.geopunt.be/core"
      self.resultCount = 0
      
      if (isinstance(proxyUrl, unicode) or isinstance(proxyUrl, str)) & proxyUrl.startswith("http://"):
        netLoc = proxyUrl.strip() + ":" + port
        proxy = urllib2.ProxyHandler({'http': netLoc })
        self.opener = urllib2.build_opener(proxy)
      else:
        self.opener = None
      
      #TODO: What if no WGS coordinates as input???
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
         if self.opener: response = self.opener.open(url, timeout=self.timeout)
         else: response = urllib2.urlopen(url, timeout=self.timeout)
      except urllib2.HTTPError as e:
         return json.load(e)["Message"]
      except urllib2.URLError as e:
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
         if self.opener: response = self.opener.open(url, timeout=self.timeout)
         else: response = urllib2.urlopen(url, timeout=self.timeout)
      except urllib2.HTTPError as e:
         return json.load(e)["Message"]
      except urllib2.URLError as e:
         return str( e.reason )
      except:
         return  str( sys.exc_info()[1] )
      else:
         poicategories = json.load(response)
      categories = [(  n["value"], n["term"]) for n in poicategories["categories"] ]
      return categories
    
  def listPoitypes(self, themeid="", categoriename=""):
      "http://{base}/{path}/themes/{themeid}/categories/{categoriename}/POITypes"
      if themeid and categoriename:
        url = self._poiUrl + "/themes/" + themeid + "/categories/" + categoriename +"/poitypes"
      #elif categoriename  :
        #url = self._poiUrl + "/categories/" + categoriename +"/poitypes"
      else:
        url = self._poiUrl + "/poitypes"
        
      poitypes = None
      try:
         if self.opener: response = self.opener.open(url, timeout=self.timeout)
         else: response = urllib2.urlopen(url, timeout=self.timeout)
      except urllib2.HTTPError as e:
         return json.load(e)["Message"]
      except urllib2.URLError as e:
         return str( e.reason )
      except:
         return  str( sys.exc_info()[1] )
      else:
         poitypes = json.load(response)
      types = [(  n["value"], n["term"]) for n in poitypes["categories"] ]
      return types
    
  def _createPoiUrl(self, q, c=30, srs=31370, maxModel=False, bbox=None, theme='', category='', POItype='', region='' ):
      poiUrl = self._poiUrl
      data = {}
      if q : data["keyword"] = unicode(q).encode('utf-8')
      data["srsOut"] = srs
      data["srsIn"] = srs    #i am assuming srsIn wil always be same as srsOut
      data["maxcount"] = c
      data["theme"]  = theme
      data["category"]  = category
      data["POItype"]  = POItype
      data["region"] = str( region )
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
      result = poiUrl + "?" + values
      return result
    
  def fetchPoi(self, q,  c=30, srs=31370, maxModel=True , updateResults=True, bbox=None,  theme='', category='', POItype='', region='' ):
        url = self._createPoiUrl( q, c, srs, maxModel, bbox, theme, category, POItype, region)
        poi = None
        try:
          if self.opener: response = self.opener.open(url, timeout=self.timeout)
          else: response = urllib2.urlopen(url, timeout=self.timeout)
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
              straat = n['location']["address"]["street"]
              huisnr = n['location']["address"]["streetnumber"]
              postcode = n['location']["address"]["postalcode"]
              gemeente = n['location']["address"]["municipality"]
              if  'boxnumber' in n['location']["address"]:
                  busnr = n['location']["address"]["boxnumber"]
                  address = u"{} {} {}, {} {}".format(straat, huisnr, busnr, postcode, gemeente)
              else: 
                  address = u"{} {}, {} {}".format(straat, huisnr, postcode, gemeente)
                
          else: address = ''
          
          if self.maxModel: 
            Thema= n["categories"][0]["value"]
            Categorie = n["categories"][1]["value"]
            Type = n["categories"][2]["value"]
          else:
            Type = ["categories"][0]["value"]
            Thema, Categorie = "",""

          labels += [(recID, Thema, Categorie, Type , name , address )] 
        
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

class gipod:
  def __init__(self, timeout=15, proxyUrl="", port="" ):
      self.timeout = timeout
      self.baseUri = 'http://gipod.api.agiv.be/ws/v1/'
      
      if (isinstance(proxyUrl, unicode) or isinstance(proxyUrl, str)) & proxyUrl.startswith("http://"):
          netLoc = proxyUrl.strip() + ":" + port
          proxy = urllib2.ProxyHandler({'http': netLoc })
          self.opener = urllib2.build_opener(proxy)
      else:
          self.opener = None
  
  def getCity(self, q="" ):
      query = urllib.quote(q)
      url = self.baseUri + "referencedata/city/" + query 
      try:
        if self.opener: response = self.opener.open(url, timeout=self.timeout)
        else: response = urllib2.urlopen(url, timeout=self.timeout)
      except (urllib2.HTTPError, urllib2.URLError) as e:
        raise geopuntError(str( e.reason ))
      except:
        raise geopuntError( str( sys.exc_info()[1] ))
      else:
        city = json.load(response)
        return city

  def getProvince(self, q="" ):
      query = urllib.quote(q)
      url = self.baseUri + "referencedata/province/" + query
      try:
        if self.opener: response = self.opener.open(url, timeout=self.timeout)
        else: response = urllib2.urlopen(url, timeout=self.timeout)
      except (urllib2.HTTPError, urllib2.URLError) as e:
        raise geopuntError(str( e.reason ))
      except:
        raise geopuntError( str( sys.exc_info()[1] ))
      else:
        province = json.load(response)
        return province

  def getEventType(self, q="" ):
      query = urllib.quote(q)
      url = self.baseUri + "referencedata/eventtype/" + query
      try:
        if self.opener: response = self.opener.open(url, timeout=self.timeout)
        else: response = urllib2.urlopen(url, timeout=self.timeout)
      except (urllib2.HTTPError, urllib2.URLError) as e:
        raise geopuntError( str( e.reason ))
      except:
        raise geopuntError( str( sys.exc_info()[1] ))
      else:
        eventtype = json.load(response)
        return eventtype

  def getOwner(self, q=''):
      query = urllib.quote(q)
      url = self.baseUri + "referencedata/owner/" + query
      try:
        if self.opener: response = self.opener.open(url, timeout=self.timeout)
        else: response = urllib2.urlopen(url, timeout=self.timeout)
      except (urllib2.HTTPError, urllib2.URLError) as e:
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
      values = urllib.urlencode(data)
      result = endpoint + values
      return result

  def fetchWorkassignment(self,owner="", startdate=None, enddate=None, city="", province="", srs=31370, bbox=[], c=50, offset=0 ):
      url = self._createWorkassignmentUrl(owner, startdate, enddate, city, province, srs, bbox, c, offset )
      try:
        if self.opener: response = self.opener.open(url, timeout=self.timeout)
        else: response = urllib2.urlopen(url, timeout=self.timeout)
      except  (urllib2.HTTPError, urllib2.URLError) as e:
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
      values = urllib.urlencode(data)
      result = endpoint + values
      return result
  
  def fetchManifestation(self, owner="", eventtype="", startdate=None, enddate=None, city="", province="", srs=31370, bbox=[], c=50, offset=0 ):
      url = self._createManifestationUrl(owner, eventtype, startdate, enddate, city, province, srs, bbox, c, offset )
      try:
        if self.opener: response = self.opener.open(url, timeout=self.timeout)
        else: response = urllib2.urlopen(url, timeout=self.timeout)
      except  (urllib2.HTTPError, urllib2.URLError) as e:
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
  
class elevation:
  def __init__(self, timeout=15, proxyUrl="", port="" ):
      self.timeout = timeout
      self.baseUri = 'http://dhm.beta.agiv.be/api/elevation/v1/DHMVMIXED/request'
      
      if (isinstance(proxyUrl, unicode) or isinstance(proxyUrl, str)) & proxyUrl.startswith("http://"):
        netLoc = proxyUrl.strip() + ":" + port
        proxy = urllib2.ProxyHandler({'http': netLoc })
        self.opener = urllib2.build_opener(proxy)
      else:
        self.opener = None
      
  def _createElevationRequest(self, LineString, srs=31370, samples=50 ):
      geojson = {}
      geojson["SrsIn"] = srs
      geojson["SrsOut"] = srs 
      geojson["LineString"] = {"coordinates": LineString , "type":"LineString" }
      geojson["Samples"] = samples
      data =  json.dumps(geojson)
      req = urllib2.Request(self.baseUri , data, {'Content-Type': 'application/json'})
      return req
  
  def fetchElevaton(self, LineString, srs=31370, samples=50 ):
      "LineString= a serie of points in form [[4.2,51.27],[4.7,51.2],...], srs=ESPGcode, samples=nummer to return"
      req = self._createElevationRequest( LineString, srs, samples )
      try:
        if self.opener: response = self.opener.open(req, timeout= self.timeout)
        else: response = urllib2.urlopen(req, timeout= self.timeout)
      except  (urllib2.HTTPError, urllib2.URLError) as e:
        raise geopuntError( str( e.reason ))
      except:
        raise geopuntError( str( sys.exc_info()[1] ))
      else:
        elevationJson = json.load(response)
        return elevationJson

class perceel:
    def __init__(self, timeout=15, proxyUrl="", port="" ):
      self.timeout = timeout
      self.baseUrl = "http://ws.beta.agiv.be/capakey/api/v0"
      if (isinstance( proxyUrl, unicode ) or isinstance( proxyUrl, str )) & proxyUrl.startswith("http://"):
         netLoc = proxyUrl.strip() + ":" + port
         proxy = urllib2.ProxyHandler({'http': netLoc })
         self.opener = urllib2.build_opener(proxy)
      else:
         self.opener = None
    
    def getMunicipalities(self):
        url = self.baseUrl + "/municipality/"
        try:
          if self.opener: response = self.opener.open(url, timeout=self.timeout)
          else: response = urllib2.urlopen(url, timeout=self.timeout)
        except (urllib2.HTTPError, urllib2.URLError) as e:
            raise geopuntError( e.reason )
        except:
            raise geopuntError( sys.exc_info()[1] )
        else:
            municipalities = json.load(response)
            return municipalities["municipalities"]

    def getMunicipalitieInfo(self, niscode, srs=31370, geometryType="no" ):

        data = {}
        if srs in [31370, 4326, 3857]: data["srs"] = srs
        if geometryType in ["no", "full", "bbox"]: data["geometry"] = geometryType
        values = urllib.urlencode(data)
        
        url = "{0}/municipality/{1}?{2}".format( self.baseUrl, niscode, values )
        
        try:
          if self.opener: response = self.opener.open(url, timeout=self.timeout)
          else: response = urllib2.urlopen(url, timeout=self.timeout)
        except (urllib2.HTTPError, urllib2.URLError) as e:
           raise geopuntError( e.reason )
        except:
           raise geopuntError( sys.exc_info()[1] )
        else:
            municipality = json.load(response)
            return municipality

    def getDepartments(self, niscode):
        url = "{0}/municipality/{1}/department/".format( self.baseUrl, niscode)

        try:
          if self.opener: response = self.opener.open(url, timeout=self.timeout)
          else: response = urllib2.urlopen(url, timeout=self.timeout)
        except (urllib2.HTTPError, urllib2.URLError) as e:
            raise geopuntError( e.reason )
        except:
            raise geopuntError( sys.exc_info()[1] )
        else:
            departments = json.load(response)
            return departments['departments']

    def getDepartmentInfo(self, niscode, departmentCode, srs=31370, geometryType="no" ):
        
        data = {}
        if srs in [31370, 4326, 3857]: data["srs"] = srs
        if geometryType in ["no", "full", "bbox"]: data["geometry"] = geometryType
        values = urllib.urlencode(data)

        url = "{0}/municipality/{1}/department/{2}?{3}".format( 
                                    self.baseUrl, niscode, departmentCode, values)
        try:
          if self.opener: response = self.opener.open(url, timeout=self.timeout)
          else: response = urllib2.urlopen(url, timeout=self.timeout)
        except (urllib2.HTTPError, urllib2.URLError) as e:
            raise geopuntError( e.reason )
        except:
            raise geopuntError( sys.exc_info()[1] )
        else:
            department = json.load(response)
            return department

    def getSections(self, niscode, departmentCode):
        url = "{0}/municipality/{1}/department/{2}/section/".format( self.baseUrl, niscode, departmentCode)

        try:
          if self.opener: response = self.opener.open(url, timeout=self.timeout)
          else: response = urllib2.urlopen(url, timeout=self.timeout)
        except (urllib2.HTTPError, urllib2.URLError) as e:
            raise geopuntError( e.reason )
        except:
            raise geopuntError( sys.exc_info()[1] )
        else:
            secties = json.load(response)
            return secties['sections']

    def getSectionInfo(self, niscode, departmentCode, sectieCode, srs=31370, geometryType="no" ):
      
        data = {}
        if srs in [31370, 4326, 3857]: data["srs"] = srs
        if geometryType in ["no", "full", "bbox"]: data["geometry"] = geometryType
        values = urllib.urlencode(data)
      
        url = "{0}/municipality/{1}/department/{2}/section/{3}?{4}".format( 
                                  self.baseUrl, niscode, departmentCode, sectieCode, values)
        try:
          if self.opener: response = self.opener.open(url, timeout=self.timeout)
          else: response = urllib2.urlopen(url, timeout=self.timeout)
        except (urllib2.HTTPError, urllib2.URLError) as e:
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
          if self.opener: response = self.opener.open(url, timeout=self.timeout)
          else: response = urllib2.urlopen(url, timeout=self.timeout)
        except (urllib2.HTTPError, urllib2.URLError) as e:
            raise geopuntError( e.reason )
        except:
            raise geopuntError( sys.exc_info()[1] )
        else:
            parcels = json.load(response)
            return parcels['parcels']
          
    def getParcel(self, niscode, departmentCode, sectieCode, perceelnummer, srs=31370, geometryType="no"):
      
        data = {}
        if srs in [31370, 4326, 3857]: data["srs"] = srs
        if geometryType in ["no", "full", "bbox"]: data["geometry"] = geometryType
        values = urllib.urlencode(data)
  
        url = "{0}/municipality/{1}/department/{2}/section/{3}/parcel/{4}?{5}".format( 
                              self.baseUrl, niscode, departmentCode, sectieCode, perceelnummer, values)
        try:
          if self.opener: response = self.opener.open(url, timeout=self.timeout)
          else: response = urllib2.urlopen(url, timeout=self.timeout)
        except (urllib2.HTTPError, urllib2.URLError) as e:
            raise geopuntError( e.reason )
        except:
            raise geopuntError( sys.exc_info()[1] )
        else:
            parcel = json.load(response)
            return parcel
          

class geopuntError(Exception):
    def __init__(self, message):
      self.message = message
    def __str__(self):
      return repr(self.message)
      
      
def internet_on(timeout=15, proxyUrl="", port="" ):
    if (isinstance(proxyUrl, unicode) or isinstance(proxyUrl, str)) & proxyUrl.startswith("http://"):
        netLoc = proxyUrl.strip() + ":" + port
        proxy = urllib2.ProxyHandler({'http': netLoc })
        opener = urllib2.build_opener(proxy)
    else:
        opener = None
    try:
      if opener:
          opener.open( 'http://loc.api.geopunt.be', timeout=timeout ) 
      else:
          urllib2.urlopen('http://loc.api.geopunt.be',timeout=timeout)
      return True
    except: 
        return False