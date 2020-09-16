# -*- coding: utf-8 -*-
import urllib.parse, json, sys
import requests
from urllib.request import getproxies
import xml.etree.ElementTree as ET

class MDdata(object):
    def __init__(self, metadataXML): 
        self.start = int( metadataXML.attrib["from"] )
        self.to =    int( metadataXML.attrib["to"] )
        self.count = int( metadataXML[0].attrib["count"] )
        self.records = []
        
        mds = metadataXML.findall("metadata")
        for md in mds:
           record = {}
                      
           geonet =  md.find('{http://www.fao.org/geonetwork}info')
           if geonet.find('uuid').text != None: 
              record['uuid'] = geonet.find('uuid').text
           else: 
              continue  #records with no id are just wrong
              
           if (md.find('title') != None) and (md.find('title').text != None):
              record['title'] = md.find('title').text
           else: 
              record['title'] = ''
             
           if (md.find('abstract') != None) and (md.find('abstract').text != None):
              record['abstract'] = md.find('abstract').text
           else: 
              record['abstract'] = ''
           
           if (md.find('geoBox') != None) and (md.find('geoBox').text != None): 
              record['geoBox'] = md.find('geoBox').text  #[float(i) for i in md.find('geoBox').text.split('|') ]
           else: 
              record['geoBox'] = ""
           
           record['wms'] = self._findWMS( md )
           record['wfs'] = self._findWFS( md )
           record['download'] = self._findDownload( md )
           
           self.records.append(record)
           
    def _findWFS(self , node ):
        links =  "|".join( [ n.text for n in node.findall("link") ] )
        links = links.split('|') 
        for n in range(1, len( links )):
            if "OGC:WFS" in links[n].upper(): 
              if "http" in  links[n - 1]: #some wfs are store with relative path's, ignore those
                  return links[n - 1]
        return ""
      
    def _findWMS(self , node ):
        links =  "|".join( [ n.text for n in node.findall("link") ] )
        links = links.split('|') 
        for n in range(1, len( links )):
            if "OGC:WMS" in links[n].upper(): 
              if "http" in  links[n - 1]: #some wms are stored with relative path's, ignore those
                  return links[n - 1]
        return ""

    def _findDownload(self , node):
        links =  "|".join( [ n.text for n in node.findall("link") ] )
        links = links.split('|') 
        for n in range(1, len( links )):
            if "DOWNLOAD" in links[n].upper(): 
               if "http" in  links[n - 1]: #some files are stored with relative path's, ignore those
                  return links[n - 1]
        return ""


