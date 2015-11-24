# -*- coding: utf-8 -*-
import urllib2, urllib, json, sys
import xml.etree.ElementTree as ET

class MDdata:
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


class MDReader:
    def __init__(self, timeout=15, proxyUrl="" ):
        self.timeout = timeout
        self.geoNetworkUrl = "http://geoservices.beta.informatievlaanderen.be/zoekdienst/srv/dut/"

        self.dataTypes = [["Dataset", "dataset"],["Datasetserie","series"],
                          ["Objectencatalogus","model"],["Service","service"]]
        self.inspireServiceTypes =  ["Discovery","Transformation","View","Other","Invoke"]
        self.inspireannex =  ["i","ii","iii"]

        if (isinstance(proxyUrl, unicode) or isinstance(proxyUrl, str)) and proxyUrl:
            proxy = urllib2.ProxyHandler({'http': proxyUrl ,'https': proxyUrl })
            self.opener = urllib2.build_opener(proxy)
        else:
            self.opener = None

    def _createFindUrl(self, q="", start=1, to=20, themekey='', orgName='', dataType='', siteId='', inspiretheme='', inspireannex='', inspireServiceType=''):
        geopuntUrl = self.geoNetworkUrl + "/q?fast=index&sortBy=changeDate&"
        data = {}
        data["any"] = "*" + unicode(q).encode('utf-8') + "*"
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

        values = urllib.urlencode(data)
        result = geopuntUrl + values
        return result

    def list_GDI_theme(self, q=''):
        url = self.geoNetworkUrl + "/xml.search.keywords?pNewSearch=true&pTypeSearch=1&pThesauri=external.theme.GDI-Vlaanderen-trefwoorden&pKeyword=*" + unicode(q).encode('utf-8') +"*"
        try:
            if self.opener: response = self.opener.open(url, timeout=self.timeout)
            else: response = urllib2.urlopen(url, timeout=self.timeout)
        except  (urllib2.HTTPError, urllib2.URLError) as e:
            raise metaError( str( e.reason ))
        except:
            raise metaError( str( sys.exc_info()[1] ))
        else:
            result = ET.parse(response)
            r= result.getroot()
            themes = [ n.find("value").text for n in  r[0].findall('keyword') ]
            themes.sort()
            return themes
          
    def list_inspire_theme(self, q=''):
        url = self.geoNetworkUrl + "/xml.search.keywords?pNewSearch=true&pTypeSearch=1&pThesauri=external.theme.inspire-theme&pKeyword=*" + unicode(q).encode('utf-8') +"*"
        try:
            if self.opener: response = self.opener.open(url, timeout=self.timeout)
            else: response = urllib2.urlopen(url, timeout=self.timeout)
        except  (urllib2.HTTPError, urllib2.URLError) as e:
            raise metaError( str( e.reason ))
        except:
            raise metaError( str( sys.exc_info()[1] ))
        else:
            result = ET.parse(response)
            r= result.getroot()
            themes = [ n.find("value").text for n in  r[0].findall('keyword') ]
            themes.sort()
            return themes
    
    def list_suggestionKeyword(self, q=''):
        url = self.geoNetworkUrl + "/main.search.suggest?field=any" 
        if q:
            url= url + "&q=" + unicode(q).encode('utf-8') 
        
        try:
            if self.opener: response = self.opener.open(url, timeout=self.timeout)
            else: response = urllib2.urlopen(url, timeout=self.timeout)
        except  (urllib2.HTTPError, urllib2.URLError) as e:
            raise metaError( str( e.reason ))
        except:
            raise metaError( str( sys.exc_info()[1] ))
        else:
            result = json.load(response)
            return result[1]

    def list_organisations(self, q=''):
        url = self.geoNetworkUrl + "/main.search.suggest?field=orgName" 
        if q:
            url= url + "&q=" + unicode(q).encode('utf-8') 
        try:
            if self.opener: response = self.opener.open(url, timeout=self.timeout)
            else: response = urllib2.urlopen(url, timeout=self.timeout)
        except  (urllib2.HTTPError, urllib2.URLError) as e:
            raise metaError( str( e.reason ))
        except:
            raise metaError( str( sys.exc_info()[1] ))
        else:
            result = json.load(response)
            if len( result ) <= 2:
               organisations = result[1]
               organisations.sort()
               return organisations
            else:
               return []
               

    def list_bronnen(self):
        url = self.geoNetworkUrl + "/xml.info?type=sources"
        try:
            if self.opener: response = self.opener.open(url, timeout=self.timeout)
            else: response = urllib2.urlopen(url, timeout=self.timeout)
        except  (urllib2.HTTPError, urllib2.URLError) as e:
            raise metaError( str( e.reason ))
        except:
            raise metaError( str( sys.exc_info()[1] ))
        else:
            result = ET.parse(response)
            r= result.getroot()
            bronnen = [ ( n.find("uuid").text, n.find("name").text ) 
                     for n in  r[0].findall('source') ]
            bronnen.sort()
            return bronnen

    def search(self, q="", start=1, to=20, themekey='', orgName='', dataType='', siteId='', inspiretheme='', inspireannex='', inspireServiceType='' ):
        url = self._createFindUrl( q, start, to, themekey, orgName, dataType, siteId, inspiretheme, inspireannex, inspireServiceType)
        try:
            if self.opener: response = self.opener.open(url, timeout=self.timeout)
            else: response = urllib2.urlopen(url, timeout=self.timeout)
        except  (urllib2.HTTPError, urllib2.URLError) as e:
                raise metaError( str( e.reason ) +' on '+ url )
        except:
            raise metaError( str( sys.exc_info()[1] ))
        else:
            result = ET.parse(response)
            resultXML = result.getroot()
            return  resultXML

    def searchAll(self, q="", themekey='', orgName='', dataType='', siteId='', inspiretheme='', inspireannex='', inspireServiceType=''):
        start= 1
        step= 100        
        searchResult = self.search(q, start, step, themekey, orgName, dataType, siteId, inspiretheme, inspireannex, inspireServiceType)
        count = int( searchResult[0].attrib["count"] )
        start += step
        while (start) <= count:  #https://metadata.geopunt.be/zoekdienst/srv/dut/q?fast=index&sortBy=changeDate&to=&from=Herbruikbaar&any=%2A%2A'
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

      
def getWmsLayerNames( url, proxyUrl=''):
    if (not "request=GetCapabilities" in url.lower()) or (not "service=wms" in url.lower()):
      capability = url.split("?")[0] + "?request=GetCapabilities&version=1.3.0&service=wms"
    else:
      capability = url

    if (isinstance(proxyUrl, unicode) or isinstance(proxyUrl, str)) and proxyUrl:
      proxy = urllib2.ProxyHandler({'http': proxyUrl ,'https': proxyUrl })
      opener = urllib2.build_opener(proxy)
      responseWMS =  opener.open(capability)
    else:
      responseWMS =  urllib2.urlopen(capability)

    result = ET.parse(responseWMS)
    layers =  result.findall( ".//{http://www.opengis.net/wms}Layer" )
    layerNames=[]

    for lyr in layers:
      name= lyr.find("{http://www.opengis.net/wms}Name")
      title = lyr.find("{http://www.opengis.net/wms}Title")
      style = lyr.find("{http://www.opengis.net/wms}Style/{http://www.opengis.net/wms}Name")
      if ( name != None) and ( title != None ):
         if style == None: layerNames.append(( name.text, title.text, ''))
         else: layerNames.append(( name.text, title.text, style.text))

    return layerNames

