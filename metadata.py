import urllib2, urllib, json, sys, os.path, datetime
import xml.etree.ElementTree as ET

class metaError(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)


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
              record['geoBox'] = None
           
           record['wms'] = self._findWMS( md )
           
           record['download'] = self._findDownload( md )
           
           self.records.append(record)
           
    def _findWMS(self , node ):
        links =  "|".join( [ n.text for n in node.findall("link") ] )
        links = links.split('|') 
        for n in range(len( links )):
            if "OGC:WMS" in links[n].upper(): 
              return links[n - 1]
        return None

    def _findDownload(self , node):
        links =  "|".join( [ n.text for n in node.findall("link") ] )
        links = links.split('|') 
        for n in range( len( links )):
            if "WWW:DOWNLOAD" in links[n].upper(): 
              return links[n - 1] 
        return None


class MDReader:
    def __init__(self, timeout=15, proxyUrl="", port="" ):
        self.timeout = timeout
        self.geoNetworkUrl = "https://metadata.geopunt.be/zoekdienst/srv/dut"

        self.inspireServiceTypes =  ["other","invoke","discovery","transformation","view"]
        self.inspireannex =  ["i","ii","iii"]

        if (proxyUrl <> "")  & proxyUrl.startswith("http://"):
            netLoc = proxyUrl.strip() + ":" + port
            proxy = urllib2.ProxyHandler({'http': netLoc })
            self.opener = urllib2.build_opener(proxy)
        else:
            self.opener = None

    def _createFindUrl(self, q="", start=1, to=20, themekey='', orgName='', inspiretheme='', inspireannex='',  serviceType=''):
        geopuntUrl = self.geoNetworkUrl + "/q?fast=index&sortBy=changeDate&"
        data = {}
        data["any"] = "*" + unicode(q).encode('utf-8') + "*"
        data["from"] = start
        data["to"] = to

        if themekey: 
            if " " in themekey and not " or " in themekey.lower():
                data["themekey"] = '"' +  themekey.lower()  + '"'
            else: 
                data["themekey"] = themekey.lower()
        if orgName: 
            if " " in orgName:
                data["orgName"] = '"' +  orgName.lower() + '"' 
            else: 
                data["orgName"] = orgName.lower()
        if inspiretheme: 
            if " " in orgName:
                data["inspiretheme"] = '"' +  inspiretheme + '"' 
            else: 
                data["inspiretheme"] = inspiretheme
                
        if inspireannex and (inspireannex.lower() in self.inspireannex ) : 
            data["inspireannex"] = inspireannex.lower()
        if serviceType and (serviceType.lower()in self.inspireServiceTypes): 
            data["serviceType"] = serviceType.lower() 

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
            return [ n.find("value").text for n in  r[0].findall('keyword') ]
          
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
            return [ n.find("value").text for n in  r[0].findall('keyword') ]
    
    def suggestionKeyword(self, q=''):
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

    def list_orgnisations(self, q=''):
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
            return result[1]

    def search(self, q="", start=1, to=20, themekey='', orgName='', inspiretheme='', inspireannex='', serviceType='' ):
        url = self._createFindUrl( q, start, to, themekey, orgName, inspiretheme, inspireannex, serviceType )
        try:
            if self.opener: response = self.opener.open(url, timeout=self.timeout)
            else: response = urllib2.urlopen(url, timeout=self.timeout)
        except  (urllib2.HTTPError, urllib2.URLError) as e:
                raise metaError( str( e.reason ))
        except:
            raise metaError( str( sys.exc_info()[1] ))
        else:
            result = ET.parse(response)
            resultXML = result.getroot()
            return  MDdata( resultXML )

        
def getWmsLayerNames( url):
      if (not "request=GetCapabilities" in url.lower()) or (not "service=wms" in url.lower()):
          capability = url.split("?")[0] + "?request=GetCapabilities&version=1.3.0&service=wms"
      else: 
          capability = url
      responseWMS =  urllib2.urlopen(capability)
      result = ET.parse(responseWMS)
      layers =  result.findall( ".//{http://www.opengis.net/wms}Layer" )
      layerNames=[]

      for lyr in layers:
          name= lyr.find("{http://www.opengis.net/wms}Name")
          title = lyr.find("{http://www.opengis.net/wms}Title")
          style = lyr.find("{http://www.opengis.net/wms}Style/{http://www.opengis.net/wms}Name")
          if ( name != None) and ( title != None ) and ( style != None ):
             layerNames.append(( name.text, title.text, style.text))

      return layerNames
    
        