class MDReader(object):
    geoNetworkUrl = "https://geoservices.informatievlaanderen.be/zoekdienst/srv/dut/"

    def __init__(self, timeout=15, proxies=None):
        self.timeout = timeout
        self.proxy = proxies if proxies else getproxies()

        self.dataTypes = [["Dataset", "dataset"],["Datasetserie","series"],
                          ["Objectencatalogus","model"],["Service","service"]]
        self.inspireServiceTypes =  ["Discovery","Transformation","View","Other","Invoke"]
        self.inspireannex =  ["i","ii","iii"]

    def _createFindUrl(self, q='', start=1, to=20, themekey='', orgName='', dataType='', siteId='', inspiretheme='', inspireannex='', inspireServiceType=''):
        geopuntUrl = self.geoNetworkUrl + "/q?fast=index&sortBy=changeDate&"
        data = {}
        data["any"] = "*" + str(q) + "*"
        data["to"] = to
        data["from"] = start
        
        if themekey: 
            if " " in themekey and not " or " in themekey.lower():
                data["themekey"] = '"' +  themekey.lower()  + '"'
            else: 
                data["themekey"] = themekey.lower()
        if orgName  and not " or " in orgName.lower():
            if " " in orgName:
                data["orgName"] = '"' +  orgName.lower() + '"' 
            else: 
                data["orgName"] = orgName.lower()
                
        if dataType: data['type']= dataType
        if siteId: data['siteId']= siteId                
                
        if inspiretheme: 
            if " " in inspiretheme and not " or " in inspiretheme.lower():
                data["inspiretheme"] = '"' +  inspiretheme + '"' 
            else: 
                data["inspiretheme"] = inspiretheme            
        if inspireannex and (inspireannex.lower() in self.inspireannex ) : 
            data["inspireannex"] = inspireannex.lower()
        if inspireServiceType : 
            data["serviceType"] = inspireServiceType.lower() 

        values = urllib.parse.urlencode(data)
        result = geopuntUrl + values
        return result

    def list_GDI_theme(self, q=''):
        url = self.geoNetworkUrl + "/xml.search.keywords?pNewSearch=true&pTypeSearch=1&pThesauri=external.theme.GDI-Vlaanderen-trefwoorden&pKeyword=*" + str(q) +"*"
        response = requests.get(url, timeout=self.timeout, verify=False , proxies=self.proxy )
        r = ET.fromstring(response.content)
        themes = [ n.find("value").text for n in  r[0].findall('keyword') ]
        themes.sort()
        return themes
          
    def list_inspire_theme(self, q=''):
        url = self.geoNetworkUrl + "/xml.search.keywords?pNewSearch=true&pTypeSearch=1&pThesauri=external.theme.inspire-theme&pKeyword=*{}*".format(q)
        response = requests.get(url, timeout=self.timeout, verify=False , proxies=self.proxy )
        r = ET.fromstring(response.content)
        themes = [ n.find("value").text for n in  r[0].findall('keyword') ]
        themes.sort()
        return themes
    
    def list_suggestionKeyword(self, q=''):
        url = self.geoNetworkUrl + "/main.search.suggest?field=any" 
        if q: url= url + "&q=" + str(q) 
        response = requests.get(url, timeout=self.timeout, verify=False , proxies=self.proxy )
        return response.json()[1]

    def list_organisations(self, q=''):
        url = self.geoNetworkUrl + "/main.search.suggest?field=orgName" 
        if q: 
            url= url + "&q=" + str(q) 
        response = requests.get(url, timeout=self.timeout, verify=False, proxies=self.proxy )
        result = response.json()
        if len( result ) <= 2:
            organisations = result[1]
            organisations.sort()
            return organisations
        else:
            return []
               
    def list_bronnen(self):
        url = self.geoNetworkUrl + "/xml.info?type=sources"
        response = requests.get(url, timeout=self.timeout, verify=False, proxies=self.proxy )
        r = ET.fromstring(response.content)
        bronnen = [ ( n.find("uuid").text, n.find("name").text ) 
                    for n in  r[0].findall('source') ]
        bronnen.sort()
        return bronnen

    def search(self, q='', start=1, to=20, themekey='', orgName='', dataType='', siteId='', 
                                            inspiretheme='', inspireannex='', inspireServiceType='' ):
        url = self._createFindUrl( q, start, to, themekey, orgName, dataType, siteId, inspiretheme, 
                                                                        inspireannex, inspireServiceType)
        response = requests.get(url, timeout=self.timeout, verify=False, proxies=self.proxy )
        result = ET.fromstring(response.content)
        return  result

    def searchAll(self, q='', themekey='', orgName='', dataType='', siteId='', inspiretheme='', 
                                                                    inspireannex='', inspireServiceType=''):
        start= 1
        step= 1000       
        searchResult = self.search(q, start, step, themekey, orgName, dataType, siteId, inspiretheme, inspireannex, inspireServiceType)
        count = int( searchResult[0].attrib["count"] )
        start += step
        while (start) <= count:
           result = self.search(q, start, (start + step -1), themekey, orgName, dataType, siteId, inspiretheme, inspireannex, inspireServiceType)
           mds= result.findall("metadata")
           for md in mds: searchResult.append( md )
           start += step
        return searchResult


class metaError(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)

      
def getWmsLayerNames( url='', proxies=None):
    proxy = proxies if proxies else getproxies()
    if (not "request=GetCapabilities" in url.lower()) or (not "service=wms" in url.lower()):
      capability = url.split("?")[0] + "?request=GetCapabilities&version=1.3.0&service=wms"
    else:
      capability = url
        
    response = requests.get(capability, verify=False , proxies=proxy )
    result = ET.fromstring(response.content)

    layers =  result.findall( ".//{http://www.opengis.net/wms}Layer" ) + result.findall( ".//Layer" ) 
    layerNames=[]

    for lyr in layers:
      name= lyr.find("{http://www.opengis.net/wms}Name")
      if name is None: name= lyr.find("Name")
      title = lyr.find("{http://www.opengis.net/wms}Title")
      if title is None: title = lyr.find("Title")
      style = lyr.find("{http://www.opengis.net/wms}Style/{http://www.opengis.net/wms}Name")
      if ( name != None) and ( title != None ):
         if style == None: layerNames.append(( name.text, title.text, ''))
         else: layerNames.append(( name.text, title.text, style.text))

    return layerNames

def getWFSLayerNames( url, proxies=None):
    proxy = proxies if proxies else getproxies()
    if (not "request=GetCapabilities" in url.lower()) or (not "service=wfs" in url.lower()):
        capability = url.split("?")[0] + "?request=GetCapabilities&version=1.0.0&service=wfs"
    else: 
        capability = url
        
    response = requests.get(capability, verify=False , proxies=proxy )
    result = ET.fromstring(response.content)

    layers =  result.findall( ".//{http://www.opengis.net/wfs}FeatureType" )
    layerNames=[]

    for lyr in layers:
        name= lyr.find("{http://www.opengis.net/wfs}Name")
        title = lyr.find("{http://www.opengis.net/wfs}Title")
        srs = lyr.find("{http://www.opengis.net/wfs}SRS")
        if ( name != None) and ( title != None ):
            if srs == None: layerNames.append(( name.text, title.text, 'EPSG:31370'))
            else: layerNames.append(( name.text, title.text, srs.text))

    return layerNames

