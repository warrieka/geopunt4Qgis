# -*- coding: utf-8 -*-
import json, urllib.parse
from ..tools import getUrlData

class Poi(object):
  def __init__(self):
      self._poiUrl = "https://poi.api.geopunt.be/v1/core"
      self.resultCount = 0
      
      #REMARK: WGS coordinates as input!
      self.maxBounds = [1.17, 49.77, 7.29, 52.35]  
      self.resultBounds =  [1.17, 49.77, 7.29, 52.35]  
      self.PoiResult = []
      self.qry = ""
      self.srs = 31370
      self.maxModel=True
     
  def listPoiThemes(self):
      url = self._poiUrl + "/themes"
      poithemes = None
      response = getUrlData(url)
      poithemes = json.loads(response)
      themes = [(  n["value"], n["term"]) for n in poithemes["categories"] ] #only need value and  term
      return themes
     
  def listPoiCategories(self, themeid=""):
      if themeid:
        url = self._poiUrl + "/themes/" + themeid +"/categories"
      else:
        url = self._poiUrl + "/categories"

      response = getUrlData(url)
      poicategories = json.loads(response)
      categories = [(n["value"], n["term"]) for n in poicategories["categories"] ]
      return categories
    
  def listPoitypes(self, themeid="", categoriename=""):
      if themeid and categoriename:
        url = self._poiUrl + "/themes/" + themeid + "/categories/" + categoriename +"/poitypes"
      else:
        url = self._poiUrl + "/poitypes"
      response = getUrlData(url)
      poitypes = json.loads( response )
      types = [(  n["value"], n["term"]) for n in poitypes["categories"] ]
      return types
    
  def _createPoiUrl(self, q, c=30, srs=31370, maxModel=False, bbox=None, theme='', category='',
                                                              POItype='', region='', clustering=True):
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

        response = getUrlData(url)
        poi = json.loads( response )
      
        if updateResults:
            self.resultCount =  int( poi["labels"][0]["value"] )
            if bbox:
                self.resultBounds = bbox
            else:
                self.resultBounds = self._getBounds(poi["pois"])
            self.PoiResult = poi["pois"]
            self.qry = q
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