def getWFSLayerNames( url, proxyUrl=''):
      if (not "request=GetCapabilities" in url.lower()) or (not "service=wfs" in url.lower()):
          capability = url.split("?")[0] + "?request=GetCapabilities&version=1.0.0&service=wfs"
      else: 
          capability = url
      if (isinstance(proxyUrl, unicode) or isinstance(proxyUrl, str)) and proxyUrl:
          proxy = urllib2.ProxyHandler({'http': proxyUrl ,'https': proxyUrl })
          opener = urllib2.build_opener(proxy)
          responseWFS =  opener.open(capability)
      else:
          responseWFS =  urllib2.urlopen(capability)
      
      result = ET.parse(responseWFS)
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

def getWMTSlayersNames( url, proxyUrl='' ):
    if (not "request=getcapabilities" in url.lower()) or (not "service=wmts" in url.lower()):
        capability = url.split("?")[0] + "?service=WMTS&request=Getcapabilities"
    else:
        capability = url
    if (isinstance(proxyUrl, unicode) or isinstance(proxyUrl, str)) and proxyUrl:
        proxy = urllib2.ProxyHandler({'http': proxyUrl, 'https': proxyUrl })
        auth = urllib2.HTTPBasicAuthHandler()
        opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler)
        responseWMTS =  opener.open(capability)
    else:
        responseWMTS =  urllib2.urlopen(capability)

    result = ET.parse(responseWMTS).getroot()
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