def getWMTSlayersNames( url, proxies=None):
    proxy = proxies if proxies else getproxies()
    if (not "request=getcapabilities" in url.lower()) or (not "service=wmts" in url.lower()):
        capability = url.split("?")[0] + "?service=WMTS&request=Getcapabilities"
    else:
        capability = url
            
    response = requests.get(capability, verify=False , proxies=proxy )
    result = ET.fromstring(response.content)

    content = result.find( "{http://www.opengis.net/wmts/1.0}Contents" )
    layers =  content.findall( "{http://www.opengis.net/wmts/1.0}Layer" )
    layerNames = []

    matrixSets = content.findall("{http://www.opengis.net/wmts/1.0}TileMatrixSet")

    for lyr in layers:
        name= lyr.find("{http://www.opengis.net/ows/1.1}Identifier")
        title = lyr.find("{http://www.opengis.net/ows/1.1}Title")
        matrix = lyr.find("{http://www.opengis.net/wmts/1.0}TileMatrixSetLink/{http://www.opengis.net/wmts/1.0}TileMatrixSet")
        format = lyr.find("{http://www.opengis.net/wmts/1.0}Format")

        srsList = [ n.find("{http://www.opengis.net/ows/1.1}SupportedCRS").text
                    for n in matrixSets if n.find("{http://www.opengis.net/ows/1.1}Identifier").text == matrix.text]

        if srsList: srs =  "EPSG:"+ srsList[0].split(':')[-1]
        else: srs = ""

        if ( name != None) and ( title != None ) and ( matrix != None ) and ( format != None ):
              layerNames.append(( name.text, title.text, matrix.text, format.text, srs ))

    return layerNames

def getWCSlayerNames( url, proxies=None ):
    proxy = proxies if proxies else getproxies()
    wcsNS = "http://www.opengis.net/wcs/1.1"

    if (not "request=getcapabilities" in url.lower()) or (not "service=wcs" in url.lower()):
      capability = url.split("?")[0] + "?request=GetCapabilities&version=1.1.0&service=wcs"
    else:
      capability = url

    response = requests.get(capability, verify=False , proxies=proxy ).content

    if 'xmlns:wcs="http://www.opengis.net/wcs/1.1.1"' in response:
        wcsNS = "http://www.opengis.net/wcs/1.1.1"

    result = ET.fromstring(response)
    content = result.find( "{%s}Contents" % wcsNS)
    layers =  content.findall( "{%s}CoverageSummary" % wcsNS)
    layerNames = []

    for lyr in layers:
       Identifier= lyr.find("{%s}Identifier" % wcsNS)
       title = lyr.find("{http://www.opengis.net/ows/1.1}Title")

       DescribeCoverage = url.split("?")[0] + "?request=DescribeCoverage&version=1.1.0&service=wcs&Identifiers=" + Identifier.text
       response = requests.get(DescribeCoverage, verify=False , proxies=proxy )
       resultDC = ET.fromstring(response.content)
       CoverageDescription = resultDC.find( "{%s}CoverageDescription" % wcsNS)
       Identifier = CoverageDescription.find("{%s}Identifier" % wcsNS)
       formats =  CoverageDescription.findall( "{%s}SupportedFormat" % wcsNS)
       if [n.text for n in formats if 'tiff' in n.text.lower()] :
          format = [n.text for n in formats if 'tiff' in n.text.lower()][0]
       elif formats: format = formats[0].text.split(";")[0]
       else: format = "image/tiff"

       if ( Identifier != None) and (title != None):
            layerNames.append(( Identifier.text, title.text, format ))

    return layerNames

def makeWFSuri( url, name='', srsname="EPSG:31370", version='1.0.0', bbox=None ):
    params = {  'SERVICE': 'WFS',
                'VERSION': version ,
                'REQUEST': 'GetFeature',
                'TYPENAME': name,
                'SRSNAME': srsname }
    if bbox: params['BBOX'] = ",".join([str(s) for s in bbox])

    uri = url.split('?')[0] + '?' + urllib.parse.unquote( urllib.parse.urlencode(params) )

    return uri

def makeWMTSuri( url, layer, tileMatrixSet, srsname="EPSG:3857", styles='', format='image/png' ):
    params = {  'tileMatrixSet': tileMatrixSet,
                'styles': styles,
                'format': format ,
                'layers': layer,
                'crs': srsname,
                'url': url.split('?')[0]  + '?service=WMTS'}

    uri = urllib.parse.unquote( urllib.parse.urlencode(params)  )
    return uri

def makeWCSuri( url, layer,srsname="EPSG:31370", format="GeoTIFF" ):
    """ cache=PreferNetwork
        crs=EPSG:28992
        format=GeoTIFF
        identifier=dank:altr_a04_gi_bodemC
        url=http://geodata.rivm.nl/geoserver/wcs?version%3D1.0.0%26"""
    params = {  'cache': 'PreferNetwork',
                'format': format ,
                'identifier': layer,
                'crs': srsname,
                'url': url.split('?')[0]  } #+ '?version%3D1.0.0%26'

    uri = urllib.parse.unquote( urllib.parse.urlencode(params)  )
    return uri