def getWCSlayerNames( url, proxyUrl='' ):
    wcsNS = "http://www.opengis.net/wcs/1.1"

    if (not "request=getcapabilities" in url.lower()) or (not "service=wcs" in url.lower()):
      capability = url.split("?")[0] + "?request=GetCapabilities&version=1.1.0&service=wcs"
    else:
      capability = url
    if (isinstance(proxyUrl, unicode) or isinstance(proxyUrl, str)) and proxyUrl:
      proxy = urllib2.ProxyHandler({'http': proxyUrl, 'https': proxyUrl})
      auth = urllib2.HTTPBasicAuthHandler()
      opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler)
      responseWCS =  opener.open(capability)
    else:
      responseWCS =  urllib2.urlopen(capability)

    responseTxt = responseWCS.read()
    if 'xmlns:wcs="http://www.opengis.net/wcs/1.1.1"' in responseTxt:
        wcsNS = "http://www.opengis.net/wcs/1.1.1"

    result = ET.fromstring(responseTxt)
    content = result.find( "{%s}Contents" % wcsNS)
    layers =  content.findall( "{%s}CoverageSummary" % wcsNS)
    layerNames = []

    for lyr in layers:
       Identifier= lyr.find("{%s}Identifier" % wcsNS)
       title = lyr.find("{http://www.opengis.net/ows/1.1}Title")

       DescribeCoverage = url.split("?")[0] + "?request=DescribeCoverage&version=1.1.0&service=wcs&Identifiers=" + Identifier.text
       if (isinstance(proxyUrl, unicode) or isinstance(proxyUrl, str)) and proxyUrl:
         proxy = urllib2.ProxyHandler({'http': proxyUrl, 'https': proxyUrl})
         auth = urllib2.HTTPBasicAuthHandler()
         opener = urllib2.build_opener(proxy, auth, urllib2.HTTPHandler)
         responseDC =  opener.open(DescribeCoverage)
       else:
         responseDC =  urllib2.urlopen(DescribeCoverage)

       resultDC = ET.parse(responseDC).getroot()
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

    uri = url.split('?')[0] + '?' + urllib.unquote( urllib.urlencode(params) )
    return uri

def makeWMTSuri( url, layer, tileMatrixSet, srsname="EPSG:3857", styles='', format='image/png' ):
    params = {  'tileMatrixSet': tileMatrixSet,
                'styles': styles,
                'format': format ,
                'layers': layer,
                'crs': srsname,
                'url': url.split('?')[0]  + '?service=WMTS'}

    uri = urllib.unquote( urllib.urlencode(params)  )
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

    uri = urllib.unquote( urllib.urlencode(params)  )
    return uri